from datetime import datetime

from flask import request
from flask_login import current_user


def registrar_footer(app):
    @app.after_request
    def insertar_footer(response):
        content_type = response.headers.get("Content-Type", "")

        if response.status_code != 200:
            return response

        if "text/html" not in content_type:
            return response

        if request.path.startswith("/static"):
            return response

        if not current_user or not current_user.is_authenticated:
            return response

        html = response.get_data(as_text=True)

        if "</head>" in html and "footer.css" not in html:
            css_link = '<link rel="stylesheet" href="/static/css/footer.css">'
            html = html.replace("</head>", css_link + "</head>")

        if "</body>" not in html:
            return response

        if "app-footer" in html:
            return response

        year = datetime.now().year

        footer_html = f"""
<footer class="app-footer">
    <div class="app-footer-content">
        <div>
            <div class="app-footer-brand">Sistema Taller Mecánico</div>
            <div class="app-footer-text">
                Gestión de clientes, vehículos, órdenes, repuestos, pagos e inteligencia artificial.
            </div>
        </div>

        <div class="app-footer-links">
            <a href="/">Inicio</a>
            <a href="/asistente-ia/">Asistente IA</a>
            <a href="/repuestoview/list/">Repuestos</a>
            <a href="/ordentrabajoview/list/">Órdenes</a>
        </div>

        <div class="app-footer-text">
            © {year} Taller Mecánico
        </div>
    </div>
</footer>
"""

        html = html.replace("</body>", footer_html + "</body>")
        response.set_data(html)
        response.headers["Content-Length"] = str(len(response.get_data()))

        return response