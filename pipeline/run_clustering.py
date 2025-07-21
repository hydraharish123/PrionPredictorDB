import os
import sys
import pandas as pd
import numpy as np
import json
from Bio.PDB import PDBParser
from sklearn.cluster import DBSCAN
from collections import defaultdict

uid = sys.argv[1]
output_dir = sys.argv[2]

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

    with open(f"{directory}/{file_name}_clustering.json", "w") as f:
        json.dump(cluster_output, f, indent=4)

    


def get_all_cords(output_dir):
    pdb_file = os.path.join(output_dir, f"{uid}.pdb")
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("protein", pdb_file)

    residue_coords = []

    for model in structure:
        for chain in model:
            for residue in chain:
                res_id = residue.get_id()[1]  
                if res_id:
                    if "CA" in residue:  
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


def clustering(output_dir, uid):
    a3d_dir = os.path.join(output_dir, f"a3d_{uid}")
    a3d_csv = os.path.join(a3d_dir, 'A3D.csv')
    pdb_file = f"{os.path.join(output_dir, uid)}.pdb"
    a3d_scores = pd.read_csv(a3d_csv)

    plaac_df = pd.read_csv(os.path.join(output_dir, f"{uid}_plaac.txt"), comment="#", sep="\t")
    start = plaac_df['PRDstart'].values[0]
    end = plaac_df['PRDend'].values[0]
    threshold = 0.5

    high_score_residues = a3d_scores[(a3d_scores['score'] > threshold) & (a3d_scores['residue'] >= start) &  (a3d_scores['residue'] <= end)]
    if(len(high_score_residues) == 0):
        sys.exit(6)
                
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("protein", pdb_file)

    res_coords = []
    res_ids = []

    for model in structure:
        for chain in model:
            chain_id = chain.get_id()
            for residue in chain:
                res_id = residue.get_id()[1]
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


    save_aggregation_data(clusters=clusters, file_name=uid, directory=output_dir)
    residue_coords = get_all_cords(output_dir)
    write_centroids_pdb(os.path.join(output_dir, f"{uid}_centroids.pdb"), res_coords, res_ids, labels)


clustering(output_dir, uid)
