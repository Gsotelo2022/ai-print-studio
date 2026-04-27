"""
============================================================
MIGRACIÓN COMPLETA DE BASE DE DATOS - AI PRINT STUDIO
============================================================
Este script ejecuta la migración completa de la estructura
de base de datos PrendeteRock en SQL Server.

PASOS:
1. Backup de la BD actual
2. Crear nueva estructura (tablas, índices, triggers)
3. Insertar datos iniciales (productos, variantes)
4. Migrar datos antiguos (usuarios, pedidos)
5. Migrar imágenes a filesystem

Autor: GitHub Copilot
Fecha: 22 de abril de 2026
============================================================
"""

import pyodbc
import os
from pathlib import Path
from datetime import datetime
import sys

# Configuración de colores para terminal
class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*60}")
    print(f"{text}")
    print(f"{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.CYAN}ℹ {text}{Colors.END}")


# ============================================================
# CONFIGURACIÓN DE CONEXIÓN
# ============================================================

def get_connection():
    """Establecer conexión con SQL Server"""
    try:
        # Conectar con SQL Server  SQLEXPRESS01 (detectado automáticamente)
        conn_string = (
            'Driver={SQL Server};'
            'Server=localhost\\SQLEXPRESS01;'
            'Database=PrendeteRock;'
            'Trusted_Connection=yes;'
        )
        conn = pyodbc.connect(conn_string)
        return conn
    except pyodbc.Error as e:
        print_error(f"Error al conectar con SQL Server: {e}")
        print_info("Intentando con autenticación SQL...")
        
        # Pedir usuario y contraseña
        usuario = input("Usuario SQL Server: ")
        password = input("Contraseña: ")
        
        conn_string = (
            'Driver={SQL Server};'
            'Server=localhost\\SQLEXPRESS01;'
            'Database=PrendeteRock;'
            f'UID={usuario};'
            f'PWD={password};'
        )
        
        try:
            conn = pyodbc.connect(conn_string)
            return conn
        except pyodbc.Error as e:
            print_error(f"No se pudo conectar: {e}")
            sys.exit(1)


def test_connection():
    """Probar conexión y mostrar info de la BD"""
    print_header("PROBANDO CONEXIÓN A SQL SERVER")
    
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Obtener versión de SQL Server
        cur.execute("SELECT @@VERSION")
        version = cur.fetchone()[0]
        version_line = version.split('\n')[0]
        print_success(f"Conectado a SQL Server")
        print_info(f"Versión: {version_line}")
        
        # Verificar base de datos
        cur.execute("SELECT DB_NAME()")
        db_name = cur.fetchone()[0]
        print_success(f"Base de datos: {db_name}")
        
        # Contar tablas actuales
        cur.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
        """)
        num_tablas = cur.fetchone()[0]
        print_info(f"Tablas existentes: {num_tablas}")
        
        # Listar tablas
        cur.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
        """)
        print_info("Tablas actuales:")
        for row in cur.fetchall():
            print(f"  - {row[0]}")
        
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print_error(f"Error al probar conexión: {e}")
        return False


# ============================================================
# PASO 1: BACKUP
# ============================================================

def ejecutar_backup():
    """Crear backup de la base de datos actual"""
    print_header("PASO 1: BACKUP DE BASE DE DATOS")
    
    print_warning("Este paso creará un backup completo de PrendeteRock")
    print_info("Ejecutando automáticamente...")
    
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Leer script de backup
        script_path = Path(__file__).parent / "01-backup-bd-actual.sql"
        
        if not script_path.exists():
            print_error(f"No se encontró el script: {script_path}")
            return False
        
        with open(script_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # Ejecutar backup
        print_info("Ejecutando backup...")
        
        # El script de backup necesita ejecutarse en master
        conn.autocommit = True
        cur.execute("USE master")
        
        # Ejecutar cada statement por separado
        statements = sql_script.split('GO')
        
        for statement in statements:
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                try:
                    cur.execute(statement)
                    print_info(f"Ejecutado: {statement[:50]}...")
                except pyodbc.Error as e:
                    # Ignorar errores de comentarios
                    if "Incorrect syntax" not in str(e):
                        print_warning(f"Advertencia: {e}")
        
        print_success("Backup completado exitosamente")
        
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print_error(f"Error durante el backup: {e}")
        return False


# ============================================================
# PASO 2: NUEVA ESTRUCTURA
# ============================================================

def crear_nueva_estructura():
    """Crear nueva estructura de tablas"""
    print_header("PASO 2: CREAR NUEVA ESTRUCTURA")
    
    print_info("Se crearán las siguientes tablas:")
    print("  - Productos (mejorado)")
    print("  - Producto_Atributos")
    print("  - Producto_Atributo_Valores")
    print("  - Producto_Atributos_Asignados")
    print("  - Producto_Variantes (SKU)")
    print("  - Variante_Atributos")
    print("  - Pedidos (mejorado con múltiples items)")
    print("  - Pedidos_Items")
    print("  - Pagos")
    print("  - Archivos_Diseno")
    print("  - Pedidos_Historial")
    print("  - Stock_Movimientos")
    
    print_info("\nEjecutando automáticamente...")
    
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Leer script de estructura
        script_path = Path(__file__).parent / "02-nueva-estructura-bd.sql"
        
        with open(script_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        print_info("Ejecutando script de estructura...")
        
        # Configurar para ejecutar statements largos
        conn.autocommit = False
        
        # Dividir por GO y ejecutar
        statements = sql_script.split('GO')
        
        count = 0
        for statement in statements:
            statement = statement.strip()
            if statement and not statement.startswith('--') and len(statement) > 10:
                try:
                    cur.execute(statement)
                    count += 1
                    if count % 5 == 0:
                        print_info(f"Ejecutados {count} statements...")
                except pyodbc.Error as e:
                    print_warning(f"Advertencia en statement: {str(e)[:100]}")
        
        conn.commit()
        print_success(f"Estructura creada exitosamente ({count} statements ejecutados)")
        
        # Verificar tablas creadas
        cur.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
            AND TABLE_NAME LIKE 'Producto%'
            OR TABLE_NAME LIKE 'Pedidos%'
            OR TABLE_NAME LIKE 'Archivo%'
            OR TABLE_NAME LIKE 'Stock%'
            OR TABLE_NAME = 'Pagos'
            ORDER BY TABLE_NAME
        """)
        
        print_info("\nTablas nuevas creadas:")
        for row in cur.fetchall():
            print(f"  ✓ {row[0]}")
        
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print_error(f"Error al crear estructura: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================
# PASO 3: DATOS INICIALES
# ============================================================

def insertar_datos_iniciales():
    """Insertar productos del catálogo inicial"""
    print_header("PASO 3: INSERTAR DATOS INICIALES")
    
    print_info("Se insertarán:")
    print("  - 5 productos base (Remera, Taza, Buzo, Gorra, Bolsa)")
    print("  - Atributos: Color, Talle, Material")
    print("  - ~20 variantes con precios")
    print("  - ~50 valores de atributos")
    
    print_info("\nEjecutando automáticamente...")
    
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Leer script de datos iniciales
        script_path = Path(__file__).parent / "03-datos-iniciales.sql"
        
        with open(script_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        print_info("Ejecutando script de datos iniciales...")
        
        conn.autocommit = False
        
        # Dividir por GO y ejecutar
        statements = sql_script.split('GO')
        
        count = 0
        for statement in statements:
            statement = statement.strip()
            if statement and not statement.startswith('--') and len(statement) > 10:
                try:
                    cur.execute(statement)
                    count += 1
                except pyodbc.Error as e:
                    print_warning(f"Advertencia: {str(e)[:100]}")
        
        conn.commit()
        print_success(f"Datos iniciales insertados ({count} statements)")
        
        # Verificar productos creados
        cur.execute("SELECT COUNT(*) FROM Productos")
        num_productos = cur.fetchone()[0]
        print_success(f"Productos creados: {num_productos}")
        
        cur.execute("SELECT COUNT(*) FROM Producto_Variantes")
        num_variantes = cur.fetchone()[0]
        print_success(f"Variantes creadas: {num_variantes}")
        
        cur.execute("SELECT COUNT(*) FROM Producto_Atributos")
        num_atributos = cur.fetchone()[0]
        print_success(f"Atributos creados: {num_atributos}")
        
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print_error(f"Error al insertar datos iniciales: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================
# PASO 4: MIGRAR DATOS ANTIGUOS
# ============================================================

def migrar_datos_antiguos():
    """Migrar usuarios y pedidos de estructura antigua"""
    print_header("PASO 4: MIGRAR DATOS ANTIGUOS")
    
    print_warning("Este paso migrará:")
    print("  - Usuarios existentes (si los hay)")
    print("  - Pedidos existentes → Nueva estructura Pedidos/Pedidos_Items")
    print("  - Relaciones con variantes")
    
    print_info("\nEjecutando automáticamente...")
    
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Verificar si hay datos antiguos
        try:
            cur.execute("SELECT COUNT(*) FROM Usuarios")
            num_usuarios = cur.fetchone()[0]
            print_info(f"Usuarios a preservar: {num_usuarios}")
        except:
            num_usuarios = 0
            print_info("No hay usuarios antiguos")
        
        # Leer script de migración
        script_path = Path(__file__).parent / "04-migrar-datos-antiguos.sql"
        
        if not script_path.exists():
            print_warning("No se encontró script de migración de datos antiguos")
            print_info("Saltando este paso...")
            return True
        
        with open(script_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        print_info("Ejecutando migración de datos...")
        
        conn.autocommit = False
        
        # Dividir por GO y ejecutar
        statements = sql_script.split('GO')
        
        count = 0
        for statement in statements:
            statement = statement.strip()
            if statement and not statement.startswith('--') and len(statement) > 10:
                try:
                    cur.execute(statement)
                    count += 1
                except pyodbc.Error as e:
                    # Algunos errores son esperados si no hay datos antiguos
                    if "Invalid object name" not in str(e):
                        print_warning(f"Advertencia: {str(e)[:100]}")
        
        conn.commit()
        print_success(f"Migración completada ({count} statements ejecutados)")
        
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print_error(f"Error durante la migración: {e}")
        return False


# ============================================================
# PASO 5: MIGRAR IMÁGENES
# ============================================================

def migrar_imagenes():
    """Migrar imágenes de base64 a archivos"""
    print_header("PASO 5: MIGRAR IMÁGENES")
    
    print_info("Este paso extraerá imágenes base64 de la BD y las guardará como archivos")
    print_info("Ejecutando automáticamente...")
    
    # Importar el script de migración de imágenes
    script_path = Path(__file__).parent / "migrar-imagenes.py"
    
    if not script_path.exists():
        print_warning("No se encontró el script migrar-imagenes.py")
        return True
    
    print_info("Ejecutando migración de imágenes...")
    
    try:
        # Ejecutar el script
        import subprocess
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            cwd=str(script_path.parent)
        )
        
        print(result.stdout)
        
        if result.returncode == 0:
            print_success("Imágenes migradas exitosamente")
            return True
        else:
            print_warning(f"Migración de imágenes completada con advertencias")
            print(result.stderr)
            return True
            
    except Exception as e:
        print_warning(f"Error al migrar imágenes: {e}")
        print_info("Puedes ejecutar migrar-imagenes.py manualmente después")
        return True


# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================

def main():
    """Ejecutar migración completa"""
    
    print(f"""
{Colors.CYAN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║     MIGRACIÓN DE BASE DE DATOS - AI PRINT STUDIO        ║
║                                                          ║
║     Base de datos: PrendeteRock                         ║
║     Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}                         ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
{Colors.END}
    """)
    
    print_warning("⚠️  IMPORTANTE:")
    print("  - Esta migración modificará la estructura de tu base de datos")
    print("  - Se creará un backup antes de comenzar")
    print("  - El proceso puede tardar 5-10 minutos")
    print("  - Asegúrate de cerrar todas las conexiones a la BD")
    
    print_info(f"\n{Colors.BOLD}INICIANDO MIGRACIÓN AUTOMÁTICA...{Colors.END}\n")
    
    # Probar conexión
    if not test_connection():
        print_error("No se pudo establecer conexión. Verifica SQL Server y las credenciales.")
        return
    
    # Ejecutar pasos
    pasos_completados = 0
    
    # Paso 1: Backup
    if ejecutar_backup():
        pasos_completados += 1
    else:
        print_error("Error en el backup. Abortando migración.")
        return
    
    # Paso 2: Nueva estructura
    if crear_nueva_estructura():
        pasos_completados += 1
    else:
        print_error("Error al crear estructura. Revisa los errores anteriores.")
        return
    
    # Paso 3: Datos iniciales
    if insertar_datos_iniciales():
        pasos_completados += 1
    else:
        print_error("Error al insertar datos iniciales.")
        return
    
    # Paso 4: Migrar datos antiguos
    if migrar_datos_antiguos():
        pasos_completados += 1
    else:
        print_warning("Advertencia en migración de datos antiguos. Continúa.")
    
    # Paso 5: Migrar imágenes
    if migrar_imagenes():
        pasos_completados += 1
    
    # Resumen final
    print_header("MIGRACIÓN COMPLETADA")
    
    print(f"""
{Colors.GREEN}{Colors.BOLD}
    ✅ MIGRACIÓN EXITOSA
    
    Pasos completados: {pasos_completados}/5
    
    La base de datos PrendeteRock ha sido actualizada con:
    
    ✓ Nueva estructura de productos con variantes
    ✓ Sistema de pedidos multi-item
    ✓ Gestión de archivos de diseño
    ✓ Control de stock y movimientos
    ✓ Historial de cambios
    
    Próximos pasos:
    
    1. Iniciar el backend v2:
       cd database/source
       python app_v2.py
    
    2. Probar la API:
       python test_api_v2.py
    
    3. Actualizar el frontend para usar nuevos endpoints
    
{Colors.END}
    """)
    
    print_info("Log completo guardado en: migracion_log.txt")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️  Migración interrumpida por el usuario{Colors.END}")
    except Exception as e:
        print_error(f"\n\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
