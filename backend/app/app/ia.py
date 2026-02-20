import os
import glob
import fitz
import torch
import numpy as np
import logging
import re
import unicodedata
import json
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from sentence_transformers import CrossEncoder
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import chromadb

PDF_DIR = os.getenv('PDF_DIR', '/Users/annabittencourt/projetos/IC_METAVERSO/backend/app/Data')
CHROMA_PERSIST_DIR = os.getenv('CHROMA_PERSIST_DIR', '/Users/annabittencourt/projetos/IC_METAVERSO/backend/app/chroma_db')
HUGGINGFACE_TOKEN = os.getenv('HUGGINGFACE_TOKEN', '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')
EMBEDDING_MODEL_NAME = 'intfloat/multilingual-e5-large'
CROSS_ENCODER_MODEL = 'BAAI/bge-reranker-v2-m3'
LLM_MODEL_NAME = 'meta-llama/Llama-3.1-8B-Instruct'

MIN_CROSS_ENCODER_SCORE = 0.2
MIN_RELATIVE_SCORE = 0.25
MAX_CONTEXT_TOKENS = 2200

logging.basicConfig(level=logging.INFO)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def clean_text_content(text):
    text = unicodedata.normalize('NFKC', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    return '\n'.join(lines)

def find_table_caption(page, table_bbox, max_distance=50):
    text_blocks = page.get_text("blocks")
    table_top = table_bbox[1]
    
    for block in text_blocks:
        if len(block) >= 5:
            block_bottom = block[3]
            if 0 < (table_top - block_bottom) < max_distance:
                text = block[4].strip()
                if re.match(r'^(Tabela|Table|Quadro)\s*\d+', text, re.IGNORECASE):
                    return text
    return None

def sanitize_cell_content(cell_content):
    if cell_content is None:
        return ""
    
    cell_str = str(cell_content).strip()
    cell_str = cell_str.replace('\n', '<br>').replace('\r', '<br>')
    cell_str = re.sub(r'<br>\s*<br>', '<br>', cell_str)
    cell_str = cell_str.replace('|', '\\|')
    
    return cell_str

def extract_tables_markdown(tables, page_num, page=None):
    table_text = ""
    if not tables:
        return table_text
    
    for table_idx, table in enumerate(tables):
        try:
            caption = None
            if page and hasattr(table, 'bbox'):
                caption = find_table_caption(page, table.bbox)
            
            table_data = table.extract()
            if not table_data or len(table_data) == 0:
                continue
            
            num_cols = max(len(row) for row in table_data)
            normalized_data = []
            for row in table_data:
                normalized_row = list(row) + [""] * (num_cols - len(row))
                normalized_data.append(normalized_row)
            
            if len(normalized_data) > 1 and num_cols >= 2:
                header = f"**[{caption if caption else f'Tabela {table_idx + 1}'} - Página {page_num + 1}]**\n\n"
                table_md = ""
                attribute_headers = [sanitize_cell_content(h) for h in normalized_data[0]]
                
                for row in normalized_data[1:]:
                    sanitized_cells = [sanitize_cell_content(cell) for cell in row]
                    identifier = sanitized_cells[0] if sanitized_cells else ""
                    attributes = []
                    
                    for i, attr_value in enumerate(sanitized_cells[1:], 1):
                        if attr_value.strip():
                            attr_name = attribute_headers[i] if i < len(attribute_headers) else ""
                            if attr_name:
                                attributes.append(f"{attr_name}: {attr_value}")
                            else:
                                attributes.append(attr_value)
                    
                    if identifier.strip():
                        table_md += f"[{identifier}]: {' | '.join(attributes)}\n"
                
                table_text += f"\n{header}{table_md}\n"
        except Exception as e:
            logging.error(f"Erro ao processar tabela {table_idx + 1} na página {page_num + 1}: {str(e)}")
            continue
    
    return table_text

def chunk_documents(documents):
    chunks = []
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=300,
        separators=[
            "\n\n",
            "\n---",
            "\n===",
            "\n| ",
            "\n",
            ". ",
            ": ",
            "; ",
            "! ",
            "? ",
            " "
        ],
        keep_separator=True
    )
    
    for doc in documents:
        doc_chunks = text_splitter.split_documents([Document(
            page_content=doc['text'],
            metadata=doc['metadata']
        )])
        chunks.extend(doc_chunks)
    
    filtered_chunks = [chunk for chunk in chunks if len(chunk.page_content.strip()) > 50]
    return filtered_chunks

def extract_tables_with_fallback(page, page_num, use_strict_strategy=False):
    table_text = ""
    patterns_found = []
    strategy_used = "none"
    
    try:
        if not use_strict_strategy:
            tables = page.find_tables(strategy="lines")
        else:
            tables = []
        
        if tables:
            logging.info(f"  Página {page_num + 1}: {len(tables)} tabela(s) detectada(s) (estratégia: lines)")
            table_text = extract_tables_markdown(tables, page_num, page)
            strategy_used = "lines"
            return table_text, [], strategy_used
        
        logging.debug(f"  Página {page_num + 1}: Tentando strategy='lines_strict'...")
        tables = page.find_tables(strategy="lines_strict")
        
        if tables:
            logging.info(f"  Página {page_num + 1}: {len(tables)} tabela(s) detectada(s) (estratégia: lines_strict)")
            table_text = extract_tables_markdown(tables, page_num, page)
            strategy_used = "lines_strict"
            return table_text, [], strategy_used
        
        logging.debug(f"  Página {page_num + 1}: Tentando strategy='text'...")
        tables = page.find_tables(strategy="text")
        
        if tables:
            logging.info(f"  Página {page_num + 1}: {len(tables)} tabela(s) detectada(s) (estratégia: text)")
            table_text = extract_tables_markdown(tables, page_num, page)
            strategy_used = "text"
            return table_text, [], strategy_used
        
        logging.debug(f"  Página {page_num + 1}: Nenhuma tabela detectada")
        strategy_used = "none"
        return "", [], strategy_used
    
    except Exception as e:
        logging.error(f"Erro ao extrair tabelas da página {page_num + 1}: {str(e)}")
        return "", [], "error"

def load_pdfs_improved(directory):
    documents = []
    files = glob.glob(os.path.join(directory, '**/*.pdf'), recursive=True)
    if not files:
        logging.warning(f"Nenhum PDF encontrado em {directory}")
        return documents
    
    total_tables_extracted = 0
    strategy_stats = {'lines': 0, 'lines_strict': 0, 'text': 0, 'regex_patterns': 0, 'none': 0}
    
    for filepath in files:
        try:
            logging.info(f"Processando {os.path.basename(filepath)}...")
            doc = fitz.open(filepath)
            
            for page_num, page in enumerate(doc):
                try:
                    table_text, patterns, strategy = extract_tables_with_fallback(page, page_num)
                    
                    if strategy != "none":
                        strategy_stats[strategy] = strategy_stats.get(strategy, 0) + 1
                        total_tables_extracted += 1
                    
                    text = page.get_text()
                    combined_text = table_text + text if table_text else text
                    
                    if combined_text.strip():
                        clean_text = clean_text_content(combined_text)
                        if clean_text:
                            documents.append({
                                "text": clean_text,
                                "metadata": {
                                    "source": os.path.basename(filepath),
                                    "page": page_num + 1,
                                    "path": filepath,
                                    "tables_count": 1 if table_text else 0,
                                    "extraction_strategy": strategy
                                }
                            })
                except Exception as e:
                    logging.error(f"Erro ao processar página {page_num + 1} de {os.path.basename(filepath)}: {str(e)}")
                    continue
            
            doc.close()
        except Exception as e:
            logging.error(f"Erro ao abrir {filepath}: {str(e)}")
            continue
    
    logging.info(f"Processamento concluído:")
    logging.info(f"  - Total de páginas extraídas: {len(documents)}")
    logging.info(f"  - Total de tabelas detectadas: {total_tables_extracted}")
    logging.info(f"  - Estratégias usadas:")
    for strategy, count in strategy_stats.items():
        if count > 0:
            logging.info(f"    • {strategy}: {count}")
    
    return documents

GLOSSARIO_6G_BRASIL_COMPLETO = {
    'cp': ['cyclic prefix', 'prefixo cíclico', 'proteção multipercurso'],
    'cs': ['cyclic suffix', 'sufixo cíclico', 'janelamento no tempo'],
    'rb': ['resource block', 'bloco de recursos', '180 khz x 1 subquadro'],
    're': ['resource element', 'elemento de recurso', 'subsímbolo por subportadora'],
    'pss': ['primary synchronization signal', 'sinal de sincronização primário'],
    'subquadro': ['4,6 ms', 'agrupamento de símbolos gfdm'],
    'ofdm': ['orthogonal frequency division multiplexing', 'multiplexação por divisão de frequência ortogonal'],
    'gfdm': ['generalized frequency division multiplexing', 'multiplexação por divisão de frequência generalizada'],
    'f-ofdm': ['filtered ofdm', 'ofdm filtrada'],
    'fbmc': ['filter bank multicarrier', 'multiportadora por banco de filtros'],
    'ufmc': ['universal filtered multicarrier', 'multiportadora filtrada universal'],
    'otfs': ['orthogonal time-frequency space', 'espaço ortogonal tempo-frequência', 'domínio atraso-doppler'],
    'ftn': ['faster-than-nyquist', 'sinalização mais rápida que nyquist', 'compressão temporal'],
    'ftn-gfdm': ['forma de onda não ortogonal brasil 6g', 'eficiência espectral aprimorada'],
    'scma': ['sparse code multiple access', 'acesso múltiplo por código esparso', 'codebook esparso'],
    'noma': ['non-orthogonal multiple access', 'acesso múltiplo não ortogonal'],
    'mimo': ['multiple-input multiple-output', 'múltiplas entradas múltiplas saídas'],
    'sm-mimo': ['spatial multiplexing mimo', 'multiplexação espacial'],
    'zf': ['zero forcing', 'forçamento a zero', 'inversão de canal'],
    'mmse': ['minimum mean square error', 'erro quadrático médio mínimo'],
    'ml': ['maximum likelihood', 'máxima verossimilhança'],
    'sd': ['sphere detector', 'detector esférico', 'busca em esfera'],
    'sic': ['successive interference cancellation', 'cancelamento sucessivo de interferência'],
    'lra': ['lattice reduction aided', 'auxiliado por redução de reticulado'],
    'amp': ['approximate message-passing', 'passagem aproximada de mensagens'],
    'papr': ['peak-to-average power ratio', 'relação pico-média', 'eficiência de amplificadores'],
    'qpsk': ['quadrature phase shift keying', 'modulação 4-qam'],
    '16-qam': ['16 quadrature amplitude modulation', '4 bits por símbolo'],
    '64-qam': ['64 quadrature amplitude modulation', '6 bits por símbolo'],
    '256-qam': ['256 quadrature amplitude modulation', '8 bits por símbolo'],
    'ldpc': ['low-density parity-check', 'código de verificação de paridade de baixa densidade'],
    'polar codes': ['códigos polares', 'codificação de canal 5g/6g'],
    'dpd': ['digital pre-distortion', 'pré-distorção digital', 'linearização de amplificadores'],
    'mzm': ['mach-zehnder modulator', 'modulador mach-zehnder', 'modulador eletro-óptico'],
    'dml': ['directly modulated laser', 'laser modulado diretamente'],
    'rof': ['radio over fiber', 'rádio sobre fibra', 'distribuição rf por fibra óptica'],
    'smf': ['single-mode fiber', 'fibra monomodo'],
    'ld': ['laser diode', 'diodo laser'],
    'tvws': ['television white spaces', 'espaços em branco de tv', 'canais ociosos vhf/uhf'],
    'erac': ['enhanced remote area communications', 'comunicações aprimoradas em áreas remotas', 'super células'],
    'vhf': ['very high frequency', '30-300 mhz', 'faixa baixa para longo alcance'],
    'uhf': ['ultra high frequency', '300 mhz - 3 ghz', 'faixa média para tv digital'],
    'isac': ['integrated sensing and communications', 'sensoriamento e comunicação integrados'],
    'channel charting': ['mapeamento geométrico do canal', 'representação espacial sem gps', 'autoencoder'],
    'csi': ['channel state information', 'informação do estado do canal', 'vetor de características'],
    'gnss': ['global navigation satellite systems', 'sistemas globais de navegação por satélite'],
    'gps': ['global positioning system', 'sistema de posicionamento global'],
    'lidar': ['light detection and ranging', 'detecção e medição por laser', 'nuvem de pontos 3d'],
    'ia nativa': ['ai-native', 'integração profunda de ia na arquitetura', 'ia como princípio fundamental 6g'],
    'ia embarcada': ['on-device ai', 'processamento de ia no terminal', 'inferência local'],
    'ia generativa': ['genai', 'criação de conteúdo e serviços personalizados', 'automação de planejamento'],
    'free5gc': ['plataforma core network 5g open source', 'implementação sba do 3gpp'],
    'oai': ['openairinterface', 'implementação open source de ran', 'plataforma sdr para 5g/6g'],
    'open ran': ['redes desfragmentadas', 'interfaces abertas', 'desagregação hardware/software'],
    'sba': ['service-based architecture', 'arquitetura baseada em serviços', 'core 5g/6g'],
    'amf': ['access and mobility management function', 'gerenciamento de acesso e mobilidade'],
    'smf': ['session management function', 'gerenciamento de sessão'],
    'upf': ['user plane function', 'função do plano do usuário'],
    'pcf': ['policy control function', 'controle de política'],
    'nwdaf': ['network data analytics function', 'análise de dados da rede'],
    'ran slicing': ['fatiamento de rede de acesso', 'network slicing ran', 'fatias virtuais'],
    'mec': ['multi-access edge computing', 'computação na borda de múltiplo acesso'],
    'embb': ['enhanced mobile broadband', 'banda larga móvel aprimorada'],
    'urllc': ['ultra reliable low latency communications', 'comunicações ultra confiáveis de baixa latência'],
    'mmtc': ['massive machine-type communications', 'comunicações machine-type massivas'],
    'uav': ['unmanned aerial vehicle', 'veículo aéreo não tripulado', 'drone'],
    'v2x': ['vehicle-to-everything', 'comunicações veiculares'],
    'sub-6ghz': ['faixas baixas e médias', 'below 6 ghz', '3.5 ghz', '6 ghz'],
    'mmwave': ['ondas milimétricas', 'millimeter wave', '24-40 ghz', 'sub-100 ghz'],
    'sub-thz': ['sub-terahertz', '100-300 ghz', 'faixa sub-terahertz'],
    'thz': ['terahertz', 'faixa acima 100 ghz', '0.1-10 thz'],
    'vlc': ['visible light communication', 'comunicação por luz visível', '400-800 thz'],
    'usrp': ['universal software radio peripheral', 'plataforma sdr'],
    'fpga': ['field-programmable gate array', 'circuito reconfigurável', 'processamento em hardware'],
    'irs': ['intelligent reflecting surface', 'superfície refletora inteligente', 'metamateriais'],
    'full duplex': ['operação full duplex', 'transmissão simultânea', 'mesma frequência'],
    'fwa': ['fixed wireless access', 'acesso sem fio fixo', 'substituição de fibra em áreas remotas'],
    'imt-2030': ['international mobile telecommunications-2030', 'framework 6g da itu', 'requisitos técnicos'],
    '3gpp': ['3rd generation partnership project', 'parceria de projeto de 3ª geração', 'padronização 5g/6g'],
}

def tokenize_query(query):
    tokens = re.findall(r'\b[a-záàâãéêíóôõúç0-9_-]+\b', query.lower())
    return tokens

def find_glossary_matches(query, max_matches=3):
    matches = []
    query_lower = query.lower()
    tokens = tokenize_query(query)
    
    for key, synonyms in GLOSSARIO_6G_BRASIL_COMPLETO.items():
        pattern = r'\b' + re.escape(key.lower()) + r'\b'
        if re.search(pattern, query_lower):
            matches.append((key, synonyms, len(key)))
            continue
        
        key_tokens = tokenize_query(key)
        if len(key_tokens) > 1:
            if all(token in tokens for token in key_tokens):
                matches.append((key, synonyms, len(key_tokens)))
                continue
        
        for token in tokens:
            if len(token) >= 4:
                key_lower = key.lower()
                if token in key_lower or key_lower in token:
                    if len(token) >= len(key_lower) * 0.5:
                        matches.append((key, synonyms, len(key_tokens)))
                        break
    
    matches.sort(key=lambda x: x[2], reverse=True)
    
    seen = set()
    unique_matches = []
    for key, synonyms, length in matches:
        if key not in seen:
            seen.add(key)
            unique_matches.append((key, synonyms))
    
    return unique_matches[:max_matches]

def expand_query_with_embeddings(query, embeddings_model, vectorstore, max_expansions=3):
    try:
        initial_results = vectorstore.similarity_search(query, k=20)
        candidate_terms = set()
        
        for doc in initial_results[:10]:
            words = re.findall(r'\b[a-záàâãéêíóôõúç]{4,}\b', doc.page_content.lower())
            candidate_terms.update(words[:5])
        
        query_embedding = embeddings_model.embed_query(query)
        term_scores = []
        
        for term in list(candidate_terms)[:50]:
            if term not in query.lower():
                term_embedding = embeddings_model.embed_query(term)
                similarity = np.dot(query_embedding, term_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(term_embedding)
                )
                if similarity > 0.6:
                    term_scores.append((term, similarity))
        
        term_scores.sort(key=lambda x: x[1], reverse=True)
        expansion_terms = [term for term, _ in term_scores[:max_expansions]]
        return f"{query} {' '.join(expansion_terms)}"
    
    except Exception as e:
        logging.warning(f"Erro na expansão: {e}")
        return query

def expand_query(query, embeddings_model=None, vectorstore=None):
    matches = find_glossary_matches(query, max_matches=3)
    
    if matches:
        expansion_terms = []
        for key, synonyms in matches:
            expansion_terms.extend(synonyms[:3])
        
        seen = set()
        unique_expansions = []
        for term in expansion_terms:
            term_lower = term.lower()
            if term_lower not in seen:
                seen.add(term_lower)
                unique_expansions.append(term)
        
        expanded = f"{query} {' '.join(unique_expansions[:5])}"
        logging.debug(f"Expansão glossário: {len(matches)} correspondência(s) encontrada(s)")
        logging.debug(f"Termos expandidos: {unique_expansions[:5]}")
        return expanded
    
    if embeddings_model and vectorstore:
        logging.debug("Nenhuma correspondência de glossário, usando expansão por embeddings")
        return expand_query_with_embeddings(query, embeddings_model, vectorstore)
    
    logging.debug(f"Nenhuma expansão disponível para: {query}")
    return query

def setup_vectorstore():
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        model_kwargs={'device': device, 'token': HUGGINGFACE_TOKEN}
    )
    
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    
    try:
        collection = client.get_collection(name="6g_docs")
        vectorstore = Chroma(
            client=client,
            collection_name="6g_docs",
            embedding_function=embeddings
        )
        logging.info(f"Carregando banco de dados existente com {collection.count()} documentos...")
    
    except Exception as e:
        logging.info("Criando novo banco de dados...")
        documents = load_pdfs_improved(PDF_DIR)
        chunks = chunk_documents(documents)
        
        vectorstore = Chroma.from_documents(
            chunks,
            embeddings,
            client=client,
            collection_name="6g_docs"
        )
        logging.info(f"Banco de dados criado com {len(chunks)} chunks")
    
    base_retriever = vectorstore.as_retriever(search_kwargs={'k': 8})
    return base_retriever, embeddings

# Classe de Re-Ranking
class ReRankingRetriever:
    def __init__(self, base_retriever, cross_encoder, top_k=4):
        self.base_retriever = base_retriever
        self.cross_encoder = cross_encoder
        self.top_k = top_k
    
    def get_relevant_documents(self, query):
        expanded_query = expand_query(query)
        initial_docs = self.base_retriever.invoke(expanded_query)
        
        if not initial_docs:
            return []
        
        pairs = [(query, doc.page_content) for doc in initial_docs]
        scores = self.cross_encoder.predict(pairs)
        
        docs_with_scores = []
        for doc, score in zip(initial_docs, scores):
            source = doc.metadata.get('source', 'desconhecido') if hasattr(doc, 'metadata') else 'desconhecido'
            is_pdf = 'pdf' in source.lower() or source.endswith('.pdf')
            priority_boost = 1.2 if is_pdf else 1.0
            adjusted_score = score * priority_boost
            
            docs_with_scores.append({
                'doc': doc,
                'original_score': score,
                'adjusted_score': adjusted_score,
                'is_pdf': is_pdf,
                'source': source
            })
        
        valid_docs = [d for d in docs_with_scores if d['adjusted_score'] > MIN_CROSS_ENCODER_SCORE]
        
        if not valid_docs:
            return []
        
        valid_docs.sort(key=lambda x: (x['is_pdf'], x['adjusted_score']), reverse=True)
        max_score = valid_docs[0]['adjusted_score']
        threshold = max_score * MIN_RELATIVE_SCORE
        
        filtered_docs = [d['doc'] for d in valid_docs if d['adjusted_score'] >= threshold][:self.top_k]
        
        for i, doc in enumerate(filtered_docs):
            if not hasattr(doc, 'metadata'):
                doc.metadata = {}
            for d in valid_docs:
                if d['doc'] == doc:
                    doc.metadata['source_type'] = 'PDF' if d['is_pdf'] else 'Modelo'
                    doc.metadata['retrieval_score'] = float(d['adjusted_score'])
                    break
        
        return filtered_docs

# Prompt do sistema
SYSTEM_PROMPT = """VOCÊ É UM MOTOR ESPECIALIZADO EM EXTRAÇÃO E SÍNTESE DE DADOS TÉCNICOS.
O texto intitulado "CONTEXTO" constitui a ÚNICA FONTE VÁLIDA DE VERDADE.
Toda resposta deve ser estritamente fundamentada nesse conteúdo.

DIRETRIZES FUNDAMENTAIS:
- É terminantemente proibido afirmar ausência de acesso a documentos ou classificar informações como hipotéticas.
- Se o dado estiver presente no CONTEXTO, ele deve ser extraído, interpretado e apresentado.
- É vedado adicionar conhecimento externo, inferências não suportadas ou complementações técnicas não explicitamente contidas no texto.
- Em caso de conflito informacional, priorize exclusivamente dados provenientes de PDF sobre quaisquer outros modelos ou fontes mencionadas.

ESCOPO E PRECISÃO:
- Caso a pergunta mencione uma entidade específica (ex: "Numerologia ID 0"), responda exclusivamente sobre essa entidade.
- Não inclua informações de outras numerologias, IDs ou objetos não solicitados.
- Garanta precisão terminológica, coesão lógica e consistência interna entre atributos.
- Cada dado deve estar semanticamente vinculado ao seu respectivo objeto.

PROCESSAMENTO DE TABELAS:
- A primeira coluna representa o identificador/âncora do objeto.
- A primeira linha define atributos e respectivas unidades de medida.
- Cada valor extraído deve ser corretamente associado ao cabeçalho correspondente.
- Não misture atributos entre diferentes âncoras.

TRATAMENTO DA INFORMAÇÃO:
- Extraia dados técnicos diretamente do texto.
- Sintetize em linguagem técnica objetiva.
- Reescreva conceitos sem copiar literalmente.
- Preserve unidades, valores numéricos e nomenclaturas técnicas.

FORMATO DE SAÍDA:
- Resposta técnica direta em 1–2 parágrafos.
- Linguagem formal, objetiva e impessoal.
- Sem listas, enumerações ou comentários adicionais.
- Foco exclusivo nos dados técnicos extraídos.

PROIBIDO:
1. INVENTAR termos ausentes no contexto
2. COMPLETAR lacunas com conhecimento externo ou suposições
3. GENERALIZAR respostas
4. CONFUNDIR tecnologias
"""

def query_documents(question, retriever):
    try:
        relevant_docs = retriever.get_relevant_documents(question)
        if not relevant_docs:
            return "Não foram encontrados documentos relevantes."
        
        pdf_docs = []
        model_docs = []
        
        for doc in relevant_docs:
            source_type = doc.metadata.get('source_type', 'Desconhecido') if hasattr(doc, 'metadata') else 'Desconhecido'
            if source_type == 'PDF':
                pdf_docs.append(doc)
            else:
                model_docs.append(doc)
        
        prioritized_docs = pdf_docs + model_docs
        context_parts = []
        total_chars = 0
        source_indicators = []
        
        for doc in prioritized_docs:
            content = doc.page_content.strip()
            source_type = doc.metadata.get('source_type', 'Desconhecido') if hasattr(doc, 'metadata') else 'Desconhecido'
            score = doc.metadata.get('retrieval_score', 0.0) if hasattr(doc, 'metadata') else 0.0
            
            if total_chars + len(content) <= MAX_CONTEXT_TOKENS:
                context_parts.append(content)
                source_indicators.append(f"[{source_type} | Score: {score:.2f}]")
                total_chars += len(content)
            else:
                remaining_chars = MAX_CONTEXT_TOKENS - total_chars
                if remaining_chars > 100:
                    context_parts.append(content[:remaining_chars] + "...")
                    source_indicators.append(f"[{source_type} | Truncado]")
                break
        
        context = "\n\n".join(context_parts)
        
        logging.info(f"PDFs encontrados: {len(pdf_docs)}")
        logging.info(f"Modelos encontrados: {len(model_docs)}")
        logging.debug(f"Ordem de prioridade: {source_indicators}")
        
        prompt = f"""{SYSTEM_PROMPT}

Contexto dos documentos (Prioridade: PDF > Modelo):
{context}

Pergunta: {question}

Resposta:"""
        
        return prompt, context, relevant_docs, {
            'pdf_count': len(pdf_docs),
            'model_count': len(model_docs),
            'source_indicators': source_indicators
        }
    
    except Exception as e:
        logging.error(f"Erro em query_documents: {str(e)}")
        return f"Erro: {str(e)}"

def generate_answer(prompt, model, tokenizer, metadata=None):
    try:
        question_start = prompt.find('Pergunta: ') + len('Pergunta: ')
        question_end = prompt.find('\n\nResposta:')
        question = prompt[question_start:question_end].strip()
        
        context_start = prompt.find('Contexto dos documentos (Prioridade: PDF > Modelo):\n') + len('Contexto dos documentos (Prioridade: PDF > Modelo):\n')
        context_end = prompt.find('\n\nPergunta:')
        context = prompt[context_start:context_end].strip()
        
        messages = [
            {"role": "user", "content": f"Com base no contexto fornecido, responda de forma técnica: {question}\n\nContexto: {context}"}
        ]
        
        input_text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(input_text, return_tensors="pt", truncation=True, max_length=3072)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=400,
                temperature=0.1,
                do_sample=True,
                top_p=0.9,
                repetition_penalty=1.2,
                pad_token_id=tokenizer.eos_token_id
            )
        
        generated_tokens = outputs[0][inputs['input_ids'].shape[1]:]
        response = tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()
        
        if metadata:
            if metadata.get('pdf_count', 0) > 0:
                confidence_indicator = "✅ [Baseado em PDF]"
            elif metadata.get('model_count', 0) > 0:
                confidence_indicator = "⚠️ [Baseado em Modelo]"
            else:
                confidence_indicator = "❓ [Fonte desconhecida]"
            
            response = f"{response}\n\n{confidence_indicator}"
            logging.info(f"Hierarquia aplicada: {confidence_indicator}")
        
        return response if response else 'Não foi possível gerar uma resposta baseada no contexto.'
    
    except Exception as e:
        logging.error(f"Erro em generate_answer: {str(e)}")
        return f"Erro ao gerar resposta: {str(e)}"

def hierarchical_search_and_generate(question, retriever, model, tokenizer):
    try:
        logging.info(f"=== BUSCA HIERÁRQUICA: {question} ===")
        query_result = query_documents(question, retriever)
        
        if isinstance(query_result, str):
            return {
                'response': query_result,
                'confidence': 'erro',
                'hierarchy_info': None
            }
        
        prompt, context, relevant_docs, metadata = query_result
        pdf_percentage = (metadata['pdf_count'] / max(len(relevant_docs), 1)) * 100
        
        hierarchy_info = {
            'total_docs': len(relevant_docs),
            'pdf_docs': metadata['pdf_count'],
            'model_docs': metadata['model_count'],
            'pdf_percentage': pdf_percentage,
            'source_types': metadata['source_indicators']
        }
        
        logging.info(f"📊 Hierarquia: {metadata['pdf_count']} PDFs + {metadata['model_count']} Modelos")
        logging.info(f"📈 Confiança: {pdf_percentage:.1f}% de documentos são PDFs")
        
        response = generate_answer(prompt, model, tokenizer, metadata=metadata)
        
        if pdf_percentage >= 75:
            confidence = 'alta'
            confidence_desc = '✅ Alta (Maioria é PDF)'
        elif pdf_percentage >= 25:
            confidence = 'média'
            confidence_desc = '⚠️ Média (Mix de PDF e Modelo)'
        else:
            confidence = 'baixa'
            confidence_desc = '❌ Baixa (Maioria é Modelo)'
        
        logging.info(f"🎯 Nível de confiança: {confidence_desc}")
        
        return {
            'response': response,
            'confidence': confidence,
            'confidence_desc': confidence_desc,
            'hierarchy_info': hierarchy_info,
            'question': question,
            'docs': relevant_docs
        }
    
    except Exception as e:
        logging.error(f"Erro em hierarchical_search_and_generate: {str(e)}")
        return {
            'response': f"Erro: {str(e)}",
            'confidence': 'erro',
            'hierarchy_info': None
        }

class IASystem:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.retriever = None
        self.embeddings = None
        
    def initialize(self):
        logging.info("Inicializando sistema IA...")
        
        torch.cuda.empty_cache()
        
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True
        )
        
        logging.info(f"Carregando modelo {LLM_MODEL_NAME}...")
        self.tokenizer = AutoTokenizer.from_pretrained(
            LLM_MODEL_NAME,
            token=HUGGINGFACE_TOKEN
        )
        
        self.model = AutoModelForCausalLM.from_pretrained(
            LLM_MODEL_NAME,
            quantization_config=bnb_config,
            device_map="auto",
            token=HUGGINGFACE_TOKEN,
            torch_dtype=torch.float16
        )
        
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.tokenizer.pad_token_id = self.tokenizer.eos_token_id
        
        logging.info("LLM carregado com sucesso!")
        
        base_retriever, self.embeddings = setup_vectorstore()
        
        cross_encoder = CrossEncoder(CROSS_ENCODER_MODEL, device=device)
        
        self.retriever = ReRankingRetriever(base_retriever, cross_encoder)
        
        logging.info("Sistema IA inicializado com sucesso!")
    
    def ask(self, question):
        if not self.model or not self.retriever:
            raise RuntimeError("Sistema não inicializado. Chame initialize() primeiro.")
        
        return hierarchical_search_and_generate(question, self.retriever, self.model, self.tokenizer)

def main():
    ia_system = IASystem()
    ia_system.initialize()
    
    print("Sistema pronto! Faça suas perguntas.")
    print("Digite 'sair' para terminar.\n")
    
    while True:
        question = input("Digite sua pergunta (ou 'sair' para terminar): ")
        
        if question.lower() == 'sair':
            print("Sessão encerrada.")
            break
        
        result = ia_system.ask(question)
        
        if result.get('confidence') != 'erro':
            print("\n=== RESPOSTA ===")
            print(result['response'])
            print(f"\n=== CONFIANÇA: {result['confidence_desc']} ===")
            
            if result.get('hierarchy_info'):
                info = result['hierarchy_info']
                print(f"📊 Total: {info['total_docs']} docs | PDFs: {info['pdf_docs']} | Modelos: {info['model_docs']}")
            
            if result.get('docs'):
                print("\n=== FONTES ===")
                for i, doc in enumerate(result['docs'], 1):
                    print(f"{i}. {doc.metadata['source']} - Página {doc.metadata['page']}")
            print("\n" + "="*50 + "\n")
        else:
            print(f"\nErro: {result['response']}\n")

if __name__ == "__main__":
    main()
