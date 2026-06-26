from datetime import date
from decimal import Decimal

from app import app, db, appbuilder
from app.models import (
    Cliente,
    DetalleRepuesto,
    Mecanico,
    OrdenTrabajo,
    Pago,
    Repuesto,
    Servicio,
    Vehiculo,
)


def get_or_create_role(nombre):
    return appbuilder.sm.find_role(nombre) or appbuilder.sm.add_role(nombre)


def add_user_if_missing(username, first_name, last_name, email, role_name, password):
    if appbuilder.sm.find_user(username=username):
        return
    role = get_or_create_role(role_name)
    appbuilder.sm.add_user(
        username=username,
        first_name=first_name,
        last_name=last_name,
        email=email,
        role=role,
        password=password,
    )


with app.app_context():
    db.create_all()

    add_user_if_missing('admin', 'Admin', 'Taller', 'admin@taller.com', 'Admin', 'admin')
    add_user_if_missing('supervisor', 'Supervisor', 'Taller', 'supervisor@taller.com', 'Supervisor', 'supervisor')
    add_user_if_missing('usuario', 'Usuario', 'Taller', 'usuario@taller.com', 'Usuario', 'usuario')

    if db.session.query(Cliente).count() == 0:
        c1 = Cliente(nombre='Juan Pérez', ci_nit='7010101', telefono='70011122', direccion='Zona Central')
        c2 = Cliente(nombre='María López', ci_nit='8020202', telefono='70022233', direccion='Av. Principal')
        c3 = Cliente(nombre='Carlos Rojas', ci_nit='9030303', telefono='70033344', direccion='Barrio Norte')
        db.session.add_all([c1, c2, c3])
        db.session.flush()

        v1 = Vehiculo(placa='ABC-123', marca='Toyota', modelo='Corolla', anio=2016, color='Blanco', cliente=c1)
        v2 = Vehiculo(placa='XYZ-987', marca='Nissan', modelo='Sentra', anio=2018, color='Azul', cliente=c2)
        v3 = Vehiculo(placa='BOL-456', marca='Suzuki', modelo='Vitara', anio=2020, color='Rojo', cliente=c3)
        db.session.add_all([v1, v2, v3])

        m1 = Mecanico(nombre='Pedro Mamani', especialidad='Motor', telefono='71111111', estado='Activo')
        m2 = Mecanico(nombre='Luis Flores', especialidad='Frenos', telefono='72222222', estado='Activo')
        m3 = Mecanico(nombre='Ana Vargas', especialidad='Electricidad', telefono='73333333', estado='Activo')
        db.session.add_all([m1, m2, m3])

        s1 = Servicio(nombre='Cambio de aceite', descripcion='Cambio de aceite y filtro', precio_base=Decimal('120.00'))
        s2 = Servicio(nombre='Revisión de frenos', descripcion='Pastillas, discos y líquido', precio_base=Decimal('180.00'))
        s3 = Servicio(nombre='Diagnóstico eléctrico', descripcion='Escaneo y revisión eléctrica', precio_base=Decimal('150.00'))
        db.session.add_all([s1, s2, s3])

        r1 = Repuesto(nombre='Filtro de aceite', codigo='REP-001', stock=10, precio_unitario=Decimal('45.00'))
        r2 = Repuesto(nombre='Pastillas de freno', codigo='REP-002', stock=4, precio_unitario=Decimal('160.00'))
        r3 = Repuesto(nombre='Bujía', codigo='REP-003', stock=2, precio_unitario=Decimal('35.00'))
        db.session.add_all([r1, r2, r3])
        db.session.flush()

        o1 = OrdenTrabajo(fecha_ingreso=date(2026, 6, 20), vehiculo=v1, mecanico=m1, servicio=s1, diagnostico='Mantenimiento preventivo', estado='Terminado', costo_mano_obra=Decimal('80.00'))
        o2 = OrdenTrabajo(fecha_ingreso=date(2026, 6, 21), vehiculo=v2, mecanico=m2, servicio=s2, diagnostico='Ruido al frenar', estado='En proceso', costo_mano_obra=Decimal('120.00'))
        o3 = OrdenTrabajo(fecha_ingreso=date(2026, 6, 22), vehiculo=v3, mecanico=m3, servicio=s3, diagnostico='Falla de encendido', estado='Pendiente', costo_mano_obra=Decimal('100.00'))
        db.session.add_all([o1, o2, o3])
        db.session.flush()

        d1 = DetalleRepuesto(orden=o1, repuesto=r1, cantidad=1, precio_unitario=Decimal('45.00'), subtotal=Decimal('45.00'))
        d2 = DetalleRepuesto(orden=o2, repuesto=r2, cantidad=1, precio_unitario=Decimal('160.00'), subtotal=Decimal('160.00'))
        d3 = DetalleRepuesto(orden=o3, repuesto=r3, cantidad=4, precio_unitario=Decimal('35.00'), subtotal=Decimal('140.00'))
        db.session.add_all([d1, d2, d3])

        p1 = Pago(fecha=date(2026, 6, 20), orden=o1, metodo='Efectivo', monto=Decimal('125.00'), observacion='Pago completo')
        p2 = Pago(fecha=date(2026, 6, 21), orden=o2, metodo='QR', monto=Decimal('200.00'), observacion='Adelanto')
        p3 = Pago(fecha=date(2026, 6, 22), orden=o3, metodo='Transferencia', monto=Decimal('100.00'), observacion='Adelanto')
        db.session.add_all([p1, p2, p3])

    db.session.commit()
    print('Base de datos, roles, usuarios y datos de prueba creados correctamente.')
    print('Usuarios: admin/admin | supervisor/supervisor | usuario/usuario')
