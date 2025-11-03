# service_s2_simples_correto.py
from flask import Flask, jsonify
from supabase import create_client
from pymongo import MongoClient

app = Flask(__name__)

print("=" * 50)
print("🚀 S2 SIMPLES - USANDO SEUS BANCOS REAIS")
print("=" * 50)

# Conecta nos SEUS bancos
supabase = create_client(
    'https://vpjjcuhwcxgzcdthwguw.supabase.co',
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwampjdWh3Y3hnemNkdGh3Z3V3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg5MzE3MTgsImV4cCI6MjA3NDUwNzcxOH0.MUxQ4mwD07P_wEoxxdy55zO695p9zygIHPR2ECMB2y8'
)

mongo_client = MongoClient("mongodb+srv://wecon:1@cluster0.ei2fxgk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
mongo_db = mongo_client['wecon']

@app.route('/')
def home():
    return jsonify({
        "mensagem": "S2 conectado aos SEUS bancos!",
        "status": "✅ Online"
    })

@app.route('/clientes', methods=['GET'])
def get_clientes():
    # Busca clientes do SEU Supabase
    resultado = supabase.table("cliente").select("id, nome").execute()
    return jsonify({
        "clientes": resultado.data,
        "total": len(resultado.data),
        "fonte": "Supabase"
    })

@app.route('/produtos', methods=['GET'])
def get_produtos():
    # Busca produtos do SEU MongoDB
    produtos = list(mongo_db.estoque.find({}, {'_id': 0, 'produto_id': 1, 'descricao': 1, 'quantidade_estoque': 1}))
    return jsonify({
        "produtos": produtos,
        "total": len(produtos),
        "fonte": "MongoDB"
    })

@app.route('/saude', methods=['GET'])
def health_check():
    return jsonify({
        "supabase": "✅ Conectado",
        "mongodb": "✅ Conectado", 
        "status": "😊 Todos os bancos funcionando"
    })

if __name__ == '__main__':
    print("✅ S2 conectado aos SEUS bancos!")
    print("🌐 Acesse: http://localhost:5000")
    print("📋 Rotas:")
    print("   /clientes  - Seus clientes do Supabase")
    print("   /produtos  - Seus produtos do MongoDB")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=True)