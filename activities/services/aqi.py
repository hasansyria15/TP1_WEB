import os
import urllib.request
import json


def get_air_quality(city=None):
    token = os.getenv("AQICN_TOKEN")
    if not token:
        raise ValueError("Le token AQICN n'est pas défini")

    # Construire l'URL en fonction de la ville ou de la localisation actuelle
    if city:
        url = f'https://api.waqi.info/feed/{city}/?token={token}'
    else:
        url = f'https://api.waqi.info/feed/here/?token={token}'

    try:
        res = urllib.request.urlopen(url)
        data = json.loads(res.read())

        # Vérifier le statut de la réponse
        if data.get("status") != "ok":
            error_message = data.get("data", "Erreur inconnue")
            raise ValueError(f"Erreur API AQI: {error_message}")

        # Vérifier si les données AQI sont disponibles (utile si la ville n'est pas trouvée)
        if "data" not in data or "aqi" not in data["data"]:
            raise ValueError("Données AQI non disponibles pour cette localisation ou ville")

        return data
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise ValueError("Ville non trouvée ou données indisponibles") from e
        else:
            raise ValueError(f"Erreur HTTP lors de la récupération des données AQI: {e}") from e
    except urllib.error.URLError as e:
        raise ValueError(f"Erreur de réseau lors de la récupération des données AQI: {e}") from e
    except json.JSONDecodeError as e:
        raise ValueError(f"Erreur de décodage JSON: {e}") from e
    except Exception as e:
        raise ValueError(f"Erreur inattendue lors de la récupération des données AQI: {e}") from e
