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

from app.ia_floating import registrar_boton_flotante_ia

registrar_boton_flotante_ia(app)

from app.footer import registrar_footer

registrar_footer(app)

def generar_pronosticos_servicios(servicios_data):
    datos = [(nombre or "Sin nombre", int(total or 0)) for nombre, total in servicios_data]
    total_ordenes = sum(total for _, total in datos)

    if not datos or total_ordenes == 0:
        return [
            "Todavía no hay suficientes órdenes para pronosticar la demanda por servicio.",
            "Cuando se registren más órdenes, el sistema identificará qué servicios tienen mayor movimiento.",
            "Se recomienda cargar órdenes reales para mejorar el análisis operativo del taller.",
        ]

    servicio_mayor = max(datos, key=lambda item: item[1])
    promedio = total_ordenes / len(datos)
    servicios_bajo_promedio = [nombre for nombre, total in datos if total < promedio]

    return [
        f"El servicio con mayor demanda es {servicio_mayor[0]}, con {servicio_mayor[1]} órdenes registradas.",
        f"Si la tendencia continúa, conviene priorizar repuestos y personal para el servicio {servicio_mayor[0]}.",
        (
            "Los servicios por debajo del promedio podrían necesitar promoción o revisión comercial: "
            + ", ".join(servicios_bajo_promedio[:3])
            if servicios_bajo_promedio
            else "Todos los servicios están mostrando un comportamiento equilibrado frente al promedio."
        ),
    ]


def generar_pronosticos_pagos(pagos_data):
    datos = [(metodo or "Sin método", float(total or 0)) for metodo, total in pagos_data]
    total_ingresos = sum(total for _, total in datos)

    if not datos or total_ingresos == 0:
        return [
            "Todavía no hay suficientes pagos registrados para pronosticar ingresos.",
            "Cuando se registren pagos, el sistema identificará el método de pago más usado.",
            "Se recomienda registrar todos los pagos para mejorar el control financiero del taller.",
        ]

    metodo_mayor = max(datos, key=lambda item: item[1])
    porcentaje = (metodo_mayor[1] / total_ingresos) * 100

    return [
        f"El método de pago con mayor ingreso es {metodo_mayor[0]}, concentrando aproximadamente {porcentaje:.1f}% del total.",
        f"Si se mantiene esta tendencia, el taller debería priorizar control y conciliación de pagos por {metodo_mayor[0]}.",
        "Se recomienda comparar los métodos de pago cada semana para detectar cambios en el comportamiento de los clientes.",
    ]


class DashboardIndexView(IndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect('/login/')

        from app.models import (
            Cliente,
            Mecanico,
            OrdenTrabajo,
            Pago,
            Repuesto,
            Servicio,
            Vehiculo,
        )

        total_clientes = db.session.query(func.count(Cliente.id)).scalar() or 0
        total_vehiculos = db.session.query(func.count(Vehiculo.id)).scalar() or 0
        total_mecanicos = db.session.query(func.count(Mecanico.id)).scalar() or 0

        ordenes_activas = (
            db.session.query(func.count(OrdenTrabajo.id))
            .filter(OrdenTrabajo.estado != 'Terminado')
            .scalar()
            or 0
        )

        stock_bajo = (
            db.session.query(func.count(Repuesto.id))
            .filter(Repuesto.stock <= 3)
            .scalar()
            or 0
        )

        ingresos = (
            db.session.query(func.coalesce(func.sum(Pago.monto), 0))
            .scalar()
            or Decimal('0')
        )

        servicios = (
            db.session.query(Servicio.nombre, func.count(OrdenTrabajo.id))
            .outerjoin(OrdenTrabajo, OrdenTrabajo.servicio_id == Servicio.id)
            .group_by(Servicio.nombre)
            .all()
        )

        metodos_pago = (
            db.session.query(Pago.metodo, func.coalesce(func.sum(Pago.monto), 0))
            .group_by(Pago.metodo)
            .all()
        )

        pronosticos_servicios = generar_pronosticos_servicios(servicios)
        pronosticos_pagos = generar_pronosticos_pagos(metodos_pago)

        repuestos_bajos = (
            db.session.query(Repuesto)
            .filter(Repuesto.stock <= 3)
            .order_by(Repuesto.stock.asc())
            .limit(6)
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
            pagos_labels=json.dumps([x[0] for x in metodos_pago], ensure_ascii=False),
            pagos_values=json.dumps([float(x[1] or 0) for x in metodos_pago]),
            repuestos_bajos=repuestos_bajos,
            ordenes_recientes=ordenes_recientes,
            pronosticos_servicios=pronosticos_servicios,
            pronosticos_pagos=pronosticos_pagos,
        )


with app.app_context():
    appbuilder = AppBuilder(app, db.session, indexview=DashboardIndexView)
    from app import views  # noqa: E402,F401