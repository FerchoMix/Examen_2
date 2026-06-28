from flask import request
from flask_login import current_user


FLOATING_IA_HTML = """
<style>
.ia-floating-button {
    position: fixed;
    right: 24px;
    bottom: 24px;
    width: 62px;
    height: 62px;
    border-radius: 50%;
    background: linear-gradient(135deg, #1f6feb, #00b894);
    color: #ffffff !important;
    z-index: 99999;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 12px 28px rgba(0, 0, 0, .28);
    text-decoration: none !important;
    font-size: 26px;
    transition: transform .2s ease, box-shadow .2s ease;
}

.ia-floating-button:hover {
    transform: translateY(-4px) scale(1.04);
    box-shadow: 0 16px 32px rgba(0, 0, 0, .34);
    color: #ffffff !important;
    text-decoration: none !important;
}

.ia-floating-tooltip {
    position: fixed;
    right: 94px;
    bottom: 37px;
    background: #1f2937;
    color: white;
    padding: 8px 12px;
    border-radius: 10px;
    font-size: 13px;
    z-index: 99999;
    box-shadow: 0 8px 20px rgba(0, 0, 0, .20);
    opacity: 0;
    pointer-events: none;
    transform: translateX(8px);
    transition: all .2s ease;
}

.ia-floating-wrapper:hover .ia-floating-tooltip {
    opacity: 1;
    transform: translateX(0);
}
</style>

<div class="ia-floating-wrapper">
    <span class="ia-floating-tooltip">Asistente IA</span>
    <a class="ia-floating-button" href="/asistente-ia/" title="Asistente IA">
        <i class="fa fa-magic"></i>
    </a>
</div>
"""


def registrar_boton_flotante_ia(app):
    @app.after_request
    def insertar_boton_flotante_ia(response):
        content_type = response.headers.get("Content-Type", "")

        if response.status_code != 200:
            return response

        if "text/html" not in content_type:
            return response

        if request.path.startswith("/static"):
            return response

        if request.path.startswith("/login"):
            return response

        if not current_user or not current_user.is_authenticated:
            return response

        html = response.get_data(as_text=True)

        if "</body>" not in html:
            return response

        if "ia-floating-button" in html:
            return response

        html = html.replace("</body>", FLOATING_IA_HTML + "</body>")
        response.set_data(html)
        response.headers["Content-Length"] = str(len(response.get_data()))

        return response
    