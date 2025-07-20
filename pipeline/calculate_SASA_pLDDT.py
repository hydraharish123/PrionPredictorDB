from Bio.PDB import PDBParser
import freesasa
import os
import pandas as pd
import json
import sys

output_dir = sys.argv[1]
uid = sys.argv[2]

pdb_path = os.path.join(output_dir, f"{uid}.pdb")
plaac_path = os.path.join(output_dir, f"{uid}_plaac.txt")
plaac_df = pd.read_csv(plaac_path, sep="\t", comment="#")
output_path = os.path.join(output_dir, f"{uid}_SASA_pLDDT.json")

start_pos = int(plaac_df['PRDstart'].values[0])
end_pos = int(plaac_df['PRDend'].values[0])


def get_pLLDT_SASA(uniprot_id, start, end):
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("AF", pdb_path)
    model = structure[0]
    fsa_structure = freesasa.Structure(pdb_path)
    fsa_result = freesasa.calc(fsa_structure)
    start_res, end_res = start, end
    plddt_vals = []
    sasa_total = 0.0

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
    output = {
        'SASA': sasa_total,
        'Average_pLDDT': avg_plddt,
        'start': start,
        'end' : end
    }

    
    with open(output_path, "w") as f:
        json.dump(output, f)
    
    

get_pLLDT_SASA(uniprot_id=uid, start=start_pos, end=end_pos)

    