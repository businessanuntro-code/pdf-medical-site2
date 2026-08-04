import requests


def publish_article(data):

    url = "https://diaconu-daniel.ro/api/import.php"

    response = requests.post(
        url,
        json=data
    )

    response.raise_for_status()

    return response.json()
