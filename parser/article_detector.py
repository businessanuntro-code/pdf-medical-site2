import os
import re
from bs4 import BeautifulSoup


def get_html_files(html_folder):
    """
    Returnează paginile HTML în ordinea corectă.
    """

    files = []

    for file in os.listdir(html_folder):

        if file.lower().endswith(".html"):

            files.append(file)


    def sort_key(filename):

        if filename.lower() == "publication.html":
            return 0


        match = re.search(
            r"publication-(\d+)\.html",
            filename,
            re.IGNORECASE
        )


        if match:
            return int(match.group(1))


        return 999999


    return sorted(
        files,
        key=sort_key
    )



def extract_title(html_path):
    """
    Extrage titlul articolului.
    
    Prima prioritate:
    id="_idTextSpan001"

    """

    with open(
        html_path,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as file:

        content = file.read()



    soup = BeautifulSoup(
        content,
        "html.parser"
    )



    # Titlul principal
    title_element = soup.find(
        id="_idTextSpan001"
    )


    if title_element:

        return title_element.get_text(
            " ",
            strip=True
        )



    # Titlurile următoare
    title_element = soup.find(
        "p",
        class_="TITLU ParaOverride-1"
    )


    if title_element:

        return title_element.get_text(
            " ",
            strip=True
        )



    return None




def detect_articles(html_folder):

    """
    Grupează paginile HTML în articole.
    """

    html_files = get_html_files(
        html_folder
    )


    articles = []

    current_article = None


    for filename in html_files:


        full_path = os.path.join(
            html_folder,
            filename
        )


        title = extract_title(
            full_path
        )


        # Dacă găsim titlu nou
        if title:


            # închidem articolul anterior
            if current_article:

                articles.append(
                    current_article
                )


            current_article = {

                "id": len(articles) + 1,

                "title": title,

                "pages": [
                    filename
                ]

            }


        else:

            # pagina continuă articolul curent

            if current_article:

                current_article["pages"].append(
                    filename
                )



    # ultimul articol
    if current_article:

        articles.append(
            current_article
        )


    return articles
