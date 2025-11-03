# service_s1_simples_correto.py
import requests
import time

print("=" * 50)
print("🎯 S1 - TESTANDO SEUS DADOS REAIS")
print("=" * 50)

S2_URL = "http://localhost:5000"

def testar_dados_reais():
    print("🔍 Conectando aos SEUS bancos via S2...")
    
    try:
        # Teste 1 - Clientes do SEU Supabase
        print("\n1. 👥 Seus clientes (Supabase):")
        resposta = requests.get(f"{S2_URL}/clientes")
        dados = resposta.json()
        print(f"   Total: {dados['total']} clientes")
        for cliente in dados['clientes'][:3]:  # Mostra só 3
            print(f"   - {cliente['nome']} (ID: {cliente['id']})")
        
        # Teste 2 - Produtos do SEU MongoDB
        print("\n2. 🛍️ Seus produtos (MongoDB):")
        resposta = requests.get(f"{S2_URL}/produtos")
        dados = resposta.json()
        print(f"   Total: {dados['total']} produtos")
        for produto in dados['produtos'][:3]:  # Mostra só 3
            print(f"   - {produto['descricao']} (Estoque: {produto['quantidade_estoque']})")
        
        # Teste 3 - Saúde
        print("\n3. 🩺 Saúde do sistema:")
        resposta = requests.get(f"{S2_URL}/saude")
        dados = resposta.json()
        print(f"   {dados['status']}")
        
        print("\n" + "=" * 50)
        print("✅ PRONTO! S1 acessando SEUS dados reais!")
        print(f"📊 Você tem {dados['total']} clientes e produtos!")
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        print("💡 Execute primeiro: python service_s2_simples_correto.py")

if __name__ == "__main__":
    testar_dados_reais()