import tkinter as tk
from tkinter import messagebox, filedialog 
from PIL import Image, ImageDraw, ImageTk
import re 


# --- 1. CONFIGURACIÓN DE LA GRILLA Y COLORES ---

GRID_SIZE = 32    
CANVAS_SIZE = 512 
PIXEL_SIZE = CANVAS_SIZE // GRID_SIZE 

COLOR_ACTUAL = "black"  
COLOR_SYMBOL = "N"      

COLORES_MAP = {
    "NEGRO": {"code": "black", "symbol": "N"},
    "BLANCO": {"code": "white", "symbol": "B"},
    "AZUL": {"code": "blue", "symbol": "A"},
    "ROJO": {"code": "red", "symbol": "R"},
    "VERDE": {"code": "green", "symbol": "V"},
    "AMARILLO": {"code": "yellow", "symbol": "Y"},
    "TRANSPARENTE": {"code": "white", "symbol": "T"} 
}

SYMBOL_TO_CODE = {v['symbol']: v['code'] for v in COLORES_MAP.values()}


matriz_colores = [['T' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

# --- 2. FUNCIONES DE DIBUJO Y LÓGICA ---

def seleccionar_color(nombre_color):
    """Cambia el color actual de dibujo y su símbolo RLE."""
    global COLOR_ACTUAL, COLOR_SYMBOL
    COLOR_ACTUAL = COLORES_MAP[nombre_color]["code"]
    COLOR_SYMBOL = COLORES_MAP[nombre_color]["symbol"]
    root.title(f"Mini-Paint: Dibujando con {nombre_color} ({COLOR_SYMBOL})")

def pintar_pixel(event):
    """Calcula la celda de la grilla y la pinta."""
    global COLOR_ACTUAL, COLOR_SYMBOL
    
    x_grid = event.x // PIXEL_SIZE
    y_grid = event.y // PIXEL_SIZE
    
    if 0 <= x_grid < GRID_SIZE and 0 <= y_grid < GRID_SIZE:
        
        x1 = x_grid * PIXEL_SIZE
        y1 = y_grid * PIXEL_SIZE
        x2 = x1 + PIXEL_SIZE
        y2 = y1 + PIXEL_SIZE
        
        canvas.create_rectangle(x1, y1, x2, y2, fill=COLOR_ACTUAL, outline="lightgray", width=1)
        
        matriz_colores[y_grid][x_grid] = COLOR_SYMBOL

def borrar_lienzo():
    """Limpia el Canvas y resetea la matriz_colores a 'T'."""
    canvas.delete("all")
    dibujar_grilla() 
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            matriz_colores[y][x] = 'T'
    messagebox.showinfo("Lienzo Borrado", "El lienzo ha sido limpiado y la matriz de datos ha sido reseteada.")

def dibujar_grilla():
    """Dibuja las líneas de la grilla de 32x32."""
    for i in range(GRID_SIZE + 1):
        x = i * PIXEL_SIZE
        canvas.create_line(x, 0, x, CANVAS_SIZE, fill="lightgray")
        
        y = i * PIXEL_SIZE
        canvas.create_line(0, y, CANVAS_SIZE, y, fill="lightgray")


# --- FUNCIONES DE COMPRESIÓN / DESCOMPRESIÓN ---

def comprimir_rle(datos_entrada):
    """Comprime una cadena de símbolos usando Run-Length Encoding (RLE)."""
    if not datos_entrada:
        return ""

    color_comprimido = ""
    prev = datos_entrada[0]
    num = 1 
    
    for i in datos_entrada[1:]:
        if i == prev:
            num += 1
        else:
            color_comprimido += str(num) + prev
            prev = i
            num = 1

    color_comprimido += str(num) + prev
    return color_comprimido

def descomprimir_rle(datos_rle):
    """
    Descomprime una cadena RLE (ej: "5T6N") a la matriz RAW de 1024 símbolos.
    """
    datos_descomprimidos = ""
    grupos = re.findall(r'(\d+)([A-Z])', datos_rle)
    
    for count_str, symbol in grupos:
        count = int(count_str)
        datos_descomprimidos += symbol * count
        
    return datos_descomprimidos


# --- FUNCIONES DE MANEJO DE ARCHIVOS ---

def repintar_canvas():
    """Limpia el canvas y lo redibuja completamente basándose en la matriz_colores."""
    canvas.delete("all")
    dibujar_grilla()
    
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            symbol = matriz_colores[y][x]
            color_code = SYMBOL_TO_CODE.get(symbol, 'white') 
            
            if symbol != 'T':
                x1 = x * PIXEL_SIZE
                y1 = y * PIXEL_SIZE
                x2 = x1 + PIXEL_SIZE
                y2 = y1 + PIXEL_SIZE
                canvas.create_rectangle(x1, y1, x2, y2, fill=color_code, outline="lightgray", width=1)


def cargar_archivo():
    """Abre un diálogo, carga el archivo RLE y actualiza la matriz y el canvas."""
    
    nombre_archivo = filedialog.askopenfilename(
        defaultextension=".dreerz",
        filetypes=[
            ("Archivos Dreerz (.dreerz)", "*.dreerz"), 
            ("Archivos RLE Comprimidos (.rle)", "*.rle"), 
            ("Archivos de Texto", "*.txt")
        ]
    )
    
    if not nombre_archivo:
        return 
    
    try:
        with open(nombre_archivo, "r") as f:
            datos_rle = f.read().strip() 
            
        datos_raw = descomprimir_rle(datos_rle)
        
        if len(datos_raw) != GRID_SIZE * GRID_SIZE:
            messagebox.showerror(
                "Error de Carga", 
                f"El archivo es inválido. Se esperaban {GRID_SIZE * GRID_SIZE} píxeles (símbolos), pero se encontraron {len(datos_raw)}."
            )
            return

        k = 0
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                matriz_colores[y][x] = datos_raw[k]
                k += 1
                
        repintar_canvas()
        
        messagebox.showinfo("Carga Exitosa", f"Arte cargado exitosamente desde '{nombre_archivo}'.")
        
    except FileNotFoundError:
        messagebox.showerror("Error", "El archivo no se encontró.")
    except Exception as e:
        messagebox.showerror("Error de Carga", f"Ocurrió un error al cargar o procesar el archivo: {e}")


def exportar_matriz():
    """
    Convierte la matriz 32x32 en una cadena RAW, la COMPRIME usando RLE,
    y guarda la cadena resultante en un archivo de texto (.dreerz).
    """
    
    rle_data_raw = "".join("".join(fila) for fila in matriz_colores)

    datos_comprimidos = comprimir_rle(rle_data_raw)
    
    nombre_archivo_rle = filedialog.asksaveasfilename(
        defaultextension=".dreerz",
        filetypes=[("Archivos Dreerz", "*.dreerz"), ("Archivos de Texto", "*.txt")],
        initialfile="mi_pixel_art.dreerz"
    )

    if not nombre_archivo_rle:
        return 

    try:
        with open(nombre_archivo_rle, "w") as f:
            f.write(datos_comprimidos)
            
        messagebox.showinfo(
            "Guardado RLE Exitoso", 
            f"Cadena RLE (formato .dreerz) guardada en:\n{nombre_archivo_rle}\n\n"
            f"Longitud de la cadena comprimida: {len(datos_comprimidos)}"
        )

        print(f"\n--- CADENA RLE COMPRIMIDA GUARDADA EN {nombre_archivo_rle} ---")
        print(datos_comprimidos)
        print("----------------------------------------------------------------\n")
        
    except Exception as e:
        messagebox.showerror("Error al Guardar RLE", f"Ocurrió un error al guardar el archivo: {e}")

    return datos_comprimidos


def exportar_png():
    """
    Exporta el contenido del canvas (el arte) a un archivo PNG usando Pillow.
    """
    try:
        nombre_archivo = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("Archivos PNG", "*.png")],
            initialfile="mi_pixel_art.png"
        )
        
        if not nombre_archivo:
            return 

        img = Image.new('RGB', (GRID_SIZE, GRID_SIZE), color='white')
        draw = ImageDraw.Draw(img) 

        color_map_hex = {
            data["symbol"]: data["code"] for data in COLORES_MAP.values()
        }

        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                symbol = matriz_colores[y][x]
                color_code = color_map_hex.get(symbol, 'white')
                draw.point((x, y), fill=color_code)

        img_escalada = img.resize((256, 256), resample=Image.NEAREST)
        
        img_escalada.save(nombre_archivo)
        
        messagebox.showinfo(
            "Exportación PNG Exitosa",
            f"¡Tu pixel art ha sido guardado como '{nombre_archivo}'!\n"
            f"Se exportó la matriz de 32x32 y se escaló a 256x256 para mayor visibilidad."
        )

    except NameError:
        messagebox.showerror(
            "Error de Librería",
            "La librería 'Pillow' no está instalada.\n"
            "Por favor, instálala ejecutando este comando en tu terminal:\n"
            "pip install Pillow"
        )
    except Exception as e:
        messagebox.showerror("Error al Guardar", f"Ocurrió un error al guardar el archivo: {e}")


# --- 3. CREACIÓN DE LA INTERFAZ ---

root = tk.Tk()
seleccionar_color("NEGRO") 

control_frame = tk.Frame(root)
control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

for nombre, data in COLORES_MAP.items():
    if nombre == "TRANSPARENTE":
        btn = tk.Button(
            control_frame, 
            text=f"BORRADOR ({data['symbol']})", 
            command=lambda n=nombre: seleccionar_color(n)
        )
    else:
        btn = tk.Button(
            control_frame, 
            text=f"{nombre} ({data['symbol']})", 
            bg=data["code"], 
            fg="white" if data["code"] == "black" else "black",
            command=lambda n=nombre: seleccionar_color(n)
        )
    btn.pack(side=tk.LEFT, padx=3, pady=5)

btn_borrar_todo = tk.Button(
    control_frame,
    text="BORRAR TODO",
    command=borrar_lienzo,
    bg="#f0f0f0"
)
btn_borrar_todo.pack(side=tk.LEFT, padx=10)

btn_cargar_rle = tk.Button(
    control_frame,
    text="CARGAR ARTE (DREERZ)", 
    command=cargar_archivo,
    bg="#1E90FF", 
    fg="white"
)
btn_cargar_rle.pack(side=tk.LEFT, padx=5)


btn_exportar_rle = tk.Button(
    control_frame,
    text="GUARDAR DREERZ",
    command=exportar_matriz,
    bg="#4CAF50",
    fg="white"
)
btn_exportar_rle.pack(side=tk.RIGHT, padx=5)

btn_exportar_png = tk.Button(
    control_frame,
    text="GUARDAR COMO PNG",
    command=exportar_png,
    bg="#FFC107",
    fg="black"
)
btn_exportar_png.pack(side=tk.RIGHT, padx=5)


canvas = tk.Canvas(
    root, 
    width=CANVAS_SIZE, 
    height=CANVAS_SIZE, 
    bg=COLORES_MAP["BLANCO"]["code"] 
)
canvas.pack(padx=10, pady=10)

dibujar_grilla()
canvas.bind("<Button-1>", pintar_pixel)

canvas.bind("<B1-Motion>", pintar_pixel)

root.mainloop()
