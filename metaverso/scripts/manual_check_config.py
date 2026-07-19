#!/usr/bin/env python3
"""
Script de teste para validar a configuração do sistema RAG.
Executa verificações básicas antes de iniciar o servidor.
"""

import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def check_environment():
    """Verifica se as variáveis de ambiente estão configuradas."""
    logger.info("🔍 Verificando variáveis de ambiente...")
    
    required_vars = ["GROQ_API_KEY"]
    missing = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
            logger.error(f"  ❌ {var} não está definida")
        else:
            logger.info(f"  ✅ {var} configurada")
    
    return len(missing) == 0


def check_dependencies():
    """Verifica se as dependências estão instaladas."""
    logger.info("🔍 Verificando dependências...")
    
    required_packages = [
        "fastapi",
        "uvicorn",
        "chromadb",
        "langchain",
        "sentence_transformers",
        "groq",
        "fitz",
        "numpy",
        "pandas"
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"  ✅ {package} instalado")
        except ImportError:
            missing.append(package)
            logger.error(f"  ❌ {package} não está instalado")
    
    if missing:
        logger.warning(f"\n📦 Instale os pacotes faltando com:")
        logger.warning(f"   pip install {' '.join(missing)}")
    
    return len(missing) == 0


def check_directories():
    """Verifica se os diretórios necessários existem."""
    logger.info("🔍 Verificando diretórios...")
    
    from app.config import CHROMA_PERSIST_DIR, PDF_DIR
    
    # ChromaDB
    if os.path.exists(CHROMA_PERSIST_DIR):
        logger.info(f"  ✅ Diretório ChromaDB existe: {CHROMA_PERSIST_DIR}")
    else:
        logger.warning(f"  ⚠️ Diretório ChromaDB não existe: {CHROMA_PERSIST_DIR}")
        logger.info(f"    Será criado na primeira ingestão de PDFs")
    
    # PDFs
    if os.path.exists(PDF_DIR):
        pdf_count = len([f for f in os.listdir(PDF_DIR) if f.endswith('.pdf')])
        logger.info(f"  ✅ Diretório PDFs existe: {PDF_DIR}")
        logger.info(f"     Encontrados {pdf_count} arquivos PDF")
    else:
        logger.warning(f"  ⚠️ Diretório PDFs não existe: {PDF_DIR}")
        logger.info(f"    Crie o diretório: mkdir -p {PDF_DIR}")


def check_database():
    """Verifica o status do banco de dados."""
    logger.info("🔍 Verificando banco de dados...")
    
    try:
        from app.ingest import get_database_info
        info = get_database_info()
        
        if info.get('exists'):
            logger.info(f"  ✅ Banco de dados existe")
            logger.info(f"     Documentos: {info.get('documents', 0)}")
            logger.info(f"     Fontes: {info.get('source_count', 0)}")
        else:
            logger.warning(f"  ⚠️ Banco de dados ainda não foi criado")
            logger.info(f"    Execute: python -m app.ingest ingest")
    
    except Exception as e:
        logger.error(f"  ❌ Erro ao verificar banco: {e}")


def test_imports():
    """Testa se os módulos principais podem ser importados."""
    logger.info("🔍 Testando imports dos módulos...")
    
    try:
        from app.config import GROQ_API_KEY, CHROMA_PERSIST_DIR
        logger.info("  ✅ app.config importado com sucesso")
    except Exception as e:
        logger.error(f"  ❌ Erro ao importar app.config: {e}")
        return False
    
    try:
        from app.rag import hierarchical_search_and_generate
        logger.info("  ✅ app.rag importado com sucesso")
    except Exception as e:
        logger.error(f"  ❌ Erro ao importar app.rag: {e}")
        return False
    
    try:
        from app.main import app
        logger.info("  ✅ app.main importado com sucesso")
    except Exception as e:
        logger.error(f"  ❌ Erro ao importar app.main: {e}")
        return False
    
    return True


def main():
    """Executa todas as verificações."""
    logger.info("=" * 60)
    logger.info("🧪 TESTE DE CONFIGURAÇÃO - METAVERSO 6G RAG")
    logger.info("=" * 60)
    
    checks = [
        ("Variáveis de Ambiente", check_environment),
        ("Dependências Python", check_dependencies),
        ("Diretórios", check_directories),
        ("Imports de Módulos", test_imports),
        ("Banco de Dados", check_database),
    ]
    
    results = []
    for name, check_func in checks:
        logger.info("")
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            logger.error(f"Erro ao executar {name}: {e}")
            results.append((name, False))
    
    # Resumo
    logger.info("")
    logger.info("=" * 60)
    logger.info("📋 RESUMO DOS TESTES")
    logger.info("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "✅ OK" if result else "❌ FALHOU"
        logger.info(f"{status}: {name}")
        if not result:
            all_passed = False
    
    logger.info("=" * 60)
    
    if all_passed:
        logger.info("✅ Todos os testes passaram! Sistema pronto para uso.")
        logger.info("")
        logger.info("Para iniciar o servidor, execute:")
        logger.info("  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        return 0
    else:
        logger.error("❌ Alguns testes falharam. Verifique os erros acima.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
