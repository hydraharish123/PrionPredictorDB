import requests
import pandas as pd
import sys
import os

uid = sys.argv[1]
output_dir = sys.argv[2] if len(sys.argv) > 2 else "."
output_file = os.path.join(output_dir, f"{uid}.pdb")

def download_alphafold_pdb(uniprot_id, output_path=None):
    url = f"https://alphafold.ebi.ac.uk/files/AF-{uniprot_id}-F1-model_v4.pdb"

    response = requests.get(url)
    if response.status_code == 200:
        with open(output_path, 'wb') as f:
            f.write(response.content)
    else:
        sys.exit(2)

def splitUniprotHeader(text):
    return text.split('|')[1]


download_alphafold_pdb(uniprot_id=uid, output_path=output_file)