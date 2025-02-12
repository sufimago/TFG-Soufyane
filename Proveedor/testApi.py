from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
import datetime

# 📌 Configuración de SQLite
DATABASE_URL = "sqlite:///./proveedor.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 📌 Modelos de Base de Datos

class Alojamiento(Base):
    __tablename__ = "alojamientos"
    listing = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    ubicacion = Column(String)
    disponible = Column(Boolean, default=True)

class Cliente(Base):
    __tablename__ = "clientes"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    email = Column(String, unique=True, index=True)

class Reserva(Base):
    __tablename__ = "reservas"
    id = Column(Integer, primary_key=True, index=True)
    listing = Column(Integer, ForeignKey("alojamientos.listing"))
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    fecha_reserva = Column(DateTime, default=datetime.datetime.now)
    fecha_entrada = Column(DateTime)
    fecha_salida = Column(DateTime)
    
    alojamiento = relationship("Alojamiento")
    cliente = relationship("Cliente")

class Servicio(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True, index=True)
    listing = Column(Integer, ForeignKey("alojamientos.listing"))
    nombre = Column(String)
    descripcion = Column(String)

class Comision(Base):
    __tablename__ = "listing_comision"
    id = Column(Integer, primary_key=True, index=True)
    listing = Column(Integer, ForeignKey("alojamientos.listing"))
    comision_porcentaje = Column(Float)

# 📌 Crear tablas en la base de datos
Base.metadata.create_all(bind=engine)

# 📌 Dependencia para obtener sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 📌 Instancia de FastAPI
app = FastAPI()

# 📌 Endpoints

@app.get("/")
def home():
    return {"mensaje": "API del Proveedor en funcionamiento 🚀"}


# 📌 Listar alojamientos
@app.get("/alojamientos")
def listar_alojamientos(db: Session = Depends(get_db)):
    return db.query(Alojamiento).all()

# 📌 Consultar disponibilidad de un alojamiento
@app.get("/disponibilidad/{id}")
def consultar_disponibilidad(id: int, db: Session = Depends(get_db)):
    alojamiento = db.query(Alojamiento).filter(Alojamiento.id == id).first()
    if not alojamiento:
        raise HTTPException(status_code=404, detail="Alojamiento no encontrado")
    return {"id": alojamiento.id, "disponible": alojamiento.disponible}

# 📌 Registrar un nuevo alojamiento
class AlojamientoRequest(BaseModel):
    nombre: str
    ubicacion: str
    disponible: bool = True

@app.post("/alojamientos")
def crear_alojamiento(alojamiento: AlojamientoRequest, db: Session = Depends(get_db)):
    nuevo_alojamiento = Alojamiento(nombre=alojamiento.nombre, ubicacion=alojamiento.ubicacion, disponible=alojamiento.disponible)
    db.add(nuevo_alojamiento)
    db.commit()
    db.refresh(nuevo_alojamiento)
    return nuevo_alojamiento

# 📌 Registrar un cliente
class ClienteRequest(BaseModel):
    nombre: str
    email: str

@app.post("/clientes")
def crear_cliente(cliente: ClienteRequest, db: Session = Depends(get_db)):
    nuevo_cliente = Cliente(nombre=cliente.nombre, email=cliente.email)
    db.add(nuevo_cliente)
    db.commit()
    db.refresh(nuevo_cliente)
    return nuevo_cliente

# 📌 Hacer una reserva
class ReservaRequest(BaseModel):
    alojamiento_id: int
    cliente_id: int
    fecha_estancia: str  # formato "YYYY-MM-DD"

@app.post("/reservar")
def hacer_reserva(reserva: ReservaRequest, db: Session = Depends(get_db)):
    alojamiento = db.query(Alojamiento).filter(Alojamiento.id == reserva.alojamiento_id).first()
    if not alojamiento or not alojamiento.disponible:
        raise HTTPException(status_code=400, detail="Alojamiento no disponible")

    nueva_reserva = Reserva(
        alojamiento_id=reserva.alojamiento_id,
        cliente_id=reserva.cliente_id,
        fecha_estancia=datetime.datetime.strptime(reserva.fecha_estancia, "%Y-%m-%d"),
    )
    
    db.add(nueva_reserva)
    db.commit()
    db.refresh(nueva_reserva)
    
    return {"mensaje": "Reserva confirmada", "detalles": nueva_reserva}

# 📌 Obtener todas las reservas
@app.get("/reservas")
def listar_reservas(db: Session = Depends(get_db)):
    return db.query(Reserva).all()
