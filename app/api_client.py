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

    
    print("===== SCIENTIFIC API DEBUG =====")
    print("STATUS:", response.status_code)
    print("URL:", response.url)
    print("CONTENT-TYPE:", response.headers.get("content-type"))
    print("RESPONSE:", response.text[:5000])
    print("================================")
    return response.json()
