from faker import Faker
import random
from supabase import create_client, Client

# ============================================================================================================
# =========================== SUPABASE - PREENCHIMENTO DO RDB ================================================
# ============================================================================================================

supabase_url = 'https://vpjjcuhwcxgzcdthwguw.supabase.co'
supabase_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwampjdWh3Y3hnemNkdGh3Z3V3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg5MzE3MTgsImV4cCI6MjA3NDUwNzcxOH0.MUxQ4mwD07P_wEoxxdy55zO695p9zygIHPR2ECMB2y8'
supabase: Client = create_client(supabase_url, supabase_key)

fake = Faker('pt_BR')

cores = ["Preto", "Branco", "Azul", "Vermelho", "Verde", "Amarelo", "Cinza", "Rosa", "Bege"]

produtos_catalogo = {
    "Camisetas": {
        "produtos": ["Blusa", "Camisa", "Regata", "Camiseta", "Moletom", "Camiseta Dry-fit", "Top esportivo"],
        "tamanhos": ["PP", "P", "M", "G", "GG"]
    },
    "Calças e Saias": {
        "produtos": ["Saia", "Calça jeans", "Calça social", "Legging"],
        "tamanhos": ["34", "36", "38", "40", "42", "44"]
    },
    "Calçados": {
        "produtos": ["Tênis", "Sandália", "Sapato social", "Bota"],
        "tamanhos": ["36", "37", "38", "39", "40", "41", "42", "43"]
    },
    "Acessórios": {
        "produtos": ["Boné", "Cinto", "Bolsa", "Cachecol", "Óculos de sol"],
        "tamanhos": ["Único"]
    }
}

# endereços
res_end = supabase.table("endereco").select("id_endereco").execute()
if len(res_end.data) == 0:
    enderecos = []
    for _ in range(40):
        enderecos.append({
            "numero": random.randint(1, 9999),
            "bairro": fake.bairro(),
            "complemento": random.choice(["Casa", "Apto 101", "Fundos", "Bloco B", None]),
            "cidade": fake.city(),
            "rua": fake.street_name()
        })
    supabase.table("endereco").insert(enderecos).execute()
    print("endereços inseridos com sucesso!")

# clientes
res_cliente = supabase.table("cliente").select("id").execute()
if len(res_cliente.data) == 0:
    end_ids = [e["id_endereco"] for e in supabase.table("endereco").select("id_endereco").execute().data]
    clientes = []
    for _ in range(40):
        clientes.append({
            "nome": fake.name(),
            "documento": str(random.randint(10000000000, 99999999999)),
            "id_endereco": random.choice(end_ids)
        })
    supabase.table("cliente").insert(clientes).execute()
    print("clientes inseridos com sucesso!")

# produtos
res_produto = supabase.table("produto").select("id").execute()
if len(res_produto.data) == 0:
    dados_produto = []
    for categoria, dados in produtos_catalogo.items():
        for p in dados["produtos"]:
            dados_produto.append({
                "descricao": p,
                "tamanho": random.choice(dados["tamanhos"]),
                "cor": random.choice(cores),
                "preco": round(random.uniform(49.9, 299.9), 2)
            })
    supabase.table("produto").insert(dados_produto).execute()
    print("produtos inseridos com sucesso!")

# pedidos
res_pedido = supabase.table("pedido").select("id").execute()
if len(res_pedido.data) == 0:
    cliente_ids = [c["id"] for c in supabase.table("cliente").select("id").execute().data]
    pedidos = []
    for _ in range(80):
        pedidos.append({
            "id_cliente": random.choice(cliente_ids)
        })
    supabase.table("pedido").insert(pedidos).execute()
    print("pedidos inseridos com sucesso!")

# item
res_item = supabase.table("item_pedido").select("id_item").execute()
if len(res_item.data) == 0:
    pedidos = supabase.table("pedido").select("id").execute().data
    produtos = supabase.table("produto").select("id").execute().data

    pedido_ids = [p["id"] for p in pedidos]
    produto_ids = [p["id"] for p in produtos]

    itens = []
    for pedido_id in pedido_ids:
        for _ in range(random.randint(1, 5)): 
            itens.append({
                "id_pedido": pedido_id,
                "id_produto": random.choice(produto_ids),
                "quantidade": random.randint(1, 3)
            })

    supabase.table("item_pedido").insert(itens).execute()
    print("itens de pedido inseridos com sucesso!")

print("Banco preenchido!")


# ============================================================================================================
# =========================== MongoDB - PREENCHIMENTO DB1 ====================================================
# ============================================================================================================


from pymongo import MongoClient
import random
from pymongo.server_api import ServerApi
from datetime import datetime

connection_string = "mongodb+srv://wecon:1@cluster0.ei2fxgk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

print("Conectando ao MongoDB")

try:
    mongo_client = MongoClient(
        connection_string,
        server_api=ServerApi('1'),
        maxPoolSize=50,
        connectTimeoutMS=30000,
        socketTimeoutMS=30000
    )
    
    mongo_client.admin.command('ping')
    print("Conectado ao MongoDB com sucesso!")
    
    mongo_db = mongo_client['wecon']
    estoque_collection = mongo_db['estoque']
    
except Exception as e:
    print(f"Erro ao conectar com Mongo: {e}")
    exit(1)

def popular_mongodb():
    try:
        if estoque_collection.count_documents({}) == 0:
            print("Buscando produtos do Supabase")
            
            produtos_supabase = supabase.table("produto").select("*").execute().data
            
            if not produtos_supabase:
                print("Nenhum produto encontrado no Supabase")
                return
            
            documentos_estoque = []
            
            for produto in produtos_supabase:
                historico_movimentacao = []
                for _ in range(random.randint(1, 3)):
                    historico_movimentacao.append({
                        "data": fake.date_this_year().isoformat(),  
                        "tipo": "entrada",
                        "quantidade": random.randint(10, 50),
                        "motivo": "compra_fornecedor"
                    })
                
                documento_estoque = {
                    "produto_id": produto["id"],
                    "descricao": produto["descricao"],
                    "tamanho": produto["tamanho"],
                    "cor": produto["cor"],
                    "quantidade_estoque": random.randint(0, 100),
                    "localizacao": random.choice(["Prateleira A", "Prateleira B", "Armazém 1", "Armazém 2"]),
                    "fornecedor": {
                        "nome": fake.company(),
                        "contato": fake.phone_number(),
                        "tempo_entrega_dias": random.randint(1, 15)
                    },
                    "historico_movimentacao": historico_movimentacao,
                    "ultima_atualizacao": datetime.now().isoformat(),
                    "criado_em": datetime.now().isoformat()
                }
                documentos_estoque.append(documento_estoque)
            
            result = estoque_collection.insert_many(documentos_estoque)
            print(f"Estoque populado no MongoDB com sucesso! {len(result.inserted_ids)} documentos inseridos.")
            
        else:
            count = estoque_collection.count_documents({})
            print(f"MongoDB já possui {count} documentos de estoque")
            
    except Exception as e:
        print(f"Erro ao popular MongoDB: {e}")
        import traceback
        traceback.print_exc()

popular_mongodb()

total = estoque_collection.count_documents({})
print(f"Total de documentos na collection 'estoque': {total}")
    
# ============================================================================================================
# ======================================= Neo4j - PREENCHIMENTO DB2 ==========================================
# ============================================================================================================

from neo4j import GraphDatabase
import random
from datetime import datetime

NEO4J_URI = "neo4j+s://4efaccc5.databases.neo4j.io"  
NEO4J_USERNAME = "neo4j"  
NEO4J_PASSWORD = "umFciuf3FKNJQscatpJ5fvHvxIYNkgzfuWDtfXOsPFc"  

try:
    print("Conectando ao Neo4j")
    neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    with neo4j_driver.session() as session:
        result = session.run("RETURN 'Conectado ao Neo4j!' as message")
        print(f"{result.single()['message']}")
    
except Exception as e:
    print(f"Erro ao conectar com Neo4j: {e}")
    exit(1)

def criar_historico_neo4j():
    try:
        with neo4j_driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            
            print("Buscando clientes e pedidos do Supabase")
            
            clientes_supabase = supabase.table("cliente").select("*").execute().data
            print(f"{len(clientes_supabase)} clientes encontrados")
            
            pedidos_supabase = supabase.table("pedido").select("*").execute().data
            print(f"{len(pedidos_supabase)} pedidos encontrados")
            
            itens_pedido_supabase = supabase.table("item_pedido").select("*").execute().data
            print(f"{len(itens_pedido_supabase)} itens de pedido encontrados")
            
            print("Buscando produtos do MongoDB...")
            produtos_mongo = list(estoque_collection.find({}))
            print(f"{len(produtos_mongo)} produtos no estoque")
            
            print("Criando nós de clientes no Neo4j")
            for cliente in clientes_supabase:
                session.run("""
                    CREATE (c:Cliente {
                        id: $id, 
                        nome: $nome, 
                        documento: $documento
                    })
                """, id=cliente["id"], nome=cliente["nome"], documento=cliente["documento"])
            
            print("Criando nós de produtos no Neo4j")
            for produto in produtos_mongo:
                session.run("""
                    CREATE (p:Produto {
                        produto_id: $produto_id, 
                        descricao: $descricao, 
                        tamanho: $tamanho,
                        cor: $cor,
                        categoria: $categoria
                    })
                """, 
                produto_id=produto["produto_id"],
                descricao=produto["descricao"],
                tamanho=produto["tamanho"],
                cor=produto["cor"],
                categoria=produto.get("categoria", "Geral")
                )

            print("Criando histórico de compras")
            compras_criadas = 0
            
            for pedido in pedidos_supabase:
                cliente_id = pedido["id_cliente"]
                itens_do_pedido = [item for item in itens_pedido_supabase if item["id_pedido"] == pedido["id"]]
                
                for item in itens_do_pedido:
                    produto_id = item["id_produto"]
                    quantidade = item["quantidade"]
                    
                    produto_info = next((p for p in produtos_mongo if p["produto_id"] == produto_id), None)
                    
                    if produto_info:
                        session.run("""
                            MATCH (c:Cliente {id: $cliente_id}), (p:Produto {produto_id: $produto_id})
                            CREATE (c)-[r:COMPROU {
                                pedido_id: $pedido_id,
                                quantidade: $quantidade,
                                data: datetime(),
                                valor_total: $quantidade * 50  // Valor aproximado
                            }]->(p)
                        """, 
                        cliente_id=cliente_id,
                        produto_id=produto_id,
                        pedido_id=pedido["id"],
                        quantidade=quantidade
                        )
                        
                        compras_criadas += 1
            
            print(f"Histórico criado com sucesso! {compras_criadas} relações de compra")
            
            print("Criando relações de recomendação...")
            
            session.run("""
                MATCH (p1:Produto)
                MATCH (p2:Produto)
                WHERE p1.produto_id <> p2.produto_id AND p1.categoria = p2.categoria
                MERGE (p1)-[:RECOMENDADO_PARA {tipo: "mesma_categoria"}]->(p2)
            """)
            session.run("""
                MATCH (p1:Produto)
                MATCH (p2:Produto {cor: p1.cor})
                WHERE p1.produto_id <> p2.produto_id
                MERGE (p1)-[:RECOMENDADO_PARA {tipo: "mesma_cor"}]->(p2)
            """)
            
            print("Relações de recomendação criadas!")
            
    except Exception as e:
        print(f"Erro ao criar histórico: {e}")
        import traceback
        traceback.print_exc()


def consultar_historico_cliente(cliente_id):
    try:
        with neo4j_driver.session() as session:
            result = session.run("""
                MATCH (c:Cliente {id: $cliente_id})-[r:COMPROU]->(p:Produto)
                RETURN c.nome as cliente, p.descricao as produto, 
                       r.quantidade as quantidade, r.data as data_compra
                ORDER BY r.data DESC
            """, cliente_id=cliente_id)
            
            historico = [dict(record) for record in result]
            return historico
    except Exception as e:
        print(f"Erro ao consultar histórico: {e}")
        return []

def consultar_recomendacoes(cliente_id):
    try:
        with neo4j_driver.session() as session:
            result = session.run("""
                MATCH (c:Cliente {id: $cliente_id})-[:COMPROU]->(p1:Produto)
                MATCH (p1)-[:RECOMENDADO_PARA]->(p2:Produto)
                WHERE NOT (c)-[:COMPROU]->(p2)
                RETURN p2.descricao as produto, p2.categoria as categoria,
                       p2.cor as cor, count(*) as score
                ORDER BY score DESC
                LIMIT 5
            """, cliente_id=cliente_id)
            
            recomendacoes = [dict(record) for record in result]
            return recomendacoes
    except Exception as e:
        print(f"Erro ao consultar recomendações: {e}")
        return []

def consultar_estatisticas():
    try:
        with neo4j_driver.session() as session:
            result = session.run("""
                MATCH (c:Cliente)
                WITH count(c) as total_clientes
                MATCH (p:Produto)
                WITH total_clientes, count(p) as total_produtos
                MATCH ()-[r:COMPROU]->()
                RETURN total_clientes, total_produtos, count(r) as total_compras
            """)
            
            stats = dict(result.single())
            return stats
    except Exception as e:
        print(f"Erro ao consultar estatísticas: {e}")
        return {}

if __name__ == "__main__":
    print("Iniciando criação de histórico no Neo4j...")
    
    criar_historico_neo4j()
    stats = consultar_estatisticas()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\nHistórico do cliente 1:")
    historico = consultar_historico_cliente(1)
    for compra in historico:
        print(f"   {compra['produto']} - {compra['quantidade']} unidades")
    
    print("\nRecomendações para cliente 1:")
    recomendacoes = consultar_recomendacoes(1)
    for rec in recomendacoes:
        print(f"   {rec['produto']} ({rec['categoria']}) - score: {rec['score']}")
    
    neo4j_driver.close()
    print("\nProcesso concluído!")