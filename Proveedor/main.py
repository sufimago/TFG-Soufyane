from random import randint
import random
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
    occupants = Column(Integer, default=1)
    seasonal_prices = relationship("seasonalPrices", backref="alojamiento")

class PoliticaCancelacion(Base):
    __tablename__ = "politicas_cancelacion"
    id = Column(Integer, primary_key=True, autoincrement=True)
    dias_antes_cancelacion = Column(Integer, nullable=False)  # Por ejemplo: 7, 3, 1
    porcentaje_penalizacion = Column(Float, nullable=False)   # Porcentaje: 0.25, 0.5, 1.0    

class seasonalPrices(Base):
    __tablename__ = "seasonal_prices"
    id = Column(Integer, primary_key=True, autoincrement=True) 
    listing = Column(Integer, ForeignKey("alojamientos.listing"))
    price = Column(Float)
    start_date = Column(DateTime)    
    end_date = Column(DateTime)

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
    localizador = Column(Integer, unique=True, index=True)  # Localizador único para la reserva

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
    occupants: int = 1  # Agregado parámetro occupants

class SeasonalPricesCreate(BaseModel):
    listing: int
    price: float
    start_date: datetime.datetime    
    end_date: datetime.datetime

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
    nuevo_alojamiento = Alojamiento(**alojamiento.dict())
    try:
        db.add(nuevo_alojamiento)
        db.commit()
        db.refresh(nuevo_alojamiento)
        return {"mensaje": "Alojamiento creado exitosamente", "alojamiento": nuevo_alojamiento}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

        

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
@app.post("/listing/Commission")
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
@app.post("/listing/services")
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
@app.post("/cliente")
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
@app.post("/reserva")
def crear_reserva(reserva: ReservaCreate, db: Session = Depends(get_db)):
    nueva_reserva = Reserva(
        listing_id=reserva.listing_id,
        cliente_id=reserva.cliente_id,
        fecha_entrada=reserva.fecha_entrada,
        fecha_salida=reserva.fecha_salida,
        localizador=reserva.localizador  # Localizador único para la reserva
    )
    
    try:
        db.add(nueva_reserva)
        db.commit()
        db.refresh(nueva_reserva)
        # Opcional: obtener datos del cliente para mostrar
        cliente = db.query(Cliente).filter(Cliente.id == reserva.cliente_id).first()

        return {
            "mensaje": "Reserva creada exitosamente",
            "reserva": nueva_reserva,
            "cliente": {"nombre": cliente.nombre, "email": cliente.email},
            "localizador": reserva.localizador
        }
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
@app.get("/listings/ids")
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


# Obtener alojamientos que no tienen reservas en un rago de fechas para la disponibilidad
@app.get("/check-availability")
def obtener_alojamiento_disponible(
    fecha_entrada: datetime.datetime, 
    fecha_salida: datetime.datetime, 
    listing_id: int,  # Solo un ID de alojamiento
    occupants: int,  # Número de personas
    db: Session = Depends(get_db)
):
    # Consultar el alojamiento específico
    alojamiento_disponible = db.query(Alojamiento).filter(
        Alojamiento.disponible == True,
        Alojamiento.listing == listing_id,  # Filtramos por el ID del alojamiento
        Alojamiento.occupants == occupants  # Verificamos la capacidad del alojamiento
    ).first()

    if not alojamiento_disponible:
        raise HTTPException(status_code=404, detail="Alojamiento no encontrado o no disponible")

    # Verificar si el alojamiento está reservado en las fechas solicitadas
    reserva_existente = db.query(Reserva).filter(
        Reserva.listing_id == alojamiento_disponible.listing,
        (Reserva.fecha_entrada < fecha_salida), 
        (Reserva.fecha_salida > fecha_entrada)
    ).first()

    # Obtener políticas de cancelación (ordenadas de mayor a menor)
    politicas = db.query(PoliticaCancelacion).order_by(PoliticaCancelacion.dias_antes_cancelacion.desc()).all()

    #Obtener la url de la imagen del alojamiento
    imagen = db.query(Image).filter(Image.listing_id == alojamiento_disponible.listing).first()

    if reserva_existente:
        raise HTTPException(status_code=404, detail="El alojamiento no está disponible en estas fechas")

    # Obtener precios de temporada para el alojamiento específico
    precios = db.query(seasonalPrices).filter(
        seasonalPrices.listing == alojamiento_disponible.listing,
        seasonalPrices.start_date <= fecha_salida,
        seasonalPrices.end_date >= fecha_entrada
    ).all()

    if not precios:
        raise HTTPException(status_code=404, detail="No hay precios disponibles para estas fechas")

    # Calcular el precio total de la estancia
    total_precio = 0
    dias_totales = (fecha_salida - fecha_entrada).days

    for dia in range(dias_totales):
        fecha_actual = fecha_entrada + datetime.timedelta(days=dia)
        for precio in precios:
            if precio.start_date <= fecha_actual <= precio.end_date:
                total_precio += precio.price
                break  # Tomamos el primer precio válido para esa fecha        

    # Devolver el resultado
    return {
        "alojamiento": alojamiento_disponible,
        "precio_por_dia": total_precio / dias_totales,
        "ocupantes": occupants,
        "imagen": imagen.link if imagen else None,
        "politicas_cancelacion": [
        {
            "dias_antes": p.dias_antes_cancelacion,
            "penalizacion": p.porcentaje_penalizacion
        } for p in politicas
    ]
    }

@app.get("/quote")
def cotizar_alojamiento(
    fecha_entrada: datetime.datetime,
    fecha_salida: datetime.datetime,
    listing_id: int,
    num_personas: int,
    db: Session = Depends(get_db)
):
    alojamiento = db.query(Alojamiento).filter(Alojamiento.listing == listing_id, Alojamiento.disponible == True).first()
    if not alojamiento:
        raise HTTPException(status_code=404, detail="Alojamiento no encontrado o no disponible")

    if num_personas > alojamiento.occupants:
        raise HTTPException(status_code=400, detail=f"El alojamiento solo permite hasta {alojamiento.occupants} personas")

    reserva_existente = db.query(Reserva).filter(
        Reserva.listing_id == alojamiento.listing,
        (Reserva.fecha_entrada < fecha_salida), 
        (Reserva.fecha_salida > fecha_entrada)
    ).first()
    
    politicas = db.query(PoliticaCancelacion).order_by(PoliticaCancelacion.dias_antes_cancelacion.desc()).all()

    # Obtener la url de la imagen del alojamiento
    imagen = db.query(Image).filter(Image.listing_id == alojamiento.listing).first()


    if reserva_existente:
        raise HTTPException(status_code=400, detail="El alojamiento no está disponible en estas fechas")

    precios = db.query(seasonalPrices).filter(
        seasonalPrices.listing == alojamiento.listing,
        seasonalPrices.start_date <= fecha_salida,
        seasonalPrices.end_date >= fecha_entrada
    ).all()

    if not precios:
        raise HTTPException(status_code=404, detail="No hay precios disponibles para estas fechas")

    total_precio = 0
    dias_totales = (fecha_salida - fecha_entrada).days

    for dia in range(dias_totales):
        fecha_actual = fecha_entrada + datetime.timedelta(days=dia)
        for precio in precios:
            if precio.start_date <= fecha_actual <= precio.end_date:
                total_precio += precio.price
                break  

    return {
    "alojamiento": alojamiento,
    "precio_total": total_precio,
    "precio_por_dia": total_precio / dias_totales,
    "num_personas": num_personas,
    "imagen": imagen.link if imagen else None,
    "politicas_cancelacion": [
        {
            "dias_antes": p.dias_antes_cancelacion,
            "penalizacion": p.porcentaje_penalizacion
        } for p in politicas
    ]
}

@app.post("/confirm")
def confirmar_reserva(
    data: ReservaCreate,
    db: Session = Depends(get_db)
):
    # Verificar alojamiento
    alojamiento = db.query(Alojamiento).filter(
        Alojamiento.disponible == True,
        Alojamiento.listing == data.listing_id
    ).first()

    if not alojamiento:
        raise HTTPException(status_code=404, detail="Alojamiento no disponible")

    # Verificar que no haya reservas en el rango
    reserva_existente = db.query(Reserva).filter(
        Reserva.listing_id == data.listing_id,
        (Reserva.fecha_entrada < data.fecha_salida), 
        (Reserva.fecha_salida > data.fecha_entrada)
    ).first()

    if reserva_existente:
        raise HTTPException(status_code=400, detail="El alojamiento ya está reservado en ese rango de fechas")

    # Obtener precios
    precios = db.query(seasonalPrices).filter(
        seasonalPrices.listing == data.listing_id,
        seasonalPrices.start_date <= data.fecha_salida,
        seasonalPrices.end_date >= data.fecha_entrada
    ).all()

    if not precios:
        raise HTTPException(status_code=404, detail="No hay precios para este alojamiento en estas fechas")

    dias_totales = (data.fecha_salida - data.fecha_entrada).days
    total_precio = 0

    for dia in range(dias_totales):
        fecha_actual = data.fecha_entrada + datetime.timedelta(days=dia)
        for precio in precios:
            if precio.start_date <= fecha_actual <= precio.end_date:
                total_precio += precio.price
                break

    localizador = generar_localizador_unico(db)            
    nueva_reserva = Reserva(
        listing_id=data.listing_id,
        cliente_id=data.cliente_id,
        fecha_entrada=data.fecha_entrada,
        fecha_salida=data.fecha_salida,
        localizador = localizador  # Localizador único para la reserva
    )

    try:
        db.add(nueva_reserva)
        db.commit()
        db.refresh(nueva_reserva)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al confirmar la reserva: {str(e)}")

    # select alojamiento desde base de datos
    alojamiento = db.query(Alojamiento).filter(Alojamiento.listing == data.listing_id).first()
    cliente = db.query(Cliente).filter(Cliente.id == data.cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    return {
        "mensaje": "Reserva confirmada exitosamente",
        "reserva": {
            "alojamiento_id": data.listing_id,
            "cliente_id": data.cliente_id,
            "fecha_entrada": data.fecha_entrada,
            "fecha_salida": data.fecha_salida,
            "localizador": localizador,
            "precio_total": total_precio,
            "precio_por_dia": total_precio / dias_totales,
            "información alojamiento": alojamiento,
            "información cliente": {
                "nombre": cliente.nombre,  
                "email": cliente.email
            },
            "localizador": localizador
        }
    }

def generar_localizador_unico(db: Session):
    while True:
        localizador = randint(100000, 9999999)
        existe = db.query(Reserva).filter(Reserva.localizador == localizador).first()
        if not existe:
            return localizador


# Endpoint para eliminar la informacion de imagenes de un alojamiento
@app.delete("/images/{image_id}")
def eliminar_imagen(image_id: int, db: Session = Depends(get_db)):
    imagen = db.query(Image).filter(Image.id == image_id).first()
    if not imagen:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")
    
    try:
        db.delete(imagen)
        db.commit()
        return {"mensaje": "Imagen eliminada exitosamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar la imagen: {str(e)}")
    

@app.post("/listing/prices")
def crear_precio(precio: SeasonalPricesCreate, db: Session = Depends(get_db)):
    nuevo_precio = seasonalPrices(
        listing=precio.listing,
        price=precio.price,
        start_date=precio.start_date,
        end_date=precio.end_date
    )
    try:
        db.add(nuevo_precio)
        db.commit()
        db.refresh(nuevo_precio)
        return {"mensaje": "Precio de temporada creado exitosamente", "precio": nuevo_precio}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear el precio: {str(e)}")
