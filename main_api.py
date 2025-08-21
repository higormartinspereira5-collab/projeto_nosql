# Importa as ferramentas necessárias
from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from bson.objectid import ObjectId

# --- CONFIGURAÇÃO INICIAL DA API ---
app = FastAPI(
    title="Marca Jogo API",
    description="API para organizar e consultar partidas de esportes.",
    version="1.0.0"
)

# --- CONEXÃO COM O BANCO DE DADOS MONGODB ---
# Lembre-se de colar a sua Connection String correta aqui!
MONGO_URI = "mongodb+srv://usuario_projeto:32224447@cluster0.m6raoxu.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client['marca_jogo_db']

# --- ENDPOINTS DA API ---

# Endpoint raiz, apenas para teste
@app.get("/")
def read_root():
    return {"Status": "API do Marca Jogo está online!"}

# ====================================================================
# === ENTREGA 3: BUSCA USANDO UM ÍNDICE (createIndex)
# ====================================================================

@app.get("/partidas/buscar")
def buscar_partidas_por_texto(termo: str):
    """
    Busca partidas que contenham o 'termo' na descrição ou no local.
    IMPORTANTE: Esta busca requer um índice de texto na coleção 'partidas'.
    """
    try:
        query = {"$text": {"$search": termo}}
        projection = {"score": {"$meta": "textScore"}}
        partidas_cursor = db.partidas.find(query, projection)

        resultados = []
        for partida in partidas_cursor:
            partida['_id'] = str(partida['_id'])
            partida['esporte_id'] = str(partida['esporte_id'])
            partida['organizador_id'] = str(partida['organizador_id'])
            if 'participantes_ids' in partida:
                partida['participantes_ids'] = [str(pid) for pid in partida['participantes_ids']]
            resultados.append(partida)

        if not resultados:
            raise HTTPException(status_code=404, detail="Nenhuma partida encontrada com este termo.")

        return resultados
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro interno: {e}")

# ====================================================================
# === ENTREGA 4: DUAS OPERAÇÕES COM AGGREGATION PIPELINE
# ====================================================================

# --- OPERAÇÃO 1: Listar partidas com detalhes do esporte e organizador ---
@app.get("/partidas/detalhadas")
def obter_partidas_com_detalhes():
    """
    Lista todas as partidas com informações detalhadas do esporte e do organizador,
    usando um Aggregation Pipeline com $lookup para "juntar" coleções.
    """
    pipeline = [
        {"$lookup": {"from": "esportes", "localField": "esporte_id", "foreignField": "_id", "as": "detalhes_esporte"}},
        {"$lookup": {"from": "usuarios", "localField": "organizador_id", "foreignField": "_id", "as": "detalhes_organizador"}},
        {"$unwind": "$detalhes_esporte"},
        {"$unwind": "$detalhes_organizador"},
        {"$project": {
            "_id": 0, "id_partida": "$_id", "descricao_partida": "$descricao", "local": "$local", "data_hora": "$data_hora",
            "esporte": "$detalhes_esporte.nome", "organizador": "$detalhes_organizador.nome",
        }}
    ]

    resultados = list(db.partidas.aggregate(pipeline))
    for r in resultados:
        r['id_partida'] = str(r['id_partida'])

    return resultados

# --- OPERAÇÃO 2: Contar quantas partidas existem por esporte ---
@app.get("/estatisticas/partidas-por-esporte")
def obter_estatisticas_por_esporte():
    """
    Calcula o número de partidas por esporte, usando um Aggregation
    Pipeline com $group para agrupar e contar.
    """
    pipeline = [
        {"$lookup": {"from": "esportes", "localField": "esporte_id", "foreignField": "_id", "as": "detalhes_esporte"}},
        {"$unwind": "$detalhes_esporte"},
        {"$group": {"_id": "$detalhes_esporte.nome", "total_partidas": {"$sum": 1}}},
        {"$project": {"_id": 0, "esporte": "$_id", "quantidade_de_partidas": "$total_partidas"}}
    ]

    return list(db.partidas.aggregate(pipeline))