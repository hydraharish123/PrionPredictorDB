import sys
import os
import subprocess

if len(sys.argv) != 5:
    print("Usage: python run_plaac.py <sample.fasta> <reference.fasta> <output_dir> <uniprot_id>")
    sys.exit(3)

sample = sys.argv[1]
reference = sys.argv[2]
output_dir = sys.argv[3]
uid = sys.argv[4]

def run_plaac(sample, reference, output_dir, uid):
    plaac_output_path = os.path.join(output_dir, f"{uid}_plaac.txt")
    plaac_jar_path = os.path.join("plaac", "cli", "target", "plaac.jar")

    try:
        with open(plaac_output_path, "w") as out:
            subprocess.run([
                "java", "-jar", plaac_jar_path,
                "-i", sample,
                "-b", reference,
                "-a", "0"
            ], stdout=out, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError as e:
        sys.exit(3)

run_plaac(sample, reference, output_dir, uid)