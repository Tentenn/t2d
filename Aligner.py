# Implements the Aligner Class. It handles SVG file creation
#
import random
import re
import string
import time
from utils import get_filename
import datetime
import os
import datetime
import sys
import subprocess
import base64

class Aligner():
    def __init__(self):
        self.effect_path = os.getcwd() + "\\data\\effects\\"
        self.out = os.getcwd() + "\\data\\out\\"
        self.y_offset_start = 100
        self.y_offset = 200
        self.template_raw = self._get_template_text()
        self.disable_banner = False

    def set_disable_banner(self, bl):
        self.disable_banner = bl


    def get_new_design(self, textline, effects):
        template_text = self.template_raw
        print(f"[{str(datetime.datetime.now()).split('.')[0]}] Processing {textline}")
        # print(f"Templace effects: '{effects}'")
        t0 = time.time()
        # for each effect/text
        y_plus = self.y_offset  # offset after each line of text
        arguments = []
        for i, effect in enumerate(effects):
            arguments.append((effect, y_plus, textline, i, self.effect_path))
            y_plus += self.y_offset

        r_string_list = map(self.get_effect_format, arguments)

        for r_string in r_string_list:
            template_text = template_text.replace("</svg>", r_string)
        print(f"[{str(datetime.datetime.now()).split('.')[0]}] Replacing done")

        final_svg_name = get_filename(textline, effects)
        filepath = self.out + final_svg_name
        with open(filepath, "w") as f:
            f.write(template_text)
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

    def get_effect_format(self, arguments):
        effect, y_plus, text, i, effect_path = arguments
        # print(arguments)
        try:
            print(f"[{str(datetime.datetime.now()).split('.')[0]}] Handling '{text[i]}'")
        except IndexError:
            print("ERROR IndexError in get_effect_format()")
            print(f"Arguments: '{arguments}'")
            assert False, "see above"

        # TODO: EXTRACT LINEAR GRADIENT AND INSERT INTO template text
        with open(effect_path + effect, "r") as fx:
            fxraw = fx.read().replace("!!EFFECT!!", text[i])  # Text that is appended

        # find right fontsize
        # TODO: DEBUG # insert_text, x, y, w, h, need_filler = get_right_fontsized_text(fxraw)
        # insert_text, x, y, w, h, need_filler = get_right_fontsized_text2(fxraw)
        insert_text, x, y, w, h, need_filler = self.get_right_fontsized_text(fxraw)
        contents = ""

        # y wird hier nochmal verändert
        y_updated, replace_list = self.replace_y(insert_text, text[i], y_plus)
        for e in replace_list:
            insert_text = insert_text.replace(*e)
            # Extract def (g) pattern <g </g> <g\s|.*<\/g>
            contents = insert_text[insert_text.find("<g") + 1:insert_text.find("</g>")]

        return_text = "<" + contents + "</g>\n</svg>"

        # need_filler = False
        if not self.disable_banner:
            if need_filler:
                # print("Adding filler... ")
                iid, filler = self.get_filler()
                return_text = self.add_filler(x, y_updated, w, h, contents, filler, iid)
                return_text = self.align_filler(return_text)

        return return_text

    def get_right_fontsized_text(self, i_text):
        STEP = 40
        # i_text = inserted text of effect svg
        tmp_folder = os.getcwd() + "/data/tmp/"
        tmp_file = tmp_folder + f"{self.get_rand_string()}_tmp.svg"
        with open(tmp_file, "w") as f:
            f.write(i_text)
        x, y, w, h = self.get_dim_svg2(tmp_file)  # of .svg file (only single textlayer erlaubt!)
        # print("ink: ",x, y, w, h)
        # print("cairo: ", *tuple(round(float(e), 3) for e in get_dim_itext(i_text)[:4]))
        # print()
        fsize = float(self.get_fontsize(i_text))
        insert_text = i_text
        if w < 4200:
            # print("too small")
            while w < 3800:
                old_fsize = fsize
                # make font bigger
                fsize += STEP
                # check if font size ok (update template text and find w)
                insert_text = insert_text.replace(str(old_fsize), str(fsize))
                with open(tmp_file, "w") as f:
                    f.write(insert_text)
                x, y, w, h = self.get_dim_svg2(tmp_file)
                # print("ink: ", x, y, w, h)
                # print("cairo: ", *tuple(round(float(e), 3) for e in get_dim_itext(insert_text)[:4]))
                # print()
                if h > 180:
                    break
                # print(f"updated font. Now w={w} with fsize={fsize}")
        elif w > 4400:
            # print(w, "Too big")
            while w > 4400:
                old_fsize = fsize
                fsize -= STEP
                # check if font size ok (update template text and find w)
                insert_text = insert_text.replace(str(old_fsize), str(fsize))
                with open(tmp_file, "w") as f:
                    f.write(insert_text)
                x, y, w, h = self.get_dim_svg2(tmp_file)
                # print("ink: ", x, y, w, h)
                # print("cairo: ", *tuple(round(float(e), 3) for e in get_dim_itext(insert_text)[:4]))
                # print()
                if h < 180:
                    break
                # print(f"updated font. Now w={w}")
        # print(f"Size OK. Now w={w} with fsize={fsize}")
        # TODO: maybe check after too big if too small
        # print(f"tmp file deleted: '{tmp_file}'")
        need_filler = True if w < 3300 else False

        os.remove(tmp_file)
        return insert_text, x, y, w, h, need_filler

    def get_dim_svg2(self, file, it=0, rec=False):
        if rec:
            it += 1
        if rec and it == 20:
            assert False, "Tried 20 times. Didn't work. Closing down."
        # p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        try:
            cmd = f'"C:/Programme/Inkscape/bin/inkscape.exe" {file} --actions="select-all:layers;query-all;file-close;quit-inkscape"'
            p = subprocess.run(cmd, text=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=2.5)
            # print(p.stderr)
            dim = p.stdout
            return (float(e) for e in dim.split("\n")[0].split(",")[1:])
        except subprocess.TimeoutExpired:
            print(
                "########################## Timeout Expired, sorry #######################################################")
            return self.get_dim_svg2(file, it=it, rec=True)

    def replace_y(self, ytext, text2, y_plus):
        y_pat = 'y="[0-9]*\.[0-9]*">' + text2
        ycoords_str_list = re.findall(y_pat, ytext)
        # print(ycoords_str_list)
        replacelist = []
        y_updated = -1  # needed for updating the y in the filler segment. Otherwise filler and text will not align
        for e in ycoords_str_list:
            y = self.ytext2float(e) + y_plus
            if y_updated == -1:
                y_updated = y
            replacelist.append((str(self.ytext2float(e)), str(y)))
        return y_updated, replacelist

    def align_filler(self, return_text):
        # aligns the text and the filler
        # read tempalte
        with open(self.effect_path + "startertemplate.svg", "r") as t:
            tmpl = t.read()
        # make use template and retuntext to make file
        new_tmpl = tmpl.replace("</svg>", return_text)
        ## align file
        # Aligning filler
        with open(self.effect_path + "tmp_startertemplate.svg", "w") as st:
            st.write(new_tmpl)
        st_tmp = self.effect_path + "tmp_startertemplate.svg"
        cmd = f'"C:/Programme/Inkscape/bin/inkscape.exe" {st_tmp} --actions="select-all;object-align:vcenter biggest;export-do;file-close"'
        # print("aligning filler")
        p = subprocess.run(cmd, text=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        std = p.stdout
        # read sligned file, return new returned_text
        with open(self.effect_path + "tmp_startertemplate_out.svg", "r") as aligned:
            insert_text = aligned.read()
            contents = insert_text[insert_text.find(f"<g") + 1:insert_text.find("</g>")]
            return_text = "<" + contents + "</g>\n</svg>"

        os.remove(st_tmp)
        os.remove(self.effect_path + "tmp_startertemplate_out.svg")
        return return_text

    def add_filler(self, x_ef, y_ef, w_ef, h_ef, contents, filler, iid):
        # add left
        x_p_l, y_p_l, w_p_l, h_p_l = self.get_xywh(x_ef, y_ef, w_ef, h_ef, side="left")
        left_filler_base64 = self.get_base64_str(filler.replace(".png", "l.png"))
        img_svg_str_left = self.make_png_string(x_p_l, y_p_l, w_p_l, h_p_l, left_filler_base64, iid)
        # add right
        x_p_r, y_p_r, w_p_r, h_p_r = self.get_xywh(x_ef, y_ef, w_ef, h_ef, side="right")
        right_filler_base64 = self.get_base64_str(filler.replace(".png", "r.png"))
        img_svg_str_right = self.make_png_string(x_p_r, y_p_r, w_p_r, h_p_r, right_filler_base64, iid)
        # print(x_ef)

        # print(img_svg_str_right)
        assembled = "<" + contents + "\n\t" + img_svg_str_left + "\n\t" + img_svg_str_right + "\n</g>\n</svg>"
        # assembled = f'<g\n<g\nid="g-{get_rand_string(3)}">' + contents[1:] + "</g>" + "\n\t" + img_svg_str_left + "\n\t" + img_svg_str_right + "\n</g>\n</svg>"
        # print("ASSEMBLED: ")
        # print(assembled)
        return assembled

    def get_filler(self):
        filler = self.effect_path + f"f{random.choice(range(1, 9))}.png"
        # print("DEBUG USING NON RANDOM FILLER")
        # filler = f"effects/f5.png"
        iid = filler.split("\\")[1].replace(".png", "") + "-" + self.get_rand_string(4)
        return iid, filler

    def get_xywh(self, x, y, w, h, side="left"):
        dk = 0.26458334
        margin = 30
        half_len = (4300 - w) / 2
        if side == "left":
            xt = x * dk - half_len * dk
            yt = y - (h * dk)
            wt = half_len * dk - margin
            ht = h * dk
        elif side == "right":
            xt = x * dk + w * dk + margin
            yt = y - (h * dk)
            wt = half_len * dk - margin
            ht = h * dk
        else:
            print(f"ERROR IN get_xywh(): {side} not recognized.")
            sys.exit(1)
        return xt, yt, wt, ht

    def get_base64_str(self, image_file):
        with open(image_file, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            return encoded_string.decode()

    def make_png_string(self, x, y, w, h, content, iid):
        imagedata = f'\t<image\n\t\t' \
                    f'width="{w}"\n\t\t' \
                    f'height="{h}"\n\t\t' \
                    f'preserveAspectRatio="none"\n\t\t' \
                    f'xlink:href="data:image/png;base64,{content}"\n\t\t' \
                    f'id="image{iid}"\n\t\t' \
                    f'x="{x}"\n\t\t' \
                    f'y="{y}"\n\t\t' \
                    f'/>'
        return imagedata

    def ytext2float(self, e):
        return float(e.split("=")[1].split(">")[0].replace('"', ""))

    def get_rand_string(self, k=8):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=k))

    def get_fontsize(self, i_text):
        r_str = "font-size:[0-9]*\.[0-9]*px"
        matches = re.findall(r_str, i_text)
        return matches[0][10:-2]