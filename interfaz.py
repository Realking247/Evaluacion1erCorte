"""Interfaz web interactiva del explorador de archivos de Google Drive.

Nueva asignación: explorador de archivos con buscador en tiempo real y
algoritmos de ordenamiento QuickSort (nombres) y BubbleSort (tamaño).
Está pensado para ejecutarse en Google Colab: monta Drive, crea archivos
de prueba si no existen, procesa el directorio y renderiza la interfaz
como HTML mediante IPython.display.
"""

from google.colab import drive
import os
import json
from datetime import datetime
from IPython.display import HTML, display

# 1. Montar Google Drive
drive.mount('/content/drive', force_remount=False)

# 2. Constante de ruta configurada
DIRECTORIO = '/content/drive/My Drive/LPII_2026'

# Crear carpeta y archivos de prueba automáticamente si no existen
os.makedirs(DIRECTORIO, exist_ok=True)

ruta_inv = os.path.join(DIRECTORIO, 'inventario.json')
if not os.path.exists(ruta_inv):
    with open(ruta_inv, 'w', encoding='utf-8') as f:
        json.dump([
            {"codigo": "P001", "articulo": "Monitor 24 pulgadas", "stock": 12},
            {"codigo": "P002", "articulo": "Silla Gamer", "stock": 5},
            {"codigo": "P003", "articulo": "Audífonos Inalámbricos", "stock": 20}
        ], f, indent=4)

ruta_csv = os.path.join(DIRECTORIO, 'ventas.csv')
if not os.path.exists(ruta_csv):
    with open(ruta_csv, 'w', encoding='utf-8') as f:
        f.write("id,producto,precio\n1,Laptop,1200.50\n2,Mouse,25.00\n3,Teclado,45.00")

ruta_json = os.path.join(DIRECTORIO, 'config.json')
if not os.path.exists(ruta_json):
    with open(ruta_json, 'w', encoding='utf-8') as f:
        json.dump({"version": "1.0", "autor": "Estudiante", "ambiente": "produccion"}, f, indent=4)

# 3. Función modular estructurada
def procesar_directorio_datos(directorio):
    resultado_api = {
        "estado": "exitoso",
        "directorio": directorio,
        "timestamp_consulta": datetime.now().isoformat(),
        "inventario": [],
        "archivos_procesados": []
    }

    try:
        if not os.path.exists(directorio):
            raise FileNotFoundError(f"El directorio '{directorio}' no existe.")

        elementos = os.listdir(directorio)

        ruta_inventario = os.path.join(directorio, 'inventario.json')
        if os.path.exists(ruta_inventario):
            try:
                with open(ruta_inventario, 'r', encoding='utf-8') as f:
                    datos_inventario = json.load(f)
                    if isinstance(datos_inventario, list):
                        resultado_api["inventario"] = datos_inventario
            except json.JSONDecodeError:
                pass

        for nombre_archivo in elementos:
            if nombre_archivo.lower().endswith(('.json', '.csv')):
                ruta_completa = os.path.join(directorio, nombre_archivo)
                if os.path.isfile(ruta_completa):
                    tamanio_bytes = os.path.getsize(ruta_completa)
                    tamanio_kb = round(tamanio_bytes / 1024, 2)
                    timestamp_mod = os.path.getmtime(ruta_completa)
                    fecha_modificacion = datetime.fromtimestamp(timestamp_mod).strftime('%Y-%m-%d %H:%M:%S')

                    info_archivo = {
                        "nombre": nombre_archivo,
                        "tamanio_kb": tamanio_kb,
                        "ultima_modificacion": fecha_modificacion
                    }
                    resultado_api["archivos_procesados"].append(info_archivo)

    except Exception as e:
        resultado_api["estado"] = "error"
        resultado_api["mensaje"] = str(e)

    return resultado_api

# 4. Procesar los datos y formatear JSON para JavaScript
datos_salida_api = procesar_directorio_datos(DIRECTORIO)
archivos_json = json.dumps(datos_salida_api.get("archivos_procesados", []))

# 5. Generar e Inyectar la Interfaz Web con los escapes de f-string corregidos
html_interfaz = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; background-color: #f4f4f9; padding: 20px; }}
        .contenedor {{ max-width: 700px; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); margin: auto; }}
        h2 {{ color: #333; margin-top: 0; }}
        .controles {{ display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }}
        input, select {{ padding: 10px; border: 1px solid #ccc; border-radius: 5px; flex: 1; min-width: 150px; }}
        .algoritmo-info {{ background-color: #e3f2fd; color: #1565c0; padding: 10px; border-radius: 5px; font-weight: bold; font-size: 14px; margin-bottom: 20px; display: none; }}
        .tarjeta {{ border-left: 5px solid #4CAF50; background: #f9f9f9; margin-bottom: 10px; padding: 15px; border-radius: 4px; display: flex; justify-content: space-between; align-items: center; }}
        .tarjeta h4 {{ margin: 0 0 5px 0; color: #222; }}
        .tarjeta p {{ margin: 0; color: #666; font-size: 13px; }}
        .badge {{ background: #eee; padding: 3px 8px; border-radius: 12px; font-size: 12px; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="contenedor">
        <h2>🔍 Explorador de Archivos y Algoritmos de Ordenamiento</h2>

        <div class="controles">
            <input type="text" id="buscador" placeholder="Filtrar por nombre o extensión..." oninput="aplicarFiltros()">
            <select id="ordenador" onchange="aplicarFiltros()">
                <option value="original">Orden de lectura (Por defecto)</option>
                <option value="nombre_asc">Nombre (A-Z) - QuickSort</option>
                <option value="tamanio_desc">Tamaño (Mayor a Menor) - BubbleSort</option>
            </select>
        </div>

        <div id="infoAlgoritmo" class="algoritmo-info"></div>
        <div id="listaResultados"></div>
    </div>

    <script>
        const datosOriginales = {archivos_json};

        // Algoritmo 1: QuickSort (Cadenas)
        function quickSort(arr, key) {{
            if (arr.length <= 1) return arr;
            let pivot = arr[Math.floor(arr.length / 2)];
            let left = [], right = [], equal = [];
            for (let obj of arr) {{
                let val = obj[key].toLowerCase();
                let pivotVal = pivot[key].toLowerCase();
                if (val < pivotVal) left.push(obj);
                else if (val > pivotVal) right.push(obj);
                else equal.push(obj);
            }}
            return quickSort(left, key).concat(equal, quickSort(right, key));
        }}

        // Algoritmo 2: BubbleSort (Números)
        function bubbleSort(arr, key) {{
            let arrayCopy = [...arr];
            let n = arrayCopy.length;
            for (let i = 0; i < n - 1; i++) {{
                for (let j = 0; j < n - i - 1; j++) {{
                    if (arrayCopy[j][key] < arrayCopy[j + 1][key]) {{
                        let temp = arrayCopy[j];
                        arrayCopy[j] = arrayCopy[j + 1];
                        arrayCopy[j + 1] = temp;
                    }}
                }}
            }}
            return arrayCopy;
        }}

        function aplicarFiltros() {{
            const textoBuscado = document.getElementById("buscador").value.toLowerCase();
            const criterioOrden = document.getElementById("ordenador").value;
            const infoDiv = document.getElementById("infoAlgoritmo");

            let datosFiltrados = datosOriginales.filter(archivo =>
                archivo.nombre.toLowerCase().includes(textoBuscado)
            );

            if (criterioOrden === "nombre_asc") {{
                let inicio = performance.now();
                datosFiltrados = quickSort(datosFiltrados, "nombre");
                let fin = performance.now();
                infoDiv.style.display = "block";
                infoDiv.innerHTML = `⚙️ Algoritmo ejecutado: <b>QuickSort</b> (Tiempo de cómputo: ${{(fin - inicio).toFixed(3)}} ms)`;
            }}
            else if (criterioOrden === "tamanio_desc") {{
                let inicio = performance.now();
                datosFiltrados = bubbleSort(datosFiltrados, "tamanio_kb");
                let fin = performance.now();
                infoDiv.style.display = "block";
                infoDiv.innerHTML = `⚙️ Algoritmo ejecutado: <b>Bubble Sort</b> (Tiempo de cómputo: ${{(fin - inicio).toFixed(3)}} ms)`;
            }}
            else {{
                infoDiv.style.display = "none";
            }}

            renderizarLista(datosFiltrados);
        }}

        function renderizarLista(archivos) {{
            const contenedor = document.getElementById("listaResultados");
            contenedor.innerHTML = "";

            if (archivos.length === 0) {{
                contenedor.innerHTML = "<p style='text-align:center; color:#999;'>No se encontraron archivos que coincidan con la búsqueda.</p>";
                return;
            }}

            archivos.forEach(archivo => {{
                let tipo = archivo.nombre.split('.').pop().toUpperCase();

                const tarjeta = document.createElement("div");
                tarjeta.className = "tarjeta";
                tarjeta.innerHTML = `
                    <div>
                        <h4>${{archivo.nombre}}</h4>
                        <p>Modificado: ${{archivo.ultima_modificacion}}</p>
                    </div>
                    <div style="text-align: right;">
                        <span class="badge">${{tipo}}</span>
                        <p style="margin-top: 5px; font-weight: bold;">${{archivo.tamanio_kb}} KB</p>
                    </div>
                `;
                contenedor.appendChild(tarjeta);
            }});
        }}

        renderizarLista(datosOriginales);
    </script>
</body>
</html>
"""

display(HTML(html_interfaz))
