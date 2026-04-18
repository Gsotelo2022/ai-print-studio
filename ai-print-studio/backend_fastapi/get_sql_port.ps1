$instance = 'SQLEXPRESS01'
$regPath = 'HKLM:\SOFTWARE\Microsoft\Microsoft SQL Server\Instance Names\SQL'
if (-not (Test-Path $regPath)) {
    Write-Output "No se encontró mapeo de instancias en registro: $regPath"
    exit 1
}
$map = Get-ItemProperty -Path $regPath
$iid = $map.$instance
Write-Output "InstanceId=$iid"
if (-not $iid) {
    Write-Output "Instancia '$instance' no encontrada en mapeo. Entradas disponibles:" 
    $map | Get-Member -MemberType NoteProperty | ForEach-Object { Write-Output $_.Name }
    exit 1
}
$ipall = "HKLM:\SOFTWARE\Microsoft\Microsoft SQL Server\$iid\MSSQLServer\SuperSocketNetLib\Tcp\IPAll"
if (-not (Test-Path $ipall)) {
    Write-Output "No existe la clave $ipall"
    exit 1
}
Get-ItemProperty -Path $ipall | Select-Object TcpPort,TcpDynamicPorts | Format-List
Write-Output "\nListado de IP* bajo SuperSocketNetLib\Tcp:"
$tcpRoot = "HKLM:\\SOFTWARE\\Microsoft\\Microsoft SQL Server\\$iid\\MSSQLServer\\SuperSocketNetLib\\Tcp"
Get-ChildItem -Path $tcpRoot | ForEach-Object {
    $key = $_.PSPath
    Write-Output "---- $($_.PSChildName) ----"
    Get-ItemProperty -Path $key | Select-Object IPAddress,Enabled,Active,TcpPort,TcpDynamicPorts | Format-List
}
