import arcpy
import os

aprx = arcpy.mp.ArcGISProject("CURRENT")
layout = aprx.listLayouts("Plantilla Predial")[0]
map_series = layout.mapSeries

salida = r"C:\Exportados"
if not os.path.exists(salida):
    os.makedirs(salida)

for pagina in range(1, map_series.pageCount + 1):
    map_series.currentPageNumber = pagina
    nombre = map_series.pageRow.PREDIO
    pdf = os.path.join(salida, f"{nombre}.pdf")
    layout.exportToPDF(pdf)
    print(f"Exportado: {nombre}")
