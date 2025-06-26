from Bio.PDB import PDBParser
import freesasa
import os
import pandas as pd

def get_pLLDT_SASA(uniprot_id, start, end):
    SASA_pLDDT[uniprot_id] = {}
    SASA_pLDDT[uniprot_id]
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("AF", f"./../data/PLAAC_PDBs/{uniprot_id}.pdb")
    model = structure[0]
    fsa_structure = freesasa.Structure(f"./../data/PLAAC_PDBs/{uniprot_id}.pdb")
    fsa_result = freesasa.calc(fsa_structure)
    start_res, end_res = start, end
    plddt_vals = []
    sasa_total = 0.0

    # Iterate over all chains
    for chain in model:
        for residue in chain:
            res_id = residue.get_id()
            resnum = res_id[1]

            if start_res <= resnum <= end_res and 'CA' in residue:
                atom = residue['CA']
                plddt_vals.append(atom.get_bfactor())

                for i in range(fsa_structure.nAtoms()):
                    atom_i = fsa_structure.atomName(i)
                    resn_i = fsa_structure.residueNumber(i)
                    chain_i = fsa_structure.chainLabel(i)
                    if atom_i.strip() == 'CA' and int(resn_i) == resnum and chain_i == chain.id:
                        sasa_total += fsa_result.atomArea(i)
                        break

    avg_plddt = sum(plddt_vals) / len(plddt_vals) if plddt_vals else 0.0
    SASA_pLDDT[uniprot_id] = {
        'SASA': sasa_total,
        'Average_pLDDT': avg_plddt,
        'start': start,
        'end' : end
    }
    print(f"UniprotID: {uniprot_id} Total chains: {len(model)} Region {start_res}-{end_res} → Avg pLDDT: {avg_plddt:.2f}, SASA: {sasa_total:.2f} Å²")


directory = "./../data/PLAAC_PDBs"
df = pd.read_csv('./../data/Valid_Prion_Protein_PLAAC.csv')
file_names = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

for uid in file_names:
    filtered_df = df[df['SEQid'].str.contains(uid.split('.')[0])]
    if not filtered_df.empty:
        start_pos = int(filtered_df['PRDstart'].values[0])
        end_pos = int(filtered_df['PRDend'].values[0])
        get_pLLDT_SASA(uniprot_id=uid.split('.')[0], start=start_pos, end=end_pos)
    else:
        print(f"{uid} not found in dataframe")
    