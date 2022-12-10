# Implements the Aligner Class. It handles SVG file creation
#

import time
from utils import get_effect_format, get_filename
import datetime
import os

class Aligner():
    def __init__(self):
        self.effect_path = os.getcwd() + "\\data\\effects\\"
        self.out = os.getcwd() + "\\data\\out\\"
        self.y_offset_start = 100
        self.y_offset = 200
        self.template_text = self._get_template_text()

    def get_new_design(self, textline, effects):
        print(f"[{str(datetime.datetime.now()).split('.')[0]}] Processing {textline}")
        # print(f"Templace effects: '{effects}'")
        t0 = time.time()
        # for each effect/text
        y_plus = self.y_offset  # offset after each line of text
        arguments = []
        for i, effect in enumerate(effects):
            arguments.append((effect, y_plus, textline, i, self.effect_path))
            y_plus += self.y_offset

        r_string_list = map(get_effect_format, arguments)

        for r_string in r_string_list:
            self.template_text = self.template_text.replace("</svg>", r_string)
        print(f"[{str(datetime.datetime.now()).split('.')[0]}] Replacing done")

        final_svg_name = get_filename(textline, effects)
        filepath = self.out + final_svg_name
        with open(filepath, "w") as f:
            f.write(self.template_text)
        self._align_svg_file(self.out + final_svg_name)
        t1 = time.time()
        print(f"[{str(datetime.datetime.now()).split('.')[0]}] Finished {final_svg_name} in {round(t1 - t0)} seconds\n")

    def _align_svg_file(self, file):
        # print("align and distribute")
        cmd = f'"C:/Program Files/Inkscape/bin/inkscape.exe" {file} --actions="select-all:layers;object-align:hcenter page;object-distribute:vgap;export-do;file-close"'
        stream = os.popen(cmd)
        t = stream.read()
        os.remove(file)
        # print("DEBUG NOT DELETING IN ALIGN FUNCTION")
        print("Align and Distribute successful.")

    def _get_template_text(self):
        with open(self.effect_path + "startertemplate.svg", "r") as st:
            return st.read()
