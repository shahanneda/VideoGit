


import subprocess

batcmd="git status"
result = subprocess.check_output(batcmd, shell=True)
print(result)
