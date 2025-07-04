from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import random
from datetime import datetime
from main import SessionLocal, seasonalPrices, Alojamiento

# Establecer conexión a la base de datos
DATABASE_URL = "sqlite:///./proveedor.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def generateSeasonalPrices(db: Session):
    target_years = [2025, 2026]

    # Temporadas por año
    def get_seasons(year):
        return [
            ("Winter", datetime(year, 1, 1), datetime(year, 3, 31), (100, 130)),
            ("Spring", datetime(year, 4, 1), datetime(year, 6, 30), (120, 150)),
            ("Summer", datetime(year, 7, 1), datetime(year, 9, 30), (140, 175)),
            ("Fall", datetime(year, 10, 1), datetime(year, 12, 31), (110, 140))
        ]

    # Obtener IDs de alojamientos que ya tienen precios
    listings_with_prices = {
        s.listing for s in db.query(seasonalPrices.listing).distinct().all()
    }

    # Obtener solo los nuevos alojamientos sin precios
    new_listings = [
        alojamiento.listing for alojamiento in db.query(Alojamiento).all()
        if alojamiento.listing not in listings_with_prices
    ]

    print(f"🏠 Nuevos alojamientos detectados: {len(new_listings)}")

    for listing in new_listings:
        for year in target_years:
            for season, start_date, end_date, price_range in get_seasons(year):
                price = seasonalPrices(
                    listing=listing,
                    price=round(random.uniform(*price_range), 2),
                    start_date=start_date,
                    end_date=end_date
                )
                db.add(price)

    db.commit()
    print(f"✅ Precios estacionales insertados para {len(new_listings)} alojamientos.")

if __name__ == "__main__":
    db = SessionLocal()
    generateSeasonalPrices(db)
    db.close()
