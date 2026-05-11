import pandas as pd
import os

def validate_csv(filepath):

    try:
        df = pd.read_csv(filepath)

        if df.empty:
            return False

        return True

    except:
        return False


def save_uploaded_file(file, upload_folder, filename):

    filepath = os.path.join(upload_folder, filename)

    file.save(filepath)

    return filepath


def delete_uploaded_file(filepath):

    if os.path.exists(filepath):

        os.remove(filepath) 