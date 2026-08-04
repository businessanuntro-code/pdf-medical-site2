import requests


def publish_article(data):

    url = "URL_API_IMPORT"

    response = requests.post(
        url,
        json=data
    )

    response.raise_for_status()

    return response.json()
