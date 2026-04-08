#!/usr/bin/env python3
"""
Script para testar a API sem precisar de curl ou Postman.
Executa requisições HTTP para testar o sistema.
"""

import requests
import json
import argparse
import sys
from typing import Dict, Any

BASE_URL = "http://localhost:8000"


def test_health() -> bool:
    """Testa o health check."""
    print("\n🏥 Testando Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Status: {data.get('status')}")
            print(f"  ℹ️  Mensagem: {data.get('message')}")
            return True
        else:
            print(f"  ❌ Erro: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Erro ao conectar: {e}")
        print(f"  💡 Verifique se o servidor está rodando em {BASE_URL}")
        return False


def test_query(question: str) -> Dict[str, Any]:
    """Testa uma consulta."""
    print(f"\n🔍 Testando Query: '{question}'")
    try:
        payload = {"question": question}
        response = requests.post(
            f"{BASE_URL}/query",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Sucesso!")
            print(f"\n  📝 Resposta:")
            print(f"  {data.get('response')}")
            print(f"\n  📊 Confiança: {data.get('confidence_desc')}")
            print(f"  📈 Documentos: {data.get('total_docs')}")
            print(f"     - PDFs: {data.get('pdf_docs')}")
            print(f"     - Modelos: {data.get('model_docs')}")
            print(f"     - PDF%: {data.get('pdf_percentage'):.1f}%")
            return data
        else:
            print(f"  ❌ Erro: Status {response.status_code}")
            print(f"  Resposta: {response.text}")
            return None
    
    except requests.exceptions.Timeout:
        print(f"  ❌ Timeout (30s) - Pergunta muito complexa?")
        return None
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return None


def test_root() -> bool:
    """Testa o endpoint raiz."""
    print("\n📚 Testando Endpoint Raiz...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ API: {data.get('title')}")
            print(f"  ℹ️  Versão: {data.get('version')}")
            print(f"  📖 Endpoints disponíveis:")
            for endpoint, url in data.get('endpoints', {}).items():
                print(f"     - {endpoint}: {url}")
            return True
        else:
            print(f"  ❌ Erro: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False


def run_suite(verbose: bool = False) -> None:
    """Executa suite completa de testes."""
    print("=" * 60)
    print("🧪 SUITE DE TESTES - METAVERSO 6G RAG API")
    print("=" * 60)
    
    # Test 1: Health Check
    health_ok = test_health()
    if not health_ok:
        print("\n⚠️  Servidor não está respondendo. Abortando testes.")
        return
    
    # Test 2: Root Endpoint
    root_ok = test_root()
    
    # Test 3: Queries
    test_queries = [
        "O que é 6G?",
        "Qual a diferença entre OFDM e GFDM?",
        "Como funciona MIMO?",
    ]
    
    print("\n" + "=" * 60)
    print("🔍 TESTANDO QUERIES")
    print("=" * 60)
    
    for query in test_queries:
        result = test_query(query)
        if result and verbose:
            print(f"\n  Resposta completa:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 60)
    print("✅ TESTES CONCLUÍDOS")
    print("=" * 60)


def interactive_mode() -> None:
    """Modo interativo para fazer queries."""
    print("=" * 60)
    print("💬 MODO INTERATIVO - METAVERSO 6G RAG")
    print("=" * 60)
    print("\nDicas:")
    print("  - Digite 'sair' para encerrar")
    print("  - Digite 'saúde' para verificar health check")
    print("  - Digite 'ajuda' para ver comandos")
    print("")
    
    while True:
        try:
            question = input("\n🤔 Sua pergunta: ").strip()
            
            if question.lower() == "sair":
                print("👋 Até logo!")
                break
            elif question.lower() == "saúde":
                test_health()
            elif question.lower() == "ajuda":
                print("\nComandos disponíveis:")
                print("  'sair'    - Encerrar")
                print("  'saúde'   - Verificar health check")
                print("  'ajuda'   - Mostrar este menu")
                print("  Ou faça qualquer pergunta sobre 6G!")
            elif question:
                test_query(question)
        
        except KeyboardInterrupt:
            print("\n\n👋 Até logo!")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Teste a API Metaverso 6G RAG",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  # Executar suite de testes completa
  python test_api.py

  # Modo interativo
  python test_api.py -i

  # Testar query específica
  python test_api.py -q "O que é 6G?"

  # Verbose (mais detalhes)
  python test_api.py -v
        """
    )
    
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Modo interativo (faça perguntas)"
    )
    
    parser.add_argument(
        "-q", "--query",
        type=str,
        help="Fazer uma pergunta específica"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Modo verbose (mais detalhes)"
    )
    
    parser.add_argument(
        "-u", "--url",
        type=str,
        default=BASE_URL,
        help=f"URL base da API (padrão: {BASE_URL})"
    )
    
    args = parser.parse_args()
    
    # Atualizar BASE_URL se fornecido
    global BASE_URL
    BASE_URL = args.url
    
    if args.interactive:
        interactive_mode()
    elif args.query:
        print("=" * 60)
        print("🧪 TESTE DE QUERY INDIVIDUAL")
        print("=" * 60)
        health_ok = test_health()
        if health_ok:
            test_query(args.query)
    else:
        run_suite(verbose=args.verbose)


if __name__ == "__main__":
    main()
