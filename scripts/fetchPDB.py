import requests
import pandas as pd

def download_alphafold_pdb(uniprot_id, output_path=None):
    url = f"https://alphafold.ebi.ac.uk/files/AF-{uniprot_id}-F1-model_v4.pdb"
    if output_path is None:
        output_path = f"./../data/PLAAC_PDBs/{uniprot_id}.pdb"

    response = requests.get(url)
    if response.status_code == 200:
        with open(output_path, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded PDB for {uniprot_id} → {output_path}")
    else:
        print(f"Failed to download AlphaFold structure for {uniprot_id} (HTTP {response.status_code})")

def splitUniprotHeader(text):
    return text.split('|')[1]


df = pd.read_csv('./../data/Valid_Prion_Protein_PLAAC.csv')
valid_prots = list(df['SEQid'].apply(lambda x: splitUniprotHeader(x)))
for uid in valid_prots:
    download_alphafold_pdb(uniprot_id=uid)