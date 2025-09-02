# Importa as ferramentas necessárias
from pymongo import MongoClient, TEXT # LINHA DE IMPORTAÇÃO ATUALIZADA
from datetime import datetime, timedelta

# --- CONEXÃO COM O BANCO ---
# Cole aqui a sua Connection String do Atlas.
# Lembre-se de substituir '<password>' pela senha que você criou!
MONGO_URI = "mongodb+srv://usuario_projeto:32224447@cluster0.m6raoxu.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Conecta ao banco de dados
client = MongoClient(MONGO_URI)
db = client['marca_jogo_db']

print("Conexão estabelecida com sucesso!")

# --- Limpando coleções para não duplicar dados ---
db.esportes.drop()
db.usuarios.drop()
db.partidas.drop()
print("Coleções antigas limpas.")

# Cria o índice de texto para os campos 'descricao' e 'local' da coleção partidas.
# Isso é necessário para que a busca textual ($text: {$search: ...}) funcione.
db.partidas.create_index([
    ('descricao', TEXT),
    ('local', TEXT)
], name='busca_texto_partidas')
print("Índice de texto criado com sucesso na coleção 'partidas'.")
# --- FIM DO TRECHO ADICIONADO ---

# --- Criando Dados de Exemplo ---

# 1. Esportes
esportes_result = db.esportes.insert_many([
    {"nome": "Futebol", "descricao": "Jogo com bola nos pés."},
    {"nome": "Vôlei", "descricao": "Jogo com rede e bola nas mãos."},
    {"nome": "Basquete", "descricao": "Jogo de arremessar a bola na cesta."}
])
print(f"{len(esportes_result.inserted_ids)} esportes inseridos.")

# 2. Usuários
usuarios_result = db.usuarios.insert_many([
    {"nome": "Ana Silva", "email": "ana.silva@example.com", "cidade": "Uberlândia"},
    {"nome": "Bruno Costa", "email": "bruno.costa@example.com", "cidade": "Araguari"}
])
print(f"{len(usuarios_result.inserted_ids)} usuários inseridos.")

# 3. Partidas (usando os dados criados acima)
id_futebol = db.esportes.find_one({"nome": "Futebol"})['_id']
id_ana = db.usuarios.find_one({"nome": "Ana Silva"})['_id']
id_bruno = db.usuarios.find_one({"nome": "Bruno Costa"})['_id']

partidas_result = db.partidas.insert_many([
    {
        "descricao": "Futebol de fim de semana no Parque do Sabiá",
        "esporte_id": id_futebol,
        "organizador_id": id_ana,
        "data_hora": datetime.now() + timedelta(days=5),
        "local": "Parque do Sabiá, Uberlândia",
        "participantes_ids": [id_ana, id_bruno],
    }
])
print(f"{len(partidas_result.inserted_ids)} partidas inseridas.")

print("\nScript finalizado. Dados inseridos no MongoDB Atlas!")
client.close()
