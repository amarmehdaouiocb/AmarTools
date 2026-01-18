"""
STT GUI - Interface graphique avec visualisation audio et arrêt automatique sur silence
"""
import tkinter as tk
import threading
import numpy as np
import time
import os
import sys
import ctypes

# Add the venv site-packages to path
venv_path = os.path.join(os.path.expanduser("~"), ".claude", "plugins", "cache",
                         "jarrodwatts-claude-stt", "claude-stt", "0.1.0", ".venv",
                         "Lib", "site-packages")
sys.path.insert(0, venv_path)

import sounddevice as sd

# Configuration
SAMPLE_RATE = 16000
CHANNELS = 1
SILENCE_THRESHOLD = 0.008  # Seuil de silence
SILENCE_DURATION = 1.0     # Secondes de silence avant arrêt auto
CHUNK_SIZE = 1024

# Windows API pour focus et moniteurs
user32 = ctypes.windll.user32
shcore = ctypes.windll.shcore

# Structures pour l'API Windows
class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long),
                ("top", ctypes.c_long),
                ("right", ctypes.c_long),
                ("bottom", ctypes.c_long)]

class MONITORINFO(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_ulong),
                ("rcMonitor", RECT),
                ("rcWork", RECT),
                ("dwFlags", ctypes.c_ulong)]

class STTApp:
    def __init__(self, initial_hwnd=None):
        self.initial_hwnd = initial_hwnd  # Fenêtre active au démarrage
        self.root = tk.Tk()
        self.root.title("🎤 STT")
        self.root.geometry("280x180")
        self.root.resizable(False, False)
        self.root.attributes('-topmost', True)
        self.root.configure(bg='#1a1a2e')

        # State
        self.is_recording = False
        self.audio_data = []
        self.current_level = 0.0
        self.last_sound_time = 0
        self.stream = None
        self.transcribing = False
        self.loading_model = False  # Pour éviter les clics multiples pendant le chargement
        self.target_window = None  # Fenêtre où coller le texte
        self.last_external_window = initial_hwnd  # Dernière fenêtre externe (non-GUI)
        self.my_hwnd = None  # HWND de notre propre fenêtre

        # Whisper model (lazy load)
        self._model = None

        self._create_ui()
        self._position_window()

        # Récupérer notre propre HWND après création de la fenêtre
        self.root.after(100, self._capture_my_hwnd)

        # Surveiller la fenêtre active en permanence
        self._track_focus()

        # Pré-charger le modèle en arrière-plan
        threading.Thread(target=self._preload_model, daemon=True).start()

    def _capture_my_hwnd(self):
        """Capture le HWND de notre propre fenêtre GUI"""
        self.my_hwnd = user32.GetForegroundWindow()

    def _track_focus(self):
        """Surveille la fenêtre active et garde la dernière fenêtre externe"""
        if not self.is_recording and not self.transcribing:
            current = user32.GetForegroundWindow()
            # Si ce n'est pas notre fenêtre GUI, mémoriser
            if current and current != self.my_hwnd:
                self.last_external_window = current
        # Continuer à surveiller
        self.root.after(100, self._track_focus)

    def _position_window(self):
        """Position en haut à droite de l'écran où se trouve la fenêtre active"""
        self.root.update_idletasks()

        try:
            # Utiliser la fenêtre capturée au démarrage (le terminal)
            hwnd = self.initial_hwnd or user32.GetForegroundWindow()

            # Trouver le moniteur de cette fenêtre
            MONITOR_DEFAULTTONEAREST = 2
            monitor = user32.MonitorFromWindow(hwnd, MONITOR_DEFAULTTONEAREST)

            # Récupérer les infos du moniteur
            mi = MONITORINFO()
            mi.cbSize = ctypes.sizeof(MONITORINFO)
            user32.GetMonitorInfoW(monitor, ctypes.byref(mi))

            # Zone de travail du moniteur (sans la taskbar)
            work_left = mi.rcWork.left
            work_top = mi.rcWork.top
            work_right = mi.rcWork.right

            # Dimensions de notre fenêtre
            win_width = self.root.winfo_width() or 280
            win_height = self.root.winfo_height() or 180

            # Position en haut à droite avec marge de 20px
            x = work_right - win_width - 20
            y = work_top + 20

        except Exception:
            # Fallback: haut à droite de l'écran principal
            screen_w = self.root.winfo_screenwidth()
            x = screen_w - 300
            y = 20

        self.root.geometry(f"+{x}+{y}")

    def _create_ui(self):
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#1a1a2e')
        main_frame.pack(expand=True, fill='both', padx=15, pady=15)

        # Titre
        title = tk.Label(main_frame, text="Voice to Text",
                        font=('Segoe UI', 12, 'bold'),
                        fg='#eee', bg='#1a1a2e')
        title.pack(pady=(0, 10))

        # Canvas pour visualisation audio
        self.canvas = tk.Canvas(main_frame, width=250, height=50,
                               bg='#16213e', highlightthickness=1,
                               highlightbackground='#0f3460')
        self.canvas.pack(pady=(0, 10))

        # Barres de visualisation
        self.bars = []
        bar_width = 6
        bar_spacing = 2
        num_bars = 30
        start_x = (250 - (num_bars * (bar_width + bar_spacing))) // 2
        for i in range(num_bars):
            x = start_x + i * (bar_width + bar_spacing)
            bar = self.canvas.create_rectangle(x, 45, x + bar_width, 47,
                                               fill='#e94560', outline='')
            self.bars.append(bar)

        # Frame pour boutons
        btn_frame = tk.Frame(main_frame, bg='#1a1a2e')
        btn_frame.pack(pady=(5, 0))

        # Bouton Record
        self.record_btn = tk.Button(btn_frame, text="🎤 Record",
                                   font=('Segoe UI', 11, 'bold'),
                                   fg='white', bg='#e94560',
                                   activebackground='#ff6b6b',
                                   activeforeground='white',
                                   relief='flat', cursor='hand2',
                                   width=12, height=1,
                                   command=self.toggle_recording)
        self.record_btn.pack(side='left', padx=5)

        # Bouton Close
        close_btn = tk.Button(btn_frame, text="✕",
                             font=('Segoe UI', 10),
                             fg='#888', bg='#1a1a2e',
                             activebackground='#2a2a4e',
                             activeforeground='white',
                             relief='flat', cursor='hand2',
                             width=3,
                             command=self.root.quit)
        close_btn.pack(side='left', padx=5)

        # Status label
        self.status_var = tk.StringVar(value="Cliquez pour enregistrer")
        self.status_label = tk.Label(main_frame, textvariable=self.status_var,
                                    font=('Segoe UI', 9),
                                    fg='#888', bg='#1a1a2e')
        self.status_label.pack(pady=(10, 0))

    def _preload_model(self):
        """Pré-charge le modèle au démarrage"""
        self.root.after(0, lambda: self.status_var.set("Chargement du modèle..."))
        self.root.after(0, lambda: self.record_btn.configure(state='disabled', text="⏳ Loading..."))
        try:
            from faster_whisper import WhisperModel
            device = os.environ.get("CLAUDE_STT_WHISPER_DEVICE", "cuda")
            compute_type = os.environ.get("CLAUDE_STT_WHISPER_COMPUTE_TYPE", "float16")
            self._model = WhisperModel("large-v3", device=device, compute_type=compute_type)
            self.root.after(0, lambda: self.status_var.set("Prêt ✓"))
            self.root.after(0, lambda: self.record_btn.configure(state='normal', text="🎤 Record"))
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"Erreur: {e}"))
            self.root.after(0, lambda: self.record_btn.configure(state='normal', text="🎤 Record"))

    def _load_model(self):
        """Charge le modèle Whisper (si pas déjà chargé)"""
        if self._model is None:
            self.loading_model = True
            self.record_btn.configure(state='disabled', text="⏳ Loading...")
            self.status_var.set("Chargement du modèle...")
            self.root.update()
            try:
                from faster_whisper import WhisperModel
                device = os.environ.get("CLAUDE_STT_WHISPER_DEVICE", "cuda")
                compute_type = os.environ.get("CLAUDE_STT_WHISPER_COMPUTE_TYPE", "float16")
                self._model = WhisperModel("large-v3", device=device, compute_type=compute_type)
                self.status_var.set("Modèle prêt ✓")
                self.record_btn.configure(state='normal', text="🎤 Record")
            except Exception as e:
                self.status_var.set(f"Erreur: {e}")
                self.record_btn.configure(state='normal', text="🎤 Record")
                self.loading_model = False
                return False
            finally:
                self.loading_model = False
        return True

    def _get_foreground_window(self):
        """Récupère la fenêtre active actuelle"""
        return user32.GetForegroundWindow()

    def _set_foreground_window(self, hwnd):
        """Remet le focus sur une fenêtre"""
        if hwnd:
            user32.SetForegroundWindow(hwnd)

    def toggle_recording(self):
        if self.transcribing or self.loading_model:
            return

        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        if not self._load_model():
            return

        # Utiliser la dernière fenêtre externe qui avait le focus
        self.target_window = self.last_external_window

        self.is_recording = True
        self.audio_data = []
        self.current_level = 0.0
        self.last_sound_time = time.time()

        self.record_btn.configure(text="⏹ Stop", bg='#ff6b6b')
        self.status_var.set("🔴 Parlez maintenant...")

        # Start audio stream
        self.stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype=np.float32,
            blocksize=CHUNK_SIZE,
            callback=self._audio_callback
        )
        self.stream.start()

        # Start visualization update
        self._update_visualization()

    def _audio_callback(self, indata, frames, time_info, status):
        """Callback pour capture audio"""
        if self.is_recording:
            self.audio_data.append(indata.copy())

            # Calculer le niveau pour la visualisation
            level = np.abs(indata).mean()
            self.current_level = level

            # Détecter le silence pour arrêt auto
            if level > SILENCE_THRESHOLD:
                self.last_sound_time = time.time()
            else:
                silence_time = time.time() - self.last_sound_time
                if silence_time >= SILENCE_DURATION and len(self.audio_data) > 20:
                    # Arrêt auto après silence
                    self.root.after(0, self.stop_recording)

    def _update_visualization(self):
        """Met à jour la visualisation audio"""
        if not self.is_recording:
            # Reset bars
            for bar in self.bars:
                coords = self.canvas.coords(bar)
                self.canvas.coords(bar, coords[0], 45, coords[2], 47)
                self.canvas.itemconfig(bar, fill='#e94560')
            return

        level = self.current_level * 80  # Scale for visualization

        # Update bars with wave effect
        for i, bar in enumerate(self.bars):
            coords = self.canvas.coords(bar)
            # Create wave effect with some variation
            wave_offset = np.sin(time.time() * 10 + i * 0.3) * 0.3
            bar_level = max(2, min(43, level * (0.6 + wave_offset + np.random.random() * 0.4)))
            new_top = 47 - bar_level
            self.canvas.coords(bar, coords[0], new_top, coords[2], 47)

            # Color based on level
            if level > 1.5:
                color = '#e94560'  # Rouge - fort
            elif level > 0.5:
                color = '#f39c12'  # Orange - moyen
            else:
                color = '#3498db'  # Bleu - faible
            self.canvas.itemconfig(bar, fill=color)

        self.root.after(30, self._update_visualization)

    def stop_recording(self):
        if not self.is_recording:
            return

        self.is_recording = False

        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        self.record_btn.configure(text="🎤 Record", bg='#e94560')

        # Reset visualization
        for bar in self.bars:
            coords = self.canvas.coords(bar)
            self.canvas.coords(bar, coords[0], 45, coords[2], 47)
            self.canvas.itemconfig(bar, fill='#e94560')

        # Transcribe
        if self.audio_data and len(self.audio_data) > 10:
            self.transcribing = True
            self.status_var.set("⏳ Transcription...")
            self.root.update()

            threading.Thread(target=self._transcribe, daemon=True).start()
        else:
            self.status_var.set("Cliquez pour enregistrer")

    def _transcribe(self):
        """Transcrit l'audio et colle dans la fenêtre cible"""
        try:
            # Concatenate audio
            audio = np.concatenate(self.audio_data, axis=0).flatten()

            # Transcribe
            segments, _ = self._model.transcribe(audio, language="fr")
            text = " ".join(segment.text.strip() for segment in segments).strip()

            if text:
                self.root.after(0, lambda: self._paste_text(text))
            else:
                self.root.after(0, lambda: self.status_var.set("Aucun texte détecté"))
                self.transcribing = False

        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"Erreur: {str(e)[:30]}"))
            self.transcribing = False
        finally:
            self.audio_data = []

    def _paste_text(self, text):
        """Colle le texte dans la fenêtre qui avait le focus"""
        try:
            # Copier dans le presse-papier
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.root.update()

            # Remettre le focus sur la fenêtre d'origine (le terminal)
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

            self.status_var.set(f"✓ {text[:35]}{'...' if len(text) > 35 else ''}")

        except Exception as e:
            self.status_var.set(f"Erreur paste: {e}")
        finally:
            self.transcribing = False

    def run(self):
        # Drag support (seulement sur le titre, pas les boutons)
        self._drag_data = {"x": 0, "y": 0}

        # On attache le drag au canvas et au label titre
        for widget in [self.canvas]:
            widget.bind("<Button-1>", self._on_drag_start)
            widget.bind("<B1-Motion>", self._on_drag_motion)

        self.root.mainloop()

    def _on_drag_start(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def _on_drag_motion(self, event):
        x = self.root.winfo_x() + event.x - self._drag_data["x"]
        y = self.root.winfo_y() + event.y - self._drag_data["y"]
        self.root.geometry(f"+{x}+{y}")

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--hwnd', type=int, default=0, help='Handle de la fenêtre cible')
    args = parser.parse_args()

    # Set environment for GPU
    os.environ.setdefault("CLAUDE_STT_WHISPER_DEVICE", "cuda")
    os.environ.setdefault("CLAUDE_STT_WHISPER_COMPUTE_TYPE", "float16")

    # Utiliser le HWND passé en argument, sinon capturer la fenêtre active
    if args.hwnd:
        initial_hwnd = args.hwnd
    else:
        initial_hwnd = user32.GetForegroundWindow()

    app = STTApp(initial_hwnd=initial_hwnd)
    app.run()
