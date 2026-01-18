# AmarTools

Outils personnels pour le développement - Configuration terminal complète.

## Installation rapide (tout-en-un)

```powershell
git clone https://github.com/amarmehdaouiocb/AmarTools.git
cd AmarTools\terminal
powershell -ExecutionPolicy Bypass -File install.ps1
```

Redémarrer le terminal après installation.

---

## Contenu

### [terminal/](./terminal/) - Configuration Terminal Complète

Configuration PowerShell avec tous les outils modernes :

| Outil | Description |
|-------|-------------|
| **Starship** | Prompt moderne et rapide |
| **zoxide** | Navigation intelligente (`z <dossier>`) |
| **fzf + PSFzf** | Fuzzy finder (`Ctrl+F`, `Ctrl+R`) |
| **PSReadLine** | Autocomplétion améliorée |
| **Aliases** | Git shortcuts, navigation rapide |

### [stt/](./stt/) - Speech to Text GUI

Interface graphique pour la transcription vocale :

- **Whisper large-v3** (le plus précis)
- **Accélération RTX/CUDA**
- **Focus intelligent** (colle dans le bon terminal)
- **Arrêt auto** après silence

**Usage :**
```powershell
stt       # Lance le GUI
sttstop   # Arrête tout
```

---

## Prérequis

- Windows 10/11
- PowerShell 7+
- GPU NVIDIA + CUDA (pour STT)
- Claude Code CLI (pour le plugin STT)

## Structure

```
AmarTools/
├── terminal/
│   ├── Microsoft.PowerShell_profile.ps1  # Profil complet
│   ├── install.ps1                       # Installation auto
│   └── README.md
├── stt/
│   ├── stt_gui.pyw                       # GUI STT
│   ├── profile-functions.ps1             # Fonctions PowerShell STT
│   ├── install.ps1                       # Installation STT
│   └── README.md
└── README.md
```

## Licence

Usage personnel.
