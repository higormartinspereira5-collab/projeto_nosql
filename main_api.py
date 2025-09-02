from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from bson.objectid import ObjectId
from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from bson.objectid import ObjectId
import redis
import json # <-- ADICIONE ESTA LINHA

app = FastAPI(
    title="Marca Jogo API",
    description="API para organizar e consultar partidas de esportes.",
    version="1.0.0"
)


MONGO_URI = "mongodb+srv://usuario_projeto:32224447@cluster0.m6raoxu.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client['marca_jogo_db']

# --- CONEXÃO COM O CACHE REDIS ---
import redis


redis_client = redis.Redis(
    host='redis-16380.c273.us-east-1-2.ec2.cloud.redislabs.com', 
    port=16380, 
    password= 'BFAlMMJS8M6EEN29Ut5rU9lSNyIswyrP',
    db=0,
    decode_responses=True 
)

# Bloco para testar a conexão e garantir que tudo está funcionando
try:
    status = redis_client.ping()
    print(f"Conexão com o servidor Redis estabelecida com sucesso!")
except redis.exceptions.ConnectionError as e:
    print(f"Não foi possível conectar ao servidor Redis: {e}")

# --- ENDPOINTS DA API ---
# ... (resto do seu código)


@app.get("/")
def read_root():
    return {"Status": "API do Marca Jogo está online!"}



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


# --- OPERAÇÃO 1: Listar partidas com detalhes do esporte e organizador ---
@app.get("/partidas/detalhadas")
def obter_partidas_com_detalhhes():
    """
    Lista todas as partidas com informações detalhadas do esporte e do organizador.
    Esta função usa cache com expiração de 5 minutos no Redis.
    """
    # Define uma chave única para este resultado no cache do Redis
    cache_key = "partidas_detalhadas_cache"

    # 1. Tenta buscar o resultado no Redis primeiro
    dados_em_cache = redis_client.get(cache_key)

    if dados_em_cache:
        print("Dados encontrados no cache! (Cache Hit)")
        # Se encontrou, converte a string JSON de volta para uma lista Python e a retorna
        return json.loads(dados_em_cache)
    
    else:
        print("Dados não encontrados no cache. Buscando no MongoDB... (Cache Miss)")
        # 2. Se não encontrou no cache, executa a consulta pesada no MongoDB
        pipeline = [
            {"$lookup": {"from": "esportes", "localField": "esporte_id", "foreignField": "_id", "as": "detalhes_esporte"}},
            {"$lookup": {"from": "usuarios", "localField": "organizador_id", "foreignField": "_id", "as": "detalhes_organizador"}},
            {"$unwind": "$detalhes_esporte"},
            {"$unwind": "$detalhes_organizador"},
            {"$project": {
                "_id": 0, "id_partida": {"$toString": "$_id"}, "descricao_partida": "$descricao", "local": "$local", "data_hora": "$data_hora",
                "esporte": "$detalhes_esporte.nome", "organizador": "$detalhes_organizador.nome",
            }}
        ]
        resultados = list(db.partidas.aggregate(pipeline))
        
        # 3. Salva o resultado no Redis COM EXPIRAÇÃO de 300 segundos (5 minutos)
        # Usamos json.dumps para converter a lista Python em uma string JSON
        redis_client.setex(cache_key, 300, json.dumps(resultados))

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
