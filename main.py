import asyncio
from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="UltraQuest Core Engine")

# Permite que a sua futura página web converse com o servidor sem bloqueios de segurança
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ESTADO_JOGADOR = {
    "rank": "DESTRUCTIVE",
    "multiplicador": 1.0,
    "pontos_totais": 0,
    "ultima_atividade": datetime.now()
}

RANKS = ["DESTRUCTIVE", "CHAOTIC", "BRUTAL", "ANARCHIC", "SUPREME", "SSADISTIC", "SSSHITSTORM", "ULTRAKILL"]
MULTIPLICADORES = {"DESTRUCTIVE": 1.0, "CHAOTIC": 1.2, "BRUTAL": 1.5, "ANARCHIC": 2.0, "SUPREME": 2.5, "SSADISTIC": 3.0, "SSSHITSTORM": 4.0, "ULTRAKILL": 5.0}
TEMPOS_LIMITE = {"DESTRUCTIVE": 999999, "CHAOTIC": 7200, "BRUTAL": 7200, "ANARCHIC": 5400, "SUPREME": 3600, "SSADISTIC": 2700, "SSSHITSTORM": 1800, "ULTRAKILL": 900}

class TarefaConcluida(BaseModel):
    titulo: str
    prazo: int
    importancia: int
    dificuldade: int

@app.on_event("startup")
async def iniciar_motor():
    asyncio.create_task(loop_de_decaimento())

async def loop_de_decaimento():
    while True:
        await asyncio.sleep(10)
        agora = datetime.now()
        tempo_inativo = (agora - ESTADO_JOGADOR["ultima_atividade"]).total_seconds()
        rank_atual = ESTADO_JOGADOR["rank"]
        
        if rank_atual != "DESTRUCTIVE" and tempo_inativo > TEMPOS_LIMITE[rank_atual]:
            idx = RANKS.index(rank_atual)
            novo_rank = RANKS[idx - 1]
            ESTADO_JOGADOR["rank"] = novo_rank
            ESTADO_JOGADOR["multiplicador"] = MULTIPLICADORES[novo_rank]
            ESTADO_JOGADOR["ultima_atividade"] = agora

@app.post("/tarefas/concluir")
async def concluir_tarefa(tarefa: TarefaConcluida):
    pontos_base = (tarefa.prazo + tarefa.importancia) * tarefa.dificuldade
    pontos_finais = int(pontos_base * ESTADO_JOGADOR["multiplicador"])
    ESTADO_JOGADOR["pontos_totais"] += pontos_finais
    
    idx = RANKS.index(ESTADO_JOGADOR["rank"])
    if idx < len(RANKS) - 1:
        novo_rank = RANKS[idx + 1]
        ESTADO_JOGADOR["rank"] = novo_rank
        ESTADO_JOGADOR["multiplicador"] = MULTIPLICADORES[novo_rank]
        
    ESTADO_JOGADOR["ultima_atividade"] = datetime.now()
    return {"mensagem": "COMBO UP!", "pontos_ganhos": pontos_finais, "estado": ESTADO_JOGADOR}

@app.get("/status")
async def obter_status():
    return ESTADO_JOGADOR
