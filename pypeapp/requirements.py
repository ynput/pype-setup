"""
This script will check installed packages in virtual environment and compare
them with those specified in pype's `requirements.txt`. If some packages
are missing from installed environment, it will return 1 exit status. This
will trigger packages installation in parent shell script.
"""
import sys
import subprocess

# get pip installed packages
installed_req = subprocess.check_output(
    [sys.executable, '-m', 'pip', 'freeze'])

# fix encoding, make all lowercase and get it as list
installed_req = installed_req.decode(sys.getfilesystemencoding())
installed_req = installed_req.splitlines()
installed_req = [s.lower() for s in installed_req]

# read required dependencies and expect it in UTF-8 BOM. This is produced
# by default on Windows with Poweshell, but works with non-BOM and ASCII too.
with open("pypeapp/requirements.txt", "r", encoding="utf-8-sig") as rf:
    requested_req = rf.readlines()

# clear those from endlines and make it lower
requested_req = [r.strip().lower() for r in requested_req]

# find all required that are not in installed
missing = [x for x in requested_req if x not in installed_req]

# try to find them in installed if they have no version specified
for i in installed_req:
    if i.split("==")[0] in missing:
        missing.remove(i.split("==")[0])

# if installed is not requested and we didn't clear any special cases
# exit with non-zero status to trigger environment install
if not set(requested_req).issubset(installed_req):
    if missing:
        for m in missing:
            print("")
            print("   - missing [ {} ]".format(m))
        sys.exit(1)
