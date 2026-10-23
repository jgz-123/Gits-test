param([switch]$Apply)
$ErrorActionPreference = 'Stop'
$metadataPath = Join-Path $PSScriptRoot '../.github/repository-metadata.json'
$metadata = Get-Content -LiteralPath $metadataPath -Raw -Encoding UTF8 | ConvertFrom-Json
$repo = $metadata.repository
Write-Output "Repository: $repo"
Write-Output "Description: $($metadata.description)"
Write-Output "Topics to add: $($metadata.topics -join ', ')"
if (-not $Apply) {
    Write-Output 'Preview only. Use -Apply with an authenticated GitHub CLI to publish.'
    return
}
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) { throw 'GitHub CLI (gh) is required.' }
$currentJson = & gh api "repos/$repo/topics"
if ($LASTEXITCODE -ne 0) { throw 'Failed to read repository topics. Check authentication and permissions.' }
$current = $currentJson | ConvertFrom-Json
$topics = @(@($current.names) + @($metadata.topics) | Where-Object { $_ } | Sort-Object -Unique)
if ($topics.Count -gt 20) { throw 'Merged topics exceed the GitHub limit of 20. Review them before applying.' }
$descriptionPayload = @{ description = $metadata.description } | ConvertTo-Json -Compress
$descriptionPayload | & gh api --method PATCH "repos/$repo" --input - --silent
if ($LASTEXITCODE -ne 0) { throw 'Failed to update description.' }
$topicsPayload = @{ names = $topics } | ConvertTo-Json -Compress
$topicsPayload | & gh api --method PUT "repos/$repo/topics" --input - --silent
if ($LASTEXITCODE -ne 0) { throw 'Description updated, but topics update failed. Re-run after resolving the error.' }
Write-Output 'Description and topics updated; existing topics preserved.'
