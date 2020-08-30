
import subprocess


getLogCommand = "git log --pretty=format:\"%h %s\"";
batcmd="git status"
commit1="700043f"
commit2="3f8d661"
class ncodevideo:
    def runSystemCommand(self, command):
        return subprocess.check_output(command, shell=True, text=True)

    def __init__(self):
        findChangedFilePaths = f"git diff --name-only {commit1}..{commit2}";
        filePaths = str.split(self.runSystemCommand(findChangedFilePaths), "\n");
        self.loopThroughFiles(filePaths, commit1, commit2);

    def loopThroughFiles(self, filePaths, startingCommit, endingCommit):
        for filePath in filePaths:
            print(filePath)
            try:
                initalFile =  self.runSystemCommand(f"git show {startingCommit}:{filePath}");
            except:
                print("Failed to open file: " + filePath);
                continue;

            print(initalFile)










nv = ncodevideo();



