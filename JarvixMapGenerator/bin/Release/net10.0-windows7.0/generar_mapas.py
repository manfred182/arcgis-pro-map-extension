import arcpy
import os
import traceback
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox

try:
    # Intentar obtener el proyecto actual
    aprx = arcpy.mp.ArcGISProject("CURRENT")
    
    # Listar layouts disponibles para depuración
    layouts = aprx.listLayouts()
    print(f"Layouts disponibles: {[l.name for l in layouts]}")
    
    # Buscar el layout específico
    layout_matches = [l for l in layouts if l.name == "Plantilla Predial"]
    if not layout_matches:
        raise ValueError("No se encontró el layout 'Plantilla Predial'. Layouts disponibles: " + str([l.name for l in layouts]))
    
    layout = layout_matches[0]
    
    # Verificar si el layout tiene serie de mapas
    if not layout.mapSeries:
        raise ValueError("El layout 'Plantilla Predial' no tiene una serie de mapas configurada.")
    
    map_series = layout.mapSeries
    print(f"Serie de mapas encontrada con {map_series.pageCount} páginas")
    
    # Obtener los campos disponibles de la capa de índice de la serie de mapas
    index_layer = map_series.indexLayer
    if index_layer is None:
        raise ValueError("No se pudo obtener la capa de índice de la serie de mapas.")
    
    # Obtener los nombres de los campos
    fields = [f.name for f in arcpy.Describe(index_layer).fields]
    print(f"Campos disponibles en la capa de índice: {fields}")
    
    # Crear ventana de configuración principal
    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana principal de tkinter
    
    # Crear una ventana personalizada para todas las configuraciones
    config_window = tk.Toplevel(root)
    config_window.title("Configurar exportación de serie de mapas")
    config_window.geometry("400x300")
    config_window.resizable(False, False)
    
    # Variable para almacenar los resultados
    result = {
        "field": None,
        "folder": None,
        "export_format": "multiple",  # "single" or "multiple"
        "page_range": "all"           # "all" or custom string like "1-3,5"
    }
    
    # Campo para nombrar archivos
    tk.Label(config_window, text="1. Seleccione el campo para nombrar los archivos:").pack(anchor="w", padx=10, pady=(10,0))
    
    field_var = tk.StringVar()
    if fields:
        field_var.set(fields[0])
        field_dropdown = tk.OptionMenu(config_window, field_var, *fields)
        field_dropdown.pack(fill="x", padx=20, pady=5)
    else:
        tk.Label(config_window, text="No hay campos disponibles", fg="red").pack(fill="x", padx=20, pady=5)
    
    # Opciones de formato de exportación
    tk.Label(config_window, text="2. Seleccione el formato de exportación:").pack(anchor="w", padx=10, pady=(10,0))
    
    format_var = tk.StringVar(value="multiple")
    format_frame = tk.Frame(config_window)
    format_frame.pack(fill="x", padx=20, pady=5)
    
    tk.Radiobutton(format_frame, text="Archivo PDF único (todas las páginas)", variable=format_var, value="single").pack(anchor="w")
    tk.Radiobutton(format_frame, text="Archivos PDF individuales (uno por página)", variable=format_var, value="multiple").pack(anchor="w")
    
    # Opciones de rango de páginas
    tk.Label(config_window, text="3. Seleccione las páginas a exportar:").pack(anchor="w", padx=10, pady=(10,0))
    
    range_var = tk.StringVar(value="all")
    range_frame = tk.Frame(config_window)
    range_frame.pack(fill="x", padx=20, pady=5)
    
    tk.Radiobutton(range_frame, text="Todas las páginas", variable=range_var, value="all").pack(anchor="w")
    tk.Radiobutton(range_frame, text="Páginas personalizadas:", variable=range_var, value="custom").pack(anchor="w")
    
    custom_range_entry = tk.Entry(range_frame, width=20)
    custom_range_entry.pack(anchor="w", padx=20, pady=2)
    custom_range_entry.insert(0, "1-3,5")  # Ejemplo predeterminado
    custom_range_entry.config(state="disabled")  # Inicialmente deshabilitado
    
    # Habilitar/deshabilitar el entry según la selección
    def toggle_custom_range():
        if range_var.get() == "custom":
            custom_range_entry.config(state="normal")
        else:
            custom_range_entry.config(state="disabled")
    
    range_var.trace("w", lambda *args: toggle_custom_range())
    toggle_custom_range()  # Inicializar estado
    
    # Botones
    button_frame = tk.Frame(config_window)
    button_frame.pack(fill="x", padx=20, pady=20)
    
    def on_ok():
        # Validar campo seleccionado
        if not fields or not field_var.get():
            messagebox.showerror("Error", "Debe seleccionar un campo para nombrar los archivos.")
            return
        
        result["field"] = field_var.get()
        result["folder"] = filedialog.askdirectory(title="Seleccione la carpeta donde guardar los PDFs")
        
        if not result["folder"]:
            messagebox.showinfo("Información", "Operación cancelada por el usuario.")
            return
        
        result["export_format"] = format_var.get()
        result["page_range"] = range_var.get()
        if result["page_range"] == "custom":
            custom_range = custom_range_entry.get().strip()
            if not custom_range:
                messagebox.showerror("Error", "Debe especificar un rango de páginas personalizado.")
                return
            result["page_range"] = custom_range
        
        config_window.destroy()
    
    def on_cancel():
        config_window.destroy()
    
    tk.Button(button_frame, text="Aceptar", command=on_ok, width=10).pack(side=tk.RIGHT, padx=5)
    tk.Button(button_frame, text="Cancelar", command=on_cancel, width=10).pack(side=tk.RIGHT, padx=5)
    
    # Esperar a que se cierre la ventana
    config_window.wait_window()
    
    # Verificar si se canceló
    if not result["field"] or not result["folder"]:
        print("Operación cancelada por el usuario.")
        exit()
    
    nombre_campo = result["field"]
    salida = result["folder"]
    export_format = result["export_format"]
    page_range = result["page_range"]
    
    print(f"Configuración seleccionada:")
    print(f"  Campo para nombrar: {nombre_campo}")
    print(f"  Carpeta de salida: {salida}")
    print(f"  Formato de exportación: {export_format}")
    print(f"  Rango de páginas: {page_range}")
    
    # Crear carpeta si no existe
    if not os.path.exists(salida):
        os.makedirs(salida)
        print(f"Carpeta de salida creada: {salida}")
    
    # Procesar el rango de páginas
    pages_to_export = []
    if page_range == "all":
        pages_to_export = list(range(1, map_series.pageCount + 1))
    else:
        # Parsear rango personalizado (ej: "1-3,5,7-10")
        try:
            parts = page_range.split(',')
            for part in parts:
                part = part.strip()
                if '-' in part:
                    start, end = map(int, part.split('-'))
                    pages_to_export.extend(range(start, end+1))
                else:
                    pages_to_export.append(int(part))
            # Eliminar duplicados y ordenar
            pages_to_export = sorted(list(set(pages_to_export)))
            # Validar que todas las páginas estén dentro del rango válido
            pages_to_export = [p for p in pages_to_export if 1 <= p <= map_series.pageCount]
            if not pages_to_export:
                raise ValueError("Ninguna de las páginas especificadas está dentro del rango válido.")
        except Exception as e:
            raise ValueError(f"Formato de rango de páginas inválido. Use formato como '1-3,5,7-10'. Error: {str(e)}")
    
    print(f"Páginas a exportar: {pages_to_export}")
    
    # Configurar opciones de exportación según el formato
    if export_format == "single":
        # Exportar a un único PDF múltiple
        pdf_filename = os.path.join(salida, "Serie_de_Mapas.pdf")
        
        # Crear opciones de exportación para serie de mapas
        map_series_export_options = arcpy.mp.CreateExportOptions('MAPSERIES')
        map_series_export_options.setExportPages('CUSTOM' if page_range != 'all' else 'ALL')
        if page_range != 'all':
            map_series_export_options.customPages = page_range
        map_series_export_options.setExportFileOptions('ExportAsSinglePDF')
        
        # Crear formato de exportación PDF
        pdf_format = arcpy.mp.CreateExportFormat('PDF', pdf_filename)
        pdf_format.Resolution = 300
        pdf_format.DoCompressVectorGraphics = True
        pdf_format.DoEmbedFonts = True
        pdf_format.HasGeoRefInfo = True
        pdf_format.ImageCompression = 'Adaptive'
        pdf_format.ImageQuality = 'Best'
        pdf_format.LayersAndAttributes = 'LayersAndAttributes'
        
        # Validar ruta de salida
        if not pdf_format.ValidateOutputFilePath():
            raise ValueError(f"Ruta de salida no válida: {pdf_filename}")
        
        # Exportar la serie de mapas
        print(f"Exportando {len(pages_to_export)} páginas a un único PDF: {pdf_filename}")
        layout.Export(pdf_format, map_series_export_options)
        print(f"Exportación completada: {pdf_filename}")
        
    else:
        # Exportar a archivos PDF individuales
        print(f"Exportando {len(pages_to_export)} páginas a archivos PDF individuales...")
        
        for pagina in pages_to_export:
            try:
                map_series.currentPageNumber = pagina
                # Verificar que el campo seleccionado exista en la fila actual
                if hasattr(map_series.pageRow, nombre_campo):
                    valor_campo = getattr(map_series.pageRow, nombre_campo)
                    # Manejar valores None o vacíos
                    if valor_campo is None or str(valor_campo).strip() == "":
                        nombre = f"Pagina_{pagina}"
                        print(f"Advertencia: Campo '{nombre_campo}' vacío para página {pagina}, usando '{nombre}'")
                    else:
                        nombre = str(valor_campo)
                else:
                    # Si el campo no existe, usar el número de página como fallback
                    nombre = f"Pagina_{pagina}"
                    print(f"Advertencia: Campo '{nombre_campo}' no encontrado en la capa, usando '{nombre}' para página {pagina}")
                
                # Limpiar nombre de archivo (eliminar caracteres no válidos)
                nombre = "".join(c for c in nombre if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
                if not nombre:
                    nombre = f"Pagina_{pagina}"
                    
                pdf = os.path.join(salida, f"{nombre}.pdf")
                
                # Exportar a PDF
                layout.exportToPDF(pdf)
                print(f"Exportado: {nombre} -> {pdf}")
                
            except Exception as e:
                print(f"Error al exportar página {pagina}: {str(e)}")
                traceback.print_exc()
        
        print(f"Proceso de exportación completado. Archivos guardados en: {salida}")

except Exception as e:
    print(f"Error crítico: {str(e)}")
    traceback.print_exc()
