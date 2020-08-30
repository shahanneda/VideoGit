
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
        for filePath in filePaths:
            try:
                initalFile = self.runSystemCommand(f"git show {startingCommit}:{filePath}");
                diffOfFile = self.runSystemCommand(f"git diff {startingCommit}..{endingCommit} {filePath}")
            except:
                print("Failed to open file: " + filePath);
                continue;
            self.handleFileDiffs(initalFile, diffOfFile)


    
    def handleFileDiffs(self, initalFile, diffOfFile):
        linesOfDiffs = str.split(diffOfFile, "\n");

        linesWithoutDiff = linesOfDiffs;
        linesToBeRemoved = [];

        for i, line in enumerate(linesOfDiffs):
            if(len(line) > 0 and line[0] == "+"):
                linesToBeRemoved.append(i);

            if(len(line) > 0 and line[0] == "-"):
                pass
                # linesWithoutDiff[i] = line[2:];


        print(linesToBeRemoved);
        for lineIndex in linesToBeRemoved:
            linesWithoutDiff.pop(lineIndex);


        print(linesWithoutDiff);
        

    








nv = ncodevideo();



