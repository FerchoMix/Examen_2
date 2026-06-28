import json
from flask import flash, request
from decimal import Decimal

from flask_appbuilder import BaseView, ModelView, expose, has_access
from flask_appbuilder.models.sqla.interface import SQLAInterface
from sqlalchemy import func

from app import appbuilder, db
from app.models import (
    Cliente,
    DetalleRepuesto,
    Mecanico,
    OrdenTrabajo,
    Pago,
    Repuesto,
    Servicio,
    Vehiculo,
    ConsultaIA,
)


class ClienteView(ModelView):
    datamodel = SQLAInterface(Cliente)
    class_permission_name = 'clientes'
    list_columns = ['nombre', 'ci_nit', 'telefono', 'direccion']
    show_columns = ['nombre', 'ci_nit', 'telefono', 'direccion', 'vehiculos']
    add_columns = ['nombre', 'ci_nit', 'telefono', 'direccion']
    edit_columns = add_columns
    label_columns = {'ci_nit': 'CI / NIT'}


class VehiculoView(ModelView):
    datamodel = SQLAInterface(Vehiculo)
    class_permission_name = 'vehiculos'
    list_columns = ['placa', 'marca', 'modelo', 'anio', 'color', 'cliente']
    show_columns = ['placa', 'marca', 'modelo', 'anio', 'color', 'cliente', 'ordenes']
    add_columns = ['placa', 'marca', 'modelo', 'anio', 'color', 'cliente']
    edit_columns = add_columns
    label_columns = {'anio': 'Año'}


class MecanicoView(ModelView):
    datamodel = SQLAInterface(Mecanico)
    class_permission_name = 'mecanicos'
    list_columns = ['nombre', 'especialidad', 'telefono', 'estado']
    add_columns = ['nombre', 'especialidad', 'telefono', 'estado']
    edit_columns = add_columns


class ServicioView(ModelView):
    datamodel = SQLAInterface(Servicio)
    class_permission_name = 'servicios'
    list_columns = ['nombre', 'precio_base', 'descripcion']
    add_columns = ['nombre', 'precio_base', 'descripcion']
    edit_columns = add_columns
    label_columns = {'precio_base': 'Precio base'}


class OrdenTrabajoView(ModelView):
    datamodel = SQLAInterface(OrdenTrabajo)
    class_permission_name = 'ordenes'
    list_columns = [
        'id', 'fecha_ingreso', 'vehiculo', 'mecanico', 'servicio', 'estado', 'costo_mano_obra'
    ]
    show_columns = [
        'fecha_ingreso', 'fecha_entrega', 'vehiculo', 'mecanico', 'servicio', 'diagnostico',
        'estado', 'costo_mano_obra', 'detalles_repuestos', 'pagos'
    ]
    add_columns = [
        'fecha_ingreso', 'fecha_entrega', 'vehiculo', 'mecanico', 'servicio',
        'diagnostico', 'estado', 'costo_mano_obra'
    ]
    edit_columns = add_columns
    label_columns = {
        'fecha_ingreso': 'Fecha de ingreso',
        'fecha_entrega': 'Fecha de entrega',
        'costo_mano_obra': 'Mano de obra (Bs)',
        'diagnostico': 'Diagnóstico',
    }


class RepuestoView(ModelView):
    datamodel = SQLAInterface(Repuesto)
    class_permission_name = 'repuestos'
    list_columns = ['codigo', 'nombre', 'stock', 'precio_unitario']
    add_columns = ['codigo', 'nombre', 'stock', 'precio_unitario']
    edit_columns = add_columns
    label_columns = {'precio_unitario': 'Precio unitario'}


class DetalleRepuestoView(ModelView):
    datamodel = SQLAInterface(DetalleRepuesto)
    class_permission_name = 'detalle_repuestos'
    list_columns = ['orden', 'repuesto', 'cantidad', 'precio_unitario', 'subtotal']
    add_columns = ['orden', 'repuesto', 'cantidad', 'precio_unitario']
    edit_columns = add_columns
    label_columns = {'precio_unitario': 'Precio unitario'}

    def pre_add(self, item):
        item.subtotal = (item.precio_unitario or Decimal('0')) * (item.cantidad or 0)

    def pre_update(self, item):
        item.subtotal = (item.precio_unitario or Decimal('0')) * (item.cantidad or 0)


class PagoView(ModelView):
    datamodel = SQLAInterface(Pago)
    class_permission_name = 'pagos'
    list_columns = ['fecha', 'orden', 'metodo', 'monto', 'observacion']
    add_columns = ['fecha', 'orden', 'metodo', 'monto', 'observacion']
    edit_columns = add_columns
    label_columns = {'metodo': 'Método de pago', 'observacion': 'Observación'}


class ReportesView(BaseView):
    route_base = '/reportes'
    class_permission_name = 'reportes'
    method_permission_name = {'ordenes': 'access', 'pagos': 'access', 'stock': 'access'}
    default_view = 'ordenes'

    @expose('/ordenes/')
    @has_access
    def ordenes(self):
        rows = (
            db.session.query(OrdenTrabajo)
            .join(Vehiculo)
            .join(Mecanico)
            .join(Servicio)
            .order_by(OrdenTrabajo.fecha_ingreso.desc())
            .all()
        )
        total_mano_obra = sum((r.costo_mano_obra or Decimal('0')) for r in rows)
        return self.render_template(
            'reportes/ordenes.html',
            rows=rows,
            total_mano_obra=total_mano_obra,
            total_registros=len(rows),
        )

    @expose('/pagos/')
    @has_access
    def pagos(self):
        rows = db.session.query(Pago).join(OrdenTrabajo).order_by(Pago.fecha.desc()).all()
        total = sum((r.monto or Decimal('0')) for r in rows)
        return self.render_template(
            'reportes/pagos.html', rows=rows, total=total, total_registros=len(rows)
        )

    @expose('/stock/')
    @has_access
    def stock(self):
        rows = db.session.query(Repuesto).order_by(Repuesto.stock.asc()).all()
        criticos = len([r for r in rows if r.stock <= 3])
        return self.render_template(
            'reportes/stock.html', rows=rows, criticos=criticos, total_registros=len(rows)
        )


class GraficasView(BaseView):
    route_base = '/graficas'
    class_permission_name = 'graficas'
    method_permission_name = {'servicios': 'access', 'mecanicos': 'access', 'ingresos': 'access'}
    default_view = 'servicios'

    def _render_chart(self, titulo, subtitulo, chart_type, data):
        labels = [str(nombre) for nombre, _ in data]
        values = [float(valor or 0) for _, valor in data]
        return self.render_template(
            'graficas/chart.html',
            titulo=titulo,
            subtitulo=subtitulo,
            chart_type=chart_type,
            labels=json.dumps(labels, ensure_ascii=False),
            values=json.dumps(values),
            total_items=len(data),
        )

    @expose('/servicios/')
    @has_access
    def servicios(self):
        data = (
            db.session.query(Servicio.nombre, func.count(OrdenTrabajo.id))
            .outerjoin(OrdenTrabajo, OrdenTrabajo.servicio_id == Servicio.id)
            .group_by(Servicio.nombre)
            .all()
        )
        return self._render_chart(
            'Órdenes por servicio',
            'Comparación de la demanda de servicios del taller.',
            'bar',
            data,
        )

    @expose('/mecanicos/')
    @has_access
    def mecanicos(self):
        data = (
            db.session.query(Mecanico.nombre, func.count(OrdenTrabajo.id))
            .outerjoin(OrdenTrabajo, OrdenTrabajo.mecanico_id == Mecanico.id)
            .group_by(Mecanico.nombre)
            .all()
        )
        return self._render_chart(
            'Trabajos por mecánico',
            'Distribución de órdenes atendidas por cada mecánico.',
            'doughnut',
            data,
        )

    @expose('/ingresos/')
    @has_access
    def ingresos(self):
        data = (
            db.session.query(Pago.metodo, func.coalesce(func.sum(Pago.monto), 0))
            .group_by(Pago.metodo)
            .all()
        )
        return self._render_chart(
            'Ingresos por método de pago',
            'Resumen de ingresos según el método de pago utilizado.',
            'polarArea',
            data,
        )

class ConsultaIAView(ModelView):
    datamodel = SQLAInterface(ConsultaIA)
    class_permission_name = 'consultas_ia'
    list_columns = ['fecha', 'usuario', 'pregunta', 'respuesta']
    show_columns = ['fecha', 'usuario', 'pregunta', 'respuesta']
    add_columns = ['pregunta', 'respuesta', 'usuario']
    edit_columns = ['pregunta', 'respuesta', 'usuario']
    label_columns = {
        'fecha': 'Fecha',
        'pregunta': 'Pregunta',
        'respuesta': 'Respuesta',
        'usuario': 'Usuario',
    }


class AsistenteIAView(BaseView):
    route_base = '/asistente-ia'
    class_permission_name = 'asistente_ia'
    method_permission_name = {'index': 'access'}
    default_view = 'index'

    @expose('/', methods=['GET', 'POST'])
    @has_access
    def index(self):
        from flask_login import current_user
        from app.ai_service import generar_respuesta_ia

        pregunta = ''
        respuesta = ''

        if request.method == 'POST':
            pregunta = request.form.get('pregunta', '').strip()

            if not pregunta:
                flash('Debes escribir una pregunta para consultar la IA.', 'warning')
            else:
                respuesta = generar_respuesta_ia(pregunta)

                consulta = ConsultaIA(
                    pregunta=pregunta,
                    respuesta=respuesta,
                    usuario=getattr(current_user, 'username', 'sistema'),
                )

                db.session.add(consulta)
                db.session.commit()

                flash('Consulta guardada en el historial IA.', 'success')

        return self.render_template(
            'ia/asistente.html',
            pregunta=pregunta,
            respuesta=respuesta,
        )
appbuilder.add_view(ClienteView, 'Clientes', icon='fa-users', category='Catálogos')
appbuilder.add_view(VehiculoView, 'Vehículos', icon='fa-car', category='Catálogos')
appbuilder.add_view(MecanicoView, 'Mecánicos', icon='fa-wrench', category='Catálogos')
appbuilder.add_view(ServicioView, 'Servicios', icon='fa-cogs', category='Catálogos')

appbuilder.add_view(OrdenTrabajoView, 'Órdenes de trabajo', icon='fa-clipboard', category='Operaciones')
appbuilder.add_view(RepuestoView, 'Repuestos', icon='fa-archive', category='Operaciones')
appbuilder.add_view(DetalleRepuestoView, 'Detalle de repuestos', icon='fa-list', category='Operaciones')
appbuilder.add_view(PagoView, 'Pagos', icon='fa-money', category='Operaciones')

appbuilder.add_view(ReportesView, 'Reporte de órdenes', icon='fa-file-text', category='Reportes')
appbuilder.add_link('Reporte de pagos', href='/reportes/pagos/', icon='fa-money', category='Reportes')
appbuilder.add_link('Reporte de stock', href='/reportes/stock/', icon='fa-warning', category='Reportes')

appbuilder.add_view(AsistenteIAView, 'Asistente IA', icon='fa-magic', category='Inteligencia Artificial')
appbuilder.add_view(ConsultaIAView, 'Historial IA', icon='fa-comments', category='Inteligencia Artificial')
appbuilder.add_link('Inicio', href='/', icon='fa-home', category='Inicio')

appbuilder.add_view(GraficasView, 'Gráfica de servicios', icon='fa-bar-chart', category='Gráficas')
appbuilder.add_link('Gráfica de mecánicos', href='/graficas/mecanicos/', icon='fa-pie-chart', category='Gráficas')
appbuilder.add_link('Gráfica de ingresos', href='/graficas/ingresos/', icon='fa-line-chart', category='Gráficas')
