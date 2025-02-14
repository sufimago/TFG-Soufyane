from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, Float, DateTime, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
import datetime

# 📌 Configuración de SQLite
DATABASE_URL = "sqlite:///./proveedor.db"  
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

listing_seq = Sequence('listing_seq', start=9000, increment=1)

# 📌 Modelos de Base de Datos
class Alojamiento(Base):
    __tablename__ = "alojamientos"
    listing = Column(Integer, listing_seq, primary_key=True, index=True)  
    nombre = Column(String, index=True)
    direccion = Column(String)
    ciudad = Column(String)
    pais = Column(String)
    imagen_id = Column(Integer, ForeignKey("images.id"), nullable=True)
    disponible = Column(Boolean, default=True)

class Image(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True, autoincrement=True) 
    listing_id = Column(Integer, ForeignKey("alojamientos.listing"))
    link = Column(String)

class ListingCommission(Base):
    __tablename__ = "listing_commission"
    id = Column(Integer, primary_key=True, autoincrement=True) 
    listing_id = Column(Integer, ForeignKey("alojamientos.listing"))
    commission = Column(Float)

class ListingService(Base):
    __tablename__ = "listing_services"
    id = Column(Integer, primary_key=True, autoincrement=True)  
    listing_id = Column(Integer, ForeignKey("alojamientos.listing"))
    name = Column(String)
    description = Column(String)

class Cliente(Base):
    __tablename__ = "clientes"
    id = Column(Integer, primary_key=True, autoincrement=True)  
    nombre = Column(String, index=True)
    email = Column(String, unique=True, index=True)

class Reserva(Base):
    __tablename__ = "reservas"
    id = Column(Integer, primary_key=True, autoincrement=True) 
    listing_id = Column(Integer, ForeignKey("alojamientos.listing"))
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    fecha_reserva = Column(DateTime, default=datetime.datetime.now)
    fecha_entrada = Column(DateTime)
    fecha_salida = Column(DateTime)

Base.metadata.create_all(bind=engine)

# 📌 Dependencia de Base de Datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 📌 Instancia de FastAPI
app = FastAPI()

# 📌 Modelos Pydantic para validación de los datos

class AlojamientoCreate(BaseModel):
    nombre: str
    direccion: str
    ciudad: str
    pais: str
    imagen_id: int  # Puede ser None si no hay imagen
    disponible: bool = True  # Agregado parámetro disponible

class ImageCreate(BaseModel):
    listing_id: int
    link: str

class ListingCommissionCreate(BaseModel):
    listing_id: int
    commission: float

class ListingServiceCreate(BaseModel):
    listing_id: int
    name: str
    description: str

class ClienteCreate(BaseModel):
    nombre: str
    email: str

class ReservaCreate(BaseModel):
    listing_id: int
    cliente_id: int
    fecha_entrada: datetime.datetime
    fecha_salida: datetime.datetime


# 📌 ENDPOINTS

# Página principal healthcheck
@app.get("/")
def read_root():
    return {"status": "OK"}

# Endpoint para crear un alojamiento
@app.post("/listings")
def crear_alojamiento(alojamiento: AlojamientoCreate, db: Session = Depends(get_db)):
    nuevo_alojamiento = Alojamiento(
        nombre=alojamiento.nombre,
        direccion=alojamiento.direccion,
        ciudad=alojamiento.ciudad,
        pais=alojamiento.pais,
        imagen_id=alojamiento.imagen_id,
        disponible=alojamiento.disponible
    )
    
    try:
        db.add(nuevo_alojamiento)
        db.commit()
        db.refresh(nuevo_alojamiento)
        return {"mensaje": "Alojamiento creado exitosamente", "alojamiento": nuevo_alojamiento}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear el alojamiento: {str(e)}")

# Endpoint para crear una imagen
@app.post("/images")
def crear_imagen(imagen: ImageCreate, db: Session = Depends(get_db)):
    nueva_imagen = Image(
        listing_id=imagen.listing_id,
        link=imagen.link
    )
    
    try:
        db.add(nueva_imagen)
        db.commit()
        db.refresh(nueva_imagen)
        return {"mensaje": "Imagen creada exitosamente", "imagen": nueva_imagen}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear la imagen: {str(e)}")


# Endpoint para crear una comisión de un alojamiento
@app.post("/listing_commissions")
def crear_comision(comision: ListingCommissionCreate, db: Session = Depends(get_db)):
    nueva_comision = ListingCommission(
        listing_id=comision.listing_id,
        commission=comision.commission
    )
    
    try:
        db.add(nueva_comision)
        db.commit()
        db.refresh(nueva_comision)
        return {"mensaje": "Comisión creada exitosamente", "comision": nueva_comision}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear la comisión: {str(e)}")


# Endpoint para crear un servicio de un alojamiento
@app.post("/listing_services")
def crear_servicio(servicio: ListingServiceCreate, db: Session = Depends(get_db)):
    nuevo_servicio = ListingService(
        listing_id=servicio.listing_id,
        name=servicio.name,
        description=servicio.description
    )
    
    try:
        db.add(nuevo_servicio)
        db.commit()
        db.refresh(nuevo_servicio)
        return {"mensaje": "Servicio creado exitosamente", "servicio": nuevo_servicio}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear el servicio: {str(e)}")


# Endpoint para crear un cliente
@app.post("/clientes")
def crear_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    nuevo_cliente = Cliente(
        nombre=cliente.nombre,
        email=cliente.email
    )
    
    try:
        db.add(nuevo_cliente)
        db.commit()
        db.refresh(nuevo_cliente)
        return {"mensaje": "Cliente creado exitosamente", "cliente": nuevo_cliente}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear el cliente: {str(e)}")


# Endpoint para crear una reserva
@app.post("/reservas")
def crear_reserva(reserva: ReservaCreate, db: Session = Depends(get_db)):
    nueva_reserva = Reserva(
        listing_id=reserva.listing_id,
        cliente_id=reserva.cliente_id,
        fecha_entrada=reserva.fecha_entrada,
        fecha_salida=reserva.fecha_salida
    )
    
    try:
        db.add(nueva_reserva)
        db.commit()
        db.refresh(nueva_reserva)
        return {"mensaje": "Reserva creada exitosamente", "reserva": nueva_reserva}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear la reserva: {str(e)}")

# Endpoint para obtener todos los alojamientos
@app.get("/listings")
def obtener_alojamientos(db: Session = Depends(get_db)):
    try:
        alojamientos = db.query(Alojamiento).all()
        if not alojamientos:
            raise HTTPException(status_code=404, detail="No hay alojamientos disponibles")
        return alojamientos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener alojamientos: {str(e)}")

# Endpoint para obtener todos los listings activos
@app.get("/listings/actives")
def obtener_alojamientos(db: Session = Depends(get_db)):
    try:
        alojamientos = db.query(Alojamiento).filter(Alojamiento.disponible == True).all()
        if not alojamientos:
            raise HTTPException(status_code=404, detail="No hay alojamientos disponibles")
        return alojamientos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener alojamientos: {str(e)}")

# Endpoint para obtener todos los listings inactivos
@app.get("/listings/inactives")
def obtener_alojamientos(db: Session = Depends(get_db)):
    try:
        alojamientos = db.query(Alojamiento).filter(Alojamiento.disponible == False).all()
        if not alojamientos:
            raise HTTPException(status_code=404, detail="No hay alojamientos disponibles")
        return alojamientos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener alojamientos: {str(e)}")

# Endpoint para obtener los listings solo el id
@app.get("/listings/id")
def obtener_alojamientos(db: Session = Depends(get_db)):
    try:
        alojamientos = db.query(Alojamiento.listing).all()
        if not alojamientos:
            raise HTTPException(status_code=404, detail="No hay alojamientos disponibles")
        
        return [a[0] for a in alojamientos]  # Extraer los valores de la tupla
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener alojamientos: {str(e)}")


# Endpoint para obtener los detalles de un alojamiento
@app.get("/listings/{hotCodigo}")
def obtener_alojamiento(hotCodigo: int, db: Session = Depends(get_db)):
    alojamiento = db.query(Alojamiento).filter(Alojamiento.listing == hotCodigo).first()
    if not alojamiento:
        raise HTTPException(status_code=404, detail="Alojamiento no encontrado")
    return alojamiento

# Endpoint para obtener las imágenes de un alojamiento
@app.get("/listings/{hotCodigo}/images")
def obtener_imagenes(hotCodigo: int, db: Session = Depends(get_db)):
    imagenes = db.query(Image).filter(Image.listing_id == hotCodigo).all()
    return imagenes if imagenes else {"mensaje": "No hay imágenes disponibles"}

# Endpoint para obtener la comisión de un alojamiento
@app.get("/listings/{hotCodigo}/commission")
def obtener_comision(hotCodigo: int, db: Session = Depends(get_db)):
    comision = db.query(ListingCommission).filter(ListingCommission.listing_id == hotCodigo).first()
    if not comision:
        raise HTTPException(status_code=404, detail="Comisión no encontrada")
    return comision

# Endpoint para obtener los servicios de un alojamiento
@app.get("/listings/{hotCodigo}/services")
def obtener_servicios(hotCodigo: int, db: Session = Depends(get_db)):
    servicios = db.query(ListingService).filter(ListingService.listing_id == hotCodigo).all()
    return servicios if servicios else {"mensaje": "No hay servicios disponibles"}

# Endpoint para obtener un cliente por su ID
@app.get("/clientes/{cliente_id}")
def obtener_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente

# Endpoint para obtener una reserva por su ID
@app.get("/reservas/{reserva_id}")
def obtener_reserva(reserva_id: int, db: Session = Depends(get_db)):
    reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    return reserva

# Endpoint para obtener todas las reservas de un cliente
@app.get("/clientes/{cliente_id}/reservas")
def obtener_reservas_cliente(cliente_id: int, db: Session = Depends(get_db)):
    reservas = db.query(Reserva).filter(Reserva.cliente_id == cliente_id).all()
    return reservas if reservas else {"mensaje": "No hay reservas para este cliente"}

# Endpoint para obtener todas las reservas de un alojamiento
@app.get("/listings/{hotCodigo}/reservas")
def obtener_reservas_alojamiento(hotCodigo: int, db: Session = Depends(get_db)):
    reservas = db.query(Reserva).filter(Reserva.listing_id == hotCodigo).all()
    return reservas if reservas else {"mensaje": "No hay reservas para este alojamiento"}
