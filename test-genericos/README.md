# 🧪 Tests Genéricos - AI Print Studio

Esta carpeta contiene scripts sueltos para realizar verificaciones E2E (End-to-End) o pruebas de carga/funcionales sobre los diferentes componentes del proyecto, pero sin agregar dependencias rígidas ni ensuciar el código del sistema.

### ¿Cómo ejecutar los tests de Cupones?

El script de testing de cupones comprueba el ciclo de vida completo de la API del agente, incluyendo la creación de un cupón mediante CRUD y culminando con el envío del contexto a Ollama y la creación de una propuesta inteligente.

**Asegúrate de tener funcionando primero el backend de cupones.** (Ejecutando `RUN.bat` o entrando a `agentes-Ollama/agente-cupones` e inicializando la app).

Para ejecutar la prueba:

```bash
cd test-genericos
python test_cupones.py
```
