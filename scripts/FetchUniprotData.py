from Bio import SeqIO
import requests
import pandas as pd
import numpy as np

fasta_file = "human_proteins.fasta"

uniprot_ids = []
for record in SeqIO.parse(fasta_file, "fasta"):
    header = record.description
    # Extract ID from header (e.g., sp|P12345|PROT_HUMAN)
    parts = header.split("|")
    if len(parts) > 1:
        uniprot_ids.append(parts[1])


final_result = []
error_ids = []

for uniprot_id in uniprot_ids:
    try:

        url = f"https://rest.uniprot.org/uniprotkb/{uniprot_id}.json"

        response = requests.get(url)
        data = response.json()

        accession = data['primaryAccession']
        entry_name = data['uniProtkbId']

        # Protein name
        protein_name = data['proteinDescription']['recommendedName']['fullName']['value']

        # Gene names
        gene_names = [gene['geneName']['value'] for gene in data.get('genes', [])]

        # Organism
        organism = data['organism']['scientificName']

        # Length
        length = data['sequence']['length']

        sequence = data['sequence']['value']

        # Function (from comments)
        function_comment = ""
        for comment in data.get("comments", []):
            if comment["commentType"] == "FUNCTION":
                function_comment = comment["texts"][0]["value"]
                break

        # GO terms
        go_terms = [xref['id'] for xref in data.get("uniProtKBCrossReferences", []) if xref['database'] == 'GO']

        # PDB IDs
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
        continue


columns = [
    "Accession", "Entry Name", "Protein Name", "Gene Names", "Organism", "Length",
    "Sequence", "Function", "GO Terms", "PDB IDs", "AlphaFold Model"
]

df = pd.DataFrame(final_result, columns=columns)
df.to_csv("uniprot_metadata.csv", index=False)

## ERROR_IDS
# ['Q6UXU0',
#  'Q6UY13',
#  'Q71RG6',
#  'Q0P140',
#  'Q6UWF5',
#  'Q6UXP9',
#  'Q6UXR8',
#  'Q6UXV3',
#  'Q6XCG6',
#  'Q8WZ26',
#  'Q9BZS9',
#  'Q9H354',
#  'Q9H379',
#  'Q9P1C3',
#  'Q9P1D8',
#  'Q9UHT4',
#  'Q9UHU1',
#  'Q9UI25',
#  'Q9UI54',
#  'Q9UI72',
#  'Q6UXR6',
#  'P09565',
#  'Q6UXQ8']