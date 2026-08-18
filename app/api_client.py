import requests


def publish_article(data):

    url = "https://diaconu-daniel.ro/api/import.php"

    headers = {
        "X-API-Key": "MEDICHUB_SECRET_2026"
    }

    response = requests.post(
        url,
        json=data,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    return response.json()
