import sys
import os
import subprocess

uid = sys.argv[1]
out_dir = sys.argv[2]

input_path = os.path.join(out_dir, "{}.pdb".format(uid))
output_path = os.path.join(out_dir, "a3d_{}".format(uid))

command = ["aggrescan", "-i", input_path, "-w", output_path, "-v", "4"]

try:
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        sys.exit(5) 
    else:
        sys.exit(0)  # Success


except Exception:
    sys.exit(5) 
