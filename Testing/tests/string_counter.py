import subprocess
counter = 0

_ , unit_info = subprocess.getstatusoutput('uhd_usrp_info -v')
unit_info = unit_info.split("\n")

for c in (unit_info):
    print(str(counter) + ": " + c)
    counter += 1
