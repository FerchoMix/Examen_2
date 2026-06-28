from flask import Flask
from flask_appbuilder import AppBuilder
from flask_appbuilder.models.sqla.base import SQLA

app = Flask(__name__)
app.config.from_object('config')

db = SQLA(app)
from app.ia_floating import registrar_boton_flotante_ia

registrar_boton_flotante_ia(app)
with app.app_context():
    appbuilder = AppBuilder(app, db.session)
    from app import views  # noqa: E402,F401
