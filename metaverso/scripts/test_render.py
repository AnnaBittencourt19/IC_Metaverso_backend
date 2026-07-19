#!/usr/bin/env python3
"""
Script para testar API no Render
Use: python test_render.py https://seu-servico.onrender.com
"""

import requests
import json
import sys
import argparse
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(title):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}{Colors.END}\n")

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

def test_health(base_url, api_key):
    """Testa health check"""
    print_header("1. Health Check")
    
    try:
        url = f"{base_url}/api/v1/health"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print_success(f"Status: {response.status_code}")
            data = response.json()
            print(f"  Status: {data.get('status')}")
            print(f"  RAG Initialized: {data.get('rag_initialized')}")
            print(f"  Timestamp: {data.get('timestamp')}")
            return True
        else:
            print_error(f"Status: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except requests.exceptions.Timeout:
        print_error("Timeout - API não respondeu em 10s")
        return False
    except Exception as e:
        print_error(f"Erro: {str(e)}")
        return False

def test_info(base_url):
    """Testa endpoint de info"""
    print_header("2. API Info")
    
    try:
        url = f"{base_url}/api/v1/info"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print_success(f"Status: {response.status_code}")
            data = response.json()
            print(f"  Name: {data.get('name')}")
            print(f"  Version: {data.get('version')}")
            print(f"  Description: {data.get('description')}")
            return True
        else:
            print_error(f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Erro: {str(e)}")
        return False

def test_ask_without_key(base_url):
    """Testa /ask sem API key"""
    print_header("3. POST /ask (SEM API KEY)")
    
    try:
        url = f"{base_url}/api/v1/ask"
        response = requests.post(
            url,
            json={"question": "O que é 6G?"},
            timeout=15
        )
        
        if response.status_code == 403:
            print_success("Corretamente rejeitou sem API key (403)")
            return True
        else:
            print_warning(f"Status: {response.status_code} (esperado 403)")
            return False
    except Exception as e:
        print_error(f"Erro: {str(e)}")
        return False

def test_ask_with_key(base_url, api_key):
    """Testa /ask com API key"""
    print_header("4. POST /ask (COM API KEY)")
    
    try:
        url = f"{base_url}/api/v1/ask"
        headers = {"X-API-Key": api_key}
        payload = {"question": "O que é 6G?"}
        
        print_info(f"Enviando: {payload}")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            print_success(f"Status: {response.status_code}")
            data = response.json()
            
            print(f"\n  Response (primeiras 100 chars):")
            print(f"    {data.get('response', '')[:100]}...")
            print(f"\n  Metadados:")
            print(f"    - Docs usados: {data.get('docs_used', 0)}")
            print(f"    - Confiança: {data.get('confidence', 'N/A')}")
            print(f"    - Timestamp: {data.get('timestamp', 'N/A')}")
            print(f"    - Sources: {len(data.get('sources', []))} documentos")
            
            # Validar campos obrigatórios
            required = ['response', 'sources', 'docs_used', 'timestamp']
            missing = [f for f in required if f not in data]
            
            if missing:
                print_warning(f"Campos faltando: {missing}")
                return False
            
            return True
        else:
            print_error(f"Status: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except requests.exceptions.Timeout:
        print_warning("Timeout - RAG está lento (esperado ~10s)")
        return False
    except Exception as e:
        print_error(f"Erro: {str(e)}")
        return False

def test_ask_audio_without_key(base_url):
    """Testa /ask-audio sem API key"""
    print_header("5. POST /ask-audio (SEM API KEY)")
    
    try:
        # Criar arquivo fake
        from io import BytesIO
        fake_audio = BytesIO(b"fake audio data")
        
        url = f"{base_url}/api/v1/ask-audio"
        files = {"audio_file": ("test.mp3", fake_audio, "audio/mpeg")}
        
        response = requests.post(url, files=files, timeout=10)
        
        if response.status_code == 403:
            print_success("Corretamente rejeitou sem API key (403)")
            return True
        else:
            print_warning(f"Status: {response.status_code} (esperado 403)")
            return False
    except Exception as e:
        print_warning(f"Endpoint /ask-audio pode não estar disponível: {str(e)}")
        return None

def test_ask_audio_with_key(base_url, api_key, audio_path):
    """Testa /ask-audio com API key"""
    print_header("6. POST /ask-audio (COM API KEY)")
    
    if not Path(audio_path).exists():
        print_warning(f"Arquivo de áudio não encontrado: {audio_path}")
        print("  Pulando teste de áudio")
        return None
    
    try:
        url = f"{base_url}/api/v1/ask-audio"
        headers = {"X-API-Key": api_key}
        
        with open(audio_path, "rb") as f:
            files = {"audio_file": (Path(audio_path).name, f, "audio/mpeg")}
            
            print_info(f"Enviando arquivo: {Path(audio_path).name}")
            response = requests.post(url, files=files, headers=headers, timeout=45)
        
        if response.status_code == 200:
            print_success(f"Status: {response.status_code}")
            data = response.json()
            
            print(f"\n  Áudio transcrito:")
            print(f"    {data.get('audio_transcribed', 'N/A')}")
            print(f"\n  Response (primeiras 100 chars):")
            print(f"    {data.get('response', '')[:100]}...")
            print(f"\n  Metadados:")
            print(f"    - Docs usados: {data.get('docs_used', 0)}")
            print(f"    - Confiança: {data.get('confidence', 'N/A')}")
            print(f"    - Is Audio: {data.get('is_audio', False)}")
            
            required = ['response', 'audio_transcribed', 'sources', 'docs_used']
            missing = [f for f in required if f not in data]
            
            if missing:
                print_warning(f"Campos faltando: {missing}")
                return False
            
            return True
        else:
            print_error(f"Status: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except requests.exceptions.Timeout:
        print_warning("Timeout - Transcrição está lenta (esperado ~15s)")
        return False
    except Exception as e:
        print_warning(f"Erro ao testar áudio: {str(e)}")
        return None

def main():
    parser = argparse.ArgumentParser(
        description="Testa API IC Metaverso no Render"
    )
    parser.add_argument(
        "url",
        nargs="?",
        default="http://localhost:8000",
        help="URL da API (ex: https://seu-servico.onrender.com)"
    )
    parser.add_argument(
        "--key",
        default="metaverso-secret-key-2026",
        help="API Key"
    )
    parser.add_argument(
        "--audio",
        default="test.mp3",
        help="Caminho do arquivo de áudio para teste"
    )
    
    args = parser.parse_args()
    
    base_url = args.url.rstrip("/")
    api_key = args.key
    audio_path = args.audio
    
    print(f"{Colors.BLUE}{Colors.BOLD}")
    print("╔════════════════════════════════════════════════════════╗")
    print("║   IC Metaverso RAG API - Teste no Render              ║")
    print("╚════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}")
    
    print_info(f"URL: {base_url}")
    print_info(f"API Key: {api_key[:10]}...")
    
    # Verificar conectividade
    print_header("Verificando Conectividade")
    try:
        response = requests.get(base_url, timeout=5)
        print_success("Servidor está acessível")
    except Exception as e:
        print_error(f"Não consegui conectar: {str(e)}")
        sys.exit(1)
    
    # Executar testes
    results = {
        "Health Check": test_health(base_url, api_key),
        "API Info": test_info(base_url),
        "POST /ask (sem key)": test_ask_without_key(base_url),
        "POST /ask (com key)": test_ask_with_key(base_url, api_key),
        "POST /ask-audio (sem key)": test_ask_audio_without_key(base_url),
        "POST /ask-audio (com key)": test_ask_audio_with_key(base_url, api_key, audio_path),
    }
    
    # Sumário
    print_header("Sumário dos Testes")
    
    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)
    total = len(results)
    
    for test_name, result in results.items():
        if result is None:
            status = f"{Colors.YELLOW}SKIPPED{Colors.END}"
        elif result:
            status = f"{Colors.GREEN}PASSOU{Colors.END}"
        else:
            status = f"{Colors.RED}FALHOU{Colors.END}"
        print(f"  {test_name}: {status}")
    
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"Total: {passed} passaram | {failed} falharam | {skipped} skipped")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    if failed == 0:
        print_success("Todos os testes passaram! 🎉")
        return 0
    else:
        print_error(f"{failed} teste(s) falharam")
        return 1

if __name__ == "__main__":
    sys.exit(main())
