from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from faker import Faker
import random
from testApi import SessionLocal, Alojamiento, Image, ListingCommission, ListingService

# Inicializar Faker
fake = Faker()

# Establecer conexión a la base de datos y crear SessionLocal
DATABASE_URL = "sqlite:///./proveedor.db"  
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Función para generar Alojamiento
def generar_alojamiento(db: Session, cantidad: int):
    for _ in range(cantidad):
        alojamiento = Alojamiento(
            nombre=fake.company(),
            direccion=fake.address(),
            ciudad=fake.city(),
            pais=fake.country(),
            disponible=random.choice([True, False])  # Aleatorio entre True y False
        )
        db.add(alojamiento)
    db.commit()

# Función para generar Imágenes
def generar_imagenes(db: Session, cantidad: int):
    alojamientos = db.query(Alojamiento).all()
    for _ in range(cantidad):
        alojamiento = random.choice(alojamientos)
        imagen = Image(
            listing_id=alojamiento.listing,
            link=fake.image_url()
        )
        db.add(imagen)
    db.commit()

# Función para generar Comisiones
def generar_comisiones(db: Session, cantidad: int):
    alojamientos = db.query(Alojamiento).all()
    for _ in range(cantidad):
        alojamiento = random.choice(alojamientos)
        comision = ListingCommission(
            listing_id=alojamiento.listing,
            commission=random.uniform(5.0, 30.0)  # Comisiones entre 5% y 30%
        )
        db.add(comision)
    db.commit()

# Función para generar Servicios
def generar_servicios(db: Session, cantidad: int):
    alojamientos = db.query(Alojamiento).all()
    for _ in range(cantidad):
        alojamiento = random.choice(alojamientos)
        servicio = ListingService(
            listing_id=alojamiento.listing,
            name=fake.word(),
            description=fake.sentence()
        )
        db.add(servicio)
    db.commit()

# Función para generar todos los datos
def generar_datos(db: Session, cantidad: int):
    generar_alojamiento(db, cantidad)
    generar_imagenes(db, cantidad)
    generar_comisiones(db, cantidad)
    generar_servicios(db, cantidad)
    print(f"{cantidad} registros generados exitosamente.")

# Llamada a la función para generar datos
if __name__ == "__main__":
    db = SessionLocal()  # Iniciar una sesión de base de datos
    generar_datos(db, 500)  # Generar 500 registros por cada tabla
