from faker import Faker
import random
from supabase import create_client, Client

supabase_url = 'https://vpjjcuhwcxgzcdthwguw.supabase.co'
supabase_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwampjdWh3Y3hnemNkdGh3Z3V3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg5MzE3MTgsImV4cCI6MjA3NDUwNzcxOH0.MUxQ4mwD07P_wEoxxdy55zO695p9zygIHPR2ECMB2y8'
supabase: Client = create_client(supabase_url, supabase_key)

fake = Faker('pt_BR')

nome_clientes = []
produtos = {
    "Camisetas": {
        "produtos": ["Blusa", "Camisa", "Regata", "Camiseta", "Moletom", "Camiseta dry-fit", "Top esportivo"],
        "tamanhos": ["PP", "P", "M", "G", "GG"]
    },
    "Calças e Saias": {
        "produtos": ["Saia", "Calça jeans", "Calça social", "Legging"],
        "tamanhos": ["34", "36", "38", "40", "42", "44"]
    },
    "Roupas Gerais": {
        "produtos": ["Vestido", "Short", "Jaqueta", "Conjunto infantil", "Macacão", "Pijama", "Cueca", "Meia"],
        "tamanhos": ["PP", "P", "M", "G", "GG"]
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
cores = ["Preto", "Branco", "Azul", "Vermelho", "Verde", "Amarelo", "Cinza", "Rosa", "Bege"]


import random

resposta_cliente = supabase.table("cliente").select("nome", "documento").execute()

if len(resposta_cliente.data) == 0:  
    dados_nome = []

    for i in range(40):
        nome = fake.name()
        documento = random.randint(1000000, 9999999)  
        dados_nome.append({
            "nome": nome,
            "documento": documento
        })

    # insere todos de uma vez
    supabase.table("cliente").insert(dados_nome).execute()

    resposta_cliente = supabase.table("cliente").select("nome", "documento").execute()
    print("Clientes inseridos")



resposta_produto = supabase.table("produto").select("descricao", "tamanho", "cor", "preco").execute()
if len(resposta_produto.data) == 0:
    dados_produto = []

    for categoria, dados in produtos.items():
        for p in dados["produtos"]:
            produto = {
                "descricao": p,
                "tamanho": random.choice(dados["tamanhos"]),
                "cor": random.choice(cores),
                "preco": round(random.uniform(49.9, 299.9), 2)
            }
            dados_produto.append(produto)

    supabase.table("produto").insert(dados_produto).execute()
    resposta_produto = supabase.table("produto").select("descricao", "tamanho", "cor", "preco").execute()
    print("Produtos inseridos")


resposta_endereco = supabase.table("endereco").select("id_endereco").execute()

if len(resposta_endereco.data) == 0:
    enderecos = []
    possiveis_complementos = ["Casa", "Apto 101", "Fundos", "Bloco B", None]

    for _ in range(40):
        try:
            bairro = fake.bairro()
        except Exception:
            bairro = random.choice(["Centro", "Jardim América", "Vila Nova", "Santa Cruz", "Boa Vista"])

        enderecos.append({
            "numero": random.randint(1, 9999),
            "bairro": bairro,
            "complemento": random.choice(possiveis_complementos),
            "cidade": fake.city(),
            "rua": fake.street_name()
        })

    supabase.table("endereco").insert(enderecos).execute()
    print("Endereços inseridos com sucesso!")

clientes = supabase.table("Cliente").select("id").execute()
produtos = supabase.table("Produto").select("id").execute()

cliente_ids = [c["id"] for c in clientes.data]
produto_ids = [p["id"] for p in produtos.data]

qtd_pedidos = 80  
pedidos = [
    {
        "id_cliente": random.choice(cliente_ids),
        "id_produto": random.choice(produto_ids)
    }
    for _ in range(qtd_pedidos)
]

# Inserir em lote
supabase.table("Pedido").insert(pedidos).execute()
print(f"{qtd_pedidos} pedidos inseridos com sucesso!")



#fazer a tabela itens pedido para abranger pedidos com mais de um produto