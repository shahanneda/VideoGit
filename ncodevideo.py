
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
        linesOfDiffs = linesOfDiffs[5:] # remove the first 3 lines, becuase its just location info

        linesWithoutDiff = linesOfDiffs;
        linesToBeRemoved = []; # we need to store this so we can add them later

        for i, line in enumerate(linesOfDiffs):
            if(len(line) > 0 and line[0] == "+"): # remove the lines that have addidiotsn, were going to add them later
                linesToBeRemoved.append(i);

            if(len(line) > 0 and line[0] == "-"): # remove the -  
                linesWithoutDiff[i] = line[1:];

        # remove all the lines queed up in linesToBeRemoved (the + ones)
        linesWithoutDiff = [line for i, line in enumerate(linesWithoutDiff) if i not in linesToBeRemoved] 

        fullCode = "\n".join(linesWithoutDiff) + "\n\n\n\n";
        
        print(fullCode);


    # def makeImageFromCode(self, code, fileName, indexOfImage): # index is for the video file
        
        

        

    








nv = ncodevideo();



