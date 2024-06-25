import os
import json

def get_subdir(path):
    subdirectories = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    return subdirectories

def get_subfile(path):
    subfiles = [d for d in os.listdir(path) if os.path.isfile(os.path.join(path, d))]
    return subfiles

def read_json(path):
    with open(path, 'r') as f:
        content = json.load(f)
    f.close()
    return content

def read_txt(path):
    with open(path, 'r') as f:
        content = f.read()
    f.close()
    return content


def get_train_id(path):
    train_id = []
    with open(path,'r') as f:
        lines = f.readlines()
        for line in lines:
            train_id.append(line.strip())
    f.close()
    return train_id

def num_tokens_from_string(string: str) -> int:
    """
    Calculates the number of tokens in a given text string according to a specific encoding.

    Args:
        text (str): The text string to be tokenized.

    Returns:
        int: The number of tokens the string is encoded into according to the model's tokenizer.
    """
    encoding = tiktoken.encoding_for_model('gpt-4-1106-preview')
    num_tokens = len(encoding.encode(string))
    return num_tokens

def calculate_paper_num_tokens(path):
    with open(path, 'r') as file:
        data = json.load(file)
    data_str = json.dumps(data)
    return num_tokens_from_string(data_str)