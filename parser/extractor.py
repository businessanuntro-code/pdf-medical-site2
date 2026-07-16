import os
import zipfile


def extract_zip(zip_path, extract_folder):
    """
    Dezarhivează revista în folderul de lucru.
    Returnează calea către folderul extras.
    """

    os.makedirs(
        extract_folder,
        exist_ok=True
    )

    with zipfile.ZipFile(zip_path, "r") as archive:

        archive.extractall(
            extract_folder
        )


    return extract_folder
