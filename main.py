import random
from PIL import Image, ImageDraw, ImageFont
from telegram import Update
from telegram.ext import Application, CommandHandler
import os
import locale
from datetime import datetime
from flask import Flask, request
import logging

# Configuración de Flask y Webhook
app = Flask(__name__)

TEMPLATE_PATH = "C:/Users/jlcal/OneDrive/Escritorio/COMPROBANTES/comprobantes_nequi_nuevo/comprobante_nequi_nuevo1.png"
FONT_PATH = "C:/Users/jlcal/OneDrive/Escritorio/Manrope/static/Manrope-Medium.ttf"
TEXT_COLOR = "#4f364f"
NEQUI_NUMBER = "123456789"
FONT_SIZE = 39
MAX_WIDTH = 920  # Ancho máximo permitido para el texto


def formatear_monto(monto: str) -> str:
    monto_int = int(monto)
    # Formatear con comas manualmente
    monto_formateado = f"{monto_int:,}"
    return f"{monto_formateado},00"


def obtener_fecha_hora():
    ahora = datetime.now()
    dia = ahora.day
    mes = "diciembre"
    anio = ahora.year
    hora = ahora.strftime("%I:%M")
    ampm = ahora.strftime("%p")
    return f"{dia} de {mes} de\n{anio} a las {hora} {ampm.lower()}"

def generar_referencia():
    referencia = "M" + "".join([str(random.randint(0, 9)) for _ in range(8)])
    return referencia

def formatear_nombre(nombre: str) -> str:
    return ' '.join([palabra.capitalize() for palabra in nombre.split()])

def ajustar_texto_a_ancho(texto, font, max_width):
    lines = []
    words = texto.split()
    current_line = ""
    
    for word in words:
        test_line = f"{current_line} {word}".strip()
        bbox = font.getbbox(test_line)
        width = bbox[2] - bbox[0]
        if width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
            
    if current_line:
        lines.append(current_line)
    
    return "\n".join(lines)

async def generar_comprobante(nombre: str, monto: str):
    imagen = Image.open(TEMPLATE_PATH)
    draw = ImageDraw.Draw(imagen)

    try:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    except IOError:
        font = ImageFont.load_default()

    monto_formateado = formatear_monto(monto)
    fecha_hora = obtener_fecha_hora()
    referencia = generar_referencia()

    nombre_formateado = formatear_nombre(nombre)
    nombre_formateado = ajustar_texto_a_ancho(nombre_formateado, font, MAX_WIDTH)
    monto_formateado = ajustar_texto_a_ancho(monto_formateado, font, MAX_WIDTH)
    fecha_hora = obtener_fecha_hora()
    referencia = ajustar_texto_a_ancho(referencia, font, MAX_WIDTH)

    nombre_bbox = font.getbbox(nombre_formateado)
    nombre_width = nombre_bbox[1] - nombre_bbox[0]
    nombre_x = 900 - nombre_width
    draw.text((nombre_x, 875), f"{nombre_formateado}", font=font, fill=TEXT_COLOR)

    monto_bbox = font.getbbox(f"$ {monto_formateado}")
    monto_width = monto_bbox[1] - monto_bbox[0]
    monto_x = 785 + (MAX_WIDTH - monto_width)
    if monto_x > 920 - monto_width:
        monto_x = 920 - monto_width
    
    draw.text((monto_x, 967), f"$ {monto_formateado}", font=font, fill=TEXT_COLOR)

    draw.text((765, 1071), f"{NEQUI_NUMBER}", font=font, fill=TEXT_COLOR)
    draw.text((670, 1164), f"{fecha_hora}", font=font, fill=TEXT_COLOR)
    draw.text((786, 1312), f"{referencia}", font=font, fill=TEXT_COLOR)

    output_image_path = "C:/Users/jlcal/OneDrive/Escritorio/comprobante_generado.png"
    imagen.save(output_image_path)

    return output_image_path

async def generar_comprobante_cmd(update: Update, context):
    if len(context.args) != 3:
        await update.message.reply_text("Por favor, ingrese el nombre, el monto y el número Nequi. Ejemplo: /comprobante Juan 100000 123456789")
        return

    nombre = context.args[0]
    monto = context.args[1]
    nequi = context.args[2]

    global NEQUI_NUMBER
    NEQUI_NUMBER = nequi

    output_image_path = await generar_comprobante(nombre, monto)

    with open(output_image_path, 'rb') as img_file:
        await update.message.reply_photo(photo=img_file)

    os.remove(output_image_path)

async def start(update: Update, context):
    welcome_message = (
        "¡Hola! Soy un bot que te permite generar comprobantes de pago falsos.\n"
        "Usa el comando /comprobante seguido del nombre, cantidad y número Nequi para generar un comprobante.\n"
        "Ejemplo: /comprobante Juan 100000 123456789"
    )
    await update.message.reply_text(welcome_message)

def main():
    application = Application.builder().token("7635357641:AAHNCSDMj50EcG3LJs3eCfxnMzccvAGHhlE").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("comprobante", generar_comprobante_cmd))

    # Activamos el webhook
    port = int(os.environ.get('PORT', 5000))  # Puerto asignado por el entorno
    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path="your-webhook-path",
        webhook_url="https://deploy-bot-xts0.onrender.com",  # Reemplaza con tu URL de webhook
    )

    # Iniciar servidor Flask
    app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    main()
