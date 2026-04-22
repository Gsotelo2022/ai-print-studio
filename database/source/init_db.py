#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para crear usuarios de prueba en la base de datos
"""

import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    try:
        print("\n[*] Inicializando base de datos...")
        print("    Importando módulos...")
        
        from db import get_connection
        from app import hash_password
        
        print("    ✓ Módulos importados correctamente\n")
        
        # Conectar a la BD
        print("    Conectando a SQL Server SQLEXPRESS01...")
        conn = get_connection()
        cur = conn.cursor()
        print("    ✓ Conexión exitosa\n")
        
        # Contraseña para los usuarios de prueba
        test_password = "password123"
        hashed_password = hash_password(test_password)
        
        print("    Creando usuarios de prueba...\n")
        
        usuarios = [
            ("Juan Cliente", "cliente@test.com", "1234567890", "cliente"),
            ("Admin Rock", "admin@test.com", "1234567890", "admin"),
        ]
        
        usuarios_creados = []
        usuarios_existentes = []
        
        for nombre, email, telefono, tipo in usuarios:
            try:
                # Verificar si ya existe
                cur.execute("SELECT COUNT(*) FROM Usuarios WHERE Email = ?", (email,))
                row = cur.fetchone()
                count = int(row[0]) if row else 0
                
                if count > 0:
                    usuarios_existentes.append(email)
                    print(f"    ⚠ {email} ya existe en la BD")
                else:
                    # Insertar
                    cur.execute(
                        "INSERT INTO Usuarios (Nombre, Email, telefono, password_user, Tipo) VALUES (?, ?, ?, ?, ?)",
                        (nombre, email, telefono, hashed_password, tipo)
                    )
                    conn.commit()
                    usuarios_creados.append(email)
                    print(f"    ✓ {email} creado correctamente")
                    
            except Exception as e:
                print(f"    ✗ Error al crear {email}: {e}")
        
        # Mostrar resumen
        print(f"\n    {'='*45}")
        
        if usuarios_creados:
            print(f"    ✓ {len(usuarios_creados)} usuario(s) creado(s):")
            for email in usuarios_creados:
                print(f"      - {email}")
        
        if usuarios_existentes:
            print(f"    ℹ {len(usuarios_existentes)} usuario(s) ya existen:")
            for email in usuarios_existentes:
                print(f"      - {email}")
        
        # Listar todos los usuarios
        print(f"\n    Total de usuarios en la BD:")
        cur.execute("SELECT COUNT(*) FROM Usuarios")
        total = cur.fetchone()[0]
        print(f"    → {total} usuario(s)")
        
        cur.close()
        conn.close()
        
        print(f"\n    ✓ Base de datos inicializada correctamente")
        print(f"    {'='*45}\n")
        
        return 0
        
    except Exception as e:
        print(f"\n    ✗ ERROR: No se pudo inicializar la BD")
        print(f"    Razón: {e}\n")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
