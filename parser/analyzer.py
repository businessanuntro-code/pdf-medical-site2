import os


def find_html_folder(base_folder):
    """
    Caută automat folderul care conține pagini HTML.
    """

    for root, dirs, files in os.walk(base_folder):

        html_files = [
            f for f in files
            if f.lower().endswith(".html")
        ]


        if html_files:

            return root


    return None



def analyze_extracted_folder(extracted_folder):

    """
    Analizează conținutul dezarhivat.
    """

    result = {

        "files_count": 0,

        "html_folder": None,

    }


    for root, dirs, files in os.walk(extracted_folder):

        result["files_count"] += len(files)



    html_folder = find_html_folder(
        extracted_folder
    )


    if html_folder:

        result["html_folder"] = html_folder



    return result
