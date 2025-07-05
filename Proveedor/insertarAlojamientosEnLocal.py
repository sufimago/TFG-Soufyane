from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Ruta absoluta a la base de datos del proveedor
engine_provider = create_engine("sqlite:///./proveedor.db", connect_args={"check_same_thread": False})
SessionProvider = sessionmaker(bind=engine_provider)
session_provider = SessionProvider()

# Ruta absoluta a la base de datos del backend (sin .db si no lo tienes)
engine_local = create_engine(r"sqlite:///C:\Users\soufyane.youbi\Desktop\TFG\Back TFG\SBEN\baseDeDatoBack", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine_local)
session_local = SessionLocal()

# Crear tabla si no existe en la base de datos local
with engine_local.connect() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS alojamientos (
            hotCodigo INTEGER PRIMARY KEY AUTOINCREMENT,
            ciudad TEXT,
            imagen_id INTEGER,
            disponible BOOLEAN,
            occupants INTEGER,
            direccion TEXT,
            listing INTEGER UNIQUE,
            nombre TEXT,
            pais TEXT
        );
    """))
    print("✅ Tabla 'alojamientos' verificada/creada en base local.")

# Obtener listings ya existentes en la base local para evitar duplicados
existing_listings = session_local.execute(text("SELECT listing FROM alojamientos")).fetchall()
existing_listing_ids = {row[0] for row in existing_listings}

# Leer alojamientos desde proveedor
alojamientos = session_provider.execute(text("SELECT listing, nombre, direccion, ciudad, pais, imagen_id, disponible, price, occupants FROM alojamientos")).fetchall()

# Insertar solo los nuevos
insert_count = 0
for alojamiento in alojamientos:
    if alojamiento.listing in existing_listing_ids:
        continue  # Ya existe, no insertar

    insert_sql = text("""
        INSERT INTO alojamientos (ciudad, imagen_id, disponible, occupants, direccion, listing, nombre, pais)
        VALUES (:ciudad, :imagen_id, :disponible, :occupants, :direccion, :listing, :nombre, :pais)
    """)
    session_local.execute(insert_sql, {
        "ciudad": alojamiento.ciudad,
        "imagen_id": alojamiento.imagen_id,
        "disponible": alojamiento.disponible,
        "occupants": alojamiento.occupants,
        "direccion": alojamiento.direccion,
        "listing": alojamiento.listing,
        "nombre": alojamiento.nombre,
        "pais": alojamiento.pais
    })
    insert_count += 1

session_local.commit()
print(f"✅ Se insertaron {insert_count} nuevos alojamientos.")
session_provider.close()
session_local.close()
