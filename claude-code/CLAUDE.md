# Global Instructions for Claude Code (User-level)

This file defines my default expectations across all projects. Follow these rules unless a repo-level CLAUDE.md overrides them.

---

## 0) Core principle
Optimize for: **speed + reliability + maintainability**.
Prefer small, verifiable iterations over big risky changes.

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
`ls`, `dir`, `pwd`, `whoami`, `date`, `echo`, `cat`, `head`, `tail`, `grep`, `find`, `wc`, `sort`, `uniq`, `cut`, `awk`, `sed`, `git`, `npm`, `pnpm`, `node`, `bun`, `python`, `pip`, `source`, `cd`, `cp`, `mv`, `mkdir`, `touch`, `ln`, `psql`, `mysql`, `sqlite3`, `mongo`

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

### 3.4 GrepAI — semantic code search (use strategically)
GrepAI is a **semantic code search tool** that uses AI embeddings to find code by meaning.

**When to use GrepAI vs Grep/Glob:**

| Search Type | Tool | Speed | Example |
|-------------|------|-------|---------|
| Conceptual / exploratory | **GrepAI** | ~500ms | "where is auth handled?" |
| Call graph analysis | **GrepAI trace** | ~300ms | "who calls getUser?" |
| Exact text match | **Grep** | ~50ms | `userId`, `SUPABASE_URL` |
| File patterns | **Glob** | ~20ms | `*.tsx`, `**/*.test.ts` |

#### GrepAI Command Reference

**Semantic search:**
```powershell
grepai search "query"                    # Basic search (10 results)
grepai search -n 5 "query"               # Limit to 5 results
grepai search --json "query"             # JSON output
grepai search --json -c "query"          # Compact JSON (~80% fewer tokens)
```

**Call graph tracing:**
```powershell
grepai trace callers "FunctionName"      # Who calls this function?
grepai trace callees "FunctionName"      # What functions does it call?
grepai trace graph "FunctionName"        # Full call graph
grepai trace graph "Func" --depth 3      # Limit depth
```

**Index management:**
```powershell
grepai status                            # Index status (files, chunks)
grepai watch                             # Real-time daemon (Ctrl+C to stop)
grepai init                              # Initialize in new project
```

**Effective query examples:**
```powershell
# Good: conceptual questions
grepai search "how are errors handled"
grepai search "user authentication flow"
grepai search "database connection setup"

# Bad: exact searches (use grep instead)
grepai search "userId"                   # → Use: grep userId
grepai search "import { Button }"        # → Use: grep "import { Button }"
```

#### Prerequisites

| Component | Status | Fix if needed |
|-----------|--------|---------------|
| **Ollama** | Auto-start Windows | `ollama serve` |
| **Model** | `nomic-embed-text` | `ollama pull nomic-embed-text` |
| **Index** | Persisted in `.grepai/` | `grepai watch` to refresh |

#### Setup for new project
```powershell
cd /path/to/project
grepai init                              # Choose: ollama + gob (defaults)
grepai watch                             # Wait for indexing, then Ctrl+C
```

**Rule of thumb:**
- Exploring/understanding code → GrepAI
- Looking for specific string → Grep
- Finding files by name → Glob

#### Daily Workflow

**On Windows boot**: Ollama starts automatically → GrepAI ready.

| Situation | Action |
|-----------|--------|
| New Claude session | Nothing to do, index already exists |
| Conceptual search | `grepai search "how does X work"` |
| Understand a flow | `grepai trace callers "myFunction"` |
| Exact text search | `grep "variableName"` (faster) |
| After major changes | `grepai watch` then Ctrl+C |

**Concrete examples:**
```powershell
# Conceptual → GrepAI
grepai search "where is payment handled"
grepai search "how does authentication work"
grepai trace callers "getAuthedUser"

# Exact → Grep
grep "SUPABASE_URL"
grep "userId"
```

#### New Project Setup (one-time)
```powershell
cd /path/to/new-project
grepai init                    # Select: ollama + gob (defaults)
grepai watch                   # Wait for indexing to complete, then Ctrl+C
# Done! Index persists in .grepai/
```

#### ⚠️ OBLIGATION : Initialiser GrepAI sur tout nouveau projet

**RÈGLE STRICTE** : Quand je crée ou clone un nouveau projet dans `C:\Users\amarm\SaaS\` :
1. **Immédiatement** après la création/clone, exécuter `grepai init` (ollama + gob)
2. Lancer `grepai watch` pour indexer, puis Ctrl+C
3. Ne pas commencer le développement avant que GrepAI soit initialisé

Cette règle s'applique à TOUS les nouveaux projets sans exception.

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
