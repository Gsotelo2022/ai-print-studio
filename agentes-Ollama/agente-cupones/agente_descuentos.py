import pyodbc
from datetime import datetime
from typing import Dict, List, Optional
import json

class AgenteDescuentos:
    """
    Agente híbrido para gestión de descuentos
    Combina SQL Server para reglas + Ollama para validaciones complejas
    """
    
    def __init__(self):
        self.max_descuento = 35  # Descuento máximo permitido (%)

    def get_db_connection(self):
        """Conectar a SQL Server"""
        try:
            conn = pyodbc.connect(
                'DRIVER={ODBC Driver 17 for SQL Server};'
                'SERVER=.\\SQLEXPRESS01;'
                'DATABASE=PrendeteRock;'
                'Trusted_Connection=yes;'
            )
            return conn
        except Exception as e:
            print(f"Error conectando a la base de datos: {e}")
            raise
    
    def calcular_descuento(self, pedido: Dict) -> Dict:
        """
        Calcula el descuento total aplicable a un pedido
        
        Args:
            pedido: {
                'id_cliente': int,
                'id_pedido': int (opcional),
                'cantidad': int,
                'total': float,
                'productos': list,
                'cupon': str (opcional)
            }
        
        Returns:
            {
                'descuento_total': float,
                'descuentos_aplicados': list,
                'precio_original': float,
                'precio_final': float,
                'ahorro': float
            }
        """
        try:
            descuentos = []
            
            # 1. Descuento por cantidad
            descuento_cantidad = self._calcular_descuento_cantidad(pedido['cantidad'])
            if descuento_cantidad:
                descuentos.append(descuento_cantidad)
            
            # 2. Descuento por cliente (historial)
            descuento_cliente = self._calcular_descuento_cliente(pedido['id_cliente'])
            if descuento_cliente:
                descuentos.append(descuento_cliente)
            
            # 3. Validar cupón si existe
            if pedido.get('cupon'):
                cupon_valido = self._validar_cupon(pedido['cupon'], pedido)
                if cupon_valido:
                    descuentos.append(cupon_valido)
            
            # 4. Descuentos temporales activos
            descuentos_temporales = self._obtener_descuentos_temporales()
            descuentos.extend(descuentos_temporales)
            
            # 5. Combinar descuentos con lógica de negocio
            descuento_final = self._combinar_descuentos(descuentos)
            
            # Aplicar límite máximo
            descuento_final = min(descuento_final, self.max_descuento)
            
            precio_original = float(pedido['total'])
            precio_final = precio_original * (1 - descuento_final / 100)
            ahorro = precio_original - precio_final
            
            return {
                'success': True,
                'descuento_total': round(descuento_final, 2),
                'descuentos_aplicados': descuentos,
                'precio_original': round(precio_original, 2),
                'precio_final': round(precio_final, 2),
                'ahorro': round(ahorro, 2)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'descuento_total': 0,
                'precio_original': pedido['total'],
                'precio_final': pedido['total']
            }
    
    def _calcular_descuento_cantidad(self, cantidad: int) -> Optional[Dict]:
        """Descuento por cantidad de productos"""
        if cantidad >= 10:
            return {'tipo': 'cantidad', 'nombre': '10+ productos', 'porcentaje': 15}
        elif cantidad >= 5:
            return {'tipo': 'cantidad', 'nombre': '5-9 productos', 'porcentaje': 10}
        elif cantidad >= 2:
            return {'tipo': 'cantidad', 'nombre': '2-4 productos', 'porcentaje': 5}
        return None
    
    def _calcular_descuento_cliente(self, id_cliente: int) -> Optional[Dict]:
        """Descuento basado en historial del cliente"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Contar pedidos completados del cliente
            query = """
                SELECT COUNT(*) as total_pedidos
                FROM Pedidos
                WHERE id_cliente = ?
                AND estado = 'completado'
            """
            cursor.execute(query, (id_cliente,))
            result = cursor.fetchone()
            
            if not result:
                # Primera compra
                return {'tipo': 'cliente', 'nombre': 'Primera compra', 'porcentaje': 10}
            
            total_pedidos = result[0]
            
            if total_pedidos >= 10:
                return {'tipo': 'cliente', 'nombre': 'Cliente VIP (10+ compras)', 'porcentaje': 12}
            elif total_pedidos >= 3:
                return {'tipo': 'cliente', 'nombre': 'Cliente frecuente (3+ compras)', 'porcentaje': 5}
            elif total_pedidos == 0:
                return {'tipo': 'cliente', 'nombre': 'Primera compra', 'porcentaje': 10}
            
            return None
            
        except Exception as e:
            print(f"Error calculando descuento cliente: {e}")
            return None
    
    def _validar_cupon(self, codigo: str, pedido: Dict) -> Optional[Dict]:
        """Validar y aplicar cupón"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Buscar cupón en BD
            query = """
                SELECT id_cupon, codigo, descuento_porcentaje, usos_maximos, 
                       usos_actuales, fecha_expiracion, activo, descripcion
                FROM Cupones
                WHERE codigo = ?
            """
            cursor.execute(query, (codigo.upper(),))
            result = cursor.fetchone()
            
            if not result:
                return None
            
            cupon_id, codigo, descuento, usos_max, usos_act, fecha_exp, activo, desc = result
            
            # Validaciones
            if not activo:
                return None
            
            if fecha_exp and datetime.now().date() > fecha_exp:
                return None
            
            if usos_max and usos_act >= usos_max:
                return None
            
            # Cupón válido - registrar uso
            self._registrar_uso_cupon(cupon_id)
            
            return {
                'tipo': 'cupon',
                'nombre': f'Cupón: {codigo}',
                'porcentaje': float(descuento),
                'descripcion': desc
            }
            
        except Exception as e:
            print(f"Error validando cupón: {e}")
            return None
    
    def _registrar_uso_cupon(self, cupon_id: int):
        """Incrementar contador de usos del cupón"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            query = """
                UPDATE Cupones
                SET usos_actuales = usos_actuales + 1
                WHERE id_cupon = ?
            """
            cursor.execute(query, (cupon_id,))
            conn.commit()
        except Exception as e:
            print(f"Error registrando uso de cupón: {e}")
    
    def _obtener_descuentos_temporales(self) -> List[Dict]:
        """Obtener descuentos temporales activos"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT tipo, nombre, descripcion, porcentaje
                FROM Descuentos
                WHERE activo = 1
                AND GETDATE() BETWEEN fecha_inicio AND fecha_fin
            """
            cursor.execute(query)
            
            descuentos = []
            for row in cursor:
                descuentos.append({
                    'tipo': row[0],
                    'nombre': row[1],
                    'porcentaje': float(row[3]),
                    'descripcion': row[2]
                })
            
            return descuentos
            
        except Exception as e:
            print(f"Error obteniendo descuentos temporales: {e}")
            return []
    
    def _combinar_descuentos(self, descuentos: List[Dict]) -> float:
        """
        Combinar múltiples descuentos con lógica de negocio
        
        Reglas:
        - Cupones no se combinan con otros descuentos (se toma el mayor)
        - Descuentos de cantidad + cliente + temporales se suman
        - El total no puede superar el máximo permitido
        """
        if not descuentos:
            return 0.0
        
        # Separar por tipo
        cupon_desc = [d for d in descuentos if d['tipo'] == 'cupon']
        otros_desc = [d for d in descuentos if d['tipo'] != 'cupon']
        
        # Si hay cupón, comparar cupón vs suma de otros
        if cupon_desc:
            max_cupon = max(cupon_desc, key=lambda x: x['porcentaje'])['porcentaje']
            suma_otros = sum(d['porcentaje'] for d in otros_desc)
            return max(max_cupon, suma_otros)
        
        # Si no hay cupón, sumar todos
        return sum(d['porcentaje'] for d in descuentos)
    
    def validar_cupon_disponible(self, codigo: str) -> Dict:
        """Verificar si un cupón existe y está disponible (sin registrar uso)"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT codigo, descuento_porcentaje, usos_maximos, 
                       usos_actuales, fecha_expiracion, activo, descripcion
                FROM Cupones
                WHERE codigo = ?
            """
            cursor.execute(query, (codigo.upper(),))
            result = cursor.fetchone()
            
            if not result:
                return {'valido': False, 'mensaje': 'Cupón no encontrado'}
            
            codigo, descuento, usos_max, usos_act, fecha_exp, activo, desc = result
            
            if not activo:
                return {'valido': False, 'mensaje': 'Cupón inactivo'}
            
            if fecha_exp and datetime.now().date() > fecha_exp:
                return {'valido': False, 'mensaje': 'Cupón expirado'}
            
            if usos_max and usos_act >= usos_max:
                return {'valido': False, 'mensaje': 'Cupón agotado'}
            
            return {
                'valido': True,
                'codigo': codigo,
                'descuento': float(descuento),
                'descripcion': desc,
                'usos_restantes': usos_max - usos_act if usos_max else None
            }
            
        except Exception as e:
            return {'valido': False, 'mensaje': f'Error: {str(e)}'}
    
    def obtener_descuentos_activos(self) -> List[Dict]:
        """Listar todos los descuentos activos"""
        try:
            descuentos = []
            
            # Descuentos temporales
            descuentos.extend(self._obtener_descuentos_temporales())
            
            # Reglas fijas (siempre activas)
            descuentos.append({
                'tipo': 'cantidad',
                'nombre': 'Descuento por cantidad',
                'descripcion': '5% (2-4), 10% (5-9), 15% (10+)',
                'permanente': True
            })
            
            descuentos.append({
                'tipo': 'cliente',
                'nombre': 'Descuento por fidelidad',
                'descripcion': '10% primera compra, 5% (3+), 12% VIP (10+)',
                'permanente': True
            })
            
            return descuentos
            
        except Exception as e:
            print(f"Error listando descuentos activos: {e}")
            return []
    
    # ==================== GESTIÓN DE CUPONES ====================
    
    def listar_cupones(self, incluir_inactivos: bool = False) -> List[Dict]:
        """Listar todos los cupones"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            if incluir_inactivos:
                query = "SELECT * FROM Cupones ORDER BY fecha_creacion DESC"
            else:
                query = """
                    SELECT * FROM Cupones 
                    WHERE activo = 1 
                    AND (fecha_expiracion IS NULL OR fecha_expiracion > GETDATE())
                    ORDER BY fecha_creacion DESC
                """
            
            cursor.execute(query)
            columns = [column[0] for column in cursor.description]
            
            cupones = []
            for row in cursor.fetchall():
                cupon = dict(zip(columns, row))
                # Convertir datetime a string para JSON
                if cupon.get('fecha_expiracion'):
                    cupon['fecha_expiracion'] = cupon['fecha_expiracion'].isoformat()
                if cupon.get('fecha_creacion'):
                    cupon['fecha_creacion'] = cupon['fecha_creacion'].isoformat()
                cupones.append(cupon)
            
            return cupones
            
        except Exception as e:
            print(f"Error listando cupones: {e}")
            return []
    
    def crear_cupon(self, cupon: Dict) -> Dict:
        """
        Crear un nuevo cupón
        
        Args:
            cupon: {
                'codigo': str,
                'descripcion': str,
                'descuento_porcentaje': float,
                'usos_maximos': int (opcional),
                'fecha_expiracion': str (opcional, ISO format)
            }
        """
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Verificar que el código no exista
            cursor.execute("SELECT id_cupon FROM Cupones WHERE codigo = ?", cupon['codigo'])
            if cursor.fetchone():
                return {
                    'success': False,
                    'mensaje': 'El código del cupón ya existe'
                }
            
            # Insertar cupon
            query = """
                INSERT INTO Cupones 
                (codigo, descripcion, descuento_porcentaje, usos_maximos, 
                 usos_actuales, fecha_expiracion, activo, fecha_creacion)
                VALUES (?, ?, ?, ?, 0, ?, 1, GETDATE())
            """
            
            cursor.execute(query, 
                cupon['codigo'],
                cupon.get('descripcion', ''),
                cupon['descuento_porcentaje'],
                cupon.get('usos_maximos'),
                cupon.get('fecha_expiracion')
            )
            
            conn.commit()
            
            return {
                'success': True,
                'mensaje': 'Cupón creado exitosamente',
                'codigo': cupon['codigo']
            }
            
        except Exception as e:
            conn.rollback()
            print(f"Error creando cupón: {e}")
            return {
                'success': False,
                'mensaje': f'Error: {str(e)}'
            }
    
    def actualizar_cupon(self, id_cupon: int, datos: Dict) -> Dict:
        """Actualizar un cupón existente"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Construir query dinámicamente
            campos = []
            valores = []
            
            if 'descripcion' in datos:
                campos.append("descripcion = ?")
                valores.append(datos['descripcion'])
            
            if 'descuento_porcentaje' in datos:
                campos.append("descuento_porcentaje = ?")
                valores.append(datos['descuento_porcentaje'])
            
            if 'usos_maximos' in datos:
                campos.append("usos_maximos = ?")
                valores.append(datos['usos_maximos'])
            
            if 'fecha_expiracion' in datos:
                campos.append("fecha_expiracion = ?")
                valores.append(datos['fecha_expiracion'])
            
            if 'activo' in datos:
                campos.append("activo = ?")
                valores.append(datos['activo'])
            
            if not campos:
                return {'success': False, 'mensaje': 'No hay datos para actualizar'}
            
            query = f"UPDATE Cupones SET {', '.join(campos)} WHERE id_cupon = ?"
            valores.append(id_cupon)
            
            cursor.execute(query, *valores)
            conn.commit()
            
            return {
                'success': True,
                'mensaje': 'Cupón actualizado exitosamente'
            }
            
        except Exception as e:
            conn.rollback()
            print(f"Error actualizando cupón: {e}")
            return {
                'success': False,
                'mensaje': f'Error: {str(e)}'
            }
    
    def eliminar_cupon(self, id_cupon: int, soft_delete: bool = True) -> Dict:
        """Eliminar un cupón (por defecto solo lo desactiva)"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            if soft_delete:
                # Solo desactivar
                cursor.execute("UPDATE Cupones SET activo = 0 WHERE id_cupon = ?", id_cupon)
            else:
                # Eliminar permanentemente
                cursor.execute("DELETE FROM Cupones WHERE id_cupon = ?", id_cupon)
            
            conn.commit()
            
            return {
                'success': True,
                'mensaje': 'Cupón eliminado exitosamente'
            }
            
        except Exception as e:
            conn.rollback()
            print(f"Error eliminando cupón: {e}")
            return {
                'success': False,
                'mensaje': f'Error: {str(e)}'
            }
    
    # ==================== ANÁLISIS Y PROPUESTAS IA ====================
    
    def obtener_estadisticas_ventas(self) -> Dict:
        """Obtener estadísticas de ventas para análisis de IA"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            stats = {}
            
            # Total de ventas último mes
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_pedidos,
                    AVG(total) as ticket_promedio,
                    SUM(total) as ingresos_totales
                FROM Pedidos 
                WHERE fecha_pedido >= DATEADD(month, -1, GETDATE())
                AND estado != 'cancelado' 
            """)
            row = cursor.fetchone()
            if row:
                stats['ultimo_mes'] = {
                    'total_pedidos': row[0] or 0,
                    'ticket_promedio': float(row[1] or 0),
                    'ingresos_totales': float(row[2] or 0)
                }
            
            # Productos más vendidos
            cursor.execute("""
                SELECT TOP 5 
                    p.nombre,
                    COUNT(*) as cantidad_vendida,
                    SUM(dp.cantidad * dp.precio_unitario) as ingresos
                FROM Pedidos_Items dp
                JOIN Producto_Variantes pv ON dp.id_variante = pv.id_variante
                JOIN Productos p ON pv.id_producto = p.id_producto
                JOIN Pedidos ped ON dp.id_pedido = ped.id_pedido
                WHERE ped.fecha_pedido >= DATEADD(month, -1, GETDATE())
                GROUP BY p.nombre
                ORDER BY cantidad_vendida DESC
            """)
            
            productos_top = []
            for row in cursor.fetchall():
                productos_top.append({
                    'nombre': row[0],
                    'cantidad': row[1],
                    'ingresos': float(row[2])
                })
            stats['productos_top'] = productos_top
            
            # Clientes nuevos vs recurrentes
            cursor.execute("""
                SELECT 
                    COUNT(CASE WHEN total_pedidos = 1 THEN 1 END) as clientes_nuevos,
                    COUNT(CASE WHEN total_pedidos > 1 THEN 1 END) as clientes_recurrentes
                FROM (
                    SELECT id_usuario, COUNT(*) as total_pedidos
                    FROM Pedidos
                    WHERE fecha_pedido >= DATEADD(month, -1, GETDATE())
                    GROUP BY id_usuario
                ) subq
            """)
            row = cursor.fetchone()
            if row:
                stats['clientes'] = {
                    'nuevos': row[0] or 0,
                    'recurrentes': row[1] or 0
                }
            
            # Eficiencia de cupones actuales
            cursor.execute("""
                SELECT 
                    c.codigo,
                    c.descuento_porcentaje,
                    c.usos_actuales,
                    c.usos_maximos
                FROM Cupones c
                WHERE c.activo = 1
                AND c.usos_actuales > 0
                ORDER BY c.usos_actuales DESC
            """)
            
            cupones_uso = []
            for row in cursor.fetchall():
                cupones_uso.append({
                    'codigo': row[0],
                    'descuento': float(row[1]),
                    'usos': row[2],
                    'usos_max': row[3],
                    'tasa_uso': (row[2] / row[3] * 100) if row[3] else 0
                })
            stats['cupones_actuales'] = cupones_uso
            
            return stats
            
        except Exception as e:
            print(f"Error obteniendo estadísticas: {e}")
            return {}
    
    def proponer_cupones_ia(self) -> Dict:
        """
        Usar Ollama para proponer cupones inteligentes basados en datos
        """
        try:
            import requests
            
            # Obtener estadísticas
            stats = self.obtener_estadisticas_ventas()
            
            # Preparar prompt para Ollama
            prompt = f"""Eres un experto en marketing y promociones para una tienda de impresión personalizada.

DATOS DE VENTAS ACTUALES:
- Pedidos último mes: {stats.get('ultimo_mes', {}).get('total_pedidos', 0)}
- Ticket promedio: ${stats.get('ultimo_mes', {}).get('ticket_promedio', 0):,.0f}
- Ingresos totales: ${stats.get('ultimo_mes', {}).get('ingresos_totales', 0):,.0f}
- Clientes nuevos: {stats.get('clientes', {}).get('nuevos', 0)}
- Clientes recurrentes: {stats.get('clientes', {}).get('recurrentes', 0)}

Productos más vendidos:
{chr(10).join([f"- {p['nombre']}: {p['cantidad']} unidades" for p in stats.get('productos_top', [])[:3]])}

Fecha actual: {datetime.now().strftime('%d/%m/%Y')}

TAREA: Propón 3 cupones de descuento estratégicos para aumentar ventas. Para cada cupón especifica:
1. Código (8-12 caracteres, sin espacios, mayúsculas)
2. Descripción breve (max 50 caracteres)
3. Porcentaje de descuento (5-25%)
4. Duración sugerida en días
5. Objetivo estratégico (1 línea)

Responde SOLO en formato JSON válido:
{{
  "cupones": [
    {{
      "codigo": "CODIGO",
      "descripcion": "Descripción",
      "descuento": 15,
      "duracion_dias": 7,
      "objetivo": "Objetivo estratégico"
    }}
  ],
  "analisis": "Breve análisis de la situación (2 líneas máximo)"
}}"""

            # Llamar a Ollama
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': 'qwen2.5:1.5b',
                    'prompt': prompt,
                    'stream': False,
                    'format': 'json'
                },
                timeout=240
            )
            
            if response.status_code == 200:
                result = response.json()
                propuesta = json.loads(result['response'])
                
                return {
                    'success': True,
                    'propuesta': propuesta,
                    'estadisticas': stats
                }
            else:
                return {
                    'success': False,
                    'mensaje': 'Error al consultar Ollama',
                    'estadisticas': stats
                }
                
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'mensaje': 'Ollama no está disponible. Inicia Ollama para usar propuestas IA.',
                'estadisticas': stats
            }
        except Exception as e:
            print(f"Error en propuesta IA: {e}")
            return {
                'success': False,
                'mensaje': f'Error: {str(e)}',
                'estadisticas': {}
            }
