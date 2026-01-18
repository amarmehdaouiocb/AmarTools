# Configuration Claude Code

Configuration complète de Claude Code avec hooks, permissions, statusline et rules.

## Contenu

| Fichier/Dossier | Description |
|-----------------|-------------|
| `settings.json` | Permissions, hooks, plugins, modèle |
| `CLAUDE.md` | Instructions globales (profil utilisateur) |
| `statusline-git.ps1` | Script pour la barre de statut Git |
| `scripts/` | Hooks de validation (PreToolUse) |
| `rules/` | Rules pour délégation GPT (Codex) |
| `song/` | Sons de notification |

## Installation

```powershell
cd chemin\vers\AmarTools\claude-code
.\install.ps1
```

### Options

```powershell
# Installation complète
.\install.ps1

# Forcer le remplacement de settings.json
.\install.ps1 -Force

# Sans les scripts de hook
.\install.ps1 -SkipScripts

# Sans les sons
.\install.ps1 -SkipSounds
```

## Fonctionnalités

### Permissions configurées

**Lecture (auto-approuvées) :**
- `cat`, `ls`, `dir`, `find`, `head`, `tail`, `tree`, `grep`, `rg`, `fd`
- `Get-Content`, `Get-ChildItem`, `Get-Item`, `Test-Path`
- `grepai search`, `grepai trace`, `grepai status`

**Navigation (auto-approuvées) :**
- `cd`, `z`, `Set-Location`, `Push-Location`, `Pop-Location`

**Git (auto-approuvées) :**
- `git status`, `git log`, `git diff`, `git branch`, `git show`
- `git add`, `git push`

### Hooks

| Hook | Description |
|------|-------------|
| `PreToolUse (Bash)` | Valide les commandes avant exécution |
| `Stop` | Joue un son quand Claude termine |
| `Notification` | Joue un son quand Claude a besoin d'input |

### Statusline

Affiche dans la barre de statut :
- Branche Git actuelle
- État du repo (propre/modifié)
- Nombre de fichiers modifiés

### Rules (Délégation GPT)

Configuration pour déléguer à des experts GPT via Codex MCP :
- **Architect** : Design système, tradeoffs
- **Plan Reviewer** : Validation de plans
- **Scope Analyst** : Analyse de scope
- **Code Reviewer** : Review de code
- **Security Analyst** : Audit sécurité

## Prérequis

- Claude Code CLI installé
- Bun (pour les scripts de hook)
- PowerShell 7+

## Structure des fichiers

```
claude-code/
├── settings.json           # Config principale
├── CLAUDE.md              # Instructions globales
├── statusline-git.ps1     # Script statusline
├── install.ps1            # Script d'installation
├── scripts/
│   ├── command-validator/ # Hook validation commandes
│   └── quality-checks/    # Hook qualité
├── rules/
│   └── delegator/         # Rules délégation GPT
└── song/
    ├── finish.mp3         # Son fin de tâche
    └── need-human.mp3     # Son besoin input
```

## Personnalisation

### Modifier les permissions

Éditer `settings.json` > `permissions` > `allow`

### Modifier les instructions globales

Éditer `CLAUDE.md`

### Désactiver les hooks

Dans `settings.json`, vider le tableau `hooks.PreToolUse`
