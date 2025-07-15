import subprocess
import os
import sys
import argparse
from pyfiglet import figlet_format

# Update these paths to match your system
PY3 = r"C:\Users\Nkris\Programming\my-env\Scripts\python.exe"
PY2 = r"C:\Users\Nkris\Programming\py27env\Scripts\python.exe"

def run_step(python_path, script, args):
    result = subprocess.run(
        [python_path, script] + args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if result.returncode != 0:
        print(f"[ERROR] {script} failed:\n{result.stderr}")
        sys.exit(1)
    return result.stdout.strip()

def main():
    parser = argparse.ArgumentParser(description="Run the PPDB pipeline.")
    parser.add_argument("sample", help="Path to sample FASTA file")
    parser.add_argument("reference", help="Path to reference FASTA file")
    parser.add_argument("-o", "--output", help="Output directory", default="ppdb_output")

    args = parser.parse_args()

    sample = args.sample
    reference = args.reference
    output_dir = args.output

    os.makedirs(output_dir, exist_ok=True)

    print(figlet_format("PPDB", font="slant"))
    print("Welcome to Prion Predictor DB\n")


    print("[*] Running step 1: Fetching UniProt ID...")
    uid = run_step(PY3, 'fetchUniprot.py', [sample, output_dir])
    print("[✔] UniProtID fetched")
    print(f"[📁] Step 1 result saved to {output_dir}/{uid}_metadata.csv")
    
if __name__ == "__main__":
    main()
