import os
from dotenv import load_dotenv
from flask_appbuilder.security.manager import AUTH_DB

load_dotenv()


SECRET_KEY = os.environ.get("SECRET_KEY", "clave-examen-taller-mecanico-2026")

MYSQL_USER = os.environ.get("MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
MYSQL_PORT = os.environ.get("MYSQL_PORT", "3306")
MYSQL_DB = os.environ.get("MYSQL_DB", "taller_mecanico_fab")

SQLALCHEMY_DATABASE_URI = (
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4"
)

SQLALCHEMY_TRACK_MODIFICATIONS = False
CSRF_ENABLED = True
AUTH_TYPE = AUTH_DB
AUTH_ROLE_ADMIN = "Admin"
AUTH_ROLE_PUBLIC = "Public"
APP_NAME = "Sistema Taller Mecánico"
APP_THEME = "yeti.css"
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")

# Admin: acceso total automático de Flask-AppBuilder.
# Supervisor: gestión operativa y reportes/gráficas.
# Usuario: registro/consulta básica sin eliminar ni ver seguridad.
FAB_ROLES = {
    "Supervisor": [
        [".*", "menu_access"],
        ["clientes", "can_list"], ["clientes", "can_show"], ["clientes", "can_add"], ["clientes", "can_edit"],
        ["vehiculos", "can_list"], ["vehiculos", "can_show"], ["vehiculos", "can_add"], ["vehiculos", "can_edit"],
        ["mecanicos", "can_list"], ["mecanicos", "can_show"], ["mecanicos", "can_add"], ["mecanicos", "can_edit"],
        ["servicios", "can_list"], ["servicios", "can_show"], ["servicios", "can_add"], ["servicios", "can_edit"],
        ["ordenes", "can_list"], ["ordenes", "can_show"], ["ordenes", "can_add"], ["ordenes", "can_edit"],
        ["repuestos", "can_list"], ["repuestos", "can_show"], ["repuestos", "can_add"], ["repuestos", "can_edit"],
        ["detalle_repuestos", "can_list"], ["detalle_repuestos", "can_show"], ["detalle_repuestos", "can_add"], ["detalle_repuestos", "can_edit"],
        ["pagos", "can_list"], ["pagos", "can_show"], ["pagos", "can_add"], ["pagos", "can_edit"],
        ["reportes", "can_access"],
        ["graficas", "can_access"],
    ],
    "Usuario": [
        [".*", "menu_access"],
        ["clientes", "can_list"], ["clientes", "can_show"], ["clientes", "can_add"],
        ["vehiculos", "can_list"], ["vehiculos", "can_show"], ["vehiculos", "can_add"],
        ["servicios", "can_list"], ["servicios", "can_show"],
        ["ordenes", "can_list"], ["ordenes", "can_show"], ["ordenes", "can_add"],
        ["reportes", "can_access"],
    ],
}
