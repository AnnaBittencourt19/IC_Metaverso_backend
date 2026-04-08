#!/usr/bin/env python3
"""
Teste para o endpoint /api/v1/ask-audio
Valida transcrição de áudio e processamento RAG
"""

import requests
import json
import tempfile
import sys
import os
from pathlib import Path

# Configuração
BASE_URL = "http://localhost:8000"
API_KEY = "metaverso-secret-key-2026"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_header(title: str):
    """Imprime um cabeçalho formatado"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}{Colors.END}\n")

def print_success(message: str):
    """Imprime mensagem de sucesso"""
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message: str):
    """Imprime mensagem de erro"""
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_warning(message: str):
    """Imprime mensagem de aviso"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")

def create_test_audio_file():
    """
    Cria um arquivo de áudio de teste usando pyttsx3
    Retorna o caminho do arquivo
    """
    try:
        print("📝 Tentando criar arquivo de áudio de teste com pyttsx3...")
        import pyttsx3
        
        engine = pyttsx3.init()
        
        # Criar arquivo temporário
        temp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        temp_path = temp_file.name
        temp_file.close()
        
        # Gerar áudio
        engine.save_to_file("O que é 6G", temp_path)
        engine.runAndWait()
        
        if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
            print_success(f"Arquivo de teste criado: {temp_path}")
            return temp_path
        else:
            print_warning("pyttsx3 não gerou arquivo válido")
            return None
            
    except ImportError:
        print_warning("pyttsx3 não está instalado")
        print("  Instale com: pip install pyttsx3")
        return None
    except Exception as e:
        print_error(f"Erro ao criar áudio: {str(e)}")
        return None

def find_test_audio():
    """
    Procura por arquivo de áudio de teste no sistema
    """
    common_paths = [
        "./test_audio.mp3",
        "./test.mp3",
        "./audio.mp3",
        Path.home() / "Downloads" / "test.mp3",
        Path.home() / "Downloads" / "audio.mp3",
    ]
    
    for path in common_paths:
        if Path(path).exists():
            print_success(f"Arquivo de teste encontrado: {path}")
            return str(path)
    
    return None

def test_ask_audio_without_api_key():
    """Testa o endpoint /ask-audio sem API key"""
    print_header("Testando POST /api/v1/ask-audio (SEM API KEY)")
    
    # Procurar arquivo de áudio
    audio_path = find_test_audio() or create_test_audio_file()
    
    if not audio_path:
        print_warning("Nenhum arquivo de áudio disponível para teste")
        print("  Crie um arquivo de áudio em ./test_audio.mp3")
        return False
    
    try:
        with open(audio_path, 'rb') as f:
            files = {'audio_file': f}
            response = requests.post(
                f"{BASE_URL}/api/v1/ask-audio",
                files=files
            )
        
        if response.status_code == 403:
            print_success("✓ API rejeitou requisição sem API key (esperado)")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            print_warning(f"Status: {response.status_code} (esperado 403)")
            return False
    except Exception as e:
        print_error(f"Erro: {str(e)}")
        return False

def test_ask_audio_with_invalid_file():
    """Testa o endpoint /ask-audio com arquivo inválido"""
    print_header("Testando POST /api/v1/ask-audio (ARQUIVO INVÁLIDO)")
    
    try:
        # Criar arquivo "fake"
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
            tmp.write(b"Not an audio file")
            fake_file = tmp.name
        
        try:
            with open(fake_file, 'rb') as f:
                files = {'audio_file': f}
                headers = {'X-API-Key': API_KEY}
                response = requests.post(
                    f"{BASE_URL}/api/v1/ask-audio",
                    files=files,
                    headers=headers
                )
            
            if response.status_code == 400:
                print_success("✓ API rejeitou arquivo com tipo inválido (esperado)")
                print(f"Response: {json.dumps(response.json(), indent=2)}")
                return True
            else:
                print_warning(f"Status: {response.status_code} (esperado 400)")
                return False
        finally:
            os.unlink(fake_file)
            
    except Exception as e:
        print_error(f"Erro: {str(e)}")
        return False

def test_ask_audio_with_valid_file():
    """Testa o endpoint /ask-audio com arquivo válido"""
    print_header("Testando POST /api/v1/ask-audio (COM API KEY E ÁUDIO VÁLIDO)")
    
    # Procurar arquivo de áudio
    audio_path = find_test_audio() or create_test_audio_file()
    
    if not audio_path:
        print_warning("Nenhum arquivo de áudio disponível para teste")
        print("  Crie um arquivo de áudio em ./test_audio.mp3")
        print("  OU use pyttsx3: pip install pyttsx3")
        return None  # Skip test
    
    try:
        with open(audio_path, 'rb') as f:
            files = {'audio_file': f}
            headers = {'X-API-Key': API_KEY}
            response = requests.post(
                f"{BASE_URL}/api/v1/ask-audio",
                files=files,
                headers=headers
            )
        
        if response.status_code == 200:
            print_success(f"Status: {response.status_code}")
            data = response.json()
            
            print(f"\nResponse parcial:")
            print(f"  - Audio transcrito: {data.get('audio_transcribed', 'N/A')[:50]}...")
            print(f"  - Response: {data.get('response', '')[:100]}...")
            print(f"  - Docs usados: {data.get('docs_used', 0)}")
            print(f"  - Confiança: {data.get('confidence', 'N/A')}")
            print(f"  - Is Audio: {data.get('is_audio', False)}")
            print(f"  - Timestamp: {data.get('timestamp', 'N/A')}")
            
            # Validar campos obrigatórios
            required_fields = ['response', 'audio_transcribed', 'sources', 'docs_used', 'confidence', 'is_audio']
            missing_fields = [f for f in required_fields if f not in data]
            
            if missing_fields:
                print_warning(f"Campos faltando: {missing_fields}")
                return False
            
            if not data.get('is_audio'):
                print_warning("Campo 'is_audio' não é True")
                return False
            
            print_success("Todos os campos obrigatórios presentes")
            return True
        else:
            print_error(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return False
            
    except Exception as e:
        print_error(f"Erro: {str(e)}")
        return False

def test_ask_audio_multipart():
    """Testa o formato multipart/form-data"""
    print_header("Testando Formato multipart/form-data")
    
    audio_path = find_test_audio() or create_test_audio_file()
    
    if not audio_path:
        print_warning("Nenhum arquivo de áudio para teste")
        return None
    
    try:
        with open(audio_path, 'rb') as f:
            files = {'audio_file': (Path(audio_path).name, f, 'audio/mpeg')}
            headers = {'X-API-Key': API_KEY}
            response = requests.post(
                f"{BASE_URL}/api/v1/ask-audio",
                files=files,
                headers=headers
            )
        
        if response.status_code == 200:
            print_success("✓ Formato multipart/form-data funciona corretamente")
            return True
        else:
            print_error(f"Status: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Erro: {str(e)}")
        return False

def main():
    """Executa todos os testes"""
    print(f"{Colors.BLUE}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║   IC Metaverso RAG API - Teste de Áudio (/ask-audio)     ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}")
    
    # Verificar se a API está rodando
    try:
        requests.get(f"{BASE_URL}/", timeout=2)
    except requests.exceptions.ConnectionError:
        print_error(f"Não consegui conectar em {BASE_URL}")
        print("\nInicie a API com:")
        print(f"  {Colors.YELLOW}uvicorn app.main:app --reload --host 0.0.0.0 --port 8000{Colors.END}")
        sys.exit(1)
    
    print_success(f"Conectado em {BASE_URL}\n")
    
    # Executar testes
    results = {
        "POST /ask-audio (sem API key)": test_ask_audio_without_api_key(),
        "POST /ask-audio (arquivo inválido)": test_ask_audio_with_invalid_file(),
        "Formato multipart/form-data": test_ask_audio_multipart(),
        "POST /ask-audio (arquivo válido)": test_ask_audio_with_valid_file(),
    }
    
    # Resumo
    print_header("Resumo dos Testes")
    passed = sum(1 for v in results.values() if v is True)
    total = sum(1 for v in results.values() if v is not None)
    
    for test_name, result in results.items():
        if result is None:
            status = f"{Colors.YELLOW}SKIPPED{Colors.END}"
        elif result:
            status = f"{Colors.GREEN}PASSOU{Colors.END}"
        else:
            status = f"{Colors.RED}FALHOU{Colors.END}"
        print(f"  {test_name}: {status}")
    
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"Total: {passed}/{total} testes passaram")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    if passed == total:
        print_success("Todos os testes passaram! 🎉")
        return 0
    else:
        print_error(f"{total - passed} teste(s) falharam")
        return 1

if __name__ == "__main__":
    sys.exit(main())
