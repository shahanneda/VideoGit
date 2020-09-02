
import os
import subprocess
import re
import sys;
import math;
import argparse
import textwrap

from termcolor import colored, cprint
import tempfile
import shutil



class videogit:
    def setup_silicon_command(self):
        self.silicon_command = f"silicon {self.temp_location}/temp_code.txt --no-line-number --output {self.temp_location}";

    def setup_temp_path(self):
        self.temp_dir_object = tempfile.TemporaryDirectory();
        self.temp_location = self.temp_dir_object.name
        if self.verbose:
            print("Temp location: ", self.temp_location);

        

    def run_system_command(self, command, silent=False):
        # altrenative way of doing this method
        # p = subprocess.Popen(command.split(" "),
        #                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # stdout, stderr = p.communicate()
        # if p.returncode != 0:
        #   raise Exception(stderr)
        #
        # return stdout;
        if silent:
            return subprocess.check_output(command, shell=True, text=True, stderr=subprocess.DEVNULL)
        return subprocess.check_output(command, shell=True, text=True)

    def dir_path(self, string): # this is just for argparse
        if os.path.isdir(string) or string == "current directory":
            return string
        else:
            cprint(f"Not a valid directory : {string} !!", "red");
            sys.exit();
        
    def handle_args(self):
        parser = argparse.ArgumentParser(description=f'{colored("VideoGit by shahanneda (shahan.ca):", "cyan")} Converts git commits, to a beautiful animated video. To get started type {colored("videogit -l", "green")}, \n', 
                formatter_class=argparse.ArgumentDefaultsHelpFormatter # to show the default values
                );

        parser.add_argument('-l','--list-git-commits',nargs=0, action=ListGitCommitsAction, help='list your recent commits and hashes')
        parser.add_argument('inital_commit', type=str, help='the hash of the commit to start the video at')
        parser.add_argument('final_commit', type=str, nargs='?', default="the most recent commit", help='the hash of the commit to end the video at, if not specified will use the HEAD')
        parser.add_argument('-f','--files',type=str, nargs="+", help=f'a list of specific files to make the video, if not set will try to to make the video for all changed files, example: {colored("videogit <hash> -f file1.cpp file2.cpp", "green")})')
        parser.add_argument('-d','--git-repo-directory', type=self.dir_path, default="current directory", help='the repo of your project, only needs to be set if it is diffrent than the current working directory')
        parser.add_argument('-w','--wpm', type=int, default="480", help='the speed of the video in words per minute')
        parser.add_argument('-r','--frame-rate', type=int, default="30", help='the framerate of the output video')
        parser.add_argument('-o','--output-dir', type=self.dir_path, default="current directory", help='the directory of the output videos')
        parser.add_argument('-u','--up-down-space', type=int, default="20", help='how many lines above and below the current editing line to include in the video')
        parser.add_argument('-m','--max_line_length', type=int, default="200", help='the maximum line length in chars before wrapping the text')
        parser.add_argument('-v', '--verbose', default=False, action='store_true', help='print any errors or logging information');

        args = parser.parse_args()

        wpm = args.wpm;
        self.chars_per_second = wpm * 5 / 60; #5 char/word * 1min/60sec

        self.frame_rate = args.frame_rate
        self.max_line_length = args.max_line_length;
        self.up_down_space = args.up_down_space;
        self.files = args.files;
        self.verbose = args.verbose;

        commit1 = args.inital_commit.strip();
        commit2 = args.final_commit.strip();

        if args.git_repo_directory is not "current directory":
            self.run_system_command(f"cd {args.git_repo_directory}");
            os.chdir(args.git_repo_directory)
            

        if(commit2 == "the most recent commit"):
            cprint(center_wrap("final commit not specified, using the most recent commit"), "white");
            try:
               commit2 = self.run_system_command("git rev-parse --short HEAD").strip();
            except:
                throw_git_not_found_error();
        
        if(args.output_dir == "current directory"):
                self.output_dir = ".";
        else:
                self.output_dir = args.output_dir; 
                if args.output_dir[-1] == "/": # remove trailing slash
                    self.output_dir = args.output_dir[:-1]

        if commit1 == commit2:
            cprint(center_wrap("Error: Starting and Ending commit the same! Try moving your starting commit back by one."), "red");
            print(center_wrap(f"{colored('Run ', 'green')}videogit -l {colored('to get a list of commits and their hashes.', 'green')} "));

        if self.verbose:
            print("selected commits: ", commit1, commit2);
        return (commit1, commit2);

    def __init__(self):
        # check for needed commands
        if not self.is_tool("ffmpeg"):
            cprint("ffmpeg not installed! Please install ffmpeg(https://ffmpeg.org/), and make sure you can run ffmpen from the console.","red");
            sys.exit();
        if not self.is_tool("silicon"):
            cprint("silicon not installed! Please install silicon(https://github.com/Aloxaf/silicon), and make sure you can run silicon from the console.","red");
            sys.exit();


        cprint(center_wrap("\n\n-------- VideoGit --------"), "cyan", end="\n\n" );
        (commit1, commit2) =  self.handle_args();

        self.setup_temp_path();
        self.find_and_go_through_commits(commit1, commit2);


    def find_and_go_through_commits(self, starting_commit, ending_commit):
        all_commits = [starting_commit];
        all_commits += reversed(self.run_system_command(f"git rev-list --abbrev-commit --ancestry-path {starting_commit}..{ending_commit}").split("\n")[:-1])
        file_paths = set();

        for i, commit in enumerate(all_commits[:-1]):
            find_changed_file_paths = f"git diff --name-only {starting_commit}..{all_commits[i+1]}";
            # try:
            file_paths.update(str.split(self.run_system_command(find_changed_file_paths, silent=True), "\n"));
            # except Exception as e:
            #     cprint("\n\nGit Diff Failed!! Make sure there is a git repo, or try checking the hash(es) of the commit(s)", "red");
            #     if self.verbose:
            #         cprint(e, "red");
            #     print("type " +colored("videogit -l","blue") + " for a list of possible hashes\n\n");
            #     sys.exit();

        file_paths = list(file_paths);
        file_paths = list(filter(None, file_paths)) # remove empty strings

        if self.verbose:
            print("File paths before user filter: ", file_paths);

        # remove any paths the user does not specify
        if self.files is not None:
            file_paths = [file_path for file_path in file_paths if file_path in self.files];
            for file in self.files:
                if file not in file_paths:
                    print(center_wrap(f"{colored('Warning: File', 'yellow')} {file} {colored('not found! Make sure file exists in git history, and you specified the right path/name to the file, relative to your git directory. This could also happen if this file did not change during the selected commit range.', 'yellow')}"));

        if self.verbose:
            print("File paths after user filter: ", file_paths);

        self.loop_through_file_paths(file_paths, all_commits);

    def loop_through_file_paths(self, file_paths, all_commits):
        for file_path in file_paths: 
            file_name = file_path.split("/")[len(file_path.split("/")) - 1] # remove the directory like /gg/gg/g and just get the last part
            completed_code_buffer = [];
            prefile_text = f"{all_commits[0]}--{all_commits[-1]}--";

            for i, commit in enumerate(all_commits[:-1]):
                try:
                    diff_of_file = self.run_system_command(f"git diff -U999999 {commit}..{all_commits[i+1]} -- {file_path}") # the -U is to make sure we get the entire file
                    completed_code_buffer += self.handle_file_diffs(diff_of_file, prefile_text + file_name)
                except Exception as e:
                    cprint("Failed to open file: " + file_path, "red");
                    if self.verbose:
                        cprint(e, "red");
                    continue;

            try:
                self.convert_completed_code_to_video(completed_code_buffer, prefile_text + file_name, file_name);
            except KeyboardInterrupt:
                print("\n");
                sys.exit(0);
            except Exception as e:
                if self.verbose:
                    cprint(e, "red");
                cprint(f"Could not create video for {file_name}, try running with the -v flag to debug, however this is normal if the file got deleted, or was created in a later commit, so you can safely ignore this message.", "red");

    def handle_line_wrap(self, line):
        
        first_non_whitespace = len(line) - len(line.lstrip());
        white_space = line[:first_non_whitespace]; # the whitepsace before the line (we want the wraped text to match it)
        after_wrap = line[self.max_line_length:]; # the text going on the next line

        #recursivly wrap enough times untill all lines are under the limit
        if len(after_wrap) > self.max_line_length:
            after_wrap = self.handle_line_wrap(after_wrap);
        return f"{line[:self.max_line_length]}\n{white_space}{after_wrap}";


    def handle_file_diffs(self, diff_of_file, file_name):
        lines_of_diffs = str.split(diff_of_file, "\n");
        lines_of_diffs = lines_of_diffs[5:] # remove the first 3 lines, becuase its just location info

        try: # remove this annoying message, if applicable
            lines_of_diffs.remove("\\ No newline at end of file");
        except:
            pass;
        

        # handle very long line wrapping
        for i, line in enumerate(lines_of_diffs):
            if len(line) > self.max_line_length:
                lines_of_diffs[i] = self.handle_line_wrap(line); # add the lien wrap

        lines_without_diff = lines_of_diffs;
        changed_lines_dict = {}; # we need to store this so we can add them later

        indices_of_lines_to_be_removed = []; # this keeps track of the index of all the lines were going to remove

        # print("\n".join(lines_without_diff));

        for i, line in enumerate(lines_of_diffs): # first remove all of the - lines, so we dont mess up the line numbers
            if(len(line) > 0 and line[0] == "-"): # remove the -  
                line = " " + line[1:]; # remove the -
                changed_lines_dict[i] = line; # add it to thhe list keeping track
                lines_without_diff[i] = line;
                indices_of_lines_to_be_removed.append(i); # special marker for later so we know to remove the line

            elif(len(line) > 0 and line[0] == "+"): # remove the lines that have addidiotsn, were going to add them later
                line = " " + line[1:] # remove + at start of line
                changed_lines_dict[i] =  line;


        # remove all the lines queed up in changed_lines_dict , if it is in the change lines, we should remove it since we will ad it later, unless it is marked to be remved, then we should not remove it since we want to see it fade
        for i, line in enumerate(lines_of_diffs):

            if(i not in changed_lines_dict or i in indices_of_lines_to_be_removed):
                lines_without_diff[i] = line;
            else:
                lines_without_diff[i] = ""; #put blank line since we will want to add it later and dont want to mess up the notation

        return(self.handle_file_incrementing(lines_without_diff, changed_lines_dict,indices_of_lines_to_be_removed, file_name));




    def handle_file_incrementing(self, file_in_list_form, lines_to_be_added, indices_of_lines_to_be_removed, file_name):
        index_of_images = 0; # for creating the video frames
        index_of_images+=1;
        completed_code_buffer = [];


        frames_per_char = self.frame_rate / self.chars_per_second;

        real_frame_rate = self.frame_rate/ frames_per_char;
        if self.verbose:
            print(f" framerate: {self.frame_rate}, frames_per_char: {frames_per_char} self.chars_per_second: {self.chars_per_second} real_frame_rate: {real_frame_rate}");
        for line_number, line in lines_to_be_added.items():
            # number_of_frames_needed = int((len(line) / self.chars_per_second) * self.frame_rate); # how many frames needed to add/remove line
            # for i in range(0,number_of_frames_needed, math.ceil(frames_per_char)):
            while len(line) > 0:
                if line_number in indices_of_lines_to_be_removed: # check if its marked to be removed

                    # handle not deling the whole line if we dont have too
                    # if our line is a substring of a line to be added, stop removing, and change the adding to how much we have
                    if line_number+1 in lines_to_be_added:
                        next_added_line_after_this = lines_to_be_added[line_number+1];
                        # we are a substirng of next line(and from), menaing we should stop removing, 
                        if line in next_added_line_after_this and next_added_line_after_this.index(line) == 0: 
                            file_in_list_form[line_number] = "" # remove the current line
                            file_in_list_form[line_number+1] = line; # add ourself to the next line instantly
                            lines_to_be_added[line_number+1] = next_added_line_after_this[len(line):] # remove this line from the next line to be added, since were not going to remove it and we already put it there

                            break # do not remove anymore


                    if len(line) >0:
                        line = line[:-1]; # remove last chharater
                        file_in_list_form[line_number] = line;
                else:
                    if len(line) > 0:
                        file_in_list_form[line_number] = file_in_list_form[line_number] + line[0] # add line, only add the first char, since we do it one char at a time
                        line = line[1:] # remove first char since we already addded it

                full_code = list(filter(None, file_in_list_form)) # remove the "" marker used before
                start_of_page_adjustemt = max(self.up_down_space - line_number, 0); # if we cant use the stuff at the top, add it to the end of the page
                full_code = full_code[max(0, (line_number - self.up_down_space)):(line_number + self.up_down_space + start_of_page_adjustemt)]; # only show the seciton we are changing, not the entire file

                full_code = "\n".join(full_code); # add newlines and make it in to string
                # print("\n\n\n\n" + full_code);
                full_code = re.sub(r'@@(.*?)@@', "", full_code); # this regex is to remove the git hulls which are @@ int ... @@


                completed_code_buffer.append(full_code);



        return completed_code_buffer;






    def convert_completed_code_to_video(self, completed_code_buffer, file_name, clean_file_name):
        self.clean_temp_directory();
        self.setup_silicon_command();
        frames_per_char = self.frame_rate / self.chars_per_second;
        real_frame_rate = self.frame_rate / frames_per_char;
        print(f"\nCreating video for {colored(clean_file_name, 'green')}:");
        for i, code in enumerate(completed_code_buffer):
            # add any extra line breaks needed to even  all images out
            # longest_line_count = self.max_line_count_dict[file_name];
            new_line_count = code.count("\n");
            extra_lines_needed = self.up_down_space*2 - new_line_count;
            while extra_lines_needed > 0:
                code += "\n";
                extra_lines_needed -=1;
            code = " " * self.max_line_length + "\n" + code;
            code += "\n" + " " * self.max_line_length + "\n";
            self.make_image_from_code(code, file_name, i, frames_per_char)

            #progress bar
            sys.stdout.write('\r');
            max_size = 80;
            progress = int(max_size * float(i/(len(completed_code_buffer)-1)));
            bar = colored("█" * progress, "green");
            bar = bar + colored("█" * (max_size-progress), "white" );
            sys.stdout.write(f"Creating Image {i} of {len(completed_code_buffer)} *** [{bar}]");
            sys.stdout.flush();

        sys.stdout.write('\n\r');
        sys.stdout.write('Creating video from image files using ffmpeg.\n');
        sys.stdout.flush();
        self.convert_images_to_video(file_name, real_frame_rate=real_frame_rate );
        cprint(f"Successfully created video for {clean_file_name}, path: {self.output_dir}/{file_name}.mp4\n\n","green");
        self.clean_temp_directory();
    # def handle_image_creation_add_line(self, line:

    def convert_images_to_video(self, file_name, real_frame_rate):

        # real framrate is the input framereate, while the -r is the output
        self.run_system_command(f"ffmpeg -framerate {real_frame_rate} -f image2 -s 1920x1080 -i {self.temp_location}/{file_name}%d.png -vcodec libx264 -crf 20 -vf \"crop=trunc(iw/2)*2:trunc(ih/2)*2\" -pix_fmt yuv420p -r {self.frame_rate} -s 1920x1080 {self.output_dir}/{file_name}.mp4 -y ", silent=True);

        # self.run_system_command(f"ffmpeg -framerate 1 -y -pattern_type glob -i '{self.temp_location}/{file_name}*.png' -c:v libx264 -r 30 -pix_fmt yuv420p -vf \"crop=trunc(iw/2)*2:trunc(ih/2)*2\" {self.temp_location}/{file_name}.mp4");
        # ffmpeg.input(f'{self.temp_location}/{file_name}*.png', pattern_type='glob', framerate=1).filter_('pad', w='ceil(in_w/2)*2', h='ceil(in_h/2)*2').output(f"{output_loc}/{file_name}.mp4", pix_fmt="yuv420p" ).run(overwrite_output=True, quiet=False);
        # self.run_system_command("


    def make_image_from_code(self, code, file_name, index_of_image, number_of_copies=1): # index is for the video file
        
        extension =  file_name.split(".")[-1]; # get the file extension
        with open(f"{self.temp_location}/temp_code.txt", "w") as text_file:
            print(code, file=text_file, end="")
        self.run_system_command(f"{self.silicon_command}/{file_name}{index_of_image}.png --language {extension}"); # make master copy


        # for i in range(0, number_of_copies): #copy it as many times as needed
        #     self.run_system_command(f"cp {self.temp_location}/{file_name}.png {self.temp_location}/{file_name}{i+index_of_image}.png");
        #
        # self.run_system_command(f"rm {self.temp_location}/{file_name}.png"); # delete origirnal to avoid confusion

    def clean_temp_directory(self):
        try:
            self.temp_dir_object.cleanup();
            shutil.rmtree(self.temp_dir_object.name);
        except Exception as e:
            pass;

        self.temp_dir_object = tempfile.TemporaryDirectory();
        self.temp_location = self.temp_dir_object.name;
        if(self.verbose):
            print("Temp location: ",self.temp_location);

    def is_tool(self, name):
        from shutil import which
        return which(name) is not None



class ListGitCommitsAction(argparse.Action):
    def __init__(self, option_strings, dest, nargs=0, **kwargs):
        super(ListGitCommitsAction, self).__init__(option_strings, dest,nargs, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        initial_print_text = center_wrap(f"Here are some of you recent commits :") ;
        print("Generate a list like this with " +  colored("git ll, or git log --pretty=format:\"%h %s\"","white" ));
        cprint(initial_print_text);
        cprint("Hash    Commit", "white" );
        try:
            print(str(subprocess.check_output("git log --pretty=format:\"%h %s\"", shell=True, text=True).center(50)))
        except:
            throw_git_not_found_error();

        later_help_text = colored("After you have picked your starting and ending commit, you can run ","blue") + colored('\nvideogit <inital_commit_hash> <final_commit_hash>\n', 'white')  + colored(" to render your video, alternativly you can leave the final commit out and videogit will use the most recent commit.To see full options type: ", "blue") + colored("videogit -h", "white");
        later_help_text = center_wrap(later_help_text, cwidth=80, width=70);
        print(later_help_text);

        sys.exit();

def center_wrap(text, cwidth=80, **kw):
    lines = textwrap.wrap(text, **kw)
    return "\n".join(line.center(cwidth) for line in lines)
def throw_git_not_found_error():
     cprint("No Git Repo Found!!, try moving to a folder with a git repo, or setting your git repo directory with -d", "red");


if __name__ == "__main__":
    nv = videogit();


def run():
    nv = videogit();
