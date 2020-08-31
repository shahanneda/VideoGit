
import os
import subprocess
import re
import sys;
import math;
import argparse


get_log_command = "git log --pretty=format:\"%h %s\"";
temp_location = "temp-img"
output_loc = temp_location;
silicon_command = f"silicon {temp_location}/temp_code.txt --no-line-number --output {temp_location}/";
batcmd="git status"
commit1="9c537ab"
commit2="4457a38"

wpm = 480;
chars_per_second = wpm * 5 / 60; #5 char/word * 1min/60sec
up_down_space = 20;
max_line_length = 140;


frame_rate = 30;
class ncodevideo:
    def run_system_command(self, command, silent=False):
        #, stderr=subprocess.DEVNULL
        return subprocess.check_output(command, shell=True, text=True)

    def dir_path(self, string): # this is just for argparse
        if os.path.isdir(string) or string == "current directory":
            return string
        else:
            raise NotADirectoryError(string)
        
    def handle_args(self):
        parser = argparse.ArgumentParser(description='Process some integers.', 
                formatter_class=argparse.ArgumentDefaultsHelpFormatter # to show the default values
                );

        parser.add_argument('inital-commit', type=str, help='the commit to start the video at')
        parser.add_argument('final-commit', type=str, nargs='?', default="the last commit", help='the commit to end the video at, if not specified will use the HEAD')
        parser.add_argument('-w','--wpm', type=int, default="480", help='the speed of the video in words per minute')
        parser.add_argument('-f','--frame-rate', type=int, default="30", help='the framerate of the output video')
        parser.add_argument('-o','--output-dir', type=self.dir_path, default="current directory", help='the framerate of the output video')
        parser.add_argument('-d','--git-repo-directory', type=self.dir_path, default="current directory", help='the repo of ')

        args = parser.parse_args()
        print(args.inital-commit, args.final-commit);


    def __init__(self):
        print("\n\n" + "-------- VideoGit --------".center(50), end="\n\n");
        self.handle_args();
        find_changed_file_paths = f"git diff --name-only {commit1}..{commit2}";
        file_paths = str.split(self.run_system_command(find_changed_file_paths), "\n");
        file_paths = list(filter(None, file_paths)) # remove empty strings

        self.find_and_go_through_commits(commit1, commit2, file_paths);


    def find_and_go_through_commits(self, starting_commit, ending_commit, file_paths):
        all_commits = [starting_commit];
        all_commits += reversed(self.run_system_command(f"git rev-list --abbrev-commit --ancestry-path {starting_commit}..{ending_commit}").split("\n")[:-1])

        print(all_commits);
        self.loop_through_file_paths(file_paths, all_commits);

    def loop_through_file_paths(self, file_paths, all_commits):
        for file_path in file_paths: 
            file_name = file_path.split("/")[len(file_path.split("/")) - 1] # remove the directory like /gg/gg/g and just get the last part
            completed_code_buffer = [];

            for i, commit in enumerate(all_commits[:-1]):
                try:
                    diff_of_file = self.run_system_command(f"git diff -U999999 {commit}..{all_commits[i+1]} {file_path}") # the -U is to make sure we get the entire file
                    completed_code_buffer += self.handle_file_diffs(diff_of_file, file_name)
                except:
                    print("Failed to open file: " + file_path);
                    continue;

            try:
                self.convert_completed_code_to_video(completed_code_buffer, f"{file_name}-all_commits[0]--all_commits[-1]");
            except KeyboardInterrupt:
                print("\n");
                sys.exit(0);
            except:
                print(f"Could not create video for {file_name}");


    def handle_file_diffs(self, diff_of_file, file_name):
        lines_of_diffs = str.split(diff_of_file, "\n");
        lines_of_diffs = lines_of_diffs[5:] # remove the first 3 lines, becuase its just location info

        # handle very long line wrapping
        for i, line in enumerate(lines_of_diffs):
            if len(line) > max_line_length:
                first_non_whitespace = len(line) - len(line.lstrip());
                white_space = line[:first_non_whitespace];
                after_wrap = line[max_line_length:];
                lines_of_diffs[i] = f"{line[:max_line_length]}\n{white_space}{after_wrap}"; # add the lien wrap

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
        self.clean_temp_directory();
        index_of_images = 0; # for creating the video frames
        index_of_images+=1;
        completed_code_buffer = [];
        longest_line = 0;

        frames_per_char = frame_rate / chars_per_second;

        real_frame_rate = frame_rate/ frames_per_char;
        print(f" framerate: {frame_rate}, frames_per_char: {frames_per_char} chars_per_second: {chars_per_second} real_frame_rate: {real_frame_rate}");
        for line_number, line in lines_to_be_added.items():
            # number_of_frames_needed = int((len(line) / chars_per_second) * frame_rate); # how many frames needed to add/remove line
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
                full_code = full_code[max(0, (line_number - up_down_space)):(line_number + up_down_space)]; # only show the seciton we are changing, not the entire file


                full_code = "\n".join(full_code); # add newlines and make it in to string
                # print("\n\n\n\n" + full_code);
                full_code = re.sub(r'@@(.*?)@@', "", full_code); # this regex is to remove the git hulls which are @@ int ... @@

                # find longest line so we space all images evenly
                new_line_count = full_code.count("\n"); 
                if new_line_count > longest_line:
                    longest_line = new_line_count;

                completed_code_buffer.append(full_code);




        return completed_code_buffer;






    def convert_completed_code_to_video(self, completed_code_buffer, file_name):
        frames_per_char = frame_rate / chars_per_second;

        real_frame_rate = frame_rate / frames_per_char;
        for i, code in enumerate(completed_code_buffer):
            # add any extra line breaks needed to even  all images
            # new_line_count = code.count("\n");
            # extra_lines_needed = longest_line - new_line_count;
            # while extra_lines_needed > 0:
            #     code += "\n";
            #     extra_lines_needed -=1;
            self.make_image_from_code(code, file_name, i, frames_per_char)

            #progress bar
            sys.stdout.write('\r');
            max_size = 100;
            progress = int(max_size * float(i/len(completed_code_buffer)));
            bar = "█" * progress;
            bar = bar + "-" * (max_size-progress);
            sys.stdout.write(f"{file_name}: Creating Image {i} of {len(completed_code_buffer)} *** [{bar}]");
            sys.stdout.flush();

        self.convert_images_to_video(file_name, real_frame_rate=real_frame_rate );
        self.clean_temp_directory();
    # def handle_image_creation_add_line(self, line:

    def convert_images_to_video(self, file_name, real_frame_rate):

        print(self.run_system_command("pwd"));
        # real framrate is the input framereate, while the -r is the output
        self.run_system_command(f"ffmpeg -framerate {real_frame_rate} -f image2 -s 1920x1080 -i {temp_location}/{file_name}%d.png -vcodec libx264 -crf 20 -vf \"crop=trunc(iw/2)*2:trunc(ih/2)*2\" -pix_fmt yuv420p -r {frame_rate} {temp_location}/{file_name}.mp4 -y");

        # self.run_system_command(f"ffmpeg -framerate 1 -y -pattern_type glob -i '{temp_location}/{file_name}*.png' -c:v libx264 -r 30 -pix_fmt yuv420p -vf \"crop=trunc(iw/2)*2:trunc(ih/2)*2\" {temp_location}/{file_name}.mp4");
        # ffmpeg.input(f'{temp_location}/{file_name}*.png', pattern_type='glob', framerate=1).filter_('pad', w='ceil(in_w/2)*2', h='ceil(in_h/2)*2').output(f"{output_loc}/{file_name}.mp4", pix_fmt="yuv420p" ).run(overwrite_output=True, quiet=False);
        # self.run_system_command("


    def make_image_from_code(self, code, file_name, index_of_image, number_of_copies=1): # index is for the video file
        # try:
        #     self.run_system_command("mkdir temp-img") # todo move this to its proper place
        # except:
        #     pass;
        #TODO: use stdin to optimise
        extension =  file_name.split(".")[-1]; # get the file extension
        with open(f"{temp_location}/temp_code.txt", "w") as text_file:
            print(code, file=text_file, end="")
        self.run_system_command(f"{silicon_command}/{file_name}{index_of_image}.png --language {extension}"); # make master copy


        # for i in range(0, number_of_copies): #copy it as many times as needed
        #     self.run_system_command(f"cp {temp_location}/{file_name}.png {temp_location}/{file_name}{i+index_of_image}.png");
        #
        # self.run_system_command(f"rm {temp_location}/{file_name}.png"); # delete origirnal to avoid confusion

    def clean_temp_directory(self):
        try:
            self.run_system_command(f"rm {temp_location}/*.png");
            pass;
        except:
            pass;



nv = ncodevideo();



