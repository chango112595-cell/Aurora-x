<#
 * AI Copilot Auto Fix Script (PowerShell)
 *
 * Features:
 * - Clones a GitHub repo
 * - Scans code files in the repo
 * - Uses AI (Copilot-like instructions) to fix bugs and improve code
 * - Creates a new branch and PR
 * - Runs tests and waits for checks
 * - Optionally merges automatically if successful
 *
 * This script is the PowerShell analogue of the "One Big Script for Copilot Instructions".
 * It expects git and PowerShell 7+ to be available on the system.
#>

[CmdletBinding()]
param()

# ----- Environment Variables -----
$env:GITHUB_TOKEN   = $env:GITHUB_TOKEN
$env:OPENAI_API_KEY = $env:OPENAI_API_KEY

if (-not $env:GITHUB_TOKEN) {
    throw "GITHUB_TOKEN environment variable is not set."
}
if (-not $env:OPENAI_API_KEY) {
    throw "OPENAI_API_KEY environment variable is not set."
}

$REPO_OWNER  = if ($env:REPO_OWNER) { $env:REPO_OWNER } else { "your-username" }
$REPO_NAME   = if ($env:REPO_NAME)  { $env:REPO_NAME }  else { "your-repo" }
$BASE_BRANCH = if ($env:BASE_BRANCH){ $env:BASE_BRANCH }else { "main" }
$TEST_COMMAND = if ($env:TEST_COMMAND) { $env:TEST_COMMAND } else { "npm test" }

$FIX_BRANCH = "ai-fixes-$([DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds())"

# ----- Copilot-style instructions for AI -----
$copilotInstructions = @"
You are an expert software engineer. Your task:
1. Review the entire repository for bugs, syntax errors, and failing tests.
2. Fix broken code while preserving functionality.
3. Ensure code follows best practices for readability and maintainability.
4. Do NOT remove essential logic or features.
5. After fixing, ensure all tests pass and code builds successfully.
Return ONLY the corrected code for each file.
"@

function Invoke-Git {
    param(
        [Parameter(Mandatory=$true)][string]$Arguments
    )
    Write-Host "git $Arguments"
    $processInfo = New-Object System.Diagnostics.ProcessStartInfo
    $processInfo.FileName = "git"
    $processInfo.Arguments = $Arguments
    $processInfo.RedirectStandardOutput = $true
    $processInfo.RedirectStandardError = $true
    $processInfo.UseShellExecute = $false
    $processInfo.CreateNoWindow = $true

    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $processInfo
    $null = $process.Start()
    $stdout = $process.StandardOutput.ReadToEnd()
    $stderr = $process.StandardError.ReadToEnd()
    $process.WaitForExit()

    if ($process.ExitCode -ne 0) {
        throw "git $Arguments failed with exit code $($process.ExitCode): `n$stderr"
    }

    if ($stdout) {
        Write-Host $stdout
    }
}

function Clone-Repo {
    Write-Host "📥 Cloning repo https://github.com/$REPO_OWNER/$REPO_NAME.git ..."
    Invoke-Git -Arguments "clone https://github.com/$REPO_OWNER/$REPO_NAME.git"
    Set-Location -Path $REPO_NAME
    Invoke-Git -Arguments "checkout -b $FIX_BRANCH origin/$BASE_BRANCH"
}

function Get-CodeFiles {
    param(
        [string]$Root = ".",
        [string[]]$Extensions = @(".js", ".ts", ".py", ".java")
    )

    $files = Get-ChildItem -Path $Root -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object {
            $ext = $_.Extension
            $Extensions -contains $ext
        }

    return $files
}

function Invoke-OpenAIFix {
    param(
        [Parameter(Mandatory=$true)][string]$Content
    )

    $uri = "https://api.openai.com/v1/chat/completions"

    $bodyObject = @{
        model    = "gpt-4.1"
        messages = @(
            @{ role = "system"; content = "You are an expert developer." },
            @{ role = "user"; content = "$copilotInstructions`n---`n$Content`n---" }
        )
    }

   $jsonBody = $bodyObject | ConvertTo-Json -Depth 5

    $headers = @{
        "Authorization" = "Bearer $($env:OPENAI_API_KEY)"
        "Content-Type"  = "application/json"
    }

    Write-Host "🔮 Calling OpenAI API..."
    $response = Invoke-RestMethod -Uri $uri -Method Post -Headers $headers -Body $jsonBody

    if (-not $response.choices -or -not $response.choices[0].message.content) {
        throw "OpenAI API did not return a valid response."
    }

    return [string]$response.choices[0].message.content
}

function Apply-Fixes {
    param(
        [Parameter(Mandatory=$true)][System.IO.FileInfo[]]$Files
    )

    foreach ($file in $Files) {
        Write-Host "✏️  Processing file: $($file.FullName)"
        $content = Get-Content -Path $file.FullName -Raw

        if (-not $content.Trim()) {
            Write-Host "   Skipping empty file."
            continue
        }

        $fixedContent = Invoke-OpenAIFix -Content $content

        # Overwrite the file with the AI-generated fixed content
        Set-Content -Path $file.FullName -Value $fixedContent -NoNewline
        Write-Host "✅ Fixed: $($file.FullName)"
    }
}

function Commit-And-Push {
    Invoke-Git -Arguments "add ."
    Invoke-Git -Arguments "commit -m `"AI Copilot fixes applied`""
    Invoke-Git -Arguments "push -u origin $FIX_BRANCH"
}

function New-GitHubPullRequest {
    param(
        [Parameter(Mandatory=$true)][string]$Owner,
        [Parameter(Mandatory=$true)][string]$Repo,
        [Parameter(Mandatory=$true)][string]$HeadBranch,
        [Parameter(Mandatory=$true)][string]$BaseBranch
    )

    $uri = "https://api.github.com/repos/$Owner/$Repo/pulls"

    $bodyObject = @{
        title = "AI Copilot Auto Fixes"
        head  = $HeadBranch
        base  = $BaseBranch
        body  = "This PR contains AI-generated fixes for the entire repo."
    }

    $headers = @{
        "Authorization" = "Bearer $($env:GITHUB_TOKEN)"
        "User-Agent"    = "ai-copilot-auto-fix-script"
        "Content-Type"  = "application/json"
    }

    $jsonBody = $bodyObject | ConvertTo-Json -Depth 5

    Write-Host "📤 Creating pull request..."
    $response = Invoke-RestMethod -Uri $uri -Method Post -Headers $headers -Body $jsonBody

    if (-not $response.number) {
        throw "Failed to create pull request."
    }

    Write-Host "🔗 PR created: $($response.html_url)"
    return [int]$response.number
}

function Invoke-Tests {
    Write-Host "🧪 Running tests: $TEST_COMMAND"
    try {
        # Execute the test command through the shell so that complex commands work.
        if ($IsWindows) {
            & cmd.exe /c $TEST_COMMAND
        } else {
            & bash -lc $TEST_COMMAND
        }
        Write-Host "✅ Tests completed successfully."
        return $true
    }
    catch {
        Write-Warning "❌ Tests failed: $($_.Exception.Message)"
        return $false
    }
}

function Wait-ForChecks {
    param(
        [Parameter(Mandatory=$true)][string]$Owner,
        [Parameter(Mandatory=$true)][string]$Repo,
        [Parameter(Mandatory=$true)][string]$Ref
    )

    Write-Host "⏳ Waiting for checks to pass on $Ref ..."

    $headers = @{
        "Authorization" = "Bearer $($env:GITHUB_TOKEN)"
        "User-Agent"    = "ai-copilot-auto-fix-script"
    }

    while ($true) {
        $uri = "https://api.github.com/repos/$Owner/$Repo/commits/$Ref/status"
        $status = Invoke-RestMethod -Uri $uri -Method Get -Headers $headers

        if ($status.state -eq "success") {
            Write-Host "✅ All checks passed!"
            break
        }
        elseif ($status.state -eq "failure") {
            Write-Warning "❌ Some checks failed."
            break
        }
        else {
            Write-Host "Checks still running (state: $($status.state))..."
            Start-Sleep -Seconds 30
        }
    }
}

function Merge-GitHubPullRequest {
    param(
        [Parameter(Mandatory=$true)][string]$Owner,
        [Parameter(Mandatory=$true)][string]$Repo,
        [Parameter(Mandatory=$true)][int]$PullNumber
    )

    $uri = "https://api.github.com/repos/$Owner/$Repo/pulls/$PullNumber/merge"

    $bodyObject = @{
        merge_method = "squash"
    }

    $headers = @{
        "Authorization" = "Bearer $($env:GITHUB_TOKEN)"
        "User-Agent"    = "ai-copilot-auto-fix-script"
        "Content-Type"  = "application/json"
    }

    $jsonBody = $bodyObject | ConvertTo-Json -Depth 5

    Write-Host "🔀 Merging PR #$PullNumber ..."
    $response = Invoke-RestMethod -Uri $uri -Method Put -Headers $headers -Body $jsonBody

    if (-not $response.merged) {
        Write-Warning "PR #$PullNumber was not merged. Message: $($response.message)"
    } else {
        Write-Host "🎉 PR merged successfully!"
    }
}

function Invoke-Main {
    try {
        Clone-Repo
        $files = Get-CodeFiles -Root "."
        if (-not $files -or $files.Count -eq 0) {
            Write-Warning "No code files found to process."
        } else {
            Apply-Fixes -Files $files
            Commit-And-Push
            $prNumber = New-GitHubPullRequest -Owner $REPO_OWNER -Repo $REPO_NAME -HeadBranch $FIX_BRANCH -BaseBranch $BASE_BRANCH

            if (Invoke-Tests) {
                # Wait for remote checks on the branch ref
                Wait-ForChecks -Owner $REPO_OWNER -Repo $REPO_NAME -Ref $FIX_BRANCH
                Merge-GitHubPullRequest -Owner $REPO_OWNER -Repo $REPO_NAME -PullNumber $prNumber
            } else {
                Write-Host "Tests failed locally; PR will remain open for manual review."
            }
        }
    }
    catch {
        Write-Error "An error occurred: $($_.Exception.Message)"
        exit 1
    }
}

# Entry point
Invoke-Main
