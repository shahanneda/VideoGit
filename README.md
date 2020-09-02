# VideoGit
## Converts git commit history, to a beautiful animated coding video.
## Installation
1. [Install Silicon with `brew install silicon` or `cargo install silicon`)](https://github.com/Aloxaf/silicon)
2. [Install FFmpeg](https://ffmpeg.org/)
3. Run `pip install videogit`
## Usage
- Make sure you cd to the root directory containing your git repo. ( You should be able to run git commands like `git status` )
- run `videogit -l` to view a list of your commits
- pick and copy the hash of your starting commit, if you do not specify final commit hash, videogit will just make the video from your starting hash to the latest commit
- run `videogit <starting_commmit_hash_here>` or `videogit <starting_commmit_hash_here> <final_commit_hash_here>` filling in the starting and ending hashes
- run `videogit -h` for a full list of options

## Example Usage
- `videogit ba12dc8 -wpm 60 -r 24 -f main.py test.cpp include/test.h`
  
  Creates a 24 fps video from the commit ba12dc8 to the HEAD, at a typing speed of 60 wpm, for files `main.y`, `test.cpp`, and `include/test.h`
 
- `videogit 5f7198d a06dcff -o output-dir` 

  Creates a video from commit 5f7198d to commit a06dcff, for all files changed over that period, and outputs the videos to `output-dir`
## Example Videos

## All Options
```
                            -------- VideoGit --------                          

usage: videogit.py [-h] [-l] [-f FILES [FILES ...]] [-d GIT_REPO_DIRECTORY]
                   [-w WPM] [-r FRAME_RATE] [-o OUTPUT_DIR] [-u UP_DOWN_SPACE]
                   [-m MAX_LINE_LENGTH] [-v]
                   inital_commit [final_commit]

VideoGit by shahanneda (shahan.ca): Converts git commits, to a
beautiful animated video. To get started type videogit -l,

positional arguments:
  inital_commit         the hash of the commit to start the video at
  final_commit          the hash of the commit to end the video at, if not
                        specified will use the HEAD (default: the most recent
                        commit)

optional arguments:
  -h, --help            show this help message and exit
  -l, --list-git-commits
                        list your recent commits and hashes (default: None)
  -f FILES [FILES ...], --files FILES [FILES ...]
                        a list of specific files to make the video, if not set
                        will try to to make the video for all changed files,
                        example: videogit <hash> -f file1.cpp
                        file2.cpp) (default: None)
  -d GIT_REPO_DIRECTORY, --git-repo-directory GIT_REPO_DIRECTORY
                        the repo of your project, only needs to be set if it
                        is diffrent than the current working directory
                        (default: current directory)
  -w WPM, --wpm WPM     the speed of the video in words per minute (default:
                        480)
  -r FRAME_RATE, --frame-rate FRAME_RATE
                        the framerate of the output video (default: 30)
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        the directory of the output videos (default: current
                        directory)
  -u UP_DOWN_SPACE, --up-down-space UP_DOWN_SPACE
                        how many lines above and below the current editing
                        line to include in the video (default: 20)
  -m MAX_LINE_LENGTH, --max_line_length MAX_LINE_LENGTH
                        the maximum line length in chars before wrapping the
                        text (default: 200)
  -v, --verbose         print any errors or logging information (default:
                        False)
```
