# VideoGit
## Converts git commit history, to a beautiful animated coding video.
## Installation
1. Install Silicon
2. Install FFmpeg
3. Run `pip install videogit`
# Usage

## Usage Help
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
