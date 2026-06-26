import json
from decimal import Decimal

from flask import Flask, redirect
from flask_appbuilder import AppBuilder, IndexView, expose
from flask_appbuilder.models.sqla.base import SQLA
from flask_login import current_user
from sqlalchemy import func

app = Flask(__name__)
app.config.from_object('config')

db = SQLA(app)


class DashboardIndexView(IndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect('/login/')

        from app.models import Cliente, Mecanico, OrdenTrabajo, Pago, Repuesto, Servicio, Vehiculo

        total_clientes = db.session.query(func.count(Cliente.id)).scalar() or 0
        total_vehiculos = db.session.query(func.count(Vehiculo.id)).scalar() or 0
        total_mecanicos = db.session.query(func.count(Mecanico.id)).scalar() or 0
        ordenes_activas = db.session.query(func.count(OrdenTrabajo.id)).filter(OrdenTrabajo.estado != 'Terminado').scalar() or 0
        stock_bajo = db.session.query(func.count(Repuesto.id)).filter(Repuesto.stock <= 3).scalar() or 0
        ingresos = db.session.query(func.coalesce(func.sum(Pago.monto), 0)).scalar() or Decimal('0')

        servicios = (
            db.session.query(Servicio.nombre, func.count(OrdenTrabajo.id))
            .outerjoin(OrdenTrabajo, OrdenTrabajo.servicio_id == Servicio.id)
            .group_by(Servicio.nombre)
            .all()
        )

        metodos = (
            db.session.query(Pago.metodo, func.coalesce(func.sum(Pago.monto), 0))
            .group_by(Pago.metodo)
            .all()
        )

        ordenes_recientes = (
            db.session.query(OrdenTrabajo)
            .order_by(OrdenTrabajo.fecha_ingreso.desc())
            .limit(5)
            .all()
        )

        return self.render_template(
            'dashboard.html',
            total_clientes=total_clientes,
            total_vehiculos=total_vehiculos,
            total_mecanicos=total_mecanicos,
            ordenes_activas=ordenes_activas,
            stock_bajo=stock_bajo,
            ingresos=float(ingresos),
            servicios_labels=json.dumps([x[0] for x in servicios], ensure_ascii=False),
            servicios_values=json.dumps([int(x[1] or 0) for x in servicios]),
            pagos_labels=json.dumps([x[0] for x in metodos], ensure_ascii=False),
            pagos_values=json.dumps([float(x[1] or 0) for x in metodos]),
            ordenes_recientes=ordenes_recientes,
        )


with app.app_context():
    appbuilder = AppBuilder(app, db.session, indexview=DashboardIndexView)
    from app import views  # noqa: E402,F401
