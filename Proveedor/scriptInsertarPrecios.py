from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import random
from datetime import datetime
from testApi import SessionLocal, seasonalPrices, Alojamiento

# Establecer conexión a la base de datos y crear SessionLocal
DATABASE_URL = "sqlite:///./proveedor.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def generateSeasonalPrices(db: Session):
    seasons = [
        ("Winter", datetime(2025, 1, 1), datetime(2025, 3, 31), (100, 130)),
        ("Spring", datetime(2025, 4, 1), datetime(2025, 6, 30), (120, 150)),
        ("Summer", datetime(2025, 7, 1), datetime(2025, 9, 30), (140, 175)),
        ("Fall", datetime(2025, 10, 1), datetime(2025, 12, 31), (110, 140))
    ]
    
    listings = [listing[0] for listing in db.query(Alojamiento.listing).all()]
    
    for listing in listings:
        for season, start_date, end_date, price_range in seasons:
            price = seasonalPrices(
                listing=listing,
                price=random.uniform(*price_range),
                start_date=start_date,
                end_date=end_date
            )
            db.add(price)
    
    db.commit()

def printPricesForListing():
    alojamiento = db.query(Alojamiento).filter(Alojamiento.listing == 9001).first()
    if alojamiento:
        for precio in alojamiento.seasonal_prices:
            print(f"Precio: {precio.price}, Desde: {precio.start_date}, Hasta: {precio.end_date}")


if __name__ == "__main__":
    db = SessionLocal()
    generateSeasonalPrices(db)
    #test()
    db.close()