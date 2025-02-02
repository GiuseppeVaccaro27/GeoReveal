from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

def get_gps_metadata(file_path):
    """
    Estrae i metadati GPS da un'immagine.
    
    :param file_path: Percorso del file immagine.
    :return: Un dizionario con le coordinate GPS (latitudine e longitudine) o None se non disponibile.
    """
    try:
        image = Image.open(file_path)
        exif_data = image._getexif()
        
        if not exif_data:
            return None
        
        gps_info = {}
        for tag, value in exif_data.items():
            tag_name = TAGS.get(tag)
            if tag_name == "GPSInfo":
                for gps_tag, gps_value in value.items():
                    gps_tag_name = GPSTAGS.get(gps_tag, gps_tag)
                    gps_info[gps_tag_name] = gps_value

        if "GPSLatitude" in gps_info and "GPSLongitude" in gps_info:
            latitude = convert_to_degrees(gps_info["GPSLatitude"])
            if gps_info.get("GPSLatitudeRef") == "S":
                latitude = -latitude

            longitude = convert_to_degrees(gps_info["GPSLongitude"])
            if gps_info.get("GPSLongitudeRef") == "W":
                longitude = -longitude

            return {"latitude": latitude, "longitude": longitude}
        else:
            return None
    except Exception as e:
        print(f"Errore nell'estrazione dei metadati GPS: {e}")
        return None

def convert_to_degrees(value):
    """
    Converte il valore GPS in gradi decimali.
    
    :param value: Valore GPS in formato (gradi, minuti, secondi).
    :return: Valore in gradi decimali.
    """
    d, m, s = value
    return d + (m / 60.0) + (s / 3600.0)


import folium
import webbrowser

def create_map(gps_data_list):
    """
    Crea una mappa centrata sulla posizione media delle foto selezionate
    e aggiunge i marcatori per ogni foto.
    
    :param gps_data_list: Lista di tuple (foto, dati GPS).
    """
    if not gps_data_list:
        print("Nessun dato GPS disponibile.")
        return

    # Calcolare la posizione media
    latitudes = [data['latitude'] for _, data in gps_data_list]
    longitudes = [data['longitude'] for _, data in gps_data_list]
    
    # Media delle latitudini e longitudini
    avg_latitude = sum(latitudes) / len(latitudes)
    avg_longitude = sum(longitudes) / len(longitudes)
    
    # Calcolare la distanza tra i punti più lontani per determinare il livello di zoom
    # Puoi usare la distanza euclidea o una formula di distanza geografica più precisa (Haversine)
    max_lat = max(latitudes)
    min_lat = min(latitudes)
    max_lon = max(longitudes)
    min_lon = min(longitudes)
    
    # Calcolare la distanza approssimativa tra i punti più lontani
    lat_diff = max_lat - min_lat
    lon_diff = max_lon - min_lon
    
    # Impostare un livello di zoom in base alla dispersione dei punti
    zoom_level = 12
    if lat_diff > 1 or lon_diff > 1:
        zoom_level = 10  # Zoom out se i punti sono distanti
    elif lat_diff < 0.1 and lon_diff < 0.1:
        zoom_level = 14  # Zoom in se i punti sono vicini

    # Crea una mappa centrata sulla posizione media
    map_center = [avg_latitude, avg_longitude]
    m = folium.Map(location=map_center, zoom_start=zoom_level)

    # Aggiungi marcatori per ogni foto
    for photo, gps_data in gps_data_list:
        folium.Marker(
            location=[gps_data['latitude'], gps_data['longitude']],
            popup=f"Foto: {photo}\nLat: {gps_data['latitude']}\nLon: {gps_data['longitude']}",
            icon=folium.Icon(color='blue')
        ).add_to(m)

    # Salva la mappa in un file HTML
    map_filename = "map.html"
    m.save(map_filename)

    # Apri la mappa nel browser
    webbrowser.open(map_filename)

