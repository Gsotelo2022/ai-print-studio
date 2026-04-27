-- ================================================================
-- SCRIPT 1: BACKUP DE BASE DE DATOS ACTUAL
-- ================================================================
-- Descripción: Crear backup completo antes de la migración
-- Fecha: 22 de abril de 2026
-- IMPORTANTE: EJECUTAR ESTO ANTES DE CUALQUIER CAMBIO
-- ================================================================

USE master;
GO

-- Crear directorio de backups si no existe
-- NOTA: Ajustar la ruta según tu instalación de SQL Server
DECLARE @BackupPath VARCHAR(500) = 'C:\SQLBackups\';
DECLARE @BackupFile VARCHAR(500);
DECLARE @BackupName VARCHAR(200);
DECLARE @SQLCommand NVARCHAR(1000);

-- Crear nombre con timestamp
SET @BackupName = 'PrendeteRock_PreMigracion_' + 
                  CONVERT(VARCHAR, GETDATE(), 112) + '_' + 
                  REPLACE(CONVERT(VARCHAR, GETDATE(), 108), ':', '');
SET @BackupFile = @BackupPath + @BackupName + '.bak';

-- Crear backup FULL
BACKUP DATABASE PrendeteRock
TO DISK = @BackupFile
WITH 
    FORMAT,
    INIT,
    NAME = @BackupName,
    SKIP,
    REWIND,
    NOUNLOAD,
    COMPRESSION,
    STATS = 10;

PRINT '✅ BACKUP COMPLETADO EXITOSAMENTE';
PRINT '📁 Ubicación: ' + @BackupFile;
PRINT '💾 Tamaño: ' + CAST((SELECT SUM(backup_size)/1024/1024 FROM msdb.dbo.backupset WHERE database_name = 'PrendeteRock' AND backup_finish_date = (SELECT MAX(backup_finish_date) FROM msdb.dbo.backupset WHERE database_name = 'PrendeteRock')) AS VARCHAR) + ' MB';

-- Script adicional: Exportar datos como INSERT statements (backup secundario)
PRINT '';
PRINT '📋 RECOMENDACIÓN: Exportar también los datos como scripts SQL';
PRINT '   Usar: SQL Server Management Studio → Tareas → Generar Scripts';
PRINT '   Seleccionar: Esquema y Datos';

GO

-- ================================================================
-- VERIFICAR INTEGRIDAD DEL BACKUP
-- ================================================================
DECLARE @BackupPath VARCHAR(500) = 'C:\SQLBackups\';
DECLARE @BackupName VARCHAR(200);
DECLARE @BackupFile VARCHAR(500);

SET @BackupName = 'PrendeteRock_PreMigracion_' + 
                  CONVERT(VARCHAR, GETDATE(), 112) + '_' + 
                  REPLACE(CONVERT(VARCHAR, GETDATE(), 108), ':', '');
SET @BackupFile = @BackupPath + @BackupName + '.bak';

RESTORE VERIFYONLY FROM DISK = @BackupFile;

PRINT '✅ VERIFICACIÓN DE BACKUP: OK';
PRINT '';
PRINT '🎯 SIGUIENTE PASO: Ejecutar script 02-nueva-estructura-bd.sql';

GO
