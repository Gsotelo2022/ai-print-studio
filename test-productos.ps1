$response = try {
    Invoke-RestMethod -Uri "http://localhost:5001/productos-ia" -Method GET -TimeoutSec 70
} catch {
    Write-Host "Error: $($_.Exception.Message)"
    exit 1
}

Write-Host "Respuesta recibida" -ForegroundColor Green
Write-Host "Total productos: $($response.Count)" -ForegroundColor Cyan

if ($response.Count -gt 0) {
    $primer = $response[0]
    Write-Host "`nPrimer producto:"
    Write-Host "   ID: $($primer.id_producto)"
    Write-Host "   Nombre: $($primer.producto)"
    Write-Host "   Precio: `$$($primer.precio)"
    Write-Host "   Variantes: $($primer.variantes.Count)"
    
    if ($primer.variantes -and $primer.variantes.Count -gt 0) {
        Write-Host "`nPrimera variante:"
        $v = $primer.variantes[0]
        Write-Host "   ID: $($v.id_variante)"
        Write-Host "   Talle: $(if ($v.talle) { $v.talle } else { 'N/A' })"
        Write-Host "   Color: $(if ($v.color) { $v.color } else { 'N/A' })"
        Write-Host "   Precio: `$$($v.precio)"
    }
}
