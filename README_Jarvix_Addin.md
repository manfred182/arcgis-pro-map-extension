# JarvixMapGenerator - Base de Add-In ArcGIS Pro

Esta carpeta contiene los archivos base para tu boton de automatizacion:

- `GenerarMapasButton.cs`
- `Module1.cs`
- `Config.daml`
- `generar_mapas.py`

## Como usarlo en Visual Studio

1. Crea un proyecto tipo `ArcGIS Pro Module Add-in` llamado `JarvixMapGenerator`.
2. Reemplaza en ese proyecto los archivos:
   - `Config.daml`
   - `Module1.cs`
3. Agrega un nuevo archivo de clase y pega el contenido de `GenerarMapasButton.cs`.
4. Guarda `generar_mapas.py` en una ruta fija (por ejemplo `C:\Jarvix\Python\generar_mapas.py`) o ajusta la ruta en `GenerarMapasButton.cs`.
5. Compila con `Build > Build Solution`.
6. Instala el `.esriAddInX` generado.

## Notas importantes

- Verifica que el layout exista con nombre exacto `Plantilla Predial`.
- Verifica que el campo `PREDIO` exista en el indice del `Map Series`.
- Si cambias rutas de Python o script, actualizalas en el boton.
