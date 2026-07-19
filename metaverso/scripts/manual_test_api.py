#!/usr/bin/env python3
"""
Script de teste para a API IC Metaverso RAG
Testa todos os endpoints e valida as respostas
"""

import requests
import json
import sys
from typing import Dict, Any

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

def test_root():
    """Testa o endpoint raiz"""
    print_header("Testando GET /")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print_success(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            print_error(f"Status inesperado: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Erro: {str(e)}")
        return False

def test_health():
    """Testa o endpoint de health check"""
    print_header("Testando GET /api/v1/health")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health")
        if response.status_code == 200:
            print_success(f"Status: {response.status_code}")
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            if data.get('status') == 'healthy':
                print_success("Servidor está saudável!")
                return True
            else:
                print_warning("Status não é 'healthy'")
                return False
        else:
            print_error(f"Status inesperado: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Erro: {str(e)}")
        return False

def test_ask_without_api_key():
    """Testa o endpoint /ask sem API key"""
    print_header("Testando POST /api/v1/ask (SEM API KEY)")
    try:
        payload = {"question": "O que é 6G?"}
        response = requests.post(
            f"{BASE_URL}/api/v1/ask",
            json=payload
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

def test_ask_with_api_key():
    """Testa o endpoint /ask com API key"""
    print_header("Testando POST /api/v1/ask (COM API KEY)")
    try:
        payload = {"question": "O que é 6G?"}
        headers = {"X-API-Key": API_KEY}
        response = requests.post(
            f"{BASE_URL}/api/v1/ask",
            json=payload,
            headers=headers
        )
        if response.status_code == 200:
            print_success(f"Status: {response.status_code}")
            data = response.json()
            print(f"\nResponse parcial:")
            print(f"  - Response: {data.get('response', '')[:100]}...")
            print(f"  - Docs usados: {data.get('docs_used', 0)}")
            print(f"  - Confiança: {data.get('confidence', 'N/A')}")
            print(f"  - Timestamp: {data.get('timestamp', 'N/A')}")
            return True
        else:
            print_error(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return False
    except Exception as e:
        print_error(f"Erro: {str(e)}")
        return False

def test_info():
    """Testa o endpoint de informações"""
    print_header("Testando GET /api/v1/info")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/info")
        if response.status_code == 200:
            print_success(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            print_error(f"Status inesperado: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Erro: {str(e)}")
        return False

def test_cors_preflight():
    """Testa requisição OPTIONS (CORS preflight)"""
    print_header("Testando OPTIONS /api/v1/ask (CORS Preflight)")
    try:
        headers = {
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "X-API-Key"
        }
        response = requests.options(
            f"{BASE_URL}/api/v1/ask",
            headers=headers
        )
        if response.status_code == 200:
            print_success(f"Status: {response.status_code}")
            cors_headers = {
                k: v for k, v in response.headers.items()
                if 'access-control' in k.lower() or 'cors' in k.lower()
            }
            if cors_headers:
                print("Headers CORS recebidos:")
                for k, v in cors_headers.items():
                    print(f"  {k}: {v}")
            return True
        else:
            print_warning(f"Status: {response.status_code} (esperado 200)")
            return False
    except Exception as e:
        print_error(f"Erro: {str(e)}")
        return False

def main():
    """Executa todos os testes"""
    print(f"{Colors.BLUE}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     IC Metaverso RAG API - Suite de Testes                ║")
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
        "GET /": test_root(),
        "GET /api/v1/health": test_health(),
        "GET /api/v1/info": test_info(),
        "CORS Preflight": test_cors_preflight(),
        "POST /api/v1/ask (sem API key)": test_ask_without_api_key(),
        "POST /api/v1/ask (com API key)": test_ask_with_api_key(),
    }
    
    # Resumo
    print_header("Resumo dos Testes")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{Colors.GREEN}PASSOU{Colors.END}" if result else f"{Colors.RED}FALHOU{Colors.END}"
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
