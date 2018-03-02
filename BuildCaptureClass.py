# AUTHOR: CONG WANG
# DATE: 2017/3/12

import os

# THE CLASS OF BUILDING CAPTURE
class BuildCaptureClass:
    # INIT FUNCTION
    def __init__(self, input_folder, output_folder, shell):
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.all_file = os.path.join(output_folder, "all")
        self.line_in_all = 0
        self.output_file = os.path.join(output_folder, "output")
        self.line_in_output = 0
        self.shell = shell
        self.fs_folder = os.path.join(input_folder, "../BCFILES")