#!/usr/bin/env python3
"""
Script de prueba rápida del sistema completo
Verifica que todos los componentes estén listos para ejecutarse
"""
import sys
import subprocess
import socket

def check_port_available(port):
    """Verifica si un puerto está disponible"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result != 0  # True si disponible, False si ocupado

def check_command(command, name):
    """Verifica si un comando está disponible"""
    try:
        subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False
        )
        print(f"✅ {name} detectado")
        return True
    except FileNotFoundError:
        print(f"❌ {name} NO detectado")
        return False

def check_database():
    """Verifica conexión a SQL Server"""
    try:
        import pyodbc
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=.\\SQLEXPRESS01;'
            'DATABASE=PrendeteRock;'
            'Trusted_Connection=yes;',
            timeout=5
        )
        conn.close()
        print("✅ Conexión a SQL Server exitosa")
        return True
    except Exception as e:
        print(f"❌ Error conectando a SQL Server: {e}")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("🔍 VERIFICANDO SISTEMA - AI Print Studio")
    print("=" * 70)
    
    print("\n📦 Software Instalado:")
    print("-" * 70)
    python_ok = check_command([sys.executable, "--version"], "Python")
    node_ok = check_command(["node", "--version"], "Node.js")
    ollama_ok = check_command(["ollama", "--version"], "OLLAMA")
    
    print("\n🔌 Puertos Disponibles:")
    print("-" * 70)
    ports = {
        5173: "Vue Frontend",
        8000: "FastAPI Backend",
        8080: "PHP Backend",
        11434: "OLLAMA",
        5001: "Agente IA"
    }
    
    ports_ok = True
    for port, name in ports.items():
        available = check_port_available(port)
        status = "Disponible" if available else "OCUPADO"
        symbol = "✅" if available else "⚠️"
        print(f"{symbol} Puerto {port:5d} - {name:20s} - {status}")
        if not available and port in [5173, 8000]:
            ports_ok = False
    
    print("\n💾 Base de Datos:")
    print("-" * 70)
    db_ok = check_database()
    
    print("\n" + "=" * 70)
    if python_ok and node_ok and ports_ok and db_ok:
        print("✅ SISTEMA LISTO PARA EJECUTAR")
        print("\n🚀 Ejecuta:  RUN.bat")
    else:
        print("⚠️ SISTEMA REQUIERE CONFIGURACIÓN")
        if not python_ok:
            print("   - Instala Python 3.9+")
        if not node_ok:
            print("   - Instala Node.js 18+")
        if not ports_ok:
            print("   - Libera los puertos ocupados o detén RUN.bat anterior")
        if not db_ok:
            print("   - Verifica que SQL Server esté ejecutándose")
            print("   - Ejecuta: database\\estructura-BDD-Prendete-Rock.sql")
        if not ollama_ok:
            print("   ℹ️ OLLAMA no detectado (opcional para agente IA)")
    print("=" * 70)
