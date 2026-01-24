# Global Instructions for Claude Code (User-level)

This file defines my default expectations across all projects. Follow these rules unless a repo-level CLAUDE.md overrides them.

---

## 0) Core principle
Optimize for: **speed + reliability + maintainability**.
Prefer small, verifiable iterations over big risky changes.

### 🚨 CRITICAL: Code search policy
**STOP before every code search.** Ask yourself:
- Exploring/understanding code? → `grepai search` or `grepai trace` (MANDATORY)
- Exact string match? → `Grep` (OK)
- File patterns? → `Glob` (OK)

**Violation of this rule = failure.** See section 3.4 for details.

---

## 1) Environment (Windows + Claude Code bash)
- I develop on **Windows** using **PowerShell 7** or **Cursor terminal**.
- **Claude Code uses bash internally** (Git Bash/MSYS2), regardless of the parent shell.
- Write **bash-compatible commands** for the Bash tool (not PowerShell cmdlets).

### Shell behavior in Claude Code
- Claude Code's `Bash` tool runs commands in `/usr/bin/bash` (MSYS2/MinGW64).
- PowerShell cmdlets (`Get-Content`, `Get-ChildItem`, etc.) will NOT work.
- Use Unix-style paths: `/c/Users/amarm/` instead of `C:\Users\amarm\`
- Most CLI tools work the same: `git`, `node`, `npm`, `bun`, `grepai`, etc.

### Path conventions
| Context | Format | Example |
|---------|--------|---------|
| Claude Code Bash | Unix-style | `/c/Users/amarm/SaaS/project` |
| Outside Claude (PowerShell) | Windows-style | `C:\Users\amarm\SaaS\project` |

### What works in Claude Code Bash
- Standard Unix commands: `ls`, `cat`, `grep`, `find`, `cd`, `pwd`, `echo`
- Cross-platform CLI tools: `git`, `node`, `npm`, `bun`, `pnpm`, `grepai`
- Windows executables via PATH (they get called correctly)

### Permissions et commandes composées
Le hook `command-validator` auto-approuve les commandes composées (`|`, `&&`, `;`) si **toutes** les parties sont des commandes safe.

**Commandes Bash safe (auto-approuvées même avec pipes/chaînages) :**
`ls`, `dir`, `pwd`, `whoami`, `date`, `echo`, `cat`, `head`, `tail`, `grep`, `find`, `wc`, `sort`, `uniq`, `cut`, `awk`, `sed`, `git`, `npm`, `pnpm`, `node`, `bun`, `python`, `pip`, `source`, `cd`, `cp`, `mv`, `mkdir`, `touch`, `ln`, `psql`, `mysql`, `sqlite3`, `mongo`, `grepai`

| Commande | Résultat |
|----------|----------|
| `ls /path` | ✅ Auto-approuvé |
| `ls /path \| head -5` | ✅ Auto-approuvé (toutes safe) |
| `cd /path && pwd && ls` | ✅ Auto-approuvé (toutes safe) |
| `ls \| some-unknown-cmd` | ❓ Demande permission |

### Exécuter PowerShell depuis Claude Code Bash — IMPORTANT

**Problème** : Bash interprète `$_`, `$env:`, etc. AVANT de passer la commande à PowerShell → erreurs fréquentes.

**Solutions par ordre de préférence :**

1. **Utiliser des commandes natives Windows/bash** (pas besoin de PowerShell) :
   ```bash
   # Processus
   tasklist //FO CSV                    # Liste des processus
   taskkill //F //IM "process.exe"      # Tuer un processus
   taskkill //F //PID 1234              # Tuer par PID

   # Registre (lecture)
   reg query "HKCU\Software\..." /v "ValueName"

   # Services
   sc query "ServiceName"
   net stop "ServiceName"
   ```

2. **PowerShell simple sans variables** :
   ```bash
   powershell -NoProfile -Command "Get-Process | Select-Object Name"
   ```

3. **PowerShell avec variables → EncodedCommand** :
   ```bash
   # Encoder la commande en Base64 UTF-16LE :
   # [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes('Get-Process | Where-Object { $_.Name -like "*node*" }'))
   powershell -NoProfile -EncodedCommand "RwBlAHQALQBQAHIAbwBjAGUAcwBzAC..."
   ```

4. **Dernier recours : échapper avec `\$`** (inconsistant) :
   ```bash
   powershell -NoProfile -Command "Get-Process | Where-Object { \$_.Name -eq 'node' }"
   ```

**Règle** : Toujours essayer l'option 1 ou 2 d'abord. N'utiliser EncodedCommand que si nécessaire.

### Outils Read, Glob, Grep — auto-approuvés
Le hook auto-approuve aussi les outils Claude Code natifs :

| Outil | Comportement |
|-------|--------------|
| `Read` | ✅ Auto-approuvé si le chemin est dans un répertoire safe |
| `Glob` | ✅ Toujours auto-approuvé (read-only) |
| `Grep` | ✅ Toujours auto-approuvé (read-only) |

**Chemins safe pour Read :**
- `C:\Users\amarm\SaaS\*` (répertoire de développement)
- `C:\Users\amarm\.claude\*` (config Claude)
- `C:\Users\amarm\*` (home directory)
- Répertoire de travail courant
- `/tmp/` et répertoires temporaires

---

## 2) UX/UI policy — use `frontend-design` for UI/UX tasks
For any UI/UX work (layout, styling, components, pages, landing, dashboard, forms, responsive, typography, spacing, colors, animations, a11y):
- ALWAYS use the `frontend-design` skill/plugin.
- If `frontend-design` is unavailable, still apply its principles: premium hierarchy, consistent spacing scale, polished states (hover/focus/disabled/loading), empty/error states, accessibility.
- Prefer reusable components/tokens over ad-hoc CSS.

---

## 3) MCP Tooling policy

### 3.1 Context7 — version-accurate docs (only when needed)
When implementing/modifying code where **exact library/framework API or config details matter** (React, Next.js, Supabase, Stripe, etc.):
- Use **Context7 first** to fetch version-accurate docs/snippets.
- If Context7 is unavailable, proceed with conservative assumptions and clearly note uncertainty.

Avoid Context7 for purely local refactors that don’t depend on external API details.

### 3.2 Exa — web freshness (only when freshness matters)
When something is time-sensitive or likely to have changed (pricing, releases, deprecations, compatibility, “latest way to do X”, unclear error messages from the web):
- Use **Exa**, preferring official sources.

Avoid Exa for tasks that are purely local and fully determined by the repository.

### 3.3 Supabase MCP — verify correct `project_id` before writes
If using the Supabase MCP:
- **Before any write/destructive action** (schema changes, migrations, RLS/policies, data writes, storage changes, auth changes, secrets, edge function deploys), verify the MCP is connected to the intended **project_id**.
- Echo the verified `project_id` (and project name if available).
- If you cannot verify via tool output, STOP and ask me to confirm the target project (do not guess).
- For **read-only** actions, proceed, but still report the detected project context if available.
- Never run destructive operations (drop/truncate/reset/migration rewrites) even on the right project without explicit confirmation.

### 3.4 GrepAI — semantic code search (⛔ CRITICAL — READ THIS)

**🚨 RÈGLE NON-NÉGOCIABLE — VIOLATION = ÉCHEC**

**AVANT** d'utiliser `Grep` ou `Glob` pour explorer du code, tu DOIS te poser cette question :
> "Est-ce que je cherche un **texte exact** (variable, constante, import) ou est-ce que j'**explore/comprends** le code ?"

| Si tu cherches... | Utilise | ⛔ INTERDIT |
|-------------------|---------|-------------|
| Où est géré X ? | `grepai search` | ~~Grep~~ |
| Comment fonctionne Y ? | `grepai search` | ~~Grep~~ |
| Qui appelle cette fonction ? | `grepai trace callers` | ~~Grep~~ |
| Le flux de Z ? | `grepai search` | ~~Grep~~ |
| Une variable exacte (`userId`) | `Grep` | ✅ OK |
| Une constante (`SUPABASE_URL`) | `Grep` | ✅ OK |
| Un pattern de fichiers (`*.tsx`) | `Glob` | ✅ OK |

**❌ EXEMPLES INTERDITS** (ce que tu fais trop souvent) :
```bash
# ❌ INTERDIT — question conceptuelle avec grep
grep -r "auth" --include="*.ts"           # NON ! Utilise: grepai search "authentication flow"
grep -r "payment" --include="*.tsx"       # NON ! Utilise: grepai search "où est géré le paiement"
grep -r "getUser" .                       # NON ! Utilise: grepai trace callers "getUser"
```

**✅ EXEMPLES CORRECTS** :
```bash
# ✅ Question conceptuelle → GrepAI
grepai search "comment fonctionne l'authentification"
grepai search "où sont gérées les notifications"
grepai trace callers "getAuthedUser"

# ✅ Recherche exacte → Grep (OK)
grep "SUPABASE_URL"
grep "userId"
grep "import { Button }"
```

#### Langage naturel — parle à grepAI comme à un collègue

grepAI est un agent IA. Formule tes questions naturellement, pas comme un moteur de recherche :

| ❌ Mots-clés robotiques | ✅ Question naturelle |
|-------------------------|----------------------|
| `"auth token refresh flow"` | `"Comment fonctionne le rafraîchissement du token d'authentification ?"` |
| `"user payment stripe webhook"` | `"Comment les webhooks Stripe sont gérés pour les paiements utilisateur ?"` |
| `"error handling api response"` | `"Comment sont gérées les erreurs des réponses API ?"` |

#### Requêtes complexes — paralléliser

Si ta recherche touche **plusieurs parties du codebase**, lance plusieurs `grepai search` en parallèle :

```bash
# Exemple : comprendre le système d'auth complet
grepai search "comment fonctionne l'authentification côté frontend"
grepai search "comment le token est géré côté backend"
grepai search "comment les sessions sont persistées"
```

#### ast-grep — recherche structurelle (complément à grepai)

grepai comprend le **sens**, ast-grep comprend la **structure**. Utilise les deux :

| Question | Outil | Exemple |
|----------|-------|---------|
| "Où est géré X ?" | `grepai search` | `grepai search "comment fonctionne l'auth"` |
| "Trouve tous les appels à Y" | `ast-grep` | `ast-grep --pattern 'useAuth()'` |
| "Fonctions async sans try/catch" | `ast-grep` | `ast-grep --pattern 'async function $F($_) { $$$B }'` |
| "Pourquoi ce pattern existe ?" | `grepai search` | `grepai search "pourquoi ces fonctions sont async"` |

**Workflow combiné :**
```bash
# 1. Localiser conceptuellement (sémantique)
grepai search "où est géré le paiement Stripe"

# 2. Extraire les patterns (structure)
ast-grep --pattern 'stripe.$METHOD($_)' src/payments/
```

**Quand utiliser ast-grep seul :**
- Refactoring automatisé (renommer, restructurer)
- Trouver des anti-patterns (console.log, any, TODO)
- Audit de code (fonctions trop longues, imports inutilisés)

**📊 Decision tree :**
```
Question de l'utilisateur
    │
    ├─ Contient "où", "comment", "qui appelle", "flux", "comprendre" ?
    │   └─→ 🔴 GREPAI OBLIGATOIRE
    │
    ├─ Cherche un **pattern syntaxique** (appels, structures, refactoring) ?
    │   └─→ 🟣 ast-grep
    │
    ├─ Cherche un mot-clé exact, variable, import, constante ?
    │   └─→ 🟢 Grep OK
    │
    └─ Cherche des fichiers par pattern ?
        └─→ 🟢 Glob OK
```

---

#### Commandes avancées (référence)

```bash
# Recherche avec JSON compact (économise des tokens)
grepai search --json -c "query"

# Call graph avec profondeur limitée
grepai trace graph "Function" --depth 3

# Gestion de l'index
grepai status                  # État de l'index
grepai watch                   # Réindexer (Ctrl+C quand fini)
grepai init                    # Initialiser un nouveau projet
```

#### Prérequis

| Composant | Fix si problème |
|-----------|-----------------|
| Ollama | `ollama serve` |
| Modèle | `ollama pull nomic-embed-text` |
| Index | `grepai watch` pour rafraîchir |

#### Nouveau projet → Initialiser GrepAI

**OBLIGATOIRE** pour tout nouveau projet dans `C:\Users\amarm\SaaS\` :
```bash
cd /path/to/new-project
grepai init      # Choisir: ollama + gob
grepai watch     # Attendre l'indexation, puis Ctrl+C
```

#### Subagents (Task tool) — IMPORTANT

**Les subagents n'héritent PAS des instructions de ce fichier.**

Quand tu lances un subagent pour explorer du code :
- Utilise **`Explore` avec thoroughness "very thorough"** (pas "quick" ou "medium")
- **Copie-colle les instructions GrepAI** dans le prompt du subagent pour qu'il les respecte
- Précise explicitement : "Utilise `grepai search` pour les questions conceptuelles, pas Grep"

#### Vérification automatique en début de session

**Au début de chaque session** sur un projet existant, si tu dois faire une recherche conceptuelle :
1. Vérifie d'abord si `.grepai/` existe avec `ls -la .grepai/ 2>/dev/null || echo "NOT_INITIALIZED"`
2. Si `NOT_INITIALIZED` → Propose d'initialiser GrepAI avant de continuer
3. Si l'index existe mais semble ancien (>1 semaine sans commit), suggère `grepai watch`

---

## 4) Workflow defaults (how you should work)
Before editing:
1) Restate the goal in 1–2 lines.
2) Propose a short plan (3–7 steps).
3) Identify files likely involved (best guess).

While editing:
- Work in small batches (max ~5–10 files per iteration).
- Prefer minimal diffs.
- Avoid broad rewrites unless requested or clearly justified.

After editing:
Always provide:
- **Files changed**: list + what changed.
- **Commands to run**: exact commands for verification.
- **How to verify**: quick manual steps + expected results.

---

## 5) Git workflow — branching best practices (never work on main)
- NEVER develop directly on `main`/`master`.
- If currently on `main`/`master`, create a new branch immediately before making changes.

### Mandatory Git preflight (before any change)
Before editing any file or running any git command:
- Run `git branch --show-current`
- If branch is `main`/`master`: STOP and create a new branch (feature/*, fix/*, etc.)
- Then run `git status` and confirm the working tree state
Do not proceed until the branch is not main/master.

### Branch naming
Use consistent prefixes:
- `feature/<short-scope>` for new features
- `fix/<short-scope>` for bug fixes
- `refactor/<short-scope>` for refactors
- `chore/<short-scope>` for maintenance/tooling
- `hotfix/<short-scope>` for urgent production fixes

Use kebab-case and keep it short (e.g., `feature/loyalty-stats`, `fix/pass-sms-link`).

### Creating a branch (PowerShell)
Before starting:
- `git status` must be clean.
- Sync base branch:
  - `git switch main` (or master)
  - `git pull --ff-only`

Create branch:
- `git switch -c feature/<name>`

### Keeping branches up to date
- Rebase or merge from `main` only when needed and keep conflicts minimal.
- Prefer `git pull --rebase` on your feature branch if the repo/team workflow allows it.

### Commits
- Commit in small, coherent chunks with intent-revealing messages.
- Prefer conventional-ish prefixes: `feat:`, `fix:`, `refactor:`, `chore:`, `test:`.

### Before opening a PR/MR
- Run quality gates (typecheck/lint/tests/build when available).
- Provide a short PR summary: what changed, why, how to test, and any risks.

---

## 6) Quality gates (default definition of done)
- Prefer running existing scripts if present: typecheck, lint, tests, build, and a quick smoke test of the critical path.
- **Do not add new tooling/scripts** unless I ask or it is clearly beneficial and lightweight.

---

## 7) Safety guardrails (non-negotiable)
- Never send secrets (API keys, tokens, credentials, private URLs) to external tools.
- Never modify `.env` / secrets unless explicitly asked.
- Never run destructive commands (`rm -rf`, `drop`, `truncate`, resets) without explicit confirmation.
- For DB/migrations: always provide **plan + rollback** (or a safe alternative).

---

## 8) Windows / nvm4w conventions
- If a command fails in Claude Code, check tool resolution & versions:
  - `which <tool>` or `command -v <tool>` (bash)
  - `node -v`, `npm -v` / `pnpm -v`
- Use Unix-style paths in Claude Code: `/c/Users/amarm/...`
- For commands I run manually outside Claude, use PowerShell syntax.

---

## 9) Communication style (to keep iteration fast)
- Prefer concise, actionable instructions.
- When unsure, make a best-effort assumption but label it clearly.
- Avoid unnecessary explanations; prioritize steps and diffs I can apply.

---

## 10) Langue française — toujours utiliser les accents
Quand tu écris du texte en français (UI, commentaires, messages, labels, etc.) :
- **TOUJOURS** utiliser les accents corrects : é, è, ê, ë, à, â, ù, û, ô, î, ï, ç
- Exemples : "Créer" (pas "Creer"), "Réduction" (pas "Reduction"), "À emporter" (pas "A emporter")
- Cela s'applique aux strings dans le code, aux commentaires, et à tes réponses
- Ne jamais omettre les accents même si le clavier anglais ne les a pas facilement
