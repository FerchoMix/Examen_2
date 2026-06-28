from flask import Flask, redirect
from flask_appbuilder import AppBuilder, IndexView, expose
from flask_appbuilder.models.sqla.base import SQLA
from flask_login import current_user

app = Flask(__name__)
app.config.from_object('config')

db = SQLA(app)

from app.ia_floating import registrar_boton_flotante_ia

registrar_boton_flotante_ia(app)


class MyIndexView(IndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect('/login/')
        return super().index()


with app.app_context():
    appbuilder = AppBuilder(app, db.session, indexview=MyIndexView)
    from app import views  # noqa: E402,F401
