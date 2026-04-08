import os
import logging
import shutil
from app.rag import load_pdfs_improved, chunk_documents, setup_vectorstore
from app.config import PDF_DIR, CHROMA_PERSIST_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def reset_database():
    """
    Remove completamente o banco de dados ChromaDB existente.
    Use com cautela! Isso apagará todos os documentos indexados.
    """
    if os.path.exists(CHROMA_PERSIST_DIR):
        try:
            shutil.rmtree(CHROMA_PERSIST_DIR)
            logger.info(f"Banco de dados removido: {CHROMA_PERSIST_DIR}")
            return True
        except Exception as e:
            logger.error(f"Erro ao remover banco de dados: {e}")
            return False
    else:
        logger.info("Banco de dados não existe")
        return True


def check_database_status():
    """
    Verifica o status do banco de dados ChromaDB.
    
    Returns:
        tuple: (existe: bool, contagem: int)
    """
    if os.path.exists(CHROMA_PERSIST_DIR):
        try:
            import chromadb
            client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
            collection = client.get_collection(name="6g_docs")
            count = collection.count()
            logger.info(f"Banco de dados existe com {count} documentos")
            return True, count
        except Exception as e:
            logger.warning(f"Erro ao acessar banco de dados: {e}")
            return False, 0
    else:
        logger.info("Banco de dados não existe")
        return False, 0


def ingest_pdfs(pdf_directory=None):
    """
    Realiza ingestão de PDFs do diretório especificado.
    Se nenhum diretório for especificado, usa o padrão do config.
    
    Args:
        pdf_directory: Caminho do diretório com PDFs (opcional)
        
    Returns:
        dict: Informações sobre a ingestão
    """
    directory = pdf_directory or PDF_DIR
    
    if not os.path.exists(directory):
        logger.error(f"Diretório não existe: {directory}")
        return {
            "success": False,
            "error": f"Diretório não existe: {directory}",
            "documents": 0,
            "chunks": 0
        }
    
    try:
        logger.info(f"Iniciando ingestão de PDFs de: {directory}")
        
        # Carregar PDFs
        documents = load_pdfs_improved(directory)
        if not documents:
            logger.warning("Nenhum documento foi extraído")
            return {
                "success": False,
                "error": "Nenhum PDF encontrado ou extraído",
                "documents": 0,
                "chunks": 0
            }
        
        logger.info(f"Total de documentos extraídos: {len(documents)}")
        
        # Fazer chunking
        chunks = chunk_documents(documents)
        if not chunks:
            logger.warning("Nenhum chunk foi criado")
            return {
                "success": False,
                "error": "Nenhum chunk foi criado após processamento",
                "documents": len(documents),
                "chunks": 0
            }
        
        logger.info(f"Total de chunks criados: {len(chunks)}")
        
        # Recrear banco de dados
        logger.info("Recriando banco de dados...")
        reset_database()
        
        # Configurar vectorstore (isso vai fazer a ingestão)
        base_retriever, embeddings, vectorstore = setup_vectorstore()
        
        logger.info("Ingestão concluída com sucesso!")
        
        return {
            "success": True,
            "documents": len(documents),
            "chunks": len(chunks),
            "message": "PDFs ingeridos com sucesso"
        }
    
    except Exception as e:
        logger.error(f"Erro durante ingestão: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "documents": 0,
            "chunks": 0
        }


def get_database_info():
    """
    Retorna informações detalhadas sobre o banco de dados.
    
    Returns:
        dict: Informações do banco
    """
    try:
        import chromadb
        
        exists, count = check_database_status()
        
        if not exists:
            return {
                "exists": False,
                "path": CHROMA_PERSIST_DIR,
                "documents": 0,
                "message": "Banco de dados não foi criado"
            }
        
        client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        collection = client.get_collection(name="6g_docs")
        
        # Pegar metadata para entender o conteúdo
        all_data = collection.get()
        
        metadata_list = all_data.get('metadatas', [])
        sources = set()
        total_pages = 0
        total_tables = 0
        
        for metadata in metadata_list:
            if metadata:
                source = metadata.get('source', 'unknown')
                sources.add(source)
                total_pages += int(metadata.get('page', 0))
                total_tables += int(metadata.get('tables_count', 0))
        
        return {
            "exists": True,
            "path": CHROMA_PERSIST_DIR,
            "documents": count,
            "unique_sources": list(sources),
            "total_pages": total_pages,
            "total_tables": total_tables,
            "source_count": len(sources)
        }
    
    except Exception as e:
        logger.error(f"Erro ao obter informações do banco: {e}")
        return {
            "exists": False,
            "path": CHROMA_PERSIST_DIR,
            "error": str(e)
        }


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "ingest":
            pdf_dir = sys.argv[2] if len(sys.argv) > 2 else None
            result = ingest_pdfs(pdf_dir)
            print(result)
        
        elif command == "status":
            info = get_database_info()
            print(info)
        
        elif command == "reset":
            confirm = input("Tem certeza que deseja remover o banco de dados? (sim/nao): ")
            if confirm.lower() == "sim":
                result = reset_database()
                print(f"Banco de dados removido: {result}")
            else:
                print("Operação cancelada")
        
        else:
            print("Comandos disponíveis:")
            print("  ingest [diretorio]  - Ingere PDFs de um diretório")
            print("  status              - Mostra status do banco de dados")
            print("  reset               - Remove o banco de dados (com confirmação)")
    
    else:
        print("Comandos disponíveis:")
        print("  python -m app.ingest ingest [diretorio]")
        print("  python -m app.ingest status")
        print("  python -m app.ingest reset")
