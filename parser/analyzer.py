import os
import zipfile


def analyze_zip(zip_path):
    """
    Analizează arhiva revistei și returnează informații despre conținut.
    """

    result = {
        "files_count": 0,
        "html_folder": None,
        "articles": []
    }


    if not os.path.exists(zip_path):
        return result


    with zipfile.ZipFile(zip_path, "r") as archive:

        files = archive.namelist()


        # Număr total fișiere
        result["files_count"] = len(files)



        # Detectare folder html
        for file in files:

            normalized = file.lower()

            if "/html/" in normalized or normalized.startswith("html/"):

                result["html_folder"] = "html"
                break



        # Detectare articole publication-1, publication-2 etc.
        articles = set()


        for file in files:

            parts = file.split("/")


            for part in parts:

                if part.lower().startswith("publication-"):

                    articles.add(part)



        result["articles"] = sorted(list(articles))


    return result
