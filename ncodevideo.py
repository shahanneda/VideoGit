
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
        filePaths = list(filter(None, filePaths)) # remove empty strings

        self.loopThroughFilePaths(filePaths, commit1, commit2);
        

    def loopThroughFilePaths(self, filePaths, startingCommit, endingCommit):
        print(filePaths);
        for filePath in filePaths:
            try:
                initalFile = self.runSystemCommand(f"git show {startingCommit}:{filePath}");
                diffOfFile = self.runSystemCommand(f"git diff {filePath} {startingCommit}..{endingCommit}")
            except:
                print("Failed to open file: " + filePath);
                continue;

            print(initalFile)
            print(diffOfFile);

        print(filePaths);

    
    








nv = ncodevideo();



