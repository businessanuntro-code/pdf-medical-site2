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


    return sorted(files, key=sort_key)



def extract_title(html_path):

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


    # Titlul real
    title = soup.find(
        "p",
        class_=lambda x: x and "TITLU" in x
    )


    if title:

        text = title.get_text(
            " ",
            strip=True
        )

        return text


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


        title = extract_title(
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
