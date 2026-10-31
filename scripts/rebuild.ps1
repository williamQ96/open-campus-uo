param(
    [string]$PipelineRoot = '',
    [string]$Blender = '',
    [string]$Config = 'configs/eugene-main-campus.json',
    [switch]$AllowUnpinned
)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
if (-not $PipelineRoot) {
    $PipelineRoot = Join-Path (Split-Path $projectRoot -Parent) 'open-geospatial-to-3d-reconstruction-pipeline'
}
$PipelineRoot = (Resolve-Path -LiteralPath $PipelineRoot).Path
$lock = Get-Content -LiteralPath (Join-Path $projectRoot 'pipeline.lock.json') -Raw | ConvertFrom-Json
$actual = & git -C $PipelineRoot rev-parse HEAD
if ($LASTEXITCODE -ne 0) { throw 'Cannot read upstream checkout revision.' }
$dirty = & git -C $PipelineRoot status --porcelain
if (-not $AllowUnpinned -and ($actual -ne $lock.commit -or $dirty)) {
    throw 'Upstream must be clean and match pipeline.lock.json. Use -AllowUnpinned only for deliberate development builds.'
}
if (-not $Blender) {
    $Blender = Join-Path $PipelineRoot '.tools/blender-4.5.15-windows-x64/blender.exe'
}
$python = Join-Path $PipelineRoot '.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $python)) { throw 'Create the upstream Python environment as described in its README.' }
if (-not (Test-Path -LiteralPath $Blender)) { throw 'Pass -Blender with a Blender executable, or prepare the documented portable build.' }
$configPath = Join-Path $projectRoot $Config
$sceneConfig = Get-Content -LiteralPath $configPath -Raw | ConvertFrom-Json
$sceneName = $sceneConfig.project_id -replace '^uo-', ''
if ($sceneName -notmatch '^[a-z0-9-]+$') { throw 'Invalid scene identifier.' }
$output = Join-Path $projectRoot "exports/$sceneName"
& $python -m geospatial3d build --config $configPath --workspace $projectRoot --output $output --blender $Blender --web-public (Join-Path $projectRoot 'apps/web-preview/public/scene')
if ($LASTEXITCODE -ne 0) { throw 'Reconstruction failed. Inspect output and blender.log.' }
$assetDir = Join-Path $projectRoot "assets/$sceneName"
New-Item -ItemType Directory -Force -Path $assetDir | Out-Null
Copy-Item -LiteralPath (Join-Path $output 'scene.blend') -Destination (Join-Path $assetDir "$sceneName.blend")
Write-Output "Updated Blender asset and browser scene in $projectRoot"
