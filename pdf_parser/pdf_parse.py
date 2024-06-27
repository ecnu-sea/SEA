import subprocess
from PyPDF2 import PdfReader, PdfWriter
from .utils import *
from tqdm import tqdm
import argparse
import os
parser = argparse.ArgumentParser()
parser.add_argument('--id', type=int, default=0)
parser.add_argument('--start', type=int, default=0)
parser.add_argument('--end', type=int, default=0)

args, _ = parser.parse_known_args()

def parse(file, output_dir, ifrm):
    '''
        file: parse PDF file to be parsed
        output_dir: the output directory
        ifrm: if or not to delete the pdf file
    '''
    # nougat ../temp/out_part_1.pdf -o ./ -m 0.1.0-base
    result = subprocess.run(["conda", "deactivate"], capture_output=True, text=True)
    command_parse = ["nougat", file, "-o", output_dir, "-m", "0.1.0-base", "--no-skipping","--batchsize","8"]
    # run 
    print(file)
    print(output_dir)
    try:
        result = subprocess.run(command_parse, capture_output=True, text=True)
        if result.returncode == 0:
            if ifrm:
                command_rm = ["rm", file]
                result_rm = subprocess.run(command_rm, capture_output=True, text=True)
        else:
            print("err:"+result.stderr)
            print("Command failed with exit code:", result.returncode)
            with open('error.txt', 'a') as f1:
                f1.write(file + '\n')
            f1.close()
    except FileNotFoundError as e:
        print(f"The command 'nougat' was not found: {e}")


def run_parse(pdf_path):
    current_directory = os.path.dirname(os.path.abspath(__file__))
    mmd_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),"nougat_mmd")
    file_name, file_extension = os.path.splitext(os.path.basename(pdf_path))
    save_path = os.path.join(mmd_dir,file_name + '.mmd')
    parse(pdf_path, mmd_dir , ifrm=False)
    return save_path


if __name__=='__main__':
    run_parse("./test.pdf")
