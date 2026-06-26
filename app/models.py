from datetime import date
from decimal import Decimal

from flask_appbuilder import Model
from sqlalchemy import Column, Date, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship


class Cliente(Model):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(80), nullable=False)
    ci_nit = Column(String(30), unique=True, nullable=False)
    telefono = Column(String(30), nullable=False)
    direccion = Column(String(150))

    vehiculos = relationship("Vehiculo", back_populates="cliente")

    def __repr__(self):
        return self.nombre


class Vehiculo(Model):
    __tablename__ = "vehiculos"

    id = Column(Integer, primary_key=True)
    placa = Column(String(20), unique=True, nullable=False)
    marca = Column(String(50), nullable=False)
    modelo = Column(String(50), nullable=False)
    anio = Column(Integer)
    color = Column(String(30))
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)

    cliente = relationship("Cliente", back_populates="vehiculos")
    ordenes = relationship("OrdenTrabajo", back_populates="vehiculo")

    def __repr__(self):
        return f"{self.placa} - {self.marca} {self.modelo}"


class Mecanico(Model):
    __tablename__ = "mecanicos"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(80), nullable=False)
    especialidad = Column(String(80), nullable=False)
    telefono = Column(String(30))
    estado = Column(String(20), default="Activo")

    ordenes = relationship("OrdenTrabajo", back_populates="mecanico")

    def __repr__(self):
        return self.nombre


class Servicio(Model):
    __tablename__ = "servicios"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(80), nullable=False)
    descripcion = Column(Text)
    precio_base = Column(Numeric(10, 2), nullable=False, default=0)

    ordenes = relationship("OrdenTrabajo", back_populates="servicio")

    def __repr__(self):
        return self.nombre


class OrdenTrabajo(Model):
    __tablename__ = "ordenes_trabajo"

    id = Column(Integer, primary_key=True)
    fecha_ingreso = Column(Date, nullable=False, default=date.today)
    fecha_entrega = Column(Date)
    diagnostico = Column(Text, nullable=False)
    estado = Column(String(30), nullable=False, default="Pendiente")
    costo_mano_obra = Column(Numeric(10, 2), nullable=False, default=0)

    vehiculo_id = Column(Integer, ForeignKey("vehiculos.id"), nullable=False)
    mecanico_id = Column(Integer, ForeignKey("mecanicos.id"), nullable=False)
    servicio_id = Column(Integer, ForeignKey("servicios.id"), nullable=False)

    vehiculo = relationship("Vehiculo", back_populates="ordenes")
    mecanico = relationship("Mecanico", back_populates="ordenes")
    servicio = relationship("Servicio", back_populates="ordenes")
    detalles_repuestos = relationship("DetalleRepuesto", back_populates="orden")
    pagos = relationship("Pago", back_populates="orden")

    @property
    def total_repuestos(self):
        return sum((d.subtotal or Decimal("0")) for d in self.detalles_repuestos)

    @property
    def total_orden(self):
        return (self.costo_mano_obra or Decimal("0")) + self.total_repuestos

    def __repr__(self):
        return f"Orden #{self.id} - {self.estado}"


class Repuesto(Model):
    __tablename__ = "repuestos"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    codigo = Column(String(40), unique=True, nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    precio_unitario = Column(Numeric(10, 2), nullable=False, default=0)

    detalles = relationship("DetalleRepuesto", back_populates="repuesto")

    def __repr__(self):
        return f"{self.codigo} - {self.nombre}"


class DetalleRepuesto(Model):
    __tablename__ = "detalle_repuestos"

    id = Column(Integer, primary_key=True)
    cantidad = Column(Integer, nullable=False, default=1)
    precio_unitario = Column(Numeric(10, 2), nullable=False, default=0)
    subtotal = Column(Numeric(10, 2), nullable=False, default=0)

    orden_id = Column(Integer, ForeignKey("ordenes_trabajo.id"), nullable=False)
    repuesto_id = Column(Integer, ForeignKey("repuestos.id"), nullable=False)

    orden = relationship("OrdenTrabajo", back_populates="detalles_repuestos")
    repuesto = relationship("Repuesto", back_populates="detalles")

    def __repr__(self):
        return f"{self.repuesto} x {self.cantidad}"


class Pago(Model):
    __tablename__ = "pagos"

    id = Column(Integer, primary_key=True)
    fecha = Column(Date, nullable=False, default=date.today)
    metodo = Column(String(30), nullable=False, default="Efectivo")
    monto = Column(Numeric(10, 2), nullable=False, default=0)
    observacion = Column(String(150))
    orden_id = Column(Integer, ForeignKey("ordenes_trabajo.id"), nullable=False)

    orden = relationship("OrdenTrabajo", back_populates="pagos")

    def __repr__(self):
        return f"Pago Bs {self.monto} - Orden {self.orden_id}"
