#### Aggrescan3d runs on python 2.7

import subprocess
import os

input_dir = os.path.abspath("./../data/PLAAC_PDBs")
output_dir = os.path.abspath("./../data/aggrescan3d")
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

file_names = [f for f in os.listdir(input_dir) if f.endswith('.pdb')]

for pdb_file in file_names:
    input_path = os.path.join(input_dir, pdb_file)
    base_name = os.path.splitext(pdb_file)[0]
    output_path = os.path.join(output_dir, "a3d_{}".format(base_name))

    command = ["aggrescan", "-i", input_path, "-w", output_path, "-v", "4"]

    print("\nRunning Aggrescan on: {}".format(pdb_file))
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        
        print("Done")
        print("STDOUT:\n", stdout)
        if stderr:
            print("STDERR:\n", stderr)
    except OSError as e:
        print("Error: aggrescan not found or failed.")
        print(str(e))
