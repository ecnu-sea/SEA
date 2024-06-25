import gradio as gr
import argparse
from gradio_pdf import PDF
from pathlib import Path
from sys import path
import os
path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
dir_ = Path(__file__).parent

from pdf_parser.pdf_parse import run_parse
from paper_review.run_review_transformers import run_review_transformers,init_model_transformers
from paper_review.run_review_llama_factory import run_review_llama_factory,init_model_llama_factory

parser = argparse.ArgumentParser(description="SEA Hyper params")
parser.add_argument("--model_name_or_path",type=str,help="The name or path of the model")
parser.add_argument("--template",type=str,default="mistral",help="The template of the model")
parser.add_argument("--max_new_tokens",type=int,default=8192,help="The max number of new generated tokens of the model")
parser.add_argument("--infer_type",type=str,default='llama_factory',help="You can use LLaMA Factory or Transformers to inference. options: ['llama_factory','transformers']")
args = parser.parse_args()

DESCRIPTION = """\

# <img src="https://ecnu-sea.github.io/static/images/favicon.ico" style="width:50px; vertical-align:middle; margin-right:10px;"> SEA

Please upload your paper's pdf and click `Submit` to get the reviews.
"""
if args.infer_type == "llama_factory":
    model = init_model_llama_factory()
else:
    model,tokenizer = init_model_transformers(args)

def qa(pdf_path: str,history:list,progress=gr.Progress()):
    progress(0, desc="Staring")
    print("parsing paper pdf......")
    progress(0.05,desc="Parsing Paper's PDF...")
    mmd_path = run_parse(pdf_path)
    progress(0.5,desc="Reviewing Paper...")
    print("reviewing......")
    bot_message = ""
    if args.infer_type == "llama_factory":
        bot_message = run_review_llama_factory(mmd_path,args,model)
    else:
        bot_message = run_review_transformers(mmd_path,args,model,tokenizer)
    progress(1,desc="Finished")
    print("finish")
    history.append(("Please give me the reviews of this paper.", bot_message))
    return history


with gr.Blocks() as app:
    # gr.HTML('')
    gr.Markdown(DESCRIPTION)
    with gr.Row():
            # email_box = gr.Textbox(label='Your Email',autofocus=True,lines=1)
        chatbot = gr.Chatbot(label='SEA',height=600)
    with gr.Row():     
            # email_box = gr.Textbox(label='Your Email',autofocus=True,lines=1)
        pdf_uploader = PDF(label="Paper's PDF")
    with gr.Row():
        # clear_btn = gr.ClearButton([email_box,pdf_uploader,chatbot],value='Clear')
        clear_btn = gr.ClearButton([pdf_uploader,chatbot],value='Clear')
        submit_btn = gr.Button(value='Submit')
        # 提交query
        # submit_btn.click(qa,inputs = [email_box,pdf_uploader,chatbot],outputs=[pdf_uploader,chatbot])
        submit_btn.click(qa,inputs = [pdf_uploader,chatbot],outputs=[chatbot])

app.launch(share=True,max_threads=3)
