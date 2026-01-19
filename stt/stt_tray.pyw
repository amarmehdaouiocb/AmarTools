"""
STT Tray - Daemon systray avec visualisation dans la statusline Claude Code

Variables d'environnement :
- CLAUDE_STT_WHISPER_DEVICE : "cuda" (défaut) ou "cpu"
- CLAUDE_STT_WHISPER_COMPUTE_TYPE : "float16" (défaut), "int8", "int8_float16"
- CLAUDE_STT_WHISPER_MODEL : "large-v3" (défaut), "medium", "small", "base", "tiny"
- CLAUDE_STT_UNLOAD_DELAY : secondes avant déchargement auto du modèle (0 = jamais, défaut)
"""
import threading
import numpy as np
import time
import os
import sys
import ctypes
import tempfile

# Add the venv site-packages to path
venv_path = os.path.join(os.path.expanduser("~"), ".claude", "plugins", "cache",
                         "jarrodwatts-claude-stt", "claude-stt", "0.1.0", ".venv",
                         "Lib", "site-packages")
sys.path.insert(0, venv_path)

import sounddevice as sd
from pynput import mouse
from PIL import Image, ImageDraw
import pystray

# Configuration
SAMPLE_RATE = 16000
CHANNELS = 1
SILENCE_THRESHOLD = 0.008  # Seuil de silence
SILENCE_DURATION = 1.0     # Secondes de silence avant arrêt auto
CHUNK_SIZE = 1024
UNLOAD_DELAY = int(os.environ.get("CLAUDE_STT_UNLOAD_DELAY", "0"))  # 0 = jamais décharger

# Fichier de prompt pour Whisper (vocabulaire technique)
PROMPT_FILE = os.path.join(os.path.expanduser("~"), ".claude", "plugins", "claude-stt", "prompt.txt")

# Fichier de statut pour la statusline Claude Code
STATUS_FILE = os.path.join(os.path.expanduser("~"), ".claude", "plugins", "claude-stt", "status")

# Windows API pour focus
user32 = ctypes.windll.user32


class STTTray:
    """Application STT avec icône systray"""

    # Couleurs pour les icônes
    COLOR_IDLE = (128, 128, 128)       # Gris - prêt
    COLOR_RECORDING = (220, 50, 50)     # Rouge - enregistrement
    COLOR_TRANSCRIBING = (255, 165, 0)  # Orange - transcription
    COLOR_ERROR = (255, 200, 0)         # Jaune - erreur
    COLOR_LOADING = (100, 100, 200)     # Bleu - chargement

    def __init__(self, initial_hwnd=None):
        self.initial_hwnd = initial_hwnd

        # État
        self.is_recording = False
        self.audio_data = []
        self.current_level = 0.0
        self.last_sound_time = 0
        self.stream = None
        self.transcribing = False
        self.loading_model = False
        self.target_window = None
        self.last_external_window = initial_hwnd
        self.running = True
        self.status = "idle"  # idle, loading, recording, transcribing, error
        self.last_model_use = 0  # Timestamp dernière utilisation du modèle

        # Whisper model (lazy load)
        self._model = None
        self._whisper_prompt = self._load_prompt()

        # Créer l'icône systray
        self.icon = self._create_tray_icon()

        # Listener souris global (clic molette)
        self.mouse_listener = mouse.Listener(on_click=self._on_mouse_click)
        self.mouse_listener.start()

        # Thread pour surveiller la fenêtre active
        self.focus_thread = threading.Thread(target=self._track_focus_loop, daemon=True)
        self.focus_thread.start()

        # Pré-charger le modèle en arrière-plan
        threading.Thread(target=self._preload_model, daemon=True).start()

        # Thread de déchargement auto si configuré
        if UNLOAD_DELAY > 0:
            self.unload_thread = threading.Thread(target=self._unload_loop, daemon=True)
            self.unload_thread.start()

    def _load_prompt(self):
        """Charge le fichier prompt.txt pour le vocabulaire technique Whisper"""
        try:
            if os.path.exists(PROMPT_FILE):
                with open(PROMPT_FILE, 'r', encoding='utf-8') as f:
                    lines = []
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            lines.append(line)
                    prompt = ', '.join(lines)
                    return prompt if prompt else None
        except Exception:
            pass
        return None

    def _create_icon_image(self, color):
        """Crée une icône de microphone avec la couleur spécifiée"""
        size = 64
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Dessiner un microphone simplifié
        # Corps du micro (rectangle arrondi)
        mic_left = size // 3
        mic_right = 2 * size // 3
        mic_top = size // 6
        mic_bottom = size // 2 + size // 6
        draw.rounded_rectangle(
            [(mic_left, mic_top), (mic_right, mic_bottom)],
            radius=size // 8,
            fill=color
        )

        # Grille du micro (3 lignes horizontales)
        line_color = (min(color[0] + 40, 255), min(color[1] + 40, 255), min(color[2] + 40, 255))
        for i in range(3):
            y = mic_top + (mic_bottom - mic_top) // 4 * (i + 1)
            draw.line([(mic_left + 4, y), (mic_right - 4, y)], fill=line_color, width=2)

        # Arc inférieur (support du micro)
        arc_top = mic_bottom - size // 8
        arc_bottom = mic_bottom + size // 6
        draw.arc(
            [(mic_left - size // 8, arc_top), (mic_right + size // 8, arc_bottom + size // 12)],
            start=0, end=180,
            fill=color,
            width=3
        )

        # Pied du micro
        center_x = size // 2
        draw.line(
            [(center_x, arc_bottom + size // 16), (center_x, size - size // 8)],
            fill=color,
            width=3
        )

        # Base du micro
        base_width = size // 4
        draw.line(
            [(center_x - base_width // 2, size - size // 8),
             (center_x + base_width // 2, size - size // 8)],
            fill=color,
            width=3
        )

        return image

    def _create_tray_icon(self):
        """Crée l'icône systray avec le menu"""
        icon = pystray.Icon(
            "stt",
            self._create_icon_image(self.COLOR_LOADING),
            "STT - Chargement...",
            menu=pystray.Menu(
                pystray.MenuItem("Toggle Record (Clic molette)", self._toggle_recording_menu),
                pystray.MenuItem("Status: Chargement...", None, enabled=False),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Quitter", self._quit)
            )
        )
        return icon

    def _update_icon(self):
        """Met à jour l'icône et le tooltip selon l'état"""
        if self.status == "loading":
            color = self.COLOR_LOADING
            tooltip = "STT - Chargement du modèle..."
            status_text = "Status: Chargement..."
        elif self.status == "recording":
            color = self.COLOR_RECORDING
            tooltip = "STT - Enregistrement en cours..."
            status_text = "Status: Enregistrement"
        elif self.status == "transcribing":
            color = self.COLOR_TRANSCRIBING
            tooltip = "STT - Transcription en cours..."
            status_text = "Status: Transcription"
        elif self.status == "error":
            color = self.COLOR_ERROR
            tooltip = "STT - Erreur"
            status_text = "Status: Erreur"
        else:  # idle
            color = self.COLOR_IDLE
            tooltip = "STT - Prêt (Clic molette pour enregistrer)"
            status_text = "Status: Prêt"

        self.icon.icon = self._create_icon_image(color)
        self.icon.title = tooltip

        # Mettre à jour le menu
        self.icon.menu = pystray.Menu(
            pystray.MenuItem("Toggle Record (Clic molette)", self._toggle_recording_menu),
            pystray.MenuItem(status_text, None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quitter", self._quit)
        )

    def _write_status(self, state):
        """Écrit l'état pour la statusline Claude Code (écriture atomique)"""
        status_dir = os.path.dirname(STATUS_FILE)
        if not os.path.exists(status_dir):
            os.makedirs(status_dir, exist_ok=True)

        if state:
            # Écriture atomique : temp file + rename
            temp_file = STATUS_FILE + ".tmp"
            with open(temp_file, 'w') as f:
                f.write(state)
            os.replace(temp_file, STATUS_FILE)
        else:
            if os.path.exists(STATUS_FILE):
                try:
                    os.remove(STATUS_FILE)
                except Exception:
                    pass

    def _set_status(self, status):
        """Change l'état et met à jour l'icône + fichier status"""
        self.status = status
        self._update_icon()

        # Mettre à jour le fichier status pour la statusline
        if status == "recording":
            self._write_status("recording")
        elif status == "transcribing":
            self._write_status("transcribing")
        else:
            self._write_status(None)  # Supprimer le fichier

    def _track_focus_loop(self):
        """Surveille la fenêtre active en boucle"""
        while self.running:
            if not self.is_recording and not self.transcribing:
                try:
                    current = user32.GetForegroundWindow()
                    if current:
                        self.last_external_window = current
                except Exception:
                    pass
            time.sleep(0.1)

    def _unload_loop(self):
        """Surveille l'inactivité et décharge le modèle si nécessaire"""
        while self.running:
            if (self._model is not None and
                self.last_model_use > 0 and
                not self.is_recording and
                not self.transcribing and
                not self.loading_model):
                idle_time = time.time() - self.last_model_use
                if idle_time >= UNLOAD_DELAY:
                    self._unload_model()
            time.sleep(10)  # Vérifier toutes les 10 secondes

    def _unload_model(self):
        """Décharge le modèle pour libérer la mémoire"""
        if self._model is not None:
            print(f"Déchargement du modèle après {UNLOAD_DELAY}s d'inactivité...")
            del self._model
            self._model = None
            self.last_model_use = 0
            # Forcer le garbage collector
            import gc
            gc.collect()
            # Libérer la mémoire CUDA si disponible
            try:
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            except ImportError:
                pass
            print("Modèle déchargé, mémoire libérée.")

    def _preload_model(self):
        """Pré-charge le modèle Whisper au démarrage"""
        self._set_status("loading")
        try:
            from faster_whisper import WhisperModel
            device = os.environ.get("CLAUDE_STT_WHISPER_DEVICE", "cuda")
            compute_type = os.environ.get("CLAUDE_STT_WHISPER_COMPUTE_TYPE", "float16")
            model_size = os.environ.get("CLAUDE_STT_WHISPER_MODEL", "large-v3")
            # Optimisations RAM : réduire threads CPU et workers
            self._model = WhisperModel(
                model_size,
                device=device,
                compute_type=compute_type,
                cpu_threads=1,      # Réduit l'empreinte RAM
                num_workers=1,      # Un seul worker
            )
            self.last_model_use = time.time()
            self._set_status("idle")
        except Exception as e:
            print(f"Erreur chargement modèle: {e}")
            self._set_status("error")

    def _load_model(self):
        """Charge le modèle Whisper (si pas déjà chargé)"""
        if self._model is None:
            self.loading_model = True
            self._set_status("loading")
            try:
                from faster_whisper import WhisperModel
                device = os.environ.get("CLAUDE_STT_WHISPER_DEVICE", "cuda")
                compute_type = os.environ.get("CLAUDE_STT_WHISPER_COMPUTE_TYPE", "float16")
                model_size = os.environ.get("CLAUDE_STT_WHISPER_MODEL", "large-v3")
                # Optimisations RAM : réduire threads CPU et workers
                self._model = WhisperModel(
                    model_size,
                    device=device,
                    compute_type=compute_type,
                    cpu_threads=1,      # Réduit l'empreinte RAM
                    num_workers=1,      # Un seul worker
                )
                self.last_model_use = time.time()
                self._set_status("idle")
            except Exception as e:
                print(f"Erreur chargement modèle: {e}")
                self._set_status("error")
                self.loading_model = False
                return False
            finally:
                self.loading_model = False
        return True

    def _on_mouse_click(self, x, y, button, pressed):
        """Gère les clics souris globaux - clic molette = toggle record"""
        if button == mouse.Button.middle and pressed:
            threading.Thread(target=self.toggle_recording, daemon=True).start()

    def _toggle_recording_menu(self, icon, item):
        """Callback pour le menu toggle recording"""
        threading.Thread(target=self.toggle_recording, daemon=True).start()

    def toggle_recording(self):
        """Toggle l'enregistrement"""
        if self.transcribing or self.loading_model:
            return

        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        """Démarre l'enregistrement audio"""
        if not self._load_model():
            return

        # Mémoriser la fenêtre cible
        self.target_window = self.last_external_window

        self.is_recording = True
        self.audio_data = []
        self.current_level = 0.0
        self.last_sound_time = time.time()

        self._set_status("recording")

        # Démarrer le flux audio
        self.stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype=np.float32,
            blocksize=CHUNK_SIZE,
            callback=self._audio_callback
        )
        self.stream.start()

    def _audio_callback(self, indata, frames, time_info, status):
        """Callback pour capture audio"""
        if self.is_recording:
            self.audio_data.append(indata.copy())

            # Calculer le niveau
            level = np.abs(indata).mean()
            self.current_level = level

            # Détecter le silence pour arrêt auto
            if level > SILENCE_THRESHOLD:
                self.last_sound_time = time.time()
            else:
                silence_time = time.time() - self.last_sound_time
                if silence_time >= SILENCE_DURATION and len(self.audio_data) > 20:
                    # Arrêt auto après silence
                    threading.Thread(target=self.stop_recording, daemon=True).start()

    def stop_recording(self):
        """Arrête l'enregistrement et lance la transcription"""
        if not self.is_recording:
            return

        self.is_recording = False

        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        # Transcription
        if self.audio_data and len(self.audio_data) > 10:
            self.transcribing = True
            self._set_status("transcribing")
            threading.Thread(target=self._transcribe, daemon=True).start()
        else:
            self._set_status("idle")

    def _transcribe(self):
        """Transcrit l'audio et colle dans la fenêtre cible"""
        try:
            # Concaténer l'audio
            audio = np.concatenate(self.audio_data, axis=0).flatten()

            # Transcription avec prompt technique
            transcribe_kwargs = {"language": "fr"}
            if self._whisper_prompt:
                transcribe_kwargs["initial_prompt"] = self._whisper_prompt

            segments, _ = self._model.transcribe(audio, **transcribe_kwargs)
            text = " ".join(segment.text.strip() for segment in segments).strip()

            if text:
                self._paste_text(text)

        except Exception as e:
            print(f"Erreur transcription: {e}")
            self._set_status("error")
            time.sleep(2)
        finally:
            self.audio_data = []
            self.transcribing = False
            self.last_model_use = time.time()  # Marquer dernière utilisation
            self._set_status("idle")

    def _paste_text(self, text):
        """Colle le texte dans la fenêtre qui avait le focus"""
        try:
            import pyperclip
            pyperclip.copy(text)

            # Remettre le focus sur la fenêtre cible
            if self.target_window:
                user32.SetForegroundWindow(self.target_window)
                time.sleep(0.1)

            # Simuler Ctrl+V
            from pynput.keyboard import Controller, Key
            kb = Controller()
            kb.press(Key.ctrl)
            kb.press('v')
            kb.release('v')
            kb.release(Key.ctrl)

        except Exception as e:
            print(f"Erreur paste: {e}")

    def _quit(self, icon, item):
        """Quitte l'application"""
        self.running = False
        self._write_status(None)  # Supprimer le fichier status
        if self.mouse_listener:
            self.mouse_listener.stop()
        icon.stop()

    def run(self):
        """Lance l'application"""
        self.icon.run()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--hwnd', type=int, default=0, help='Handle de la fenêtre cible')
    args = parser.parse_args()

    # Variables d'environnement pour GPU
    os.environ.setdefault("CLAUDE_STT_WHISPER_DEVICE", "cuda")
    os.environ.setdefault("CLAUDE_STT_WHISPER_COMPUTE_TYPE", "float16")

    # HWND initial
    if args.hwnd:
        initial_hwnd = args.hwnd
    else:
        initial_hwnd = user32.GetForegroundWindow()

    app = STTTray(initial_hwnd=initial_hwnd)
    app.run()
