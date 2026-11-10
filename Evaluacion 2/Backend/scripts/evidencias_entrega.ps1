# Ejecuta las pruebas de la Evaluación 2 y guarda los registros en evidencias-entrega\
# Uso (desde la carpeta Backend, con Docker Desktop abierto):
#   powershell -ExecutionPolicy Bypass -File scripts\evidencias_entrega.ps1
# Antes: cierra run_local.py (usa los mismos puertos).

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
Set-Location (Split-Path $PSScriptRoot)
$py = ".venv\Scripts\python.exe"
$salida = Join-Path (Get-Location) "evidencias-entrega"
New-Item -ItemType Directory -Force -Path $salida | Out-Null
Start-Transcript -Path (Join-Path $salida "registro-completo.txt") -Force | Out-Null

$resumen = New-Object System.Collections.ArrayList

function Titulo($t) { Write-Host ""; Write-Host "=== $t ===" -ForegroundColor Cyan }

function Anotar($paso, $ok, $detalle) {
    $estado = if ($ok) { "OK   " } else { "FALLA" }
    [void]$resumen.Add("$estado $paso - $detalle")
    $color = if ($ok) { "Green" } else { "Red" }
    Write-Host "$estado $paso - $detalle" -ForegroundColor $color
}

function Esperar-Gateway {
    for ($i = 0; $i -lt 60; $i++) {
        try {
            $r = Invoke-WebRequest -UseBasicParsing "http://localhost:8000/api/products" -TimeoutSec 3
            if ($r.StatusCode -eq 200) { return $true }
        } catch { }
        Start-Sleep -Seconds 3
    }
    return $false
}

function Guardar($archivo, $lineas) {
    $lineas | Out-File -FilePath (Join-Path $salida $archivo) -Encoding utf8
}

if (-not (Test-Path $py)) {
    Write-Host "Falta el entorno: ejecuta primero los comandos del paso 1 de la guía (python -m venv .venv ...)." -ForegroundColor Red
    Stop-Transcript | Out-Null
    exit 1
}

# 0. Partir limpio: libera los puertos de ejecuciones anteriores
Titulo "0. Limpieza previa"
docker compose down 2>&1 | Out-Host

# 1. Pruebas de Python
Titulo "1. pytest"
$t = & $py -m pytest 2>&1 | ForEach-Object { "$_" }
Guardar "01-pytest.txt" $t
$t | Select-Object -Last 3 | Out-Host
$ok = ($t | Select-String -Pattern "52 passed" -Quiet)
Anotar "pytest" $ok "se esperaba 52 passed"

# 2. Pruebas de Node
Titulo "2. npm test (GraphQL)"
Push-Location graphql
$t = npm.cmd test 2>&1 | ForEach-Object { "$_" }
Pop-Location
Guardar "02-npm-test.txt" $t
$t | Select-Object -Last 10 | Out-Host
$ok = (($t | Select-String -Pattern "pass 15" -Quiet) -and ($t | Select-String -Pattern "fail 0" -Quiet))
Anotar "npm test" $ok "se esperaban 15 pruebas pasando y 0 fallos"

# 3. Docker real
Titulo "3. docker compose up --build"
$t = docker compose up -d --build 2>&1 | ForEach-Object { "$_" }
Guardar "03-docker-up.txt" $t
$arriba = Esperar-Gateway
Start-Sleep -Seconds 5
$ps = docker compose ps 2>&1 | ForEach-Object { "$_" }
Guardar "03-docker-ps.txt" $ps
$ps | Out-Host
Anotar "docker compose up" $arriba "el gateway responde en http://localhost:8000/api/products"

# 4. Secretos leídos desde Vault (las líneas no contienen valores secretos)
Titulo "4. Lectura de secretos desde Vault"
$logs = docker compose logs --no-color vault-init auth clients inventory orders payments gateway graphql 2>&1 | ForEach-Object { "$_" }
$lineas = $logs | Select-String -Pattern "Vault listo|secret/data|Application startup complete|GraphQL privado"
Guardar "04-secretos-vault.txt" ($lineas | ForEach-Object { $_.Line })
$lineas | Out-Host
$n = ($lineas | Select-String -Pattern "secret/data" | Measure-Object).Count
Anotar "Secretos desde Vault" ($n -ge 6) "$n servicios leyeron sus secretos (se esperaban 6 o más)"

# 5. Las 20 validaciones sobre Docker
Titulo "5. Validaciones sobre Vault y MongoDB reales"
$t = & $py scripts\evidencias.py http://localhost:8000 docs\evidencias\validaciones-docker.md --docker 2>&1 | ForEach-Object { "$_" }
Guardar "05-validaciones-docker.txt" $t
$t | Select-Object -Last 8 | Out-Host
$ok = ($t | Select-String -Pattern "20/20 validaciones OK" -Quiet)
Anotar "Validaciones sobre Docker" $ok "se esperaban 20/20 OK"
if (Test-Path docs\evidencias\validaciones-docker.md) { Copy-Item docs\evidencias\validaciones-docker.md $salida -Force }

# 6. Servicios privados sin puertos publicados
Titulo "6. Aislamiento de red"
$aislados = $true
$detalle = @()
foreach ($p in 8100, 8001, 9001, 9002, 9003, 9004, 9005) {
    $abierto = $false
    try { Invoke-WebRequest -UseBasicParsing "http://localhost:$p/" -TimeoutSec 3 | Out-Null; $abierto = $true } catch {
        if ($_.Exception.Response) { $abierto = $true }
    }
    $detalle += "puerto $p : " + $(if ($abierto) { "RESPONDE (no debería)" } else { "sin respuesta (correcto)" })
    if ($abierto) { $aislados = $false }
}
Guardar "06-aislamiento.txt" $detalle
$detalle | Out-Host
Anotar "Aislamiento de red" $aislados "los servicios privados no son accesibles desde el equipo"

# 7. Persistencia: listar, recrear los contenedores sin borrar datos, listar de nuevo
Titulo "7. Persistencia en MongoDB"
$antes = & $py scripts\consultar_pedidos.py http://localhost:8000 2>&1 | ForEach-Object { "$_" }
Guardar "07-pedidos-antes.txt" $antes
$antes | Out-Host
docker compose down 2>&1 | Out-Host
docker compose up -d 2>&1 | Out-Host
$arriba = Esperar-Gateway
Start-Sleep -Seconds 10
$despues = & $py scripts\consultar_pedidos.py http://localhost:8000 2>&1 | ForEach-Object { "$_" }
Guardar "07-pedidos-despues.txt" $despues
$despues | Out-Host
$hay = (($antes | Select-Object -First 1) -match "^[1-9]")
$igual = ((Compare-Object $antes $despues) -eq $null)
Anotar "Persistencia" ($arriba -and $hay -and $igual) "los pedidos son los mismos después de recrear los contenedores"

# 8. Vault detenido: orders no debe arrancar
Titulo "8. Vault detenido"
docker compose stop vault 2>&1 | Out-Host
docker compose restart orders 2>&1 | Out-Host
Start-Sleep -Seconds 20
$ps = docker compose ps 2>&1 | ForEach-Object { "$_" }
$lo = docker compose logs --no-color --tail 30 orders 2>&1 | ForEach-Object { "$_" }
Guardar "08-vault-detenido-ps.txt" $ps
Guardar "08-vault-detenido-orders.txt" $lo
$ps | Out-Host
$lo | Select-Object -Last 8 | Out-Host
$ok = ($lo | Select-String -Pattern "SecretsUnavailable" -Quiet)
Anotar "Vault detenido" $ok "orders se niega a arrancar (SecretsUnavailable)"

# 9. Restaurar y cerrar
Titulo "9. Restauración"
docker compose down 2>&1 | Out-Host
docker compose up -d 2>&1 | Out-Host
$arriba = Esperar-Gateway
$ps = docker compose ps 2>&1 | ForEach-Object { "$_" }
Guardar "09-restauracion-ps.txt" $ps
$ps | Out-Host
Anotar "Restauración" $arriba "el sistema vuelve a responder"
docker compose down 2>&1 | Out-Host

Titulo "RESUMEN"
Guardar "RESUMEN.txt" (@("Resumen de la ejecución - " + (Get-Date -Format "yyyy-MM-dd HH:mm:ss")) + $resumen)
$resumen | Out-Host
Write-Host ""
Write-Host "Registros en: $salida" -ForegroundColor Cyan
Stop-Transcript | Out-Null
