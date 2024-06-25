import json
import os


def read_txt_file(path):
    with open(path, 'r') as f:
        content = f.read()
    return content

def read_json_file(path):
    with open(path, 'r') as f:
        data = json.load(f)
    return data

def save_output(output, save_dir, data_id):
    with open(save_dir + data_id + ".txt", 'w') as f:
        f.write(output)
    f.close()

def get_subfile(path):
    subfiles = [d for d in os.listdir(path) if os.path.isfile(os.path.join(path, d))]
    return subfiles