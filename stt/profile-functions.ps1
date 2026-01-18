# ============================================
# Claude STT - Speech to Text (GUI)
# ============================================
# Ajouter ce bloc à votre profil PowerShell ($PROFILE)
# ============================================

$STT_VENV = "C:\Users\amarm\.claude\plugins\cache\jarrodwatts-claude-stt\claude-stt\0.1.0\.venv"
$STT_PYTHON = "$STT_VENV\Scripts\python.exe"
$STT_PYTHONW = "$STT_VENV\Scripts\pythonw.exe"
$STT_GUI = "C:\Users\amarm\.claude\plugins\claude-stt\stt_gui.pyw"
$STT_PID_FILE = "C:\Users\amarm\.claude\plugins\claude-stt\daemon.pid"

# Helper pour récupérer la fenêtre active
if (-not ([System.Management.Automation.PSTypeName]'Win32Focus').Type) {
    Add-Type @"
    using System;
    using System.Runtime.InteropServices;
    public class Win32Focus {
        [DllImport("user32.dll")]
        public static extern IntPtr GetForegroundWindow();
    }
"@
}

# Lancer le GUI STT (interface graphique)
function Start-STTGUI {
    $hwnd = [Win32Focus]::GetForegroundWindow().ToInt64()
    Start-Process $STT_PYTHONW -ArgumentList "$STT_GUI --hwnd $hwnd" -WindowStyle Hidden
}
Set-Alias -Name stt -Value Start-STTGUI

# Lancer le daemon en arrière-plan
function Start-STTDaemon {
    & $STT_PYTHON -m claude_stt.daemon start --background
}
Set-Alias -Name sttdaemon -Value Start-STTDaemon

# Lancer le daemon en avant-plan (debug)
function Start-STTForeground {
    & $STT_PYTHON -m claude_stt.daemon run
}
Set-Alias -Name sttrun -Value Start-STTForeground

# Arrêter le daemon (avec force si nécessaire)
function Stop-STT {
    # Essayer l'arrêt normal d'abord
    & $STT_PYTHON -m claude_stt.daemon stop 2>$null

    # Si le PID file existe encore, forcer l'arrêt
    if (Test-Path $STT_PID_FILE) {
        $pidData = Get-Content $STT_PID_FILE -Raw | ConvertFrom-Json -ErrorAction SilentlyContinue
        if ($pidData -and $pidData.pid) {
            $proc = Get-Process -Id $pidData.pid -ErrorAction SilentlyContinue
            if ($proc) {
                Write-Host "Forçage de l'arrêt du daemon (PID $($pidData.pid))..." -ForegroundColor Yellow
                Stop-Process -Id $pidData.pid -Force -ErrorAction SilentlyContinue
            }
            Remove-Item $STT_PID_FILE -Force -ErrorAction SilentlyContinue
        }
    }

    # Tuer tous les processus claude_stt orphelins
    Get-Process -Name python*, pythonw* -ErrorAction SilentlyContinue | ForEach-Object {
        $cmd = (Get-CimInstance Win32_Process -Filter "ProcessId=$($_.Id)" -ErrorAction SilentlyContinue).CommandLine
        if ($cmd -and ($cmd -like '*claude_stt*' -or $cmd -like '*stt_gui*')) {
            Write-Host "Arrêt du processus orphelin (PID $($_.Id))..." -ForegroundColor Yellow
            Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
        }
    }
    Write-Host "STT arrêté." -ForegroundColor Green
}
Set-Alias -Name sttstop -Value Stop-STT

# Statut du daemon
function Get-STTStatus {
    & $STT_PYTHON -m claude_stt.daemon status
}
Set-Alias -Name sttstatus -Value Get-STTStatus
