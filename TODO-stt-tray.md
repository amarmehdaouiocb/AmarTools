# Plan : STT System Tray + Visualisation au curseur

## Objectif

Remplacer le GUI fenêtre actuel par :
1. Une icône dans le **System Tray** (zone de notification Windows)
2. Une **visualisation au curseur** (onde/cercle pulsant) pendant l'enregistrement

---

## 1. System Tray avec pystray

### Installation

```powershell
pip install pystray Pillow
```

### Fonctionnalités

| Action | Comportement |
|--------|--------------|
| Clic gauche | Toggle enregistrement |
| Clic molette | Toggle enregistrement (comme maintenant) |
| Clic droit | Menu contextuel |
| Double-clic | Ouvrir les paramètres (optionnel) |

### Menu contextuel

- 🎤 Record / ⏹ Stop
- ⚙️ Paramètres (ouvrir prompt.txt)
- ❌ Quitter

### États de l'icône

| État | Icône |
|------|-------|
| Inactif | 🎤 Gris |
| Enregistrement | 🔴 Rouge pulsant |
| Transcription | ⏳ Orange |
| Erreur | ⚠️ Jaune |

### Code de base

```python
import pystray
from PIL import Image, ImageDraw

def create_icon(color='gray'):
    """Crée une icône de microphone"""
    size = 64
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    # Dessiner un cercle avec la couleur
    draw.ellipse([8, 8, size-8, size-8], fill=color)
    return image

def on_clicked(icon, item):
    """Gère les clics sur le menu"""
    if str(item) == "Record":
        toggle_recording()
    elif str(item) == "Quit":
        icon.stop()

# Créer l'icône
icon = pystray.Icon(
    "stt",
    create_icon(),
    "STT - Clic pour enregistrer",
    menu=pystray.Menu(
        pystray.MenuItem("Record", on_clicked, default=True),
        pystray.MenuItem("Quit", on_clicked)
    )
)

# Lancer dans un thread
icon.run()
```

---

## 2. Visualisation au curseur

### Approche recommandée : Fenêtre transparente flottante

Une petite fenêtre sans bordure qui :
- Apparaît uniquement pendant l'enregistrement
- Suit le curseur (avec un léger offset)
- Affiche une animation d'onde/cercle pulsant
- Disparaît à la fin de l'enregistrement

### Configuration tkinter pour transparence

```python
import tkinter as tk

root = tk.Tk()
root.overrideredirect(True)  # Pas de bordure
root.attributes('-topmost', True)  # Toujours devant
root.attributes('-transparentcolor', 'black')  # Fond transparent
root.wm_attributes('-alpha', 0.8)  # Opacité globale

# Fenêtre petite (ex: 80x80)
root.geometry("80x80")
```

### Suivre le curseur

```python
from pynput import mouse

def on_move(x, y):
    # Positionner la fenêtre près du curseur
    root.geometry(f"+{x + 20}+{y + 20}")

listener = mouse.Listener(on_move=on_move)
listener.start()
```

### Animation d'onde

Options :
1. **Cercles concentriques pulsants** - Plusieurs cercles qui s'agrandissent et disparaissent
2. **Barre audio style waveform** - Barres verticales animées (comme le GUI actuel mais miniature)
3. **Cercle avec niveau audio** - Un cercle dont la taille varie avec le volume

```python
# Exemple : cercle pulsant sur Canvas
canvas = tk.Canvas(root, width=80, height=80, bg='black', highlightthickness=0)
canvas.pack()

def animate_pulse():
    if is_recording:
        # Dessiner cercle avec taille basée sur current_level
        size = 20 + (current_level * 30)
        canvas.delete("all")
        canvas.create_oval(
            40 - size, 40 - size,
            40 + size, 40 + size,
            fill='#e94560', outline=''
        )
        root.after(30, animate_pulse)

```

---

## 3. Architecture proposée

```
stt_tray.pyw
├── TrayApp (classe principale)
│   ├── pystray.Icon (icône system tray)
│   ├── CursorOverlay (fenêtre transparente)
│   ├── WhisperTranscriber (transcription)
│   └── MouseListener (clic molette global)
```

### Flux

1. **Démarrage** : Icône apparaît dans le system tray (grise)
2. **Clic molette** :
   - Icône devient rouge
   - Overlay apparaît au curseur avec animation
   - Enregistrement démarre
3. **Clic molette (ou silence)** :
   - Overlay disparaît
   - Icône devient orange (transcription)
4. **Transcription terminée** :
   - Texte collé dans la fenêtre active
   - Icône redevient grise

---

## 4. Fichiers à créer/modifier

| Fichier | Action |
|---------|--------|
| `stt_tray.pyw` | Nouveau fichier principal |
| `stt_gui.pyw` | Garder comme backup/alternative |
| `prompt.txt` | Inchangé |
| `install.ps1` | Ajouter installation pystray + Pillow |
| `profile-functions.ps1` | Modifier alias `stt` pour lancer `stt_tray.pyw` |

---

## 5. Dépendances à ajouter

```powershell
pip install pystray Pillow
```

Pillow est nécessaire pour créer les icônes dynamiquement.

---

## 6. Étapes d'implémentation

1. [ ] Créer `stt_tray.pyw` avec icône system tray basique
2. [ ] Migrer la logique Whisper depuis `stt_gui.pyw`
3. [ ] Implémenter le changement d'icône selon l'état
4. [ ] Créer la fenêtre overlay transparente
5. [ ] Ajouter le suivi du curseur
6. [ ] Implémenter l'animation d'onde
7. [ ] Tester et ajuster les performances
8. [ ] Mettre à jour `install.ps1` et le profil PowerShell
9. [ ] Documenter dans README.md

---

## Notes

- Le clic molette global fonctionne déjà avec `pynput` (à réutiliser)
- Le code Whisper existant peut être repris tel quel
- Garder `stt_gui.pyw` comme fallback si besoin
