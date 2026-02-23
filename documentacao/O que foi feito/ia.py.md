- O código é basicamente o mesmo que o ia no colab, usei a ferramenta Amazon QA developer para passar o .ipynb para .py
EXTRA: (meu notebook tava dando erro de GPU tive que adicionar isso)
```python
    def initialize(self):
        logging.info("Inicializando sistema IA...")

        torch.cuda.empty_cache()

        # ====================== DETECÇÃO INTELIGENTE DE HARDWARE ======================
        if torch.cuda.is_available():
            device = "cuda"
            use_4bit = True
            logging.info("🚀 Detectado NVIDIA GPU → usando 4-bit quantization")
        elif torch.backends.mps.is_available():
            device = "mps"
            use_4bit = False
            logging.info("🍎 Detectado Apple Silicon (MPS) → carregando em float16 (sem BitsAndBytes)")
        else:
            device = "cpu"
            use_4bit = False
            logging.warning("⚠️  Rodando em CPU pura → vai ficar lento!")

        # ====================== CONFIGURAÇÃO DO MODELO ======================
        if use_4bit:
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
            )
            model_kwargs = {
                "quantization_config": bnb_config,
                "device_map": "auto",           # ou "cuda:0" se quiser forçar
                "torch_dtype": torch.float16,
                "low_cpu_mem_usage": True,
                "token": HUGGINGFACE_TOKEN,
            }
        else:
            # Para Mac (MPS) ou CPU
            model_kwargs = {
                "device_map": device,           # "mps" ou "cpu"
                "torch_dtype": torch.float16 if device == "mps" else torch.float32,
                "low_cpu_mem_usage": True,
                "token": HUGGINGFACE_TOKEN,
            }

        logging.info(f"Carregando modelo {LLM_MODEL_NAME} em {device.upper()}...")

        self.tokenizer = AutoTokenizer.from_pretrained(
            LLM_MODEL_NAME,
            token=HUGGINGFACE_TOKEN
        )

        self.model = AutoModelForCausalLM.from_pretrained(
            LLM_MODEL_NAME,
            **model_kwargs
        )

        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.tokenizer.pad_token_id = self.tokenizer.eos_token_id

        logging.info(f"✅ LLM carregado com sucesso em {device.upper()}!")
        
        # ====================== RESTO DO CÓDIGO (vectorstore + reranker) ======================
        base_retriever, self.embeddings = setup_vectorstore()
        
        cross_encoder = CrossEncoder(CROSS_ENCODER_MODEL, device=device if device != "mps" else "cpu")
        self.retriever = ReRankingRetriever(base_retriever, cross_encoder)
        
        logging.info("🎉 Sistema IA inicializado com sucesso!")
```
Mas mesmo assim não rodou preciso de memória RAM kkkkkkkkkkkkkkkkk não existe gambiarra pra memória RAM 
![[Captura de Tela 2026-02-23 às 07.47.59.png]]
Triste, estou fazendo uma vaquinha para comprar um PC gamer 