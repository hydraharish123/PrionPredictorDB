import json
import colorsys
import sys
import os

uid = sys.argv[1]
output_dir = sys.argv[2]

with open(os.path.abspath(os.path.join(output_dir, f"{uid}_clustering.json"))) as f:
    cluster_data = json.load(f)

def generate_unique_rgb(index, total):
    hue = (index / total) % 1.0
    r, g, b = colorsys.hsv_to_rgb(hue, 0.7, 1.0)
    return [round(r, 3), round(g, 3), round(b, 3)]

lines = []
main_pdb = os.path.abspath(os.path.join(output_dir, f"{uid}.pdb"))
centroids_pdb = os.path.abspath(os.path.join(output_dir, f"{uid}_centroids.pdb"))

lines.append(f"load {main_pdb}, main")
lines.append(f"load {centroids_pdb}, centroids")
lines.append("show spheres, centroids")
lines.append("set sphere_scale, 0.6, centroids")

total_clusters = len(cluster_data)
for i, (cluster_name, residues) in enumerate(cluster_data.items()):
    selection_expr = " or ".join(
        f"(resi {res['residue']})" for res in residues
    )
    full_selection = f"centroids and ({selection_expr})"
    lines.append(f"select {cluster_name}, {full_selection}")
    rgb = generate_unique_rgb(i, total_clusters)
    color_name = f"cluster_color_{i}"
    lines.append(f"set_color {color_name}, [{rgb[0]:.2f}, {rgb[1]:.2f}, {rgb[2]:.2f}]")
    lines.append(f"color {color_name}, {cluster_name}")
    lines.append(f"show spheres, {cluster_name}")
    lines.append(f"set sphere_scale, 0.6, {cluster_name}")
    lines.append(f"label {cluster_name}, resi")

lines.append("zoom main or centroids")

output_path = os.path.join(output_dir, f"{uid}_pymol_clusters.pml")
with open(output_path, "w") as f:
    f.write("\n".join(lines))


