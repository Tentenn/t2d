
import os
import re
import random
import string
import hashlib

EFFECTS_PATH = os.getcwd() + "/data/effects/"




def get_rand_string(k=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=k))

def get_fontsize(i_text):
    r_str = "font-size:[0-9]*\.[0-9]*px"
    matches = re.findall(r_str, i_text)
    return matches[0][10:-2]

def get_filename(text, effects):
    s = " ".join(text).encode('UTF-8')
    hash_object = hashlib.sha256(s)
    hex_dig = hash_object.hexdigest()[:9]
    return hex_dig + "_" + get_rand_string(8) + "_" +  "_".join(effects).replace(".svg", "") + ".svg"