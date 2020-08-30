
import subprocess
import re
import ffmpeg


get_log_command = "git log --pretty=format:\"%h %s\"";
temp_location = "temp-img"
output_loc = temp_location;
silicon_command = f"silicon temp_code.txt --language cpp --output {temp_location}/";
batcmd="git status"
commit1="700043f"
commit2="3f8d661"


frame_rate = 30;
class ncodevideo:
    def run_system_command(self, command):
        return subprocess.check_output(command, shell=True, text=True)

    def __init__(self):
        find_changed_file_paths = f"git diff --name-only {commit1}..{commit2}";
        file_paths = str.split(self.run_system_command(find_changed_file_paths), "\n");
        file_paths = list(filter(None, file_paths)) # remove empty strings

        self.loop_through_file_paths(file_paths, commit1, commit2);


    def loop_through_file_paths(self, file_paths, starting_commit, ending_commit):
        for file_path in file_paths:
            try:
                inital_file = self.run_system_command(f"git show {starting_commit}:{file_path}");
                diff_of_file = self.run_system_command(f"git diff {starting_commit}..{ending_commit} {file_path}")
            except:
                print("Failed to open file: " + file_path);
                continue;
            print(diff_of_file);
            self.handle_file_diffs(inital_file, diff_of_file)


    def handle_file_diffs(self, inital_file, diff_of_file):
        lines_of_diffs = str.split(diff_of_file, "\n");
        file_name = lines_of_diffs[2][5:] # get second line (has filename) and remove the - space spcae
        file_name = file_name.split("/")[len(file_name.split("/")) - 1] # remove the directory like /gg/gg/g and just get the last part

        lines_of_diffs = lines_of_diffs[5:] # remove the first 3 lines, becuase its just location info


        lines_without_diff = lines_of_diffs;
        changed_lines_dict = {}; # we need to store this so we can add them later

        indices_of_lines_to_be_removed = []; # this keeps track of the index of all the lines were going to remove


        for i, line in enumerate(lines_of_diffs): # first remove all of the - lines, so we dont mess up the line numbers
            if(len(line) > 0 and line[0] == "-"): # remove the -  
                # line = line[1:]; # remove the -
                changed_lines_dict[i] = line; # add it to thhe list keeping track
                indices_of_lines_to_be_removed.append(i); # special marker for later so we know to remove the line

            elif(len(line) > 0 and line[0] == "+"): # remove the lines that have addidiotsn, were going to add them later
                # line = line[1:]
                changed_lines_dict[i] =  line;


        # remove all the lines queed up in changed_lines_dict , if it is in the change lines, we should remove it since we will ad it later, unless it is marked to be remved, then we should not remove it since we want to see it fade
        for i, line in enumerate(lines_of_diffs):
            if(i not in changed_lines_dict or i in indices_of_lines_to_be_removed):
                lines_without_diff[i] = line;
            else:
               lines_without_diff[i] = ""; #put blank line since we will want to add it later and dont want to mess up the notation


        self.handle_file_incrementing(lines_without_diff, changed_lines_dict,indices_of_lines_to_be_removed, file_name);



    def handle_file_incrementing(self, file_in_list_form, lines_to_be_added, indices_of_lines_to_be_removed, file_name):
        self.clean_temp_directory();
        index_of_images = 0; # for creating the video frames
        index_of_images+=1;
        completed_code_buffer = [];
        longestLine = 0;

        for line_number, line in lines_to_be_added.items():
            if line_number in indices_of_lines_to_be_removed: # check if its marked to be removed
                line = ""; # we set it to blank so it doesnt mess up the line numbers in the array
                file_in_list_form[line_number] = "";
            else:
                file_in_list_form[line_number] = line # add line

            full_code = list(filter(None, file_in_list_form)) # remove the "" marker used before
            full_code = "\n".join(full_code); # add newlines and make it in to string
            full_code = re.sub(r'@@(.*?)@@', "", full_code); # this regex is to remove the git hulls which are @@ int ... @@

            # find longest line so we space all images evenly
            newLineCount = full_code.count("\n"); 
            if newLineCount > longestLine:
                longestLine = newLineCount;

            completed_code_buffer.append(full_code);


        for i, code in enumerate(completed_code_buffer):
            # add any extra line breaks needed to even  all images
            newLineCount = code.count("\n");
            extraLinesNeeded = longestLine - newLineCount;
            while extraLinesNeeded > 0:
                code += "\n";
                extraLinesNeeded -=1;


            self.make_image_from_code(code, file_name, i)

        self.convert_images_to_video(file_name);
        self.clean_temp_directory();


    def convert_images_to_video(self, file_name):

        ffmpeg.input(f'{temp_location}/{file_name}*.png', pattern_type='glob', framerate=5).filter_('pad', w='ceil(in_w/2)*2', h='ceil(in_h/2)*2').output(f"{output_loc}/{file_name}.mp4", pix_fmt="yuv420p" ).run(overwrite_output=True, quiet=False);
        # self.run_system_command("


    def make_image_from_code(self, code, file_name, index_of_image): # index is for the video file
        # try:
        #     self.run_system_command("mkdir temp-img") # todo move this to its proper place
        # except:
        #     pass;
        #TODO: use stdin to optimise
        with open("temp_code.txt", "w") as text_file:
            print(code, file=text_file, end="")
        self.run_system_command(silicon_command + file_name + str(index_of_image) + ".png");

    def clean_temp_directory(self):
        try:
            # self.run_system_command(f"rm {temp_location}/*.png");
            pass;
        except:
            pass;



nv = ncodevideo();



