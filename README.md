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

### [claude-code/](./claude-code/) - Configuration Claude Code

Configuration complète de Claude Code :

| Composant | Description |
|-----------|-------------|
| **settings.json** | Permissions, hooks, plugins |
| **CLAUDE.md** | Instructions globales |
| **Statusline** | Barre de statut Git |
| **Hooks** | Validation des commandes |
| **Rules** | Délégation GPT (Codex) |
| **Sons** | Notifications audio |

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
├── claude-code/
│   ├── settings.json          # Config principale
│   ├── CLAUDE.md              # Instructions globales
│   ├── statusline-git.ps1     # Script statusline
│   ├── install.ps1            # Installation
│   ├── scripts/               # Hooks de validation
│   ├── rules/                 # Rules délégation GPT
│   └── song/                  # Sons notification
├── terminal/
│   ├── Microsoft.PowerShell_profile.ps1
│   ├── install.ps1
│   └── README.md
├── stt/
│   ├── stt_gui.pyw
│   ├── profile-functions.ps1
│   ├── install.ps1
│   └── README.md
└── README.md
```

## Licence

Usage personnel.
