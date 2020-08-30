
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
chars_per_second = 3;


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
            # print(diff_of_file);
            self.handle_file_diffs(inital_file, diff_of_file)


    def handle_file_diffs(self, inital_file, diff_of_file):
        lines_of_diffs = str.split(diff_of_file, "\n");
        file_name = lines_of_diffs[2][5:] # get second line (has filename) and remove the - space spcae
        file_name = file_name.split("/")[len(file_name.split("/")) - 1] # remove the directory like /gg/gg/g and just get the last part

        lines_of_diffs = lines_of_diffs[5:] # remove the first 3 lines, becuase its just location info
        print(f"Starting file {file_name}");


        lines_without_diff = lines_of_diffs;
        changed_lines_dict = {}; # we need to store this so we can add them later

        indices_of_lines_to_be_removed = []; # this keeps track of the index of all the lines were going to remove


        for i, line in enumerate(lines_of_diffs): # first remove all of the - lines, so we dont mess up the line numbers
            if(len(line) > 0 and line[0] == "-"): # remove the -  
                line = " " + line[1:]; # remove the -
                changed_lines_dict[i] = line; # add it to thhe list keeping track
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


        self.handle_file_incrementing(lines_without_diff, changed_lines_dict,indices_of_lines_to_be_removed, file_name);



    def handle_file_incrementing(self, file_in_list_form, lines_to_be_added, indices_of_lines_to_be_removed, file_name):
        self.clean_temp_directory();
        index_of_images = 0; # for creating the video frames
        index_of_images+=1;
        completed_code_buffer = [];
        longest_line = 0;

        frames_per_char = int(frame_rate / chars_per_second);

        for line_number, line in lines_to_be_added.items():
            number_of_frames_needed = int((len(line) / chars_per_second) * frame_rate); # how many frames needed to add/remove line
            for i in range(0,number_of_frames_needed, frames_per_char):
                if line_number in indices_of_lines_to_be_removed: # check if its marked to be removed
                    # handle_image_creation_remove_line();
                    if len(line) >0:
                        line = line[:-1]; # remove last chharater
                        file_in_list_form[line_number] = line;
                else:
                    if len(line) > 0:
                        file_in_list_form[line_number] = file_in_list_form[line_number] + line[0] # add line
                        line = line[1:]

                full_code = list(filter(None, file_in_list_form)) # remove the "" marker used before
                full_code = "\n".join(full_code); # add newlines and make it in to string
                full_code = re.sub(r'@@(.*?)@@', "", full_code); # this regex is to remove the git hulls which are @@ int ... @@

                # find longest line so we space all images evenly
                new_line_count = full_code.count("\n"); 
                if new_line_count > longest_line:
                    longest_line = new_line_count;

                completed_code_buffer.append(full_code);


        self.convert_completed_code_to_video(completed_code_buffer, file_name, frames_per_char, longest_line);




    
    def convert_completed_code_to_video(self, completed_code_buffer, file_name, frames_per_char, longest_line):
        for i, code in enumerate(completed_code_buffer):
            # add any extra line breaks needed to even  all images
            new_line_count = code.count("\n");
            extra_lines_needed = longest_line - new_line_count;
            while extra_lines_needed > 0:
                code += "\n";
                extra_lines_needed -=1;
            self.make_image_from_code(code, file_name, i, frames_per_char)

        self.convert_images_to_video(file_name, real_frame_rate=(frames_per_char * chars_per_second) );
        self.clean_temp_directory();
    # def handle_image_creation_add_line(self, line:

    def convert_images_to_video(self, file_name, real_frame_rate):

        print(self.run_system_command("pwd"));
        self.run_system_command(f"ffmpeg -r {real_frame_rate} -f image2 -s 1920x1080 -i {temp_location}/{file_name}%d.png -vcodec libx264 -crf {20} -vf \"crop=trunc(iw/2)*2:trunc(ih/2)*2\" -pix_fmt yuv420p {temp_location}/{file_name}.mp4 -y");

        # self.run_system_command(f"ffmpeg -framerate 1 -y -pattern_type glob -i '{temp_location}/{file_name}*.png' -c:v libx264 -r 30 -pix_fmt yuv420p -vf \"crop=trunc(iw/2)*2:trunc(ih/2)*2\" {temp_location}/{file_name}.mp4");
        # ffmpeg.input(f'{temp_location}/{file_name}*.png', pattern_type='glob', framerate=1).filter_('pad', w='ceil(in_w/2)*2', h='ceil(in_h/2)*2').output(f"{output_loc}/{file_name}.mp4", pix_fmt="yuv420p" ).run(overwrite_output=True, quiet=False);
        # self.run_system_command("


    def make_image_from_code(self, code, file_name, index_of_image, number_of_copies=1): # index is for the video file
        # try:
        #     self.run_system_command("mkdir temp-img") # todo move this to its proper place
        # except:
        #     pass;
        #TODO: use stdin to optimise
        with open("temp_code.txt", "w") as text_file:
            print(code, file=text_file, end="")
        self.run_system_command(f"{silicon_command}/{file_name}{index_of_image}.png"); # make master copy

        
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



