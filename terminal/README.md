# Terminal Configuration

Configuration complète du terminal PowerShell avec tous les outils modernes.

## Outils inclus

| Outil | Description | Raccourci |
|-------|-------------|-----------|
| **Starship** | Prompt moderne et rapide | - |
| **zoxide** | Navigation intelligente (remplace cd) | `z <dossier>` |
| **fzf + PSFzf** | Fuzzy finder | `Ctrl+F`, `Ctrl+R` |
| **PSReadLine** | Autocomplétion améliorée | `Tab`, `↑`, `↓` |

## Installation

### Installation complète (recommandé)

Exécuter en tant qu'administrateur :

```powershell
cd chemin\vers\AmarTools\terminal
powershell -ExecutionPolicy Bypass -File install.ps1
```

### Options d'installation

```powershell
# Tout installer
.\install.ps1

# Sans les outils CLI (si déjà installés)
.\install.ps1 -SkipTools

# Sans les modules PowerShell
.\install.ps1 -SkipModules

# Sans le profil (garder l'existant)
.\install.ps1 -SkipProfile

# Sans le STT
.\install.ps1 -SkipSTT

# Forcer le remplacement du profil sans confirmation
.\install.ps1 -Force
```

## Alias et raccourcis

### Navigation

| Commande | Action |
|----------|--------|
| `..` | Remonter d'un niveau |
| `...` | Remonter de 2 niveaux |
| `....` | Remonter de 3 niveaux |
| `z <nom>` | Aller vers un dossier fréquent (zoxide) |
| `e` | Ouvrir l'explorateur ici |

### Git

| Commande | Action |
|----------|--------|
| `gs` | `git status` |
| `gp` | `git pull` |
| `gf` | `git fetch` |
| `gl` | `git log --oneline -20` |
| `gd` | `git diff` |
| `gds` | `git diff --staged` |

### Fichiers

| Commande | Action |
|----------|--------|
| `ll` | Liste détaillée (fichiers cachés inclus) |
| `ff <pattern>` | Recherche récursive de fichiers |

### PSFzf (Fuzzy Finder)

| Raccourci | Action |
|-----------|--------|
| `Ctrl+F` | Recherche fuzzy de fichiers |
| `Ctrl+R` | Recherche fuzzy dans l'historique |

### STT (Speech to Text)

| Commande | Action |
|----------|--------|
| `stt` | Lancer le GUI de transcription |
| `sttstop` | Arrêter tous les processus STT |
| `sttdaemon` | Lancer le daemon (hotkey global) |
| `sttstatus` | Afficher le statut |

## Fichiers

| Fichier | Description |
|---------|-------------|
| `Microsoft.PowerShell_profile.ps1` | Profil PowerShell complet |
| `install.ps1` | Script d'installation automatique |

## Prérequis

- Windows 10/11
- PowerShell 7+ (recommandé)
- winget (pour l'installation des outils)
- Droits administrateur (pour winget)

## Installation manuelle des outils

Si winget ne fonctionne pas :

```powershell
# Starship
scoop install starship
# ou
choco install starship

# zoxide
scoop install zoxide
# ou
choco install zoxide

# fzf
scoop install fzf
# ou
choco install fzf

# PSFzf
Install-Module -Name PSFzf -Scope CurrentUser -Force
```
