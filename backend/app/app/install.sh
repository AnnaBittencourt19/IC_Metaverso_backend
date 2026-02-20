#!/bin/bash

echo "Instalando dependências do sistema IA..."

pip install PyMuPDF torch numpy sentence-transformers
pip install langchain langchain-text-splitters langchain-core langchain-huggingface
pip install langchain-chroma chromadb transformers accelerate bitsandbytes

echo "Instalando unsloth e xformers..."
pip install -q unsloth
pip install -q --no-deps xformers

echo "Instalação concluída!"
