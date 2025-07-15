from Bio import SeqIO
import requests
import pandas as pd
import sys
import os

# Input FASTA file path
sample = sys.argv[1]
output_dir = sys.argv[2] if len(sys.argv) > 2 else "."

uniprot_ids = []
for record in SeqIO.parse(sample, "fasta"):
    parts = record.description.split("|")
    if len(parts) > 1:
        uniprot_ids.append(parts[1])

if not uniprot_ids:
    print("[ERROR] No UniProt ID found in FASTA header.")
    sys.exit(1)

uniprot_id = uniprot_ids[0]
final_result = []
error_ids = []

try:
    url = f"https://rest.uniprot.org/uniprotkb/{uniprot_id}.json"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    accession = data['primaryAccession']
    entry_name = data['uniProtkbId']
    protein_name = data['proteinDescription']['recommendedName']['fullName']['value']
    gene_names = [gene['geneName']['value'] for gene in data.get('genes', [])]
    organism = data['organism']['scientificName']
    length = data['sequence']['length']
    sequence = data['sequence']['value']

    function_comment = ""
    for comment in data.get("comments", []):
        if comment.get("commentType") == "FUNCTION":
            function_comment = comment["texts"][0]["value"]
            break

    go_terms = [xref['id'] for xref in data.get("uniProtKBCrossReferences", []) if xref['database'] == 'GO']
    pdb_ids = [xref['id'] for xref in data.get("uniProtKBCrossReferences", []) if xref['database'] == 'PDB']
    alphafold_id = f"AF-{uniprot_id}-F1-model_v4.pdb"

    details = (
        accession,
        entry_name,
        protein_name,
        ','.join(gene_names),
        organism,
        length,
        sequence,
        function_comment,
        ','.join(go_terms),
        ','.join(pdb_ids),
        alphafold_id
    )

    final_result.append(details)

except Exception as e:
    error_ids.append(uniprot_id)

columns = [
    "Accession", "Entry Name", "Protein Name", "Gene Names", "Organism", "Length",
    "Sequence", "Function", "GO Terms", "PDB IDs", "AlphaFold Model"
]

if final_result:
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{uniprot_id}_metadata.csv")
    df = pd.DataFrame(final_result, columns=columns)
    df.to_csv(output_file, index=False)
    print(uniprot_id) 
else:
    print(f"[ERROR] Failed to fetch metadata for: {uniprot_id}")
    sys.exit(1)
