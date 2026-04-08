import os
import glob
import fitz
import numpy as np
import logging
import re
import unicodedata
from sentence_transformers import CrossEncoder, SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_chroma import Chroma
import chromadb
import pandas as pd
from groq import Groq

from app.config import (
    PDF_DIR,
    CHROMA_PERSIST_DIR,
    EMBEDDING_MODEL_NAME,
    CROSS_ENCODER_MODEL,
    MIN_CROSS_ENCODER_SCORE,
    MIN_RELATIVE_SCORE,
    MAX_CONTEXT_TOKENS,
    INITIAL_RETRIEVAL_K,
    GROQ_API_KEY
)

logging.basicConfig(level=logging.INFO)


# ============================================================================
# WRAPPER PARA SENTENCE TRANSFORMERS COM LANGCHAIN
# ============================================================================

class SentenceTransformerEmbeddings:
    """Wrapper para usar SentenceTransformer com LangChain"""
    
    def __init__(self, model_name: str = "sentence-transformers/multilingual-e5-large"):
        self.model = SentenceTransformer(model_name)
    
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed search docs."""
        embeddings = self.model.encode(texts, convert_to_tensor=False)
        return embeddings.tolist()
    
    def embed_query(self, text: str) -> list[float]:
        """Embed query text."""
        embedding = self.model.encode([text], convert_to_tensor=False)[0]
        return embedding.tolist()



# ============================================================================
# FUNÇÕES DE LIMPEZA E PROCESSAMENTO DE TEXTO
# ============================================================================

def clean_text_content(text):
    text = unicodedata.normalize('NFKC', text)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
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
            df = table.to_pandas()
            if df is None or df.empty:
                continue
            header = f"**[{caption if caption else f'Tabela {table_idx + 1}'} - Página {page_num + 1}]**\n\n"
            table_md = df.to_markdown(index=False)
            table_text += f"\n{header}{table_md}\n"
        except Exception as e:
            logging.error(f"Erro ao processar tabela {table_idx + 1} na página {page_num + 1}: {str(e)}")
            continue

    return table_text


def chunk_documents(documents):
    TABLE_SPLITTER = RecursiveCharacterTextSplitter(
        chunk_size=1500, chunk_overlap=200,
        separators=["\n\n"], keep_separator=True
    )
    TEXT_SPLITTER = RecursiveCharacterTextSplitter(
        chunk_size=800, chunk_overlap=300,
        separators=["\n\n", "\n", ". ", ": ", "; ", "! ", "? ", " "],
        keep_separator=True
    )

    def split_into_semantic_blocks(text):
        blocks = []
        current_para = []
        for line in text.split('\n'):
            stripped = line.strip()
            if not stripped:
                if current_para:
                    blocks.append(('paragraph', '\n'.join(current_para)))
                    current_para = []
                continue
            if stripped.startswith('|') and stripped.endswith('|'):
                if current_para:
                    blocks.append(('paragraph', '\n'.join(current_para)))
                    current_para = []
                if blocks and blocks[-1][0] == 'table':
                    blocks[-1] = ('table', blocks[-1][1] + '\n' + line)
                else:
                    blocks.append(('table', line))
            elif re.match(r'^\*\*\[.+\]\*\*$', stripped) or (len(stripped) < 80 and stripped.isupper()):
                if current_para:
                    blocks.append(('paragraph', '\n'.join(current_para)))
                    current_para = []
                blocks.append(('header', stripped))
            else:
                current_para.append(line)
        if current_para:
            blocks.append(('paragraph', '\n'.join(current_para)))
        return blocks

    chunks = []
    for doc in documents:
        metadata = doc['metadata']
        for block_type, block_text in split_into_semantic_blocks(doc['text']):
            if not block_text.strip():
                continue
            splitter = TABLE_SPLITTER if block_type == 'table' else TEXT_SPLITTER
            doc_chunks = splitter.split_documents([Document(
                page_content=block_text,
                metadata={**metadata, 'block_type': block_type}
            )])
            chunks.extend(doc_chunks)
    return [c for c in chunks if len(c.page_content.strip()) > 50]


# ============================================================================
# GLOSSÁRIO E FUNÇÕES DE EXPANSÃO DE QUERY
# ============================================================================

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
    'du-pda': ['deep unfolded probability data association', 'detector com deep unfolding'],
    'mmse-pic': ['mmse parallel interference cancellation', 'cancelamento paralelo de interferência'],
    'ifpi': ['interference-free pilot insertion', 'inserção ortogonal de pilotos'],
    'uxmap': ['unrolled xmap', 'detector desdobrado com aprendizado profundo'],
    'papr': ['peak-to-average power ratio', 'relação pico-média', 'eficiência de amplificadores'],
    'dft pré-codificação': ['discrete fourier transform precoding', 'espalhamento de informação'],
    'pts': ['partial time sequence', 'sequência parcial no tempo', 'redução de papr'],
    'slm': ['selective mapping', 'mapeamento seletivo', 'técnica de redução de papr'],
    'qpsk': ['quadrature phase shift keying', 'modulação 4-qam'],
    '16-qam': ['16 quadrature amplitude modulation', '4 bits por símbolo'],
    '64-qam': ['64 quadrature amplitude modulation', '6 bits por símbolo'],
    '256-qam': ['256 quadrature amplitude modulation', '8 bits por símbolo'],
    'ldpc': ['low-density parity-check', 'código de verificação de paridade de baixa densidade'],
    'ldpc não binário': ['códigos ldpc sobre gf(q)', 'eficiência aprimorada'],
    'polar codes': ['códigos polares', 'codificação de canal 5g/6g'],
    'uep': ['unequal error protection', 'proteção desigual contra erros'],
    'mse modificado': ['mean squared error modificado', 'função de custo adaptada'],
    'dpd': ['digital pre-distortion', 'pré-distorção digital', 'linearização de amplificadores'],
    'mzm': ['mach-zehnder modulator', 'modulador mach-zehnder', 'modulador eletro-óptico'],
    'dml': ['directly modulated laser', 'laser modulado diretamente'],
    'rof': ['radio over fiber', 'rádio sobre fibra', 'distribuição rf por fibra óptica'],
    'smf': ['single-mode fiber', 'fibra monomodo'],
    'ld': ['laser diode', 'diodo laser'],
    'sbs': ['stimulated brillouin scattering', 'espalhamento brillouin estimulado'],
    'evmrms': ['error vector magnitude rms', 'métrica de qualidade de modulação'],
    'osfl': ['optimal step-size filtered least-mean-square', 'algoritmo adaptativo para dpd'],
    'vbisam': ['vector-based iterative search algorithm for mzm', 'linearização de mzm'],
    'backhaul sem fio': ['enlace ponto a ponto', 'xhaul', 'conexão troncal sem fibra'],
    'oobe': ['out-of-band emission', 'emissão fora da banda', 'interferência adjacente'],
    'tvws': ['television white spaces', 'espaços em branco de tv', 'canais ociosos vhf/uhf'],
    'erac': ['enhanced remote area communications', 'comunicações aprimoradas em áreas remotas', 'super células'],
    'vhf': ['very high frequency', '30-300 mhz', 'faixa baixa para longo alcance'],
    'uhf': ['ultra high frequency', '300 mhz - 3 ghz', 'faixa média para tv digital'],
    'sensoriamento espectral': ['detecção de energia', 'cognitive radio', 'proteção a usuários primários'],
    'anatel resolução 747': ['regulamentação tvws brasil', 'uso secundário de espectro vhf/uhf', 'potência máxima 1 watt'],
    'banco de dados geolocalizado': ['geo-location database', 'registro de transmissores', 'proteção usuários primários'],
    '5g-range': ['remote area access network for 5g', 'projeto europa-brasil para conectividade rural'],
    'isac': ['integrated sensing and communications', 'sensoriamento e comunicação integrados'],
    'channel charting': ['mapeamento geométrico do canal', 'representação espacial sem gps', 'autoencoder'],
    'mpcc': ['multipoint channel charting', 'channel charting multiponto', 'gerenciamento de recursos de rádio'],
    'csi': ['channel state information', 'informação do estado do canal', 'vetor de características'],
    'raymobtime': ['dataset brasileiro de mobilidade', 'cenários urbanos realistas', 'dados sincronizados posição-canal'],
    'deepsense6g': ['dataset sintético para sensoriamento', 'simulação de ambientes complexos'],
    'gnss': ['global navigation satellite systems', 'sistemas globais de navegação por satélite'],
    'gps': ['global positioning system', 'sistema de posicionamento global'],
    'imus': ['inertial measurement units', 'unidades de medição inercial', 'sensores de movimento'],
    'ips': ['indoor positioning system', 'sistema de posicionamento indoor'],
    'posicionamento centimétrico': ['precisão 1-10 cm', 'rastreamento de alta precisão'],
    'lidar': ['light detection and ranging', 'detecção e medição por laser', 'nuvem de pontos 3d'],
    'blensor': ['blender sensor', 'simulador de sensores lidar', 'geração de scans sintéticos'],
    'nuvem de pontos': ['point cloud', 'conjunto de coordenadas 3d', 'x y z intensidade'],
    'bbox': ['bounding box', 'caixa delimitadora', 'anotação de objetos 3d'],
    'ia nativa': ['ai-native', 'integração profunda de ia na arquitetura', 'ia como princípio fundamental 6g'],
    'ia embarcada': ['on-device ai', 'processamento de ia no terminal', 'inferência local'],
    'ia generativa': ['genai', 'criação de conteúdo e serviços personalizados', 'automação de planejamento'],
    'user+ia': ['interação humano-agente inteligente', 'agentes ia personalizados', 'experiência preditiva'],
    'terminal+ia': ['xpu no dispositivo', 'unidades de processamento especializadas', 'ia local no ue'],
    'service+ia': ['interação multimodal com agentes', 'serviços adaptativos baseados em ia'],
    'nível 0 autonomia': ['manual business', 'operações totalmente manuais'],
    'nível 1 autonomia': ['assisted operations', 'diagnóstico assistido'],
    'nível 2 autonomia': ['partial automation', 'monitoramento preditivo'],
    'nível 3 autonomia': ['conditional automation', 'automação condicional'],
    'nível 4 autonomia': ['high automation', 'automação quase total'],
    'nível 5 autonomia': ['full automation', 'rede totalmente autônoma', 'self-healing self-optimizing'],
    'closed-loop automation': ['automação em malha fechada', 'monitoramento-análise-decisão-execução'],
    'network digital twin': ['gêmeo digital da rede', 'simulação em tempo real', 'teste sem impacto operacional'],
    'ai-ran': ['inteligência artificial no ran', 'otimização de recursos de rádio por ia'],
    'ai-core': ['inteligência artificial no core network', 'nwda function', 'análise preditiva'],
    'semantic communication': ['comunicação semântica', 'transmissão de significado em vez de bits'],
    'free5gc': ['plataforma core network 5g open source', 'implementação sba do 3gpp'],
    'oai': ['openairinterface', 'implementação open source de ran', 'plataforma sdr para 5g/6g'],
    'open ran': ['redes desfragmentadas', 'interfaces abertas', 'desagregação hardware/software'],
    'sba': ['service-based architecture', 'arquitetura baseada em serviços', 'core 5g/6g'],
    'amf': ['access and mobility management function', 'gerenciamento de acesso e mobilidade'],
    'smf': ['session management function', 'gerenciamento de sessão'],
    'upf': ['user plane function', 'função do plano do usuário'],
    'pcf': ['policy control function', 'controle de política'],
    'ausf': ['authentication server function', 'servidor de autenticação'],
    'udm': ['unified data management', 'gerenciamento unificado de dados'],
    'udr': ['unified data repository', 'repositório unificado de dados'],
    'nrf': ['network repository function', 'repositório de rede'],
    'nssf': ['network slice selection function', 'seleção de fatia de rede'],
    'bsf': ['binding support function', 'suporte de vinculação'],
    'nwdaf': ['network data analytics function', 'análise de dados da rede'],
    'nef': ['network exposure function', 'exposição de capacidades da rede'],
    'n3iwf': ['non-3gpp interworking function', 'interconexão não-3gpp'],
    'ran slicing': ['fatiamento de rede de acesso', 'network slicing ran', 'fatias virtuais'],
    'nasp': ['network automation and slicing platform', 'plataforma de automação e fatiamento'],
    'nssmf': ['network slice subnet management function', 'gerenciamento de sub-rede de fatia'],
    'csmf': ['communication service management function', 'gerenciamento de serviço de comunicação'],
    'rantester': ['ferramenta de teste de ran', 'simulador de equipamento do usuário'],
    'mec': ['multi-access edge computing', 'computação na borda de múltiplo acesso'],
    'lotos': ['linear optimization for task orchestration scheduling', 'orquestração de tarefas'],
    'spprc': ['shortest path problem with resource constraints', 'caminho mais curto com restrições'],
    'milp': ['mixed-integer linear programming', 'programação linear inteira mista'],
    'gurobi': ['solver de otimização matemática', 'ferramenta para problemas milp'],
    'cplex': ['ibm ilog cplex optimizer', 'solver comercial para programação linear'],
    'scip': ['solving constraint integer programs', 'solver open source para otimização'],
    'embb': ['enhanced mobile broadband', 'banda larga móvel aprimorada'],
    'urllc': ['ultra reliable low latency communications', 'comunicações ultra confiáveis de baixa latência'],
    'mmtc': ['massive machine-type communications', 'comunicações machine-type massivas'],
    'hrllc': ['hyper-reliable low latency communication', 'comunicação hiperconfiável de baixa latência'],
    'immersiva': ['realidade estendida', 'xr', 'holográfica', 'multissensorial'],
    'gêmeos digitais': ['digital twins', 'simulação física-digital', 'modelagem preditiva'],
    'conectividade ubíqua': ['conectando os não conectados', 'cobertura universal', 'áreas remotas'],
    'ioe': ['internet of everything', 'integração físico-digital'],
    'internet tátil': ['tactile internet', 'feedback háptico', 'sensações táteis em tempo real'],
    'bci': ['brain-computer interface', 'interface cérebro-computador'],
    'uav': ['unmanned aerial vehicle', 'veículo aéreo não tripulado', 'drone'],
    'v2x': ['vehicle-to-everything', 'comunicações veiculares'],
    'cras': ['connected robotics and autonomous systems', 'robótica conectada'],
    'sub-6ghz': ['faixas baixas e médias', 'below 6 ghz', '3.5 ghz', '6 ghz'],
    'mmwave': ['ondas milimétricas', 'millimeter wave', '24-40 ghz', 'sub-100 ghz'],
    'sub-thz': ['sub-terahertz', '100-300 ghz', 'faixa sub-terahertz'],
    'thz': ['terahertz', 'faixa acima 100 ghz', '0.1-10 thz'],
    'vlc': ['visible light communication', 'comunicação por luz visível', '400-800 thz'],
    'usrp': ['universal software radio peripheral', 'plataforma sdr'],
    'usrp b210': ['plataforma sdr de baixo custo', '2x2 mimo', '70 mhz - 6 ghz'],
    'usrp n310': ['plataforma sdr de alto desempenho', '4x4 mimo', '10 mhz - 6 ghz'],
    'fpga': ['field-programmable gate array', 'circuito reconfigurável', 'processamento em hardware'],
    'xilinx zynq': ['soc com fpga', 'system-on-chip', 'processamento híbrido cpu-fpga'],
    'intel arria': ['fpga da intel', 'plataforma de aceleração'],
    'gpu nvidia': ['unidade de processamento gráfico', 'cuda cores', 'aceleração de deep learning'],
    'tesla v100': ['gpu datacenter', 'tensor cores', 'inferência de redes neurais'],
    'rtx a6000': ['gpu profissional', '48 gb de vram'],
    'gpsdo': ['gps disciplined oscillator', 'oscilador disciplinado por gps', 'referência de tempo precisa'],
    'sincronismo ptp': ['precision time protocol', 'sincronização de relógio', 'ieee 1588'],
    'gnu radio': ['framework sdr open source', 'fluxogramas de processamento', 'bloco de processamento'],
    'volk': ['vector optimized library of kernels', 'otimização simd', 'aceleração de kernels'],
    'aff3ct': ['a fast forward error correction toolbox', 'simulação de códigos', 'decodificação de canal'],
    'uhd': ['usrp hardware driver', 'abstração de hardware sdr', 'api de controle de rádio'],
    'sionna': ['biblioteca tensorflow para camada física', 'simulação de sistemas sem fio'],
    'numpy': ['numeric python', 'biblioteca de computação numérica', 'arrays multidimensionais'],
    'pandas': ['análise de dados', 'dataframes', 'manipulação de tabelas'],
    'matplotlib': ['visualização de dados', 'gráficos estáticos'],
    'scikit-learn': ['aprendizado de máquina', 'machine learning', 'algoritmos clássicos'],
    'tensorflow': ['framework de deep learning', 'aprendizado profundo'],
    'pytorch': ['biblioteca de deep learning', 'autograd', 'computação tensorial'],
    'anaconda': ['distribuição python', 'gerenciador de pacotes', 'ambiente científico'],
    'jupyter notebook': ['ambiente interativo', 'computação literária'],
    'opencv': ['open computer vision', 'processamento de imagens', 'visão computacional'],
    'cuda': ['compute unified device architecture', 'paralelismo em gpu nvidia'],
    'docker': ['containerização', 'isolamento de ambientes', 'reprodutibilidade'],
    'kubernetes': ['orquestração de containers', 'escalabilidade automática'],
    'helm': ['gerenciador de pacotes kubernetes', 'charts helm'],
    'prometheus': ['monitoramento de métricas', 'coleta de telemetria'],
    'grafana': ['visualização de métricas', 'dashboards de monitoramento'],
    'istio': ['service mesh', 'gerenciamento de tráfego entre serviços'],
    'hpc': ['high performance computing', 'computação de alto desempenho', 'supercomputação'],
    'cluster': ['agrupamento de nós', 'computação distribuída', 'paralelismo de tarefas'],
    'nó de computação': ['compute node', 'servidor dedicado', 'processamento paralelo'],
    'nó de gerenciamento': ['management node', 'controle do cluster', 'orquestração de recursos'],
    'nó de armazenamento': ['storage node', 'servidor de dados', 'sistemas de arquivos paralelos'],
    'lustre': ['sistema de arquivos paralelo', 'armazenamento distribuído', 'alto throughput'],
    'gpfs': ['general parallel file system', 'ibm spectrum scale', 'armazenamento em cluster'],
    'slurm': ['simple linux utility for resource management', 'orquestrador de jobs', 'agendamento'],
    'infiniband': ['rede de interconexão de alto desempenho', 'baixa latência', 'alta largura de banda'],
    'rdma': ['remote direct memory access', 'acesso direto à memória remota', 'zero-copy networking'],
    'gpu passthrough': ['atribuição direta de gpu', 'virtualização de aceleradores', 'cuda em vm'],
    'setup': ['configuração experimental', 'arranjo de equipamentos para teste'],
    'agendamento': ['reserva de recursos', 'planejamento de experimentos', 'gestão de tempo'],
    'rbac': ['role-based access control', 'controle de acesso baseado em papéis'],
    'administrador global': ['superusuário da plataforma', 'gestão de todas as organizações'],
    'administrador de organização': ['gestor de entidade institucional', 'controle de projetos'],
    'administrador de projeto': ['coordenador de experimento', 'gestão de setups e agendamentos'],
    'log': ['registro de atividades', 'rastreabilidade de experimentos', 'auditoria'],
    'equipamento': ['dispositivo de teste', 'hardware para validação', 'usrp sdr antena'],
    'projeto': ['experimento 6g', 'conjunto de setups relacionados', 'escopo de pesquisa'],
    'organização': ['instituição participante', 'entidade gestora', 'ufpa ufg inatel ufsc'],
    'yolov8': ['you only look once v8', 'detecção de objetos em tempo real', 'visão computacional'],
    'microsoft coco': ['common objects in context', 'base de dados de objetos comuns', '80 classes'],
    'data augmentation': ['aumento sintético de dados', 'transformações aleatórias', 'rotação ruído brilho'],
    'detecção de incêndios florestais': ['monitoramento ambiental com ia', 'visão computacional áreas verdes'],
    'agropecuária inteligente': ['agricultura de precisão com 6g', 'monitoramento de rebanhos', 'detecção pragas'],
    'pgcs': ['platform for generic communication services', 'plataforma genérica de serviços'],
    'epgs': ['embedded pgcs', 'versão compacta do pgcs para iot'],
    'hts': ['hash table storage', 'armazenamento por tabela de hash'],
    'pss': ['publish-subscribe service', 'serviço de publicação-assinatura'],
    'itu-r wp5d': ['working party 5d', 'grupo de padronização imt', 'definição do imt-2030'],
    '3gpp': ['3rd generation partnership project', 'parceria de projeto de 3ª geração', 'padronização 5g/6g'],
    'imt-2030': ['international mobile telecommunications-2030', 'framework 6g da itu', 'requisitos técnicos'],
    'imt-2020': ['international mobile telecommunications-2020', 'framework 5g da itu', 'requisitos 5g'],
    'wrc-27': ['world radiocommunication conference 2027', 'conferência mundial de radiocomunicação'],
    'anatel': ['agência nacional de telecomunicações', 'regulador brasileiro de espectro'],
    'irs': ['intelligent reflecting surface', 'superfície refletora inteligente', 'metamateriais'],
    'full duplex': ['operação full duplex', 'transmissão simultânea', 'mesma frequência'],
    'non-terrestrial': ['ntn', 'non-terrestrial network', 'satélites e haps para cobertura global'],
    'fwa': ['fixed wireless access', 'acesso sem fio fixo', 'substituição de fibra em áreas remotas'],
    'vhdl': ['vhsic hardware description language', 'linguagem de descrição de hardware'],
    'vlsi': ['very large-scale integration', 'integração em escala muito grande', 'projeto de circuitos'],
    'udn': ['ultra-dense network', 'rede ultra densa', 'células pequenas em alta densidade'],
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


def expand_query_with_embeddings(query, embeddings_model, vectorstore, max_expansions=3):
    try:
        e5_query = query if query.startswith('query: ') else f'query: {query}'
        initial_results = vectorstore.similarity_search(e5_query, k=20)
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


# ============================================================================
# SETUP DO VECTORSTORE
# ============================================================================

def _extract_table_text_fitz(page, page_num):
    for strategy in ['lines', 'lines_strict', 'text']:
        try:
            tables = page.find_tables(strategy=strategy)
            if not (tables and tables.tables):
                continue
            table_text = ''
            seen_bboxes = set()
            for i, t in enumerate(tables.tables):
                try:
                    bbox_key = tuple(round(v, 1) for v in t.bbox) if hasattr(t, 'bbox') else None
                    if bbox_key and bbox_key in seen_bboxes:
                        continue
                    if bbox_key:
                        seen_bboxes.add(bbox_key)
                    df = t.to_pandas()
                    if df is None or df.empty or df.shape[1] < 2:
                        continue
                    df = df.dropna(how='all').dropna(axis=1, how='all')
                    if df.empty:
                        continue
                    table_text += f'\n**[Tabela {i+1} - Página {page_num+1}]**\n\n{df.to_markdown(index=False)}\n'
                except Exception:
                    pass
            if table_text:
                return table_text, strategy
        except Exception:
            pass
    return '', 'none'


def load_pdfs_improved(directory):
    documents = []
    files = glob.glob(os.path.join(directory, '**/*.pdf'), recursive=True)
    if not files:
        logging.warning(f'Nenhum PDF encontrado em {directory}')
        return documents
    total_tables = 0
    for filepath in files:
        try:
            logging.info(f'Processando {os.path.basename(filepath)}...')
            doc = fitz.open(filepath)
            try:
                for page_num, page in enumerate(doc):
                    try:
                        table_text, strategy = _extract_table_text_fitz(page, page_num)
                        if strategy != 'none':
                            total_tables += 1
                        text = page.get_text("text", flags=fitz.TEXT_DEHYPHENATE)
                        combined = (table_text + '\n' + text) if table_text else text
                        clean = clean_text_content(combined)
                        if clean and len(clean.split()) >= 10:
                            documents.append({
                                'text': clean,
                                'metadata': {
                                    'source': os.path.basename(filepath),
                                    'page': page_num + 1,
                                    'path': filepath,
                                    'tables_count': 1 if table_text else 0,
                                    'extraction_strategy': strategy
                                }
                            })
                    except Exception as e:
                        logging.error(f'Erro página {page_num+1} de {os.path.basename(filepath)}: {e}')
            finally:
                doc.close()
        except Exception as e:
            logging.error(f'Erro ao abrir {filepath}: {e}')
    logging.info(f'Páginas extraídas: {len(documents)} | Tabelas detectadas: {total_tables}')
    return documents


def setup_vectorstore():
    embeddings = SentenceTransformerEmbeddings(
        model_name=EMBEDDING_MODEL_NAME
    )

    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)

    try:
        collection = client.get_collection(name="6g_docs")
        if collection.count() == 0:
            raise ValueError('Coleção vazia')
        vectorstore = Chroma(
            client=client,
            collection_name="6g_docs",
            embedding_function=embeddings
        )
        logging.info(f"Banco de dados carregado com {collection.count()} documentos")

    except (ValueError, Exception) as e:
        if 'does not exist' not in str(e) and 'Coleção vazia' not in str(e):
            logging.warning(f'Recriando banco: {e}')
        logging.info("Criando novo banco de dados...")
        documents = load_pdfs_improved(PDF_DIR)
        if not documents:
            raise ValueError(f'Nenhum texto extraído dos PDFs em {PDF_DIR}')
        chunks = chunk_documents(documents)
        if not chunks:
            raise ValueError('Chunks vazios após splitter')
        logging.info(f"Total de chunks criados: {len(chunks)}")
        for c in chunks:
            c.page_content = 'passage: ' + re.sub(r'^(passage: )+', '', c.page_content)

        vectorstore = Chroma.from_documents(
            chunks,
            embeddings,
            client=client,
            collection_name="6g_docs"
        )

    base_retriever = vectorstore.as_retriever(search_kwargs={'k': INITIAL_RETRIEVAL_K})
    logging.info(f"Retriever configurado para buscar {INITIAL_RETRIEVAL_K} documentos inicialmente")
    return base_retriever, embeddings, vectorstore


# ============================================================================
# RERANKING RETRIEVER
# ============================================================================

class ReRankingRetriever:
    def __init__(self, base_retriever, cross_encoder, top_k=4):
        self.base_retriever = base_retriever
        self.cross_encoder = cross_encoder
        self.top_k = top_k

    def get_relevant_documents(self, query):
        raw_expanded = expand_query(query)
        expanded_query = raw_expanded if raw_expanded.startswith('query: ') else f'query: {raw_expanded}'

        initial_docs = self.base_retriever.invoke(expanded_query)

        if len(initial_docs) < 5:
            logging.info(f"Poucos documentos encontrados ({len(initial_docs)}), tentando busca adicional...")
            q_prefixed = query if query.startswith('query: ') else f'query: {query}'
            additional_docs = self.base_retriever.invoke(q_prefixed)
            seen_contents = {doc.page_content for doc in initial_docs}
            for doc in additional_docs:
                if doc.page_content not in seen_contents:
                    initial_docs.append(doc)
                    seen_contents.add(doc.page_content)

        if not initial_docs:
            logging.warning("Nenhum documento encontrado na busca inicial")
            return []

        pairs = [(query, re.sub(r'^passage: ', '', doc.page_content)) for doc in initial_docs]
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
            logging.warning(f"Nenhum documento passou no threshold de score ({MIN_CROSS_ENCODER_SCORE})")
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

        logging.info(f"Retornando {len(filtered_docs)} documentos relevantes")
        return filtered_docs


# ============================================================================
# SYSTEM PROMPT
# ============================================================================

SYSTEM_PROMPT = """Você é um assistente técnico especializado em 6G. Responda de forma direta e precisa.



REGRAS:

- Comece IMEDIATAMENTE com a informação solicitada

- NÃO use frases como "Baseado nos dados", "De acordo com", "Podemos inferir", "Não está explicitamente mencionado, mas podemos inferir...", "Não especificada...", "Não especificado diretamente..."

- Preserve valores numéricos e termos técnicos exatamente como aparecem

- Se não encontrar informação específica, forneça o mais próximo disponível

- Use formatação clara (listas, tópicos) quando apropriado

- Redobre o cuidado ao analisar tabelas para gerar respostas

- Símbolos por subquadro:

ID 0 = 2 | ID 1 = 4 | ID 2 = 8 | ID 3 = 16 | ID 4 = 32 | ID 5 = 64.



EXEMPLO DE RESPOSTA INCORRETA (NUNCA FAÇA ISSO)(NUNCA MESMO):

"Baseado nos dados fornecidos, a Numerologia ID 0 possui..."

"Não está explicitamente mencionado, mas podemos inferir..."

"Não especificada..."

"Não especificado diretamente..."

Lembre-se: O usuário quer apenas a RESPOSTA, não quer saber sobre suas fontes ou limitações.

"""


# ============================================================================
# QUERY E GENERATE COM GROQ
# ============================================================================

def query_documents(question):
    try:
        relevant_docs = retriever.get_relevant_documents(question)
        pdf_docs = []
        model_docs = []
        source_indicators = []
        if not relevant_docs:
            context = ""
        else:
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
                        context_parts.append(content[:remaining_chars] + "...[TRUNCADO]")
                        source_indicators.append(f"[{source_type} | Score: {score:.2f} | TRUNCADO]")
                        logging.warning(f"Documento truncado: {doc.metadata.get('source', '?')} p.{doc.metadata.get('page', '?')} ({len(content)} -> {remaining_chars} chars)")
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
            'pdf_count': len(pdf_docs) if relevant_docs else 0,
            'model_count': len(model_docs) if relevant_docs else 0,
            'source_indicators': source_indicators if relevant_docs else []
        }
    except Exception as e:
        logging.error(f"Erro em query_documents: {str(e)}")
        return f"Erro: {str(e)}"


def generate_answer(prompt, metadata=None):
    try:
        question_start = prompt.find('Pergunta: ') + len('Pergunta: ')
        question_end = prompt.find('\n\nResposta:')
        question = prompt[question_start:question_end].strip()

        context_start = prompt.find('Contexto dos documentos (Prioridade: PDF > Modelo):\n') + len('Contexto dos documentos (Prioridade: PDF > Modelo):\n')
        context_end = prompt.find('\n\nPergunta:')
        context = prompt[context_start:context_end].strip()

        groq_client = Groq(api_key=GROQ_API_KEY)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Contexto técnico:\n{context}\n\nPergunta: {question}\n\nResponda de forma direta e profissional, sem mencionar o contexto ou suas fontes. Comece imediatamente com a informação solicitada."}
        ]

        response = groq_client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=messages,
            temperature=0.3,
            max_tokens=500
        )

        answer = response.choices[0].message.content.strip()

        unwanted_phrases = [
            'Baseado nos dados disponíveis',
            'Baseado nas informações disponíveis',
            'De acordo com o contexto',
            'Segundo os documentos',
            'Podemos inferir',
            'Não há informações explícitas',
            'Não está explicitamente mencionado',
            'Não há menção',
            'Não foi mencionado',
            'No entanto, podemos inferir',
            'É importante notar que'
        ]

        for phrase in unwanted_phrases:
            answer = answer.replace(phrase, '')
            answer = answer.replace(phrase.lower(), '')

        lines = [line for line in answer.split('\n') if line.strip()]
        answer = '\n'.join(lines)

        forbidden_phrases = [
            'baseado nos dados fornecidos',
            'de acordo com o contexto',
            'segundo os documentos',
            'podemos inferir',
            'não está explicitamente mencionado',
            'não há menção',
            'não foi mencionado',
            'não encontrei'
        ]

        answer_lower = answer.lower()
        for phrase in forbidden_phrases:
            if phrase in answer_lower:
                logging.warning(f"Resposta contém frase proibida: {phrase}")
                break

        return answer if answer else 'Não foi possível gerar uma resposta baseada no contexto.'

    except Exception as e:
        logging.error(f"Erro em generate_answer: {str(e)}")
        return f"Erro ao gerar resposta: {str(e)}"


# ============================================================================
# BUSCA HIERÁRQUICA E RESPOSTA
# ============================================================================

def hierarchical_search_and_generate(question):
    try:
        logging.info(f"=== BUSCA HIERÁRQUICA: {question} ===")
        query_result = query_documents(question)
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

        response = generate_answer(prompt, metadata=metadata)

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


# ============================================================================
# INICIALIZAÇÃO GLOBAL
# ============================================================================

base_retriever = None
embeddings = None
vectorstore = None
retriever = None

def initialize_rag():
    global base_retriever, embeddings, vectorstore, retriever
    base_retriever, embeddings, vectorstore = setup_vectorstore()
    cross_encoder = CrossEncoder(CROSS_ENCODER_MODEL, device="cpu")
    retriever = ReRankingRetriever(base_retriever, cross_encoder)


# ============================================================================
# TRANSCRIÇÃO DE ÁUDIO COM GROQ WHISPER
# ============================================================================

def transcribe_audio(audio_file_path: str) -> str:
    """
    Transcreve um arquivo de áudio usando Groq Whisper
    
    Args:
        audio_file_path: Caminho para o arquivo de áudio (mp3, wav, m4a, etc)
        
    Returns:
        str: Texto transcrito
        
    Raises:
        Exception: Se houver erro na transcrição
    """
    try:
        logging.info(f"🎤 Iniciando transcrição de áudio: {audio_file_path}")
        
        client = Groq()
        
        # Abrir arquivo de áudio
        with open(audio_file_path, "rb") as audio_file:
            # Usar Groq Whisper para transcrição
            transcript = client.audio.transcriptions.create(
                file=(audio_file_path.split('/')[-1], audio_file, "audio/mpeg"),
                model="whisper-large-v3-turbo",
                language="pt"  # Português
            )
        
        text = transcript.text
        logging.info(f"✅ Áudio transcrito com sucesso: {len(text)} caracteres")
        logging.info(f"📝 Texto: {text[:100]}...")
        
        return text
        
    except FileNotFoundError:
        error_msg = f"Arquivo de áudio não encontrado: {audio_file_path}"
        logging.error(f"❌ {error_msg}")
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f"Erro ao transcrever áudio: {str(e)}"
        logging.error(f"❌ {error_msg}")
        raise Exception(error_msg)


def process_audio_and_answer(audio_file_path: str) -> dict:
    """
    Processa um arquivo de áudio e gera uma resposta
    
    Args:
        audio_file_path: Caminho para o arquivo de áudio
        
    Returns:
        dict: Resultado com response, sources, docs_used, confidence, etc
    """
    try:
        # 1. Transcrever áudio
        question = transcribe_audio(audio_file_path)
        
        # 2. Processar pergunta normalmente
        result = hierarchical_search_and_generate(question)
        
        # 3. Adicionar informação de que foi voz
        result['audio_transcribed'] = question
        result['is_audio'] = True
        
        logging.info("✅ Processamento de áudio completo")
        return result
        
    except Exception as e:
        logging.error(f"❌ Erro no processamento de áudio: {str(e)}")
        return {
            'response': f"Erro ao processar áudio: {str(e)}",
            'confidence': 'erro',
            'hierarchy_info': None,
            'is_audio': True,
            'audio_error': str(e)
        }
