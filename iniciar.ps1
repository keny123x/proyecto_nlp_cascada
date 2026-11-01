param([ValidateSet('api', 'frontend', 'tests')][string]$Modo = 'api')
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$proyectoPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $proyectoPython)) {
    throw 'Falta el entorno .venv. Sigue la instalación del README.md antes de iniciar.'
}
$env:NLTK_DATA = Join-Path $PSScriptRoot '.venv\nltk_data'
$env:PYTHONIOENCODING = 'utf-8'
switch ($Modo) {
    'api' { & $proyectoPython -m uvicorn api.main:app --host 127.0.0.1 --port 8000 }
    'frontend' { & $proyectoPython -m http.server 5173 --bind 127.0.0.1 --directory frontend }
    'tests' { & $proyectoPython -m pytest api/test_main.py -q }
}
exit $LASTEXITCODE
