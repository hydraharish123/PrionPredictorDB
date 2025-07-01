import os
import pandas as pd
import numpy as np
import json
import pandas as pd
from Bio.PDB import PDBParser
from sklearn.cluster import DBSCAN
from collections import defaultdict

uniport_ids = os.listdir('../data/PLAAC_PDBs')
all_data = pd.read_csv('../data/Valid_Prion_Protein_PLAAC.csv')
no_aggregation_ids = []


def get_side_chain_centroid(residue):
    side_atoms = [atom for atom in residue if atom.get_name() not in ("N", "CA", "C", "O")]
    if not side_atoms:
        return None
    coords = np.array([atom.get_coord() for atom in side_atoms])
    return coords.mean(axis=0)

def save_aggregation_data(clusters, file_name, directory):
    cluster_output = {
        f"cluster_{cluster_id}": [{"chain": chain_id, "residue": resnum} for (chain_id, resnum) in residues] for cluster_id, residues in clusters.items()
    }   

    with open(f"{directory}/{file_name}.json", "w") as f:
        json.dump(cluster_output, f, indent=4)

    print(f"✅ Saved cluster results to {file_name}_clustering.json")


def get_all_cords(full_file_name):
    pdb_file =  f"./../data/PLAAC_PDBs/{full_file_name}"
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("protein", pdb_file)

    residue_coords = []

    for model in structure:
        for chain in model:
            for residue in chain:
                res_id = residue.get_id()[1]  # get residue position
                if res_id:
                    if "CA" in residue:  # Use alpha carbon for coordinate
                        coord = residue["CA"].get_coord()
                        residue_coords.append({
                            "chain": chain.id,
                            "residue_number": res_id,
                            "coord": coord
                        })
    return residue_coords


def write_centroids_pdb(output_path, centroids, res_ids, labels):
    with open(output_path, "w") as f:
        atom_serial = 1
        for i, ((chain_id, resnum), coord, label) in enumerate(zip(res_ids, centroids, labels)):
            if label == -1:
                continue  

            x, y, z = coord
            line = (
                f"HETATM{atom_serial:5d}  CEN C   {resnum:4d}    "
                f"{x:8.3f}{y:8.3f}{z:8.3f}  1.00 {label:6.2f}           C  \n"
            )
            f.write(line)
            atom_serial += 1

    print("\n\n")


for uniport_id in uniport_ids:
    uid = uniport_id.split('.')[0]
    print(f"Processing data for {uid}")
    a3d_dir = f'./../data/aggrescan3d/a3d_{uid}/A3D.csv'
    a3d_scores = pd.read_csv(a3d_dir)
    matching_row = all_data[all_data['SEQid'].str.extract(r'sp\|([A-Z0-9]+)\|')[0] == uid] ### dataframe
    start = matching_row['PRDstart'].values[0]
    end = matching_row['PRDend'].values[0]
    threshold = 0.5

    high_score_residues = a3d_scores[(a3d_scores['score'] > threshold) & (a3d_scores['residue'] >= start) &  (a3d_scores['residue'] <= end)]
    if(len(high_score_residues) == 0):
        print(f"Could not find aggregatable residues for {uid}")
        no_aggregation_ids.append(uid)
        continue

    
    pdb_file = f"./../data/PLAAC_PDBs/{uniport_id}"
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("protein", pdb_file)

    res_coords = []
    res_ids = []

    for model in structure:
        for chain in model:
            chain_id = chain.get_id()
            for residue in chain:
                res_id = residue.get_id()[1]
                # Check if residue is in high-score list
                if ((high_score_residues["residue"] == res_id) & (high_score_residues["chain"] == chain_id)).any():
                    centroid = get_side_chain_centroid(residue)
                    if centroid is not None:
                        res_coords.append(centroid)
                        res_ids.append((chain_id, res_id))


    X = np.array(res_coords)
    clustering = DBSCAN(eps=10, min_samples=2).fit(X)
    labels = clustering.labels_

    clusters = defaultdict(list)
    for label, res in zip(labels, res_ids):
        if label != -1:
            clusters[label].append(res)

    for cluster_id, residues in clusters.items():
        print(f"Cluster {cluster_id} (Aggregation Patch): {residues}")

    uid_dir = f'../data/Clustering_data/{uid}'
    
    os.makedirs(uid_dir, exist_ok=True)

    save_aggregation_data(clusters=clusters, file_name=uid, directory=uid_dir)

    residue_coords = get_all_cords(uniport_id)

    write_centroids_pdb(f"./../data/Clustering_data/{uid}/{uid}_centroids.pdb", res_coords, res_ids, labels)

    


#### no_aggregation_ids 
# ['O14776',
#  'P02810',
#  'P02812',
#  'P04280',
#  'Q156A1',
#  'Q8NDV7',
#  'Q9H3P7',
#  'Q9NZW4']