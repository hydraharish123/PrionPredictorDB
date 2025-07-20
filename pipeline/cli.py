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
        if script == 'fetchPDB.py' and result.returncode == 2:
            print(f"[❌] Could not fetch AlphaFold structure for UniProt ID '{args[0]}'.")
        if script == 'run_plaac.py' and result.returncode == 3:
            print(f"[❌] Could not run PLAAC '{args[0]}' {result.stderr}.")
        if script == 'run_a3d.py' and result.returncode == 5:
            print(f"[❌] Could not run Aggrescan3D '{args[0]}'. Either the input was not correct or aggrescan failed to compute or server failed")
        
        else:
            print(f"[ERROR] Step failed: {script}")
        print(result.stderr)
        sys.exit(result.returncode)

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
    print(f"[📁] Step 1 result saved to {os.path.join(output_dir, f'{uid}_metadata.csv')}")

    print("\n")
    
    print("[*] Running step 2: Fetching PDB...")
    run_step(PY3, 'fetchPDB.py', [uid, output_dir])
    print("[✔] PDB fetched")
    print(f"[📁] Step 2 result saved to {os.path.join(output_dir, f"{uid}.pdb")}")

    print("\n")

    print("[*] Running step 3: PLAAC analysis...")
    run_step(PY3, 'run_plaac.py', [sample, reference, output_dir, uid])
    print("[✔] PLAAC analysis complete")
    print(f"[📁] Step 3 result saved to {os.path.join(output_dir, f"{uid}_plaac.txt")}")

    print("\n")

    print("[*] Running step 4: Calculating SASA and pLDDT...")
    run_step(PY3, 'calculate_SASA_pLDDT.py', [output_dir, uid])
    print("[✔] Calculated SASA and pLDDT")
    print(f"[📁] Step 4 result saved to {os.path.join(output_dir, f"{uid}_SASA_pLDDT.txt")}")

    print("\n")

    print("[*] Running step 5: Aggrescan3D Analysis...")
    run_step(PY2, 'run_a3d.py', [uid, output_dir])
    print("[✔] Aggrescan Analysis complete")
    print(f"[📁] Step 5 result saved to {os.path.join(output_dir, f"a3d_{uid}/")}")



    
if __name__ == "__main__":
    main()
