# PowerShell Status Line Script for Claude Code
$ErrorActionPreference = 'SilentlyContinue'

# Read JSON input from stdin using Console.In
$input_json = ""
while (($line = [Console]::In.ReadLine()) -ne $null) {
    $input_json += $line
}

if (-not $input_json -or $input_json.Length -lt 2) {
    Write-Host "?" -NoNewline
    exit 0
}

# Parse JSON using ConvertFrom-Json
try {
    $data = $input_json | ConvertFrom-Json
} catch {
    Write-Host "!" -NoNewline
    exit 0
}

# Extract information
$model_name = $data.model.display_name
$current_dir = $data.workspace.current_dir
$context_size = if ($data.context_window.context_window_size) { $data.context_window.context_window_size } else { 200000 }
$current_usage = $data.context_window.current_usage

# Calculate context percentage
$context_percent = 0
if ($current_usage) {
    $current_tokens = 0
    if ($current_usage.input_tokens) { $current_tokens += $current_usage.input_tokens }
    if ($current_usage.cache_creation_input_tokens) { $current_tokens += $current_usage.cache_creation_input_tokens }
    if ($current_usage.cache_read_input_tokens) { $current_tokens += $current_usage.cache_read_input_tokens }
    if ($context_size -gt 0) {
        $context_percent = [math]::Floor($current_tokens * 100 / $context_size)
    }
}

# Build context progress bar (15 chars wide)
$bar_width = 15
$filled = [math]::Floor($context_percent * $bar_width / 100)
$empty = $bar_width - $filled
$bar = ([string][char]0x2588 * $filled) + ([string][char]0x2591 * $empty)

# Extract cost information
$cost_formatted = $null
if ($data.cost -and $data.cost.total_cost_usd) {
    $cost_formatted = $data.cost.total_cost_usd.ToString("0.0000")
}

# Get directory name
$dir_name = if ($current_dir) { Split-Path -Leaf $current_dir } else { "?" }

# ANSI Colors
$ESC = [char]27
$RED = "$ESC[31m"
$GREEN = "$ESC[32m"
$BLUE = "$ESC[34m"
$YELLOW = "$ESC[33m"
$CYAN = "$ESC[36m"
$GRAY = "$ESC[90m"
$NC = "$ESC[0m"

# Get git info
$git_info = ""
if ($current_dir -and (Test-Path $current_dir)) {
    $original_location = Get-Location
    try {
        Set-Location $current_dir -ErrorAction Stop

        $is_git = git rev-parse --is-inside-work-tree 2>$null
        if ($is_git -eq 'true') {
            $branch = git branch --show-current 2>$null
            if (-not $branch) { $branch = "detached" }

            $status_output = git status --porcelain 2>$null

            if ($status_output) {
                $total_files = @($status_output).Count

                # Get line stats
                $diff_stats = git diff --numstat HEAD 2>$null
                $added = 0
                $removed = 0

                if ($diff_stats) {
                    foreach ($line in @($diff_stats)) {
                        $parts = $line -split '\s+'
                        if ($parts[0] -match '^\d+$') { $added += [int]$parts[0] }
                        if ($parts[1] -match '^\d+$') { $removed += [int]$parts[1] }
                    }
                }

                $git_info = " ${YELLOW}($branch${NC} ${YELLOW}|${NC} ${GRAY}${total_files}f${NC}"
                if ($added -gt 0) { $git_info += " ${GREEN}+${added}${NC}" }
                if ($removed -gt 0) { $git_info += " ${RED}-${removed}${NC}" }
                $git_info += "${YELLOW})${NC}"
            } else {
                $git_info = " ${YELLOW}($branch)${NC}"
            }
        }
    } catch { }
    Set-Location $original_location -ErrorAction SilentlyContinue
}

# STT Status
$stt_status = ""
$stt_file = "$env:USERPROFILE\.claude\plugins\claude-stt\status"
if (Test-Path $stt_file) {
    $stt_state = (Get-Content $stt_file -Raw).Trim()
    switch ($stt_state) {
        "recording"    { $stt_status = " ${RED}🎤${NC}" }
        "transcribing" { $stt_status = " ${YELLOW}⏳${NC}" }
    }
}

# Add session cost if available
$cost_info = ""
if ($cost_formatted) {
    $cost_info = " ${GRAY}[`$$cost_formatted]${NC}"
}

# Build context bar display
$context_info = "${GRAY}${bar}${NC} ${context_percent}%"

# Build git separator
$git_sep = if ($git_info) { " ${GRAY}|${NC}" } else { "" }

# Output the status line
Write-Host "${BLUE}${dir_name}${NC} ${GRAY}|${NC} ${CYAN}${model_name}${NC} ${GRAY}|${NC} ${context_info}${git_sep}${git_info}${cost_info}${stt_status}" -NoNewline
