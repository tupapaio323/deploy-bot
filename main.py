import random
import string
from myapp import app
from flask import Flask
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from telegram import Update
from PIL import Image, ImageDraw, ImageFont
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler
import io
import os

IMAGENES = {
    "nequi": [
        "C:/Users/jlcal/OneDrive/Escritorio/COMPROBANTES/comprobantes_nequi/comprobante1.png",
        "C:/Users/jlcal/OneDrive/Escritorio/COMPROBANTES/comprobantes_nequi/comprobante2.png",
        "C:/Users/jlcal/OneDrive/Escritorio/COMPROBANTES/comprobantes_nequi/comprobante_qr.png",
        "C:/Users/jlcal/OneDrive/Escritorio/COMPROBANTES/comprobantes_nequi/comprobante_compartir.png",
        "C:/Users/jlcal/OneDrive/Escritorio/COMPROBANTES/comprobantes_nequi/comprobante_transfiya.png",  # Comprobante Transferencia
        "C:/Users/jlcal/OneDrive/Escritorio/COMPROBANTES/comprobantes_nequi/comprobante_compartirqr.png",  # Comprobante Compartir QR
        "C:/Users/jlcal/OneDrive/Escritorio/COMPROBANTES/comprobantes_nequi/comprobante_negocioqr.png",  # Comprobante Negocio 
        "C:/Users/jlcal/OneDrive/Escritorio/COMPROBANTES/comprobantes_nequi/comprobante_enviobanco.png"  # Comprobante Negocio QR
    ],
    "bancolombia": [
        "C:/Users/jlcal/OneDrive/Escritorio/COMPROBANTES/comprobantes_bancolombia/comprobantebancolombia1.png",
        "C:/Users/jlcal/OneDrive/Escritorio/COMPROBANTES/comprobantes_bancolombia/comprobantebancolombia2.png",
        "C:/Users/jlcal/OneDrive/Escritorio/COMPROBANTES/comprobantes_bancolombia/comprobante_qr.png",
        "C:/Users/jlcal/OneDrive/Escritorio/COMPROBANTES/comprobantes_bancolombia/comprobante_compartir.png",
        "C:/Users/jlcal/OneDrive/Escritorio/COMPROBANTES/comprobantes_bancolombia/comprobante_transferencia.png",  # Comprobante Transferencia
        "C:/Users/jlcal/OneDrive/Escritorio/COMPROBANTES/comprobantes_bancolombia/comprobante_compartir_qr.png",  # Comprobante Compartir QR
        "C:/Users/jlcal/OneDrive/Escritorio/COMPROBANTES/comprobantes_bancolombia/comprobante_negocio_qr.png"  # Comprobante Negocio QR
    ]
}

FONT_PATHS = {
    "comprobante": "C:/Users/jlcal/OneDrive/Escritorio/Manrope/static/Manrope-Regular.ttf",
    "referencia": "C:/Users/jlcal/OneDrive/Escritorio/Manrope/static/Manrope-Medium.ttf",
    "regular": "C:/Users/jlcal/OneDrive/Escritorio/Manrope/static/Manrope-Regular.ttf"
}

# Estados de la conversación
SELECCION_COMPROBANTE, NOMBRE_CORTO, NOMBRE_LARGO, CUANTO, NOMBRE_CORTO2, NUMERO_BANCO, REFERENCIA = range(7)

def generar_referencia() -> str:
    """Genera una referencia aleatoria para el comprobante."""
    return 'M' + ''.join(random.choices(string.digits, k=7))

# Función para capitalizar nombres correctamente
def capitalizar_nombre(nombre: str) -> str:
    """Convierte el nombre en formato 'Nombre Apellido' con la primera letra de cada palabra en mayúsculas.""" 
    return ' '.join([palabra.capitalize() for palabra in nombre.split()])

# Función de inicio
async def start(update: Update, context: CallbackContext) -> int:
    """Inicia la conversación y solicita la selección del banco."""
    await update.message.reply_text(
        "👑 !Bienvenido! A  🏴‍☠️NEQUI FULL EDITION🏴‍☠️! \n\n"
        "Selecciona el banco para generar el comprobante: 🏦\n\n"
        " 🟣  /nequi para generar todos los comprobantes de Nequi.\n\n"
        " 🟡  /bancolombia MATENIMIENTO...\n\n"
        " ⛔  /daviplata   PROXIMAMENTE..."
    )
    return SELECCION_COMPROBANTE

# Comando para seleccionar Nequi
async def seleccionar_nequi(update: Update, context: CallbackContext) -> int:
    """Selecciona Nequi y solicita el nombre corto."""
    context.user_data["banco"] = "nequi"
    await update.message.reply_text(
        "🟣 Has seleccionado Nequi.\n\n" 
        "👤 ¿Para? \n\n"
        "(PRIMER NOMBRE, PRIMER APELLIDO):"
    )
    return NOMBRE_CORTO

# Comando para seleccionar Bancolombia
async def seleccionar_bancolombia(update: Update, context: CallbackContext) -> int:
    """Selecciona Bancolombia y solicita el nombre corto."""
    context.user_data["banco"] = "bancolombia"
    await update.message.reply_text(
        "🟡 Has seleccionado Bancolombia.\n\n"
        "👤 Ahora, ingresa el numero de cuenta...\n\n"
        "(SIN PUNTOS NI COMAS):"
    )
    return NOMBRE_CORTO2

# Manejar la selección del banco
async def manejar_seleccion_comprobante(update: Update, context: CallbackContext) -> int:
    """Maneja la selección del banco para el comprobante."""
    await update.message.reply_text(
        "❌ Por favor, selecciona un banco válido:\n\n"
        "/nequi\n\n"
           "O\n\n"
        "/bancolombia"
    )
    return SELECCION_COMPROBANTE


# Función para formatear monto
def formatear_monto(monto: str) -> str:
    try:
        monto_num = int(monto)
        return f"{monto_num:,}".replace(",", ".")
    except ValueError:
        return monto

# Función para formatear número de Nequi
def formatear_numero_nequi(numero: str) -> str:
    if len(numero) == 10 and numero.isdigit():
        return f"{numero[:3]} {numero[3:6]} {numero[6:]}"
    return numero

async def recibir_nombre_corto(update: Update, context: CallbackContext) -> int:
    """Recibe el nombre corto (primer nombre y primer apellido)."""
    nombre_corto = update.message.text.strip()
    nombre_corto2 = update.message.text.strip()
    context.user_data["nombre_corto"] = capitalizar_nombre(nombre_corto)  # Capitalizamos el nombre
    context.user_data["nombre_corto2"] = capitalizar_nombre(nombre_corto2)
    

    # Fecha y hora actual
    fecha_actual = datetime.now()
    hora_actual = fecha_actual.strftime("%I:%M ").lower()
    fecha_formateada = f"{fecha_actual.day} de diciembre de {fecha_actual.year}, {hora_actual} p. m."
    context.user_data["fecha"] = fecha_formateada

    await update.message.reply_text("Ahora, 👤 ingresa el Nombre COMPLETO:")
    return NOMBRE_LARGO


# Recibir el nombre largo
async def recibir_nombre_largo(update: Update, context: CallbackContext) -> int:
    """Recibe el nombre completo."""
    nombre_largo = update.message.text.strip()
    nombre_largo2 = update.message.text.strip()
    context.user_data["nombre_largo"] = capitalizar_nombre(nombre_largo)  # Capitalizamos el nombre
    context.user_data["nombre_largo2"] = capitalizar_nombre(nombre_largo2)
    
    await update.message.reply_text("📱 Ingresa el número de cuenta\n\n"
                                    "Comprobante de envio Banco\n\n"
                                    "(11 dígitos):")
    return NOMBRE_CORTO2


async def recibir_numero_cuenta(update: Update, context: CallbackContext) -> int:
    """Recibe el numero de cuenta."""
    numero_cuenta = update.message.text.strip()
    
    if numero_cuenta.isdigit():
        context.user_data["numero_cuenta"] = numero_cuenta
        await update.message.reply_text("💵 ¿Cantidad de Pago?  (Sin puntos ni comas):")
        return CUANTO
    else:
        await update.message.reply_text("❌ Por favor, ingresa un numero válido (solo números).")
        return NOMBRE_CORTO2

# Recibir el monto
async def recibir_monto(update: Update, context: CallbackContext) -> int:
    """Recibe el monto del pago."""
    monto = update.message.text.strip()

    if monto.isdigit():
        monto_formateado = formatear_monto(monto)
        context.user_data["monto"] = monto_formateado
        await update.message.reply_text("📱 Ingresa el número de Nequi  (10 dígitos):")
        return NUMERO_BANCO
    else:
        await update.message.reply_text("❌ Por favor, ingresa un monto válido (solo números).")
        return CUANTO

# Recibir el número de banco
async def recibir_numero_banco(update: Update, context: CallbackContext) -> int:
    """Recibe el número de cuenta de Nequi o Bancolombia."""
    numero_banco = update.message.text.strip()

    if len(numero_banco) == 10 and numero_banco.isdigit():
        numero_banco_formateado = formatear_numero_nequi(numero_banco)
        context.user_data["numero_banco"] = numero_banco_formateado
        referencia = generar_referencia()
        context.user_data["referencia"] = referencia

        await update.message.reply_text(f"👑 Generando comprobantes con referencia: 🆔 {referencia}")
        
        banco = context.user_data["banco"]
        comprobantes = [generar_comprobante(context.user_data, banco, i) for i in range(8)]  # Ahora generamos 7 comprobantes

        # Enviar los comprobantes generados
        for i, comprobante in enumerate(comprobantes):
            if comprobante:
                with io.BytesIO() as output:
                    comprobante.save(output, format="PNG")
                    output.seek(0)
                    await update.message.reply_document(output, filename=f"comprobante_{i + 1}.png")

        await update.message.reply_text("¿Quieres generar otro comprobante? Responde /si para sí o /no para no.")
        return SELECCION_COMPROBANTE
    else:
        await update.message.reply_text("❌ El número de banco debe ser válido (10 dígitos).")
        return NUMERO_BANCO


posiciones_por_plantilla = {
    0: {  # Plantilla 1
        "nombre_corto": (90, 525),
        "nombre_largo": (122, -680),
        "monto": (122, -680),
        "numero_cuenta": (122, 680),
        "numero_banco": (87, 839),
        "referencia": (87, 1153),
        "fecha": (89, 998)
    },
    1: {  # Plantilla 2
        "nombre_corto": (210, -255),
        "nombre_largo2": (90, 466),
        "monto": (122, -1111),
        "numero_cuenta": (122, 1111),
        "numero_banco": (87, 793),
        "referencia": (89, 628),
        "fecha": (90, 956)
    },
    2: {  # Comprobante QR
        "nombre_corto": (250, -220),
        "nombre_largo": (50, 591),
        "monto": (70, -678),
        "numero_cuenta": (70, 678),
        "numero_banco": (50, 769),
        "referencia": (50, 947),
        "fecha": (51, 858)
    },
    3: {  # Comprobante Compartir
        "nombre_corto": (200, -230),
        "nombre_largo": (69, 285),
        "monto": (87, -457),
        "numero_cuenta": (87, 457),
        "numero_banco": (68, 370.5),
        "referencia": (223, 201),
        "fecha": (69, 542)
    },
    4: {  # Comprobante Transferencia
        "nombre_corto": (150, -200),
        "nombre_largo": (150, -240),
        "monto": (130, -717.4),
        "numero_cuenta": (130, 717.4),
        "numero_banco": (93, 539.5),
        "referencia": (94, 1041),
        "fecha": (92, 875)
    },
    5: {  # Comprobante Compartir QR
        "nombre_corto": (73, -629),
        "nombre_largo": (73, 629),
        "numero_cuenta": (93, 708.5),
        "monto": (93, -708.5),
        "numero_banco": (76, 778),
        "referencia": (221, 234),
        "fecha": (74, 851)
    },
    6: {  # Comprobante Negocio QR
        "nombre_corto": (250, -250),
        "nombre_largo": (53, 588),
        "numero_cuenta": (74, 687.4),
        "monto": (74, -687.4),
        "numero_banco": (50, -769),
        "referencia": (54, 877),
        "fecha": (53, 777)
    },
    7: {  # Comprobante Negocio QR
        "nombre_corto2": (53, 588),
        "nombre_largo": (53, -588), 
        "numero_cuenta": (74, 979),
        "monto": (53, 886),
        "numero_banco": (50, -769),
        "referencia": (54, -877),
        "fecha": (53, -777)
    }
}

FONT_PATHS = {
    "comprobante": "C:/Users/jlcal/OneDrive/Escritorio/Manrope/static/Manrope-Regular.ttf", "referencia": "C:/Users/jlcal/OneDrive/Escritorio/Manrope/static/Manrope-Regular.ttf", "regular": "C:/Users/jlcal/OneDrive/Escritorio/Manrope/static/Manrope-Regular.ttf",
    "nombre_corto" : "C:/Users/jlcal/OneDrive/Escritorio/Manrope/static/Manrope-Regular.ttf",
    "nombre_corto2" : "C:/Users/jlcal/OneDrive/Escritorio/Manrope/static/Manrope-Regular.ttf",
    "nombre_largo" : "C:/Users/jlcal/OneDrive/Escritorio/Manrope/static/Manrope-Regular.ttf",
    "nombre_largo2" : "C:/Users/jlcal/OneDrive/Escritorio/Manrope/static/Manrope-Regular.ttf",
    "monto" : "C:/Users/jlcal/OneDrive/Escritorio/Manrope/static/Manrope-Regular.ttf",
    "numero_banco" : "C:/Users/jlcal/OneDrive/Escritorio/Manrope/static/Manrope-Regular.ttf",
    "fecha" : "C:/Users/jlcal/OneDrive/Escritorio/Manrope/static/Manrope-Regular.ttf",
    "disponible" : "C:/Users/jlcal/OneDrive/Escritorio/Manrope/static/Manrope-Regular.ttf",
    "coma_cero" : "C:/Users/jlcal/OneDrive/Escritorio/Manrope/static/Manrope-Regular.ttf",
    "pago" : "C:/Users/jlcal/OneDrive/Escritorio/Manrope/static/Manrope-Regular.ttf",
    "qr" : "C:/Users/jlcal/OneDrive/Escritorio/Manrope/static/Manrope-Regular.ttf",
    "compartir" : "C:/Users/jlcal/OneDrive/Escritorio/Manrope/static/Manrope-Regular.ttf",
    "ref" : "C:/Users/jlcal/OneDrive/Escritorio/Manrope/static/Manrope-Regular.ttf",
    "compartirqr" : "C:/Users/jlcal/OneDrive/Escritorio/Manrope/static/Manrope-Regular.ttf",
    "tf" : "C:/Users/jlcal/OneDrive/Escritorio/Manrope/static/Manrope-Regular.ttf",
    "tf2" : "C:/Users/jlcal/OneDrive/Escritorio/Manrope/static/Manrope-Regular.ttf"
}

# Colores de texto para cada plantilla
COLOR_TEXTOS = {
    0: "#4f364f",  # Plantilla 1
    1: "#3b353b",  # Plantilla 2
    2: "#3b353b",  # Comprobante QR
    3: "#3b353b",  # Comprobante Compartir
    4: "#3b353b",  # Comprobante Transferencia
    5: "#3b353b",  # Comprobante Compartir QR
    6: "#3b353b", # Comprobante Negocio QR
    7: "#34242e"
    
}

color_disponible = "#808080"

def generar_comprobante(user_data: dict, banco: str, plantilla_id: int) -> Image:
    """Genera el comprobante con los datos del usuario y la plantilla seleccionada."""
    nombre_corto = user_data["nombre_corto"]
    nombre_corto2 = user_data["nombre_corto2"]
    numero_cuenta = user_data["numero_cuenta"]
    nombre_corto = user_data["nombre_corto"].upper()  # Convertir a mayúsculas
    nombre_largo = user_data["nombre_largo"].upper()  # Convertir a mayúsculas
    nombre_largo = user_data["nombre_largo"]
    nombre_largo2 = user_data["nombre_largo2"].upper()
    monto = user_data["monto"]
    numero_banco = user_data["numero_banco"]
    referencia = user_data["referencia"]
    fecha = user_data["fecha"]

    monto_con_decimales = f"{monto},00"
    monto_sin_decimales = f"{monto}"

    
    # Obtener las posiciones según la plantilla
    posiciones = posiciones_por_plantilla.get(plantilla_id, {})

    # Ruta base de las plantillas (ya no es una lista, sino un solo archivo dependiendo del índice)
    plantilla_path = IMAGENES[banco][plantilla_id]

    try:
        # Intentamos abrir la plantilla desde la ruta
        plantilla = Image.open(plantilla_path)
    except FileNotFoundError as e:
        print(f"Error: No se pudo encontrar la plantilla en la ruta: {plantilla_path}")
        return None
    except IOError as e:
        print(f"Error al abrir la plantilla: {e}")
        return None

    # Cargar fuentes con tamaños específicos según el comprobante
    try:
        # Tamaños de fuentes generales
        font_sizes = {
            "nombre_corto": 44.5, "nombre_largo": 44.5, "nombre_largo2": 44.5, "monto": 44.5, "referencia": 44.5, "numero_banco": 44.5,
            "fecha": 44.5, "disponible": 40, "coma_cero": 33, "pago": 44.5, "qr": 27.5, "compartir": 23,
            "ref": 29.5, "compartirqr": 25, "tf": 26, "tf2": 24
        }

        # Ajustar tamaños dependiendo del tipo de comprobante
        if plantilla_id == 4:  # Comprobante Compartir 
            font_sizes["monto"] = 28
            font_sizes["referencia"] = 38
        elif plantilla_id == 5:  # Comprobante Transfiya
            font_sizes["monto"] = 28
            font_sizes["referencia"] = 38
        elif plantilla_id == 6:  # Comprobante Compartir QR
            font_sizes["monto"] = 28
            font_sizes["referencia"] = 28
        elif plantilla_id == 7:  # Comprobante Negocio QR
            font_sizes["monto"] = 28
            font_sizes["referencia"] = 28
        elif plantilla_id == 3:  # Comprobante QR (nuevo comprobante QR)
            font_sizes["monto"] = 28
            font_sizes["referencia"] = 30
            font_sizes["qr"] = 60  # Tamaño de fuente para el QR, si lo colocas en un campo de texto

        # Cargar las fuentes con los tamaños definidos
        fonts = {
            key: ImageFont.truetype(FONT_PATHS[key], size) 
            for key, size in font_sizes.items()
        }

    except Exception as e:
        print(f"Error al cargar la fuente: {e}")
        return None

    try:
        draw = ImageDraw.Draw(plantilla)

        # Obtener el color según la plantilla
        color_texto = COLOR_TEXTOS.get(plantilla_id, "#4f364f")

        # Colocar el texto en la imagen según las posiciones, personalizado por plantilla
        if plantilla_id == 4:  # Comprobante Compartir
            draw.text(posiciones["numero_cuenta"], monto_con_decimales, font=fonts["nombre_corto"], fill=color_texto)
            draw.text(posiciones["nombre_corto"], nombre_corto, font=fonts["nombre_corto"], fill=color_texto)
            draw.text(posiciones["nombre_largo"], nombre_largo, font=fonts["nombre_corto"], fill=color_texto)
            draw.text(posiciones["monto"], monto_con_decimales, font=fonts["nombre_corto"], fill=color_texto)
            draw.text(posiciones["numero_banco"], numero_banco, font=fonts["nombre_corto"], fill=color_texto)
            draw.text(posiciones["referencia"], referencia, font=fonts["nombre_corto"], fill=color_texto)
            draw.text(posiciones["fecha"], fecha, font=fonts["nombre_corto"], fill=color_texto)

        
        elif plantilla_id == 0:  
            draw.text(posiciones["numero_cuenta"], monto_con_decimales, font=fonts["nombre_corto"], fill=color_texto)
            draw.text(posiciones["nombre_corto"], nombre_corto, font=fonts["nombre_corto"], fill=color_texto)
            draw.text(posiciones["nombre_largo"], nombre_largo, font=fonts["nombre_largo"], fill=color_texto)
            draw.text(posiciones["monto"], monto_con_decimales, font=fonts["monto"], fill=color_texto)
            draw.text(posiciones["numero_banco"], numero_banco, font=fonts["numero_banco"], fill=color_texto)
            draw.text(posiciones["referencia"], referencia, font=fonts["referencia"], fill=color_texto)
            draw.text(posiciones["fecha"], fecha, font=fonts["fecha"], fill=color_texto)

        elif plantilla_id == 2:  
            draw.text(posiciones["numero_cuenta"], monto_con_decimales, font=fonts["qr"], fill=color_texto)
            draw.text(posiciones["nombre_corto"], nombre_corto, font=fonts["qr"], fill=color_texto)
            draw.text(posiciones["nombre_largo"], nombre_largo, font=fonts["qr"], fill=color_texto)
            draw.text(posiciones["monto"], monto_con_decimales, font=fonts["qr"], fill=color_texto)
            draw.text(posiciones["numero_banco"], numero_banco, font=fonts["qr"], fill=color_texto)
            draw.text(posiciones["referencia"], referencia, font=fonts["qr"], fill=color_texto)
            draw.text(posiciones["fecha"], fecha, font=fonts["qr"], fill=color_texto)

        elif plantilla_id == 1:
            draw.text(posiciones["numero_cuenta"], monto_con_decimales, font=fonts["nombre_corto"], fill=color_texto)
            draw.text(posiciones["nombre_corto"], nombre_corto, font=fonts["nombre_corto"], fill=color_texto)
            draw.text(posiciones["nombre_largo2"], nombre_largo2, font=fonts["nombre_largo"], fill=color_texto)
            draw.text(posiciones["monto"], monto_con_decimales, font=fonts["monto"], fill=color_texto)
            draw.text(posiciones["numero_banco"], numero_banco, font=fonts["numero_banco"], fill=color_texto)
            draw.text(posiciones["referencia"], referencia, font=fonts["referencia"], fill=color_texto)
            draw.text(posiciones["fecha"], fecha, font=fonts["fecha"], fill=color_texto)

        elif plantilla_id == 5:  # Comprobante Compartir 
            draw.text(posiciones["numero_cuenta"], monto_con_decimales, font=fonts["compartirqr"], fill=color_texto)
            draw.text(posiciones["nombre_corto"], nombre_corto, font=fonts["compartirqr"], fill=color_texto)
            draw.text(posiciones["nombre_largo"], nombre_largo, font=fonts["compartirqr"], fill=color_texto)
            draw.text(posiciones["monto"], monto_con_decimales, font=fonts["compartirqr"], fill=color_texto)
            draw.text(posiciones["numero_banco"], numero_banco, font=fonts["compartirqr"], fill=color_texto)
            draw.text(posiciones["referencia"], referencia, font=fonts["ref"], fill=color_texto)
            draw.text(posiciones["fecha"], fecha, font=fonts["compartirqr"], fill=color_texto)

        elif plantilla_id == 6:  # Comprobante Negocio QR
            draw.text(posiciones["numero_cuenta"], monto_con_decimales, font=fonts["tf"], fill=color_texto)
            draw.text(posiciones["nombre_corto"], nombre_corto, font=fonts["tf"], fill=color_texto)
            draw.text(posiciones["nombre_largo"], nombre_largo, font=fonts["tf"], fill=color_texto)
            draw.text(posiciones["monto"], monto_con_decimales, font=fonts["tf"], fill=color_texto)
            draw.text(posiciones["numero_banco"], numero_banco, font=fonts["tf"], fill=color_texto)
            draw.text(posiciones["referencia"], referencia, font=fonts["tf"], fill=color_texto)
            draw.text(posiciones["fecha"], fecha, font=fonts["tf"], fill=color_texto)
        
        elif plantilla_id == 7:  # Comprobante Negocio QR
            draw.text(posiciones["numero_cuenta"], monto_con_decimales, font=fonts["tf"], fill=color_texto)
            draw.text(posiciones["nombre_corto2"], nombre_corto2, font=fonts["tf"], fill=color_texto)
            draw.text(posiciones["nombre_largo"], nombre_largo, font=fonts["tf2"], fill=color_texto)
            draw.text(posiciones["monto"], numero_cuenta, font=fonts["tf"], fill=color_texto)
            draw.text(posiciones["numero_banco"], numero_banco, font=fonts["tf"], fill=color_texto)
            draw.text(posiciones["referencia"], referencia, font=fonts["tf"], fill=color_texto)
            draw.text(posiciones["fecha"], fecha, font=fonts["tf"], fill=color_texto)

        elif plantilla_id == 3:  # Comprobante QR
            # Colocar los textos en la imagen
            draw.text(posiciones["numero_cuenta"], monto_con_decimales, font=fonts["compartir"], fill=color_texto)
            draw.text(posiciones["nombre_corto"], nombre_corto, font=fonts["compartir"], fill=color_texto)
            draw.text(posiciones["nombre_largo"], nombre_largo, font=fonts["compartir"], fill=color_texto)
            draw.text(posiciones["monto"], monto_con_decimales, font=fonts["compartir"], fill=color_texto)
            draw.text(posiciones["numero_banco"], numero_banco, font=fonts["compartir"], fill=color_texto)
            draw.text(posiciones["referencia"], referencia, font=fonts["ref"], fill=color_texto)
            draw.text(posiciones["fecha"], fecha, font=fonts["compartir"], fill=color_texto)

        

        # Si es una plantilla que necesita colocar el monto con decimales
        if plantilla_id in [0]:
            draw.text((226, 1435), f"$ {monto_sin_decimales}", font=fonts["disponible"], fill=color_disponible)
            draw.text((224 + draw.textlength(f"$ {monto_sin_decimales}", font=fonts["disponible"]), 1443),
                      ",00", font=fonts["coma_cero"], fill=color_disponible)
            
        if plantilla_id in [1]:
            draw.text((211, 1388), f"$ {monto_sin_decimales}", font=fonts["disponible"], fill=color_disponible)
            draw.text((213 + draw.textlength(f"$ {monto_sin_decimales}", font=fonts["disponible"]), 1396),
                      ",00", font=fonts["coma_cero"], fill=color_disponible)
            
        if plantilla_id in [4]:
            draw.text((233, 1344), f"$ {monto_sin_decimales}", font=fonts["disponible"], fill=color_disponible)
            draw.text((230 + draw.textlength(f"$ {monto_sin_decimales}", font=fonts["disponible"]), 1350),
                      ",00", font=fonts["coma_cero"], fill=color_disponible)
            

    except Exception as e:
        print(f"Error al escribir en la imagen: {e}")
        return None

    return plantilla


async def cancel(update: Update, context: CallbackContext) -> int:
    """Cancela la operación y termina la conversación."""
    await update.message.reply_text("❌ ¡Operación cancelada! Si necesitas algo más, no dudes en decírmelo.\n\n"
                                    "Si quieres Iniciar de nuevo Escribe: /start 😉")
    return ConversationHandler.END

# Función principal para iniciar la aplicación
def main():
    application = Application.builder().token("7635357641:AAHNCSDMj50EcG3LJs3eCfxnMzccvAGHhlE").build()

    # Configuración de la conversación
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECCION_COMPROBANTE: [
                CommandHandler("nequi", seleccionar_nequi),
                CommandHandler("bancolombia", seleccionar_bancolombia),
                CommandHandler("cancel", cancel),
                MessageHandler(filters.TEXT, manejar_seleccion_comprobante)
            ],
            NOMBRE_CORTO: [MessageHandler(filters.TEXT, recibir_nombre_corto)],
            NOMBRE_LARGO: [MessageHandler(filters.TEXT, recibir_nombre_largo)],
            CUANTO: [MessageHandler(filters.TEXT, recibir_monto)],
            NUMERO_BANCO: [MessageHandler(filters.TEXT, recibir_numero_banco)],
            NOMBRE_CORTO2: [MessageHandler(filters.TEXT, recibir_numero_cuenta)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conversation_handler)
    application.run_polling()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

