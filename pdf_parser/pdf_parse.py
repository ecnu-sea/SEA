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

# 将每个pdf划分成一页一页
# 将input.pdf每10页拆分为一个新文件，输出为output_1.pdf, output_2.pdf...
def split_pdf(input_path, output_path, output_prefix, pages_per_output):
    pdf_file = open(input_path, 'rb')
    reader = PdfReader(pdf_file)

    number_of_pages = len(reader.pages)

    print(number_of_pages)
    for i in range(number_of_pages):
        start = i*pages_per_output
        end = (i +1) * pages_per_output
        if end > number_of_pages:
            end = number_of_pages
            number_of_pdf = i
        writer = PdfWriter()
        for page_num in range(start, end):
            writer.add_page(reader.pages[page_num])
        with open(output_path + output_prefix + str(i) + ".pdf", "wb") as outfile:
            writer.write(outfile)
        outfile.close()
        if end >= number_of_pages:
            break
    return number_of_pdf

# 执行nougat命令
# 
def parse(file, output_dir, ifrm):
    '''
        file: 是要解析的pdf 
        output_dir: 是输出的目录
        ifrm: 用于是否要删除file，即解析的pdf文件，如果把一篇文章拆分开来再进行解析的话，一般可以删除pdf
    '''
    # nougat ../temp/out_part_1.pdf -o ./ -m 0.1.0-base
    result = subprocess.run(["conda", "deactivate"], capture_output=True, text=True)
    command_parse = ["nougat", file, "-o", output_dir, "-m", "0.1.0-base", "--no-skipping","--batchsize","8"]
    # 执行命令
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
            # file_id = file.split('/')[-1].split('.')[0]
            # pdftommd_one(file, output_dir + file_id + '.mmd', ifrm=True)
            with open('error.txt', 'a') as f1:
                f1.write(file + '\n')
            f1.close()
    except FileNotFoundError as e:
        print(f"The command 'nougat' was not found: {e}")

# 把分开来的output1.mmd output2.mmd ……，拼起来得到最后一篇文章的mmd
def merge_mmd(pages_num, save_path, ifrm):
    '''
        pages_num: output{}.mmd 文件的数量
        save_path: 合并好的大文件，存取的目录+文件名。
        ifrm: 用于是否要删除output{}.mmd，如果check完没问题，一般可以删除output.mmd，因为一般我们只需要最后的mmd
    '''
    content = ""
    for i in range(pages_num):
        file = "./temp_pdf_parse_v" + str(args.id) + "/output" + str(i) + ".mmd"
        with open(file,'r') as f:
            text = f.read()
            # if "[MISSING_PAGE_FAIL:" in text:
                # print('Error missing')
                # exit()
            content = content + text + ' '
        f.close()
        if ifrm:
            command_rm = ["rm", file]
            result_rm = subprocess.run(command_rm, capture_output=True, text=True)
    with open(save_path, "w") as f:
        f.write(content[:-1])
    f.close()

# 把一个pdf拆分开来，存成output，对每一个pdf解析，再拼起来
# 要注意拼的时候字符串连接
# 如果pdf显存吃不下的时候可以用这个                    
def pdftommd_one(file, save_path, ifrm=True):
    output_path = './temp_pdf_parse_v' + str(args.id) + '/'
    if not os.path.isdir(output_path):
        os.makedirs(output_path)
    pages_num = split_pdf(file, output_path, 'output', 2)
    
    for i in range(pages_num):
        parse(output_path + 'output' + str(i) + '.pdf', output_path, ifrm)
    merge_mmd(pages_num, save_path, ifrm)
    

def run_parse(pdf_path):
    # pdf_dir = './data/ARR_2022_pdf/'
    # mmd_dir = './data/ARR_2022_nougat_mmd/'
    current_directory = os.path.dirname(os.path.abspath(__file__))

    mmd_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),"nougat_mmd")
    # subdirs = get_subdir(dir)

    # idx = get_train_id('./remain_id.txt')
  
    count = 0
    file_name, file_extension = os.path.splitext(os.path.basename(pdf_path))
    # 看一眼tqdm里的，是从文件读依次解析，还是从idx解析 tqdm里 {idx,subfiles}
    save_path = os.path.join(mmd_dir,file_name + '.mmd')
    parse(pdf_path, mmd_dir , ifrm=False)
    return save_path


if __name__=='__main__':
    run_parse("./test_pdf/SUNGEN.pdf")
