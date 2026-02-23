from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from pydantic import BaseModel
import asyncio
import logging
from ia import IASystem  

logging.basicConfig(level=logging.INFO)

class QueryRequest(BaseModel):
    question: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("🚀 Iniciando servidor RAG 6G...")
    app.state.ia_system = IASystem()
    app.state.ia_system.initialize()   
    logging.info("✅ IASystem carregado e pronto!")
    yield
    logging.info("🛑 Encerrando servidor...")

app = FastAPI(title="RAG 6G Brasil - Servidor para Unity", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ask")
async def ask_http(request: QueryRequest):
    ia: IASystem = app.state.ia_system
    try:
        result = await asyncio.to_thread(ia.ask, request.question)
        return {
            "response": result["response"],
            "confidence": result["confidence"],
            "confidence_desc": result.get("confidence_desc"),
            "sources": [
                {
                    "source": doc.metadata.get("source"),
                    "page": doc.metadata.get("page"),
                    "score": doc.metadata.get("retrieval_score")
                } for doc in result.get("docs", [])
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    ia: IASystem = app.state.ia_system
    logging.info("🔌 Cliente Unity conectado ao WebSocket")

    try:
        while True:
            data = await websocket.receive_json()
            question = data.get("question")
            if not question:
                await websocket.send_json({"error": "question obrigatória"})
                continue

            result = await asyncio.to_thread(ia.ask, question)

            await websocket.send_json({
                "type": "response",
                "response": result["response"],
                "confidence": result["confidence"],
                "confidence_desc": result.get("confidence_desc"),
                "sources": [
                    {
                        "source": doc.metadata.get("source"),
                        "page": doc.metadata.get("page"),
                        "score": round(doc.metadata.get("retrieval_score", 0), 3)
                    } for doc in result.get("docs", [])
                ]
            })

    except WebSocketDisconnect:
        logging.info("❌ Cliente Unity desconectado")
    except Exception as e:
        logging.error(f"Erro no WS: {e}")
        try:
            await websocket.send_json({"error": str(e)})
        except:
            pass

@app.get("/health")
async def health():
    return {"status": "ok", "model_loaded": app.state.ia_system.model is not None}