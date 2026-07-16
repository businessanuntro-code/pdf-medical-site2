import os
import re
from bs4 import BeautifulSoup



def get_html_files(html_folder):

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




def extract_editorial_title(html_path):

    """
    Caz special pentru publication.html
    """

    with open(
        html_path,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as f:

        soup = BeautifulSoup(
            f.read(),
            "html.parser"
        )


    span = soup.find(
        id="_idTextSpan001"
    )


    if span:

        parent = span.find_parent("p")

        if parent:

            text = parent.get_text(
                " ",
                strip=True
            )

            return text


    return None





def extract_article_title(html_path):

    """
    Caută titlu normal articol
    """

    with open(
        html_path,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as f:

        soup = BeautifulSoup(
            f.read(),
            "html.parser"
        )



    title = soup.find(
        "p",
        class_=lambda classes:
            classes and
            "TITLU" in classes
    )


    if title:

        return title.get_text(
            " ",
            strip=True
        )


    return None





def detect_articles(html_folder):


    html_files = get_html_files(
        html_folder
    )


    articles = []

    current_article = None



    for filename in html_files:


        path = os.path.join(
            html_folder,
            filename
        )


        title = None



        # primul fisier = editorial
        if filename.lower() == "publication.html":

            title = extract_editorial_title(
                path
            )


        else:

            title = extract_article_title(
                path
            )



        if title:


            if current_article:

                articles.append(
                    current_article
                )



            current_article = {

                "id": len(articles)+1,

                "title": title,

                "pages": [
                    filename
                ]

            }



        else:


            if current_article:

                current_article["pages"].append(
                    filename
                )



    if current_article:

        articles.append(
            current_article
        )



    return articles
