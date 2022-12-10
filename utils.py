import datetime
import sys
import os
import re
import subprocess
import random
import string
import base64
import hashlib

EFFECTS_PATH = os.getcwd() + "/data/effects/"


def get_effect_format(arguments):
    effect, y_plus, text, i, effect_path = arguments
    # print(arguments)
    try:
        print(f"[{str(datetime.datetime.now()).split('.')[0]}] Handling '{text[i]}'")
    except IndexError:
        print("ERROR IndexError in get_effect_format()")
        print(f"Arguments: '{arguments}'")
        sys.exit(1)

    # TODO: EXTRACT LINEAR GRADIENT AND INSERT INTO template text
    with open(effect_path + effect, "r") as fx:
        fxraw = fx.read().replace("!!EFFECT!!", text[i])  # Text that is appended

    # find right fontsize
    # TODO: DEBUG # insert_text, x, y, w, h, need_filler = get_right_fontsized_text(fxraw)
    # insert_text, x, y, w, h, need_filler = get_right_fontsized_text2(fxraw)
    insert_text, x, y, w, h, need_filler = get_right_fontsized_text(fxraw)
    contents = ""

    # y wird hier nochmal verändert
    y_updated, replace_list = replace_y(insert_text, text[i], y_plus)
    for e in replace_list:
        insert_text = insert_text.replace(*e)
        # Extract def (g) pattern <g </g> <g\s|.*<\/g>
        contents = insert_text[insert_text.find("<g") + 1:insert_text.find("</g>")]

    return_text = "<" + contents + "</g>\n</svg>"

    # need_filler = False
    if need_filler:
        # print("Adding filler... ")
        iid, filler = get_filler()
        return_text = add_filler(x, y_updated, w, h, contents, filler, iid)
        return_text = align_filler(return_text)

    return return_text

def get_rand_string(k=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=k))

def get_fontsize(i_text):
    r_str = "font-size:[0-9]*\.[0-9]*px"
    matches = re.findall(r_str, i_text)
    return matches[0][10:-2]

def get_right_fontsized_text(i_text):
    STEP = 40
    # i_text = inserted text of effect svg
    tmp_folder = os.getcwd() + "/data/tmp/"
    tmp_file = tmp_folder + f"{get_rand_string()}_tmp.svg"
    with open(tmp_file, "w") as f:
        f.write(i_text)
    x, y, w, h = get_dim_svg2(tmp_file)  # of .svg file (only single textlayer erlaubt!)
    # print("ink: ",x, y, w, h)
    # print("cairo: ", *tuple(round(float(e), 3) for e in get_dim_itext(i_text)[:4]))
    # print()
    fsize = float(get_fontsize(i_text))
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
            x, y, w, h = get_dim_svg2(tmp_file)
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
            fsize -= 20
            # check if font size ok (update template text and find w)
            insert_text = insert_text.replace(str(old_fsize), str(fsize))
            with open(tmp_file, "w") as f:
                f.write(insert_text)
            x, y, w, h = get_dim_svg2(tmp_file)
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

def ytext2float(e):
    return float(e.split("=")[1].split(">")[0].replace('"', ""))

def replace_y(ytext, text2, y_plus):
    y_pat = 'y="[0-9]*\.[0-9]*">' + text2
    ycoords_str_list = re.findall(y_pat, ytext)
    # print(ycoords_str_list)
    replacelist = []
    y_updated = -1  # needed for updating the y in the filler segment. Otherwise filler and text will not align
    for e in ycoords_str_list:
        y = ytext2float(e) + y_plus
        if y_updated == -1:
            y_updated = y
        replacelist.append((str(ytext2float(e)), str(y)))
    return y_updated, replacelist

def get_dim_svg2(file, it=0, rec=False):
    if rec:
        it+=1
    if rec and it==20:
        print("Tried 20 times. Didn't work. Closing down.")
        sys.exit(1)
    # p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    try:
        cmd = f'"C:/Programme/Inkscape/bin/inkscape.exe" {file} --actions="select-all:layers;query-all;file-close;quit-inkscape"'
        p = subprocess.run(cmd, text=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=2.5)
        # print(p.stderr)
        dim = p.stdout
        return (float(e) for e in dim.split("\n")[0].split(",")[1:])
    except subprocess.TimeoutExpired:
        print("########################## Timeout Expired, sorry #######################################################")
        return get_dim_svg2(file, it=it, rec=True)

def align_filler(return_text):
    # aligns the text and the filler
    # read tempalte
    with open(EFFECTS_PATH + "startertemplate.svg", "r") as t:
        tmpl = t.read()
    # make use template and retuntext to make file
    new_tmpl = tmpl.replace("</svg>", return_text)
    ## align file
    # Aligning filler
    with open(EFFECTS_PATH + "tmp_startertemplate.svg", "w") as st:
        st.write(new_tmpl)
    st_tmp = EFFECTS_PATH + "tmp_startertemplate.svg"
    cmd = f'"C:/Programme/Inkscape/bin/inkscape.exe" {st_tmp} --actions="select-all;object-align:vcenter biggest;export-do;file-close"'
    # print("aligning filler")
    p = subprocess.run(cmd, text=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    std = p.stdout
    # read sligned file, return new returned_text
    with open(EFFECTS_PATH + "tmp_startertemplate_out.svg", "r") as aligned:
        insert_text = aligned.read()
        contents = insert_text[insert_text.find(f"<g") + 1:insert_text.find("</g>")]
        return_text = "<" + contents + "</g>\n</svg>"

    os.remove(st_tmp)
    os.remove(EFFECTS_PATH + "tmp_startertemplate_out.svg")
    return return_text

def add_filler(x_ef, y_ef, w_ef, h_ef, contents, filler, iid):
    # add left
    x_p_l, y_p_l, w_p_l, h_p_l = get_xywh(x_ef, y_ef, w_ef, h_ef, side="left")
    left_filler_base64 = get_base64_str(filler.replace(".png", "l.png"))
    img_svg_str_left = make_png_string(x_p_l, y_p_l, w_p_l, h_p_l, left_filler_base64, iid)
    # add right
    x_p_r, y_p_r, w_p_r, h_p_r = get_xywh(x_ef, y_ef, w_ef, h_ef, side="right")
    right_filler_base64 = get_base64_str(filler.replace(".png", "r.png"))
    img_svg_str_right = make_png_string(x_p_r, y_p_r, w_p_r, h_p_r, right_filler_base64, iid)
    # print(x_ef)

    # print(img_svg_str_right)
    assembled = "<" + contents + "\n\t" + img_svg_str_left + "\n\t" + img_svg_str_right + "\n</g>\n</svg>"
    # assembled = f'<g\n<g\nid="g-{get_rand_string(3)}">' + contents[1:] + "</g>" + "\n\t" + img_svg_str_left + "\n\t" + img_svg_str_right + "\n</g>\n</svg>"
    # print("ASSEMBLED: ")
    # print(assembled)
    return assembled

def get_filler():
    filler = EFFECTS_PATH + f"f{random.choice(range(1,9))}.png"
    # print("DEBUG USING NON RANDOM FILLER")
    # filler = f"effects/f5.png"
    iid = filler.split("/")[1].replace(".png", "") + "-" + get_rand_string(4)
    return iid, filler

def get_xywh(x, y, w, h, side="left"):
    dk = 0.26458334
    margin = 30
    half_len = (4300 - w) / 2
    if side == "left":
        xt = x*dk - half_len*dk
        yt = y - (h*dk)
        wt = half_len*dk - margin
        ht = h*dk
    elif side == "right":
        xt = x*dk + w*dk + margin
        yt = y - (h*dk)
        wt = half_len*dk - margin
        ht = h*dk
    else:
        print(f"ERROR IN get_xywh(): {side} not recognized.")
        sys.exit(1)
    return xt, yt, wt, ht

def get_base64_str(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
        return encoded_string.decode()

def make_png_string(x, y, w, h, content, iid):
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

def get_filename(text, effects):
    s = " ".join(text).encode('UTF-8')
    hash_object = hashlib.sha256(s)
    hex_dig = hash_object.hexdigest()[:9]
    return hex_dig + "_" + get_rand_string(8) + "_" +  "_".join(effects).replace(".svg", "") + ".svg"