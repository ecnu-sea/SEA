import torch
import torch.nn.functional as F
from torch import Tensor
from transformers import AutoTokenizer, AutoModel
import os
import datetime
import torch.nn as nn

    
class SEA_A(nn.Module):
    def __init__(self, input_size, hidden_size):
        super(SEA_A, self).__init__()
        self.wq = nn.Linear(input_size, hidden_size)
        self.wk = nn.Linear(input_size, hidden_size)
        self.act = nn.LeakyReLU()
        self.k = nn.Linear(1,1)
        
    def forward(self, hp, hr):
        qp = self.wq(hp)
        qr = self.wq(hr)
        kp = self.wk(hp)
        kr = self.wk(hr)

        qp = F.normalize(qp, p=2, dim=1)
        qr = F.normalize(qr, p=2, dim=1)
        kp = F.normalize(kp, p=2, dim=1)
        kr = F.normalize(kr, p=2, dim=1)

        out = torch.sum(torch.mul(qp, kr),dim=1) + torch.sum(torch.mul(qr, kp), dim=1)
    
        out = self.k(out.unsqueeze(1)).squeeze(1)
        return out

def last_token_pool(last_hidden_states: Tensor, attention_mask: Tensor) -> Tensor:
    """提取最后一个token的隐藏状态"""
    left_padding = (attention_mask[:, -1].sum() == attention_mask.shape[0])
    if left_padding:
        return last_hidden_states[:, -1]
    else:
        sequence_lengths = attention_mask.sum(dim=1) - 1
        batch_size = last_hidden_states.shape[0]
        return last_hidden_states[torch.arange(batch_size, device=last_hidden_states.device), sequence_lengths]


def load_models(model_path='SEA-A_reloaded.pth', embedding_model_path='./SFR-Embedding-Mistral', 
            device=None):
    if device is None:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    else:
        device = torch.device(device)
    
    tokenizer = AutoTokenizer.from_pretrained(embedding_model_path)
    embedding_model = AutoModel.from_pretrained(embedding_model_path).to(device)
    embedding_model.eval()
    
    model_data = torch.load(model_path, map_location='cpu', weights_only=False)
    
    model_config = model_data['model_config']
    state_dict = model_data['model_state_dict']
    
    input_size = model_config.get('input_size', 4096)
    hidden_dim = model_config.get('hidden_size', 128)
    
    eval_model = SEA_A(input_size, hidden_size=hidden_dim)
    eval_model.load_state_dict(state_dict)
    
    eval_model.to(device)
    eval_model.eval()
    
    return eval_model, tokenizer, embedding_model, device


def get_embedding(text: str, tokenizer, embedding_model, device, max_length=32768) -> Tensor:
    batch_dict = tokenizer(
        text, 
        max_length=max_length, 
        padding=True, 
        truncation=True, 
        return_tensors="pt"
    ).to(device)
    
    with torch.no_grad():
        outputs = embedding_model(**batch_dict)
        embedding = last_token_pool(outputs.last_hidden_state, batch_dict['attention_mask'])
    
    return embedding.cpu()


def evaluate(paper_text: str, review_text: str, eval_model, tokenizer, embedding_model, 
             device, verbose: bool = True) -> float:
    paper_embedding = get_embedding(paper_text, tokenizer, embedding_model, device)
    review_embedding = get_embedding(review_text, tokenizer, embedding_model, device)
    
    paper_embedding = F.normalize(paper_embedding, p=2, dim=1)
    review_embedding = F.normalize(review_embedding, p=2, dim=1)
    
    paper_embedding = paper_embedding.to(device)
    review_embedding = review_embedding.to(device)
    
    with torch.no_grad():
        score = eval_model(paper_embedding, review_embedding)
    
    return score.item()

def main():
    # 加载模型
    eval_model, tokenizer, embedding_model, device = load_models(
        model_path='SEA-A.pth',  # 使用包含配置信息的模型文件
        embedding_model_path='./SFR-Embedding-Mistral',
    )
    
    # 示例：评估一对论文和审稿
    paper_text = """
    This paper presents a novel approach to machine learning...
    """
    
    review_text = """
    The paper presents an interesting contribution to the field...
    """
    
    # 进行评估
    score = evaluate(paper_text, review_text, eval_model, tokenizer, embedding_model, device)
    print(f"Score: {score:.4f}")


if __name__ == '__main__':
    main()
