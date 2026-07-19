#!/usr/bin/env python3
"""
Script de teste para validar otimizações de memória
Executa múltiplas requisições e monitora o uso de memória
"""

import requests
import json
import time
import psutil
import sys
from tabulate import tabulate

# Configuração
BASE_URL = "http://localhost:8000"
API_KEY = "metaverso-secret-key-2026"
NUM_REQUESTS = 5

HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def get_memory_status():
    """Obtém status de memória via API"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/memory", headers=HEADERS, timeout=5)
        return response.json()
    except Exception as e:
        print(f"❌ Erro ao obter memória: {e}")
        return None

def test_ask_endpoint(question="O que é 6G?"):
    """Testa o endpoint /ask"""
    try:
        payload = {"question": question}
        response = requests.post(
            f"{BASE_URL}/api/v1/ask",
            json=payload,
            headers=HEADERS,
            timeout=35
        )
        return response.status_code == 200, response.json()
    except requests.Timeout:
        return False, {"error": "Timeout"}
    except Exception as e:
        return False, {"error": str(e)}

def main():
    print("=" * 80)
    print("🧪 TESTE DE OTIMIZAÇÃO DE MEMÓRIA")
    print("=" * 80)
    
    # Verificar conectividade
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print("✅ Servidor conectado\n")
    except Exception as e:
        print(f"❌ Erro ao conectar ao servidor: {e}")
        sys.exit(1)
    
    # Memória inicial
    mem_initial = get_memory_status()
    if mem_initial:
        print(f"📊 Memória Inicial:")
        print(f"   RSS: {mem_initial['memory']['rss_mb']} MB")
        print(f"   Percentual: {mem_initial['memory']['percent']}%")
        print()
    
    # Teste de requisições
    print(f"🔄 Executando {NUM_REQUESTS} requisições...\n")
    
    results = []
    questions = [
        "O que é 6G?",
        "Qual é a diferença entre 5G e 6G?",
        "Quais são as frequências do 6G?",
        "O que é NOMA?",
        "Explique sobre inteligência artificial em 6G"
    ]
    
    for i in range(NUM_REQUESTS):
        question = questions[i % len(questions)]
        print(f"[{i+1}/{NUM_REQUESTS}] Pergunta: {question[:50]}...")
        
        start_time = time.time()
        success, response = test_ask_endpoint(question)
        elapsed_time = time.time() - start_time
        
        mem_status = get_memory_status()
        
        if success:
            print(f"   ✅ Sucesso em {elapsed_time:.2f}s")
            print(f"   📊 Memória: {mem_status['memory']['rss_mb']} MB ({mem_status['memory']['percent']}%)")
            print(f"   📄 Documentos usados: {response.get('docs_used', 0)}")
            results.append({
                "Requisição": f"#{i+1}",
                "Status": "✅ OK",
                "Tempo (s)": f"{elapsed_time:.2f}",
                "Memória (MB)": f"{mem_status['memory']['rss_mb']:.1f}",
                "Docs": response.get('docs_used', 0)
            })
        else:
            print(f"   ❌ Falha: {response.get('error', 'Desconhecido')}")
            print(f"   📊 Memória: {mem_status['memory']['rss_mb']} MB ({mem_status['memory']['percent']}%)")
            results.append({
                "Requisição": f"#{i+1}",
                "Status": "❌ ERRO",
                "Tempo (s)": "-",
                "Memória (MB)": f"{mem_status['memory']['rss_mb']:.1f}",
                "Docs": "-"
            })
        
        print()
        time.sleep(1)  # Aguardar 1s entre requisições
    
    # Memória final
    mem_final = get_memory_status()
    
    print("=" * 80)
    print("📋 RESUMO DOS TESTES")
    print("=" * 80)
    print()
    print(tabulate(results, headers="keys", tablefmt="grid"))
    print()
    
    if mem_initial and mem_final:
        delta_mb = mem_final['memory']['rss_mb'] - mem_initial['memory']['rss_mb']
        delta_percent = mem_final['memory']['percent'] - mem_initial['memory']['percent']
        
        print("📊 Memória:")
        print(f"   Inicial:  {mem_initial['memory']['rss_mb']:.1f} MB ({mem_initial['memory']['percent']:.1f}%)")
        print(f"   Final:    {mem_final['memory']['rss_mb']:.1f} MB ({mem_final['memory']['percent']:.1f}%)")
        print(f"   Delta:    {delta_mb:+.1f} MB ({delta_percent:+.1f}%)")
        
        if delta_mb > 200:
            print("   ⚠️  Crescimento significativo de memória")
        elif delta_mb > 50:
            print("   ⚡ Crescimento moderado (esperado)")
        else:
            print("   ✅ Memória bem gerenciada!")
    
    print()
    print(f"🎯 Estatísticas GC: {mem_final['gc_stats']['collections']}")
    print(f"🎯 Objetos em memória: {mem_final['gc_stats']['objects']}")
    print()
    print("=" * 80)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⛔ Teste interrompido pelo usuário")
        sys.exit(0)
