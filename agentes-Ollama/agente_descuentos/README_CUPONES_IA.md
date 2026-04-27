# 🎟️ Sistema de Gestión de Cupones con IA

## 📋 Descripción

Sistema completo de gestión de cupones con **inteligencia artificial** que aprende del comportamiento de ventas y propone descuentos estratégicos automáticamente.

## ✨ Características

### 🤖 Inteligencia Artificial
- **Propuestas Automáticas**: El agente analiza tus datos de ventas y propone cupones estratégicos
- **Aprendizaje Continuo**: Estudia patrones de compra, temporadas y comportamiento de clientes
- **Análisis en Tiempo Real**: Estadísticas actualizadas de ventas y clientes

### 💼 Gestión Completa
- **CRUD de Cupones**: Crear, editar, eliminar y listar cupones
- **Panel de Administración**: Interfaz visual integrada en el admin
- **Estadísticas**: Métricas de uso, pedidos, ticket promedio, clientes

### 🎁 Descuentos Inteligentes
- **Por Cantidad**: 5% (2-4), 10% (5-9), 15% (10+)
- **Por Fidelidad**: 10% primera compra, 5% (3+), 12% VIP (10+)
- **Cupones Personalizados**: Códigos con validación y límites
- **Combinación Inteligente**: Máximo 35% de descuento total

## 🚀 Endpoints de la API

### Gestión de Cupones

#### GET `/api/cupones`
Lista todos los cupones disponibles.

**Query params:**
- `incluir_inactivos` (bool): incluir cupones desactivados

**Respuesta:**
```json
{
  "success": true,
  "cupones": [
    {
      "id_cupon": 1,
      "codigo": "PRIMERACOMPRA10",
      "descripcion": "Descuento para primera compra",
      "descuento_porcentaje": 10.0,
      "usos_maximos": null,
      "usos_actuales": 5,
      "fecha_expiracion": null,
      "activo": true,
      "fecha_creacion": "2026-04-27T12:27:30"
    }
  ],
  "total": 1
}
```

#### POST `/api/cupones`
Crear un nuevo cupón.

**Body:**
```json
{
  "codigo": "VERANO2026",
  "descripcion": "Descuento de verano",
  "descuento_porcentaje": 20,
  "usos_maximos": 100,
  "fecha_expiracion": "2026-06-30"
}
```

**Respuesta:**
```json
{
  "success": true,
  "mensaje": "Cupón creado exitosamente",
  "codigo": "VERANO2026"
}
```

#### PUT `/api/cupones/{id}`
Actualizar un cupón existente.

**Body:**
```json
{
  "descripcion": "Nueva descripción",
  "descuento_porcentaje": 25,
  "activo": true
}
```

#### DELETE `/api/cupones/{id}`
Eliminar un cupón (soft delete por defecto).

**Query params:**
- `permanente` (bool): eliminación permanente

---

### Análisis e Inteligencia

#### GET `/api/estadisticas`
Obtener estadísticas de ventas actualizadas.

**Respuesta:**
```json
{
  "success": true,
  "estadisticas": {
    "ultimo_mes": {
      "total_pedidos": 45,
      "ticket_promedio": 15000.0,
      "ingresos_totales": 675000.0
    },
    "productos_top": [
      {
        "nombre": "Remera Estampada",
        "cantidad": 120,
        "ingresos": 180000.0
      }
    ],
    "clientes": {
      "nuevos": 15,
      "recurrentes": 30
    },
    "cupones_actuales": [
      {
        "codigo": "PRIMERACOMPRA10",
        "descuento": 10.0,
        "usos": 25,
        "usos_max": 100,
        "tasa_uso": 25.0
      }
    ]
  }
}
```

#### POST `/api/cupones/proponer`
**🤖 Propuestas inteligentes con IA**

El agente analiza todos los datos y propone cupones estratégicos.

**Respuesta:**
```json
{
  "success": true,
  "propuesta": {
    "cupones": [
      {
        "codigo": "MAYO2026",
        "descripcion": "Descuento especial de mayo",
        "descuento": 15,
        "duracion_dias": 7,
        "objetivo": "Aumentar ventas en período bajo"
      },
      {
        "codigo": "NUEVOCLIENTE",
        "descripcion": "Bienvenida para nuevos usuarios",
        "descuento": 20,
        "duracion_dias": 30,
        "objetivo": "Captar nuevos clientes"
      },
      {
        "codigo": "FIDEL2026",
        "descripcion": "Recompensa por lealtad",
        "descuento": 12,
        "duracion_dias": 14,
        "objetivo": "Retener clientes recurrentes"
      }
    ],
    "analisis": "Las ventas han disminuido 15% este mes. Recomiendo cupones para impulsar nuevas compras y retener clientes."
  },
  "estadisticas": { /* ... */ }
}
```

## 🎨 Panel de Administración

Accede al panel desde **AdminDashboard → 🎟️ Cupones**

### Funcionalidades del Panel

1. **Estadísticas en Tiempo Real**
   - Pedidos del último mes
   - Ticket promedio
   - Clientes nuevos vs recurrentes

2. **Botón "🤖 Proponer Cupones con IA"**
   - Analiza tus datos automáticamente
   - Genera 3 cupones estratégicos
   - Muestra análisis de la situación actual
   - Permite crear cupones con un clic

3. **Lista de Cupones**
   - Ver todos los cupones activos/inactivos
   - Editar cupones existentes
   - Activar/Desactivar cupones
   - Eliminar cupones

4. **Crear Cupones Manualmente**
   - Formulario con validación
   - Código (solo mayúsculas y números)
   - Porcentaje de descuento
   - Límite de usos (opcional)
   - Fecha de expiración (opcional)

## 🔧 Configuración

### 1. Base de Datos

Las tablas ya están creadas:
- `Cupones`: almacena todos los cupones
- `Descuentos`: descuentos temporales/promociones

### 2. Iniciar el Servicio

```bash
# Windows
cd agentes-Ollama\agente_descuentos
start-agente-descuentos.bat

# O manualmente
python api_descuentos.py
```

El servicio estará disponible en: `http://localhost:5003`

### 3. Ollama (Opcional)

Para usar propuestas IA, asegúrate de tener Ollama corriendo:

```bash
ollama serve
```

Si Ollama no está disponible, el sistema funciona normalmente pero sin propuestas automáticas.

## 📊 Cómo Funciona la IA

1. **Recopilación de Datos**
   - Pedidos del último mes
   - Ticket promedio
   - Productos más vendidos
   - Clientes nuevos vs recurrentes
   - Eficiencia de cupones actuales

2. **Análisis con Ollama**
   - El agente envía los datos a Ollama (modelo qwen2.5:1.5b)
   - Ollama analiza patrones y tendencias
   - Genera estrategias de descuentos personalizadas

3. **Propuesta Inteligente**
   - 3 cupones con código, descripción y objetivo
   - Porcentajes optimizados (5-25%)
   - Duración sugerida
   - Análisis textual de la situación

## 🧪 Testing

Ejecuta el test completo:

```powershell
cd agentes-Ollama\agente_descuentos
.\test_simple.ps1
```

Resultado esperado:
```
✓ API funcionando
✓ Cupones listados
✓ Estadísticas obtenidas
✓ Ollama disponible
```

## 💡 Ejemplos de Uso

### Desde el Admin Panel

1. Abre el panel de administración
2. Ve a **Cupones** en el menú lateral
3. Click en **"🤖 Proponer Cupones con IA"**
4. Revisa las propuestas generadas
5. Click en **"✓ Crear Este Cupón"** para aplicar

### Desde Código (Frontend)

```javascript
// Obtener propuestas de IA
const response = await fetch('http://localhost:5003/api/cupones/proponer', {
  method: 'POST'
})
const data = await response.json()

if (data.success) {
  console.log('Análisis:', data.propuesta.analisis)
  data.propuesta.cupones.forEach(cupon => {
    console.log(`${cupon.codigo}: ${cupon.descuento}% - ${cupon.objetivo}`)
  })
}
```

```javascript
// Crear cupón manualmente
const response = await fetch('http://localhost:5003/api/cupones', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    codigo: 'ESPECIAL2026',
    descripcion: 'Oferta especial limitada',
    descuento_porcentaje: 18,
    usos_maximos: 50,
    fecha_expiracion: '2026-12-31'
  })
})
```

### Desde cURL

```bash
# Ver estadísticas
curl http://localhost:5003/api/estadisticas

# Proponer cupones
curl -X POST http://localhost:5003/api/cupones/proponer

# Crear cupón
curl -X POST http://localhost:5003/api/cupones \
  -H "Content-Type: application/json" \
  -d '{
    "codigo": "PRUEBA2026",
    "descripcion": "Cupón de prueba",
    "descuento_porcentaje": 15,
    "usos_maximos": 10
  }'
```

## 🔒 Validaciones

- **Código único**: no se pueden duplicar códigos
- **Porcentaje**: 1-99%
- **Descuento máximo**: 35% total combinado
- **Formato de código**: solo mayúsculas y números
- **Fechas**: validación de expiración

## 📈 Próximas Mejoras

- [ ] Análisis A/B de cupones
- [ ] Predicción de demanda
- [ ] Segmentación automática de clientes
- [ ] Notificaciones de cupones personalizados
- [ ] Dashboard de conversión de cupones
- [ ] Integración con mail marketing

## 🆘 Troubleshooting

**Error: "Ollama no disponible"**
- Inicia Ollama: `ollama serve`
- El sistema funciona sin IA, solo sin propuestas automáticas

**Error: "API no disponible"**
- Verifica que el servicio esté corriendo en puerto 5003
- Reinicia: `python api_descuentos.py`

**Error: "Cupón no encontrado"**
- Verifica que el cupón esté activo
- Revisa la fecha de expiración

## 📝 Notas

- Los cupones eliminados se desactivan (soft delete) por defecto
- Las estadísticas se calculan en tiempo real
- La IA requiere al menos algunos datos de ventas para propuestas útiles
- Máximo descuento combinado: 35%

---

**Documentación API completa**: http://localhost:5003/docs
