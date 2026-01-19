# Optimisations Workflow & Productivité

Idées pour améliorer le workflow de développement avec Claude Code.

---

## 1. Automatisation projet

### Template de projet (`newproject`)

Script PowerShell qui automatise la création d'un nouveau projet :

```powershell
function New-Project {
    param([string]$Name, [string]$Template = "nextjs")

    # 1. Créer le dossier
    # 2. Init git + .gitignore
    # 3. Init GrepAI (grepai init)
    # 4. Copier les configs partagées (biome, tsconfig, etc.)
    # 5. Init Supabase si besoin
    # 6. Créer .claude/context.md
    # 7. Premier commit
}
Set-Alias -Name newproject -Value New-Project
```

**Fichiers à créer :**
- `AmarTools/templates/nextjs/` - Template Next.js de base
- `AmarTools/templates/shared-configs/` - Configs partagées (biome.json, tsconfig.json)

### Pre-commit hooks (Husky + lint-staged)

```bash
# Installation
pnpm add -D husky lint-staged
pnpm exec husky init
```

```json
// package.json
{
  "lint-staged": {
    "*.{ts,tsx}": ["biome check --apply", "biome format --write"],
    "*.{json,md}": ["biome format --write"]
  }
}
```

### Alias `deploy`

```powershell
function Deploy-App {
    param([string]$Environment = "preview")

    # 1. Run tests
    # 2. Run build
    # 3. Run typecheck
    # 4. Git push
    # 5. Trigger Vercel/deploy
}
Set-Alias -Name deploy -Value Deploy-App
```

---

## 2. Qualité & Sécurité

### npm audit automatique

Hook Claude Code qui vérifie les vulnérabilités avant `pnpm add` :

```javascript
// .claude/hooks/pre-install.js
// Vérifie npm audit avant d'installer une nouvelle dépendance
```

Ou plus simple : alias PowerShell

```powershell
function Safe-Install {
    param([string]$Package)
    pnpm add $Package
    $audit = pnpm audit --json | ConvertFrom-Json
    if ($audit.metadata.vulnerabilities.high -gt 0) {
        Write-Host "⚠️ Vulnérabilités détectées !" -ForegroundColor Red
        pnpm audit
    }
}
Set-Alias -Name padd -Value Safe-Install
```

### Biome config partagée

Créer `AmarTools/shared-configs/biome.json` avec les règles strictes :

```json
{
  "linter": {
    "enabled": true,
    "rules": {
      "recommended": true,
      "security": { "recommended": true },
      "suspicious": { "recommended": true }
    }
  },
  "formatter": {
    "indentStyle": "tab",
    "lineWidth": 100
  }
}
```

Puis dans chaque projet : `"extends": ["../../AmarTools/shared-configs/biome.json"]`

### RLS Templates Supabase

Créer `AmarTools/templates/supabase-rls/` avec des snippets :

```sql
-- user-owns-row.sql
CREATE POLICY "Users can only access their own data"
ON public.{table}
FOR ALL
USING (auth.uid() = user_id);

-- team-member.sql
CREATE POLICY "Team members can access team data"
ON public.{table}
FOR ALL
USING (
  EXISTS (
    SELECT 1 FROM team_members
    WHERE team_members.team_id = {table}.team_id
    AND team_members.user_id = auth.uid()
  )
);
```

### Secrets scanner (pre-commit)

```powershell
# Hook qui scanne les fichiers pour les secrets avant commit
function Test-Secrets {
    $patterns = @(
        'sk_live_',           # Stripe
        'SUPABASE_SERVICE',   # Supabase service key
        'ghp_',               # GitHub token
        'eyJ',                # JWT tokens
        'PRIVATE_KEY'
    )

    $files = git diff --cached --name-only
    foreach ($file in $files) {
        $content = Get-Content $file -Raw -ErrorAction SilentlyContinue
        foreach ($pattern in $patterns) {
            if ($content -match $pattern) {
                Write-Host "⚠️ Secret potentiel détecté dans $file" -ForegroundColor Red
                return $false
            }
        }
    }
    return $true
}
```

---

## 3. Claude Code avancé

### Skills personnalisés

Créer des skills dans `~/.claude/skills/` :

#### `/deploy` - Déploiement rapide

```markdown
# Skill: deploy
1. Run typecheck
2. Run tests
3. Run build
4. Git add + commit avec message conventionnel
5. Git push
6. Afficher l'URL de preview
```

#### `/newfeature` - Nouvelle fonctionnalité

```markdown
# Skill: newfeature
1. Créer une branche feature/<name>
2. Créer les fichiers de base (component, test, types)
3. Mettre à jour les imports
4. Ouvrir le fichier principal
```

#### `/security-audit` - Audit de sécurité

```markdown
# Skill: security-audit
1. npm audit
2. Vérifier les RLS Supabase
3. Scanner les secrets dans le code
4. Vérifier les headers de sécurité (CSP, etc.)
5. Rapport avec recommandations
```

#### `/db-migrate` - Migration Supabase

```markdown
# Skill: db-migrate
1. Générer les types TypeScript
2. Créer le fichier de migration
3. Appliquer en local
4. Vérifier les RLS
5. Commiter
```

### Context files par projet

Créer `.claude/context.md` dans chaque projet :

```markdown
# Project: BoatAcademy

## Architecture
- Monorepo pnpm workspaces
- apps/student-web (Next.js 15, port 3001)
- apps/admin-web (Next.js 15, port 3000)
- packages/shared (types, utils)

## Stack
- Supabase (auth, db, storage)
- Tailwind + shadcn/ui
- React Hook Form + Zod

## Conventions
- Composants: PascalCase
- Fichiers: kebab-case
- Commits: conventional commits

## Endpoints importants
- /api/auth/* - Authentication
- /api/bookings/* - Réservations

## Variables d'environnement
- NEXT_PUBLIC_SUPABASE_URL
- NEXT_PUBLIC_SUPABASE_ANON_KEY
- SUPABASE_SERVICE_ROLE_KEY (server only)
```

### Hook post-edit (typecheck auto)

Ajouter dans `~/.claude/settings.json` :

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "pnpm typecheck --silent 2>&1 | head -20"
          }
        ]
      }
    ]
  }
}
```

---

## 4. Productivité quotidienne

### Alias `morning`

```powershell
function Start-Morning {
    <#
    .SYNOPSIS
    Routine du matin : lance tous les outils de dev
    #>
    Write-Host "🌅 Good morning! Starting dev environment..." -ForegroundColor Cyan

    # Vérifier Ollama
    $ollama = Get-Process ollama -ErrorAction SilentlyContinue
    if (-not $ollama) {
        Write-Host "→ Starting Ollama..." -ForegroundColor Yellow
        Start-Process "ollama" -ArgumentList "serve" -WindowStyle Hidden
    }

    # Vérifier Docker (si utilisé)
    # Start-Process "Docker Desktop" -ErrorAction SilentlyContinue

    # Afficher les projets avec des changements non commités
    Write-Host "`n📁 Projets avec changements non commités:" -ForegroundColor White
    Get-ChildItem "$env:USERPROFILE\SaaS" -Directory | ForEach-Object {
        Push-Location $_.FullName
        $status = git status --porcelain 2>$null
        if ($status) {
            Write-Host "  - $($_.Name)" -ForegroundColor Yellow
        }
        Pop-Location
    }

    # Afficher les PRs en attente (si gh installé)
    # gh pr list --author @me

    Write-Host "`n✨ Ready to code!`n" -ForegroundColor Green
}
Set-Alias -Name morning -Value Start-Morning
```

### Dashboard terminal

Script qui affiche un résumé de tous les projets :

```powershell
function Show-Dashboard {
    $projects = Get-ChildItem "$env:USERPROFILE\SaaS" -Directory

    Write-Host "`n📊 Dashboard Projets`n" -ForegroundColor Cyan
    Write-Host ("{0,-20} {1,-15} {2,-10} {3}" -f "Projet", "Branche", "Status", "Dernier commit")
    Write-Host ("-" * 70)

    foreach ($proj in $projects) {
        Push-Location $proj.FullName
        $branch = git branch --show-current 2>$null
        $status = if (git status --porcelain 2>$null) { "⚠️ dirty" } else { "✅ clean" }
        $lastCommit = git log -1 --format="%ar" 2>$null

        if ($branch) {
            Write-Host ("{0,-20} {1,-15} {2,-10} {3}" -f $proj.Name, $branch, $status, $lastCommit)
        }
        Pop-Location
    }
    Write-Host ""
}
Set-Alias -Name dashboard -Value Show-Dashboard
```

### Changelog automatique

Utiliser `conventional-changelog` ou script custom :

```powershell
function New-Changelog {
    # Génère un changelog depuis les commits conventionnels
    $commits = git log --oneline --since="1 month ago" --format="%s"

    $features = $commits | Where-Object { $_ -match "^feat" }
    $fixes = $commits | Where-Object { $_ -match "^fix" }

    Write-Host "## What's new`n"
    Write-Host "### Features"
    $features | ForEach-Object { Write-Host "- $_" }
    Write-Host "`n### Bug Fixes"
    $fixes | ForEach-Object { Write-Host "- $_" }
}
Set-Alias -Name changelog -Value New-Changelog
```

---

## 5. Monitoring & Debug

### Sentry (Error tracking)

```bash
pnpm add @sentry/nextjs
pnpm exec sentry-wizard -i nextjs
```

Config minimale dans `sentry.client.config.ts` :

```typescript
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  tracesSampleRate: 0.1,
  environment: process.env.NODE_ENV,
});
```

### Logs structurés (Pino)

```typescript
// lib/logger.ts
import pino from 'pino';

export const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  transport: {
    target: 'pino-pretty',
    options: { colorize: true }
  }
});

// Usage
logger.info({ userId, action: 'login' }, 'User logged in');
```

### Performance budgets (Next.js)

```javascript
// next.config.js
module.exports = {
  experimental: {
    webpackBuildWorker: true,
  },
  // Alerte si bundle > 500KB
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.performance = {
        hints: 'warning',
        maxAssetSize: 512000,
        maxEntrypointSize: 512000,
      };
    }
    return config;
  },
};
```

---

## 6. Priorités d'implémentation

### Quick wins (1-2h chacun)
- [ ] Alias `morning` dans le profil PowerShell
- [ ] Alias `dashboard` pour voir l'état des projets
- [ ] Template `.claude/context.md` pour les projets existants

### Medium effort (demi-journée)
- [ ] Pre-commit hooks (Husky + lint-staged) sur un projet pilote
- [ ] Config Biome partagée dans AmarTools
- [ ] Skill `/security-audit`

### Larger effort (1+ jour)
- [ ] Script `newproject` complet avec templates
- [ ] Hook post-edit typecheck dans Claude Code
- [ ] Setup Sentry sur les apps en production

---

## Notes

- Commencer par les quick wins pour voir les bénéfices rapidement
- Tester sur un projet pilote avant de généraliser
- Documenter chaque outil ajouté dans le README du projet
