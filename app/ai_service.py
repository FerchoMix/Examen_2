from flask import current_app


def obtener_repuestos_stock_bajo():
    from app import db
    from app.models import Repuesto

    limite = current_app.config.get("STOCK_ALERT_THRESHOLD", 3)

    return (
        db.session.query(Repuesto)
        .filter(Repuesto.stock <= limite)
        .order_by(Repuesto.stock.asc())
        .all()
    )


def construir_contexto_stock():
    repuestos = obtener_repuestos_stock_bajo()

    if not repuestos:
        return "Actualmente no hay repuestos con stock bajo."

    lineas = []

    for repuesto in repuestos:
        nombre = getattr(repuesto, "nombre", "Repuesto sin nombre")
        stock = getattr(repuesto, "stock", 0)

        lineas.append(
            f"- {nombre}: stock actual {stock}. Conviene comprar o reponer pronto."
        )

    return "Repuestos con stock bajo:\n" + "\n".join(lineas)


def generar_respuesta_ia(pregunta):
    pregunta = (pregunta or "").strip()

    if not pregunta:
        return "Escribe una pregunta para que el asistente pueda ayudarte."

    api_key = current_app.config.get("GEMINI_API_KEY", "")
    modelo = current_app.config.get("GEMINI_MODEL", "gemini-3.5-flash")
    contexto_stock = construir_contexto_stock()

    if not api_key:
        return respuesta_demo(pregunta, contexto_stock)

    prompt = f"""
Eres un chatbot IA integrado a un sistema web de taller mecánico.

Tu trabajo es ayudar al usuario con:
- Diagnósticos preliminares.
- Órdenes de trabajo.
- Control de repuestos.
- Pagos.
- Atención al cliente.
- Sugerencias administrativas.
- Recomendaciones de compra cuando el stock esté bajo.

Reglas:
- Responde en español claro.
- Sé práctico y directo.
- No inventes datos del sistema.
- Si hay repuestos con stock bajo, sugiere comprarlos o reponerlos.
- No reemplaces a un mecánico certificado.
- No des instrucciones peligrosas.

Estado actual del inventario:
{contexto_stock}

Pregunta del usuario:
{pregunta}
"""

    try:
        from google import genai

        client = genai.Client(api_key=api_key)

        interaction = client.interactions.create(
            model=modelo,
            input=prompt,
        )

        return interaction.output_text

    except Exception as error:
        return (
            "No se pudo conectar con Gemini.\n\n"
            f"Detalle técnico: {error}\n\n"
            "Respuesta temporal en modo demostración:\n\n"
            + respuesta_demo(pregunta, contexto_stock)
        )


def respuesta_demo(pregunta, contexto_stock):
    texto = pregunta.lower()

    if "stock" in texto or "repuesto" in texto or "inventario" in texto or "comprar" in texto:
        return (
            "Modo demostración:\n\n"
            f"{contexto_stock}\n\n"
            "Recomendación: compra primero los repuestos que estén en el nivel mínimo "
            "o por debajo del límite configurado."
        )

    if "orden" in texto or "trabajo" in texto:
        return (
            "Modo demostración: para organizar una orden de trabajo registra cliente, "
            "vehículo, diagnóstico, mecánico responsable, estado, repuestos usados, "
            "mano de obra y costo total."
        )

    if "cliente" in texto:
        return (
            "Modo demostración: atiende al cliente explicando diagnóstico, tiempo estimado, "
            "costo aproximado, repuestos necesarios y forma de pago."
        )

    return (
        "Modo demostración: soy el asistente IA del taller. Puedo ayudarte con órdenes, "
        "clientes, pagos, repuestos y compras por stock bajo.\n\n"
        f"{contexto_stock}"
    )