CUDA_VISIBLE_DEVICES=0 python webui.py \
--model_name_or_path /root/SEA-E/ \
--template mistral \
--max_new_tokens 8192 \
--infer_type transformers
