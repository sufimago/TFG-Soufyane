import requests
import json
import random  # importa la función random correctamente

# Lista de imágenes disponibles
images = [
    "https://veigler.com/wp-content/uploads/2019/07/alojamientos.jpg",
    "https://www.fundacionlengua.com/extra/imagenes/img_16/LosAlojamiento.jpg",
    "https://alojamientoscentral.com/wp-content/uploads/2021/11/HabitacionDoble-scaled.jpg",
    "https://grupomarbo.com/wp-content/uploads/2022/06/portada-resort.jpg",
    "https://www.mallorca.es/documents/43575/59098/Cabecera_Alojamientos.jpg/d96f2754-5851-2835-5b4a-260443837b68?version=1.2&t=1587460027678",
    "https://estaticos.turiaventura.com/images/alojamientos/alojamiento-rural/1571x1182/alojamiento-rural-galeria8.jpg",
    "https://www.caminodosfaros.com/wp-content/uploads/2014/01/105-habitacion_clasica_01-672x372.jpg",
    "https://fotoalquiler.com/fotos/casaverde/la-rioja-casaverde.jpg",
    "https://www.mammaproof.org/barcelona/wp-content/uploads/sites/11/2023/05/cal-carulla-portada-min-1180x885-1180x885-1-1180x885.jpg"
]

# Obtener los listings
url_listings = "http://13.38.12.142/listings"
response = requests.get(url_listings)

if response.status_code == 200:
    listings = response.json()

    for listing in listings:
        listing_id = listing.get("listing")

        # Seleccionar imagen aleatoria
        image_link = random.choice(images)

        # Construir payload
        payload = {
            "listing_id": listing_id,
            "link": image_link
        }

        # Hacer POST a /images
        url_images = "http://13.38.12.142/images"
        headers = {'Content-Type': 'application/json'}
        post_response = requests.post(url_images, headers=headers, data=json.dumps(payload))

        if post_response.status_code == 200:
            print(f"Imagen insertada correctamente en listing {listing_id}")
        else:
            print(f"Error al insertar imagen en listing {listing_id}: {post_response.text}")
else:
    print(f"Error al obtener listings: {response.status_code} - {response.text}")