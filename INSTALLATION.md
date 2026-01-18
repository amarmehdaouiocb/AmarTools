# Installation complète - Nouveau PC

Guide pour remonter l'environnement de développement complet sur un nouveau PC Windows.

## Prérequis

- Windows 10/11
- PowerShell 7+ ([Télécharger](https://github.com/PowerShell/PowerShell/releases))
- Git ([Télécharger](https://git-scm.com/download/win))
- Bun ([Télécharger](https://bun.sh)) - pour les hooks Claude Code
- GPU NVIDIA + CUDA (pour le STT)

## Étape 1 : Cloner le repo

```powershell
git clone https://github.com/amarmehdaouiocb/AmarTools.git
cd AmarTools
```

## Étape 2 : Installer Claude Code CLI

Télécharger et installer Claude Code depuis : https://claude.ai/code

Vérifier l'installation :
```powershell
claude --version
```

## Étape 3 : Installer la configuration Claude Code

```powershell
cd claude-code
.\install.ps1
cd ..
```

Cela installe :
- `settings.json` (permissions, hooks, plugins)
- `CLAUDE.md` (instructions globales)
- `statusline-git.ps1` (barre de statut Git)
- Scripts de validation (hooks PreToolUse)
- Rules de délégation GPT
- Sons de notification

## Étape 4 : Installer le terminal (PowerShell)

Exécuter en tant qu'administrateur :

```powershell
cd terminal
powershell -ExecutionPolicy Bypass -File install.ps1
cd ..
```

Cela installe :
- **Starship** (prompt moderne)
- **zoxide** (navigation intelligente avec `z`)
- **fzf + PSFzf** (fuzzy finder avec `Ctrl+F`, `Ctrl+R`)
- **PSReadLine** (autocomplétion améliorée)
- Profil PowerShell avec tous les aliases

## Étape 5 : Installer le STT (Speech to Text)

### 5.1 Installer le plugin claude-stt

```powershell
claude plugin install jarrodwatts/claude-stt
```

### 5.2 Installer le GUI STT

```powershell
cd stt
.\install.ps1
cd ..
```

## Étape 6 : Redémarrer le terminal

Fermer et rouvrir PowerShell pour appliquer tous les changements.

## Vérification

### Terminal
```powershell
# Vérifier Starship (prompt stylisé)
# Vérifier zoxide
z --version

# Vérifier fzf
fzf --version

# Tester les aliases
gs  # git status
ll  # liste détaillée
```

### Claude Code
```powershell
claude
# Vérifier la statusline Git
# Vérifier que les permissions sont appliquées
```

### STT
```powershell
stt  # Doit ouvrir le GUI
```

## Commandes disponibles après installation

### Navigation
| Commande | Description |
|----------|-------------|
| `z <dossier>` | Navigation intelligente (zoxide) |
| `..`, `...`, `....` | Remonter de 1/2/3 niveaux |
| `e` | Ouvrir l'explorateur ici |

### Git
| Commande | Description |
|----------|-------------|
| `gs` | `git status` |
| `gp` | `git pull` |
| `gf` | `git fetch` |
| `gl` | `git log --oneline -20` |
| `gd` | `git diff` |
| `gds` | `git diff --staged` |

### Fichiers
| Commande | Description |
|----------|-------------|
| `ll` | Liste détaillée |
| `ff <pattern>` | Recherche récursive |
| `Ctrl+F` | Fuzzy finder fichiers |
| `Ctrl+R` | Fuzzy finder historique |

### STT
| Commande | Description |
|----------|-------------|
| `stt` | Lancer le GUI |
| `sttstop` | Arrêter tous les processus STT |
| `sttdaemon` | Lancer le daemon (hotkey global) |
| `sttstatus` | Afficher le statut |

## Dépannage

### Starship ne s'affiche pas
```powershell
# Vérifier l'installation
starship --version

# Réinstaller si nécessaire
winget install Starship.Starship
```

### zoxide ne fonctionne pas
```powershell
# Vérifier l'installation
zoxide --version

# Réinstaller si nécessaire
winget install ajeetdsouza.zoxide
```

### Les hooks Claude Code ne fonctionnent pas
```powershell
# Vérifier que bun est installé
bun --version

# Réinstaller les dépendances
cd ~/.claude/scripts/command-validator
bun install
cd ~/.claude/scripts/quality-checks
bun install
```

### Le STT ne trouve pas le GPU
```powershell
# Vérifier CUDA
python -c "import torch; print(torch.cuda.is_available())"
```

## Mise à jour

Pour mettre à jour la configuration :

```powershell
cd AmarTools
git pull
cd claude-code && .\install.ps1 -Force && cd ..
cd terminal && .\install.ps1 -Force && cd ..
cd stt && .\install.ps1 && cd ..
```
