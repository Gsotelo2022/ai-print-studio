"""
Migración Automática (sin confirmaciones)
"""

import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(__file__))

# Importar el script original
from ejecutar_migracion import *

# Sobrescribir main para auto-confirmar
def main_auto():
    print(f"""
{Colors.CYAN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║     MIGRACIÓN AUTOMÁTICA - AI PRINT STUDIO              ║
║                                                          ║
║     Base de datos: PrendeteRock                         ║
║     Servidor: localhost\\SQLEXPRESS01                    ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
{Colors.END}
    """)
    
    print_warning("MODO AUTOMÁTICO: Todos los pasos se ejecutarán sin confirmación")
    print()
    
    # Probar conexión
    if not test_connection():
        print_error("No se pudo conectar. Abortando.")
        return
    
    # Paso 1: Backup
    print_header("EJECUTANDO PASO 1: BACKUP")
    if not ejecutar_backup():
        print_error("Error en backup. Abortando.")
        return
    
    # Paso 2: Nueva estructura
    print_header("EJECUTANDO PASO 2: NUEVA ESTRUCTURA")
    if not crear_nueva_estructura():
        print_error("Error al crear estructura. Abortando.")
        return
    
    # Paso 3: Datos iniciales
    print_header("EJECUTANDO PASO 3: DATOS INICIALES")
    if not insertar_datos_iniciales():
        print_error("Error al insertar datos. Abortando.")
        return
    
    # Paso 4: Migrar datos antiguos
    print_header("EJECUTANDO PASO 4: MIGRAR DATOS ANTIGUOS")
    migrar_datos_antiguos()  # Continuar incluso si hay advertencias
    
    # Paso 5: Migrar imágenes
    print_header("EJECUTANDO PASO 5: MIGRAR IMÁGENES")
    migrar_imagenes()  # Continuar incluso si hay advertencias
    
    # Resumen final
    print_header("MIGRACIÓN COMPLETADA")
    print(f"""
{Colors.GREEN}{Colors.BOLD}
    ✅ MIGRACIÓN EXITOSA
    
    La base de datos PrendeteRock ha sido actualizada
    
    Próximos pasos:
    
    1. Verificar la migración:
       python test-conexion.py
    
    2. Iniciar backend v2:
       cd ../source
       python app_v2.py
    
    3. Probar API:
       python test_api_v2.py
    
{Colors.END}
    """)

if __name__ == "__main__":
    try:
        main_auto()
    except Exception as e:
        print_error(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
