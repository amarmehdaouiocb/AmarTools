# STT GUI - Speech to Text pour Claude Code

Interface graphique pour la transcription vocale utilisant Whisper large-v3 sur GPU.

## Fonctionnalités

- **GUI minimaliste** avec visualisation audio en temps réel
- **Whisper large-v3** (le modèle le plus précis)
- **Accélération GPU** (CUDA/RTX)
- **Focus intelligent** : colle le texte dans le dernier terminal focusé
- **Arrêt automatique** après 2 secondes de silence

## Prérequis

- Windows 10/11
- PowerShell 7+
- Claude Code CLI installé
- GPU NVIDIA avec CUDA (testé sur RTX 5090)
- Plugin `jarrodwatts/claude-stt` installé

## Installation

### 1. Installer le plugin claude-stt (si pas déjà fait)

```powershell
claude plugin install jarrodwatts/claude-stt
```

### 2. Lancer le script d'installation

```powershell
cd chemin\vers\AmarTools\stt
.\install.ps1
```

### 3. Redémarrer le terminal

Fermez et rouvrez votre terminal PowerShell.

## Utilisation

| Commande | Description |
|----------|-------------|
| `stt` | Lance le GUI STT |
| `sttstop` | Arrête tous les processus STT |
| `sttdaemon` | Lance le daemon avec hotkey global |
| `sttstatus` | Affiche le statut du daemon |

### Workflow typique

1. Tapez `stt` dans le terminal
2. Le GUI s'ouvre en haut à droite
3. Cliquez sur le terminal où vous voulez coller le texte
4. Cliquez sur **Record** dans le GUI
5. Parlez
6. Le texte est automatiquement collé dans le terminal ciblé

## Configuration

### Modèle Whisper

Par défaut : `large-v3` sur CUDA avec float16.

Variables d'environnement optionnelles :
- `CLAUDE_STT_WHISPER_DEVICE` : `cuda` (défaut) ou `cpu`
- `CLAUDE_STT_WHISPER_COMPUTE_TYPE` : `float16` (défaut), `int8`, `float32`

### Chemins

- GUI : `~\.claude\plugins\claude-stt\stt_gui.pyw`
- Config : `~\.claude\plugins\claude-stt\config.toml`
- Logs : `~\.claude\plugins\claude-stt\daemon.log`

## Fichiers

| Fichier | Description |
|---------|-------------|
| `stt_gui.pyw` | Interface graphique principale |
| `profile-functions.ps1` | Fonctions PowerShell à ajouter au profil |
| `install.ps1` | Script d'installation automatique |

## Dépannage

### Le texte ne se colle pas dans le bon terminal

Le GUI suit en permanence la fenêtre active. Assurez-vous de cliquer sur le terminal cible **avant** de cliquer sur Record.

### Erreur CUDA

Vérifiez que PyTorch détecte votre GPU :
```powershell
python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

### Processus orphelins

```powershell
sttstop
```

## Licence

Usage personnel.
