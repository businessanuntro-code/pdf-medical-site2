import requests


def publish_article(data):

    url = "https://diaconu-daniel.ro/api/import.php"

    headers = {
        "X-API-Key": "MEDICHUB_SECRET_2026",
        "Accept": "application/json",
        "User-Agent": "MedichubRender/1.0"
    }

    print("")
    print("==============================================")
    print("===== SCIENTIFIC API REQUEST DEBUG =====")
    print("==============================================")
    print("URL:", url)
    print("METHOD: POST")
    print("HEADERS:", {
        "X-API-Key": "***HIDDEN***",
        "Accept": headers["Accept"],
        "User-Agent": headers["User-Agent"]
    })

    try:

        response = requests.post(
            url,
            json=data,
            headers=headers,
            timeout=30,
            allow_redirects=False
        )

        print("")
        print("===== RESPONSE =====")
        print("STATUS:", response.status_code)
        print("URL:", response.url)
        print("CONTENT-TYPE:", response.headers.get("Content-Type"))
        print("SERVER:", response.headers.get("Server"))
        print("LOCATION:", response.headers.get("Location"))
        print("CF-RAY:", response.headers.get("CF-Ray"))
        print("VIA:", response.headers.get("Via"))
        print("X-CACHE:", response.headers.get("X-Cache"))
        print("X-FIREWALL:", response.headers.get("X-Firewall"))

        print("")
        print("===== ALL RESPONSE HEADERS =====")

        for key, value in response.headers.items():
            print(f"{key}: {value}")

        print("")
        print("===== RESPONSE BODY =====")

        # Nu afișăm tot HTML-ul dacă este foarte mare.
        body = response.text

        if len(body) > 5000:
            print(body[:5000])
            print("")
            print("...[RESPONSE TRUNCATED]...")
            print("TOTAL RESPONSE LENGTH:", len(body))
        else:
            print(body)

        print("")
        print("==============================================")
        print("===== END SCIENTIFIC API DEBUG =====")
        print("==============================================")
        print("")

        # Încercăm JSON doar dacă serverul chiar declară JSON.
        content_type = response.headers.get(
            "Content-Type",
            ""
        ).lower()

        if "application/json" in content_type:

            try:
                return response.json()

            except ValueError:

                print("ERROR: Content-Type este JSON, dar răspunsul nu este JSON valid.")

                return {
                    "success": False,
                    "message": "API a returnat JSON invalid.",
                    "status_code": response.status_code,
                    "response_text": response.text[:2000]
                }

        # Dacă primim HTML / challenge / alt răspuns.
        print("")
        print("!!! API NU A RETURNAT JSON !!!")
        print("Content-Type:", content_type)

        return {
            "success": False,
            "message": "API-ul nu a returnat JSON.",
            "status_code": response.status_code,
            "content_type": content_type,
            "response_text": response.text[:2000]
        }

    except requests.RequestException as e:

        print("")
        print("==============================================")
        print("===== REQUEST ERROR =====")
        print("==============================================")
        print("ERROR TYPE:", type(e).__name__)
        print("ERROR:", str(e))
        print("==============================================")
        print("")

        return {
            "success": False,
            "message": "Eroare la conectarea la API.",
            "error": str(e)
        }
```
