from flask import Flask, jsonify, request
from flask_cors import CORS
import os, requests
from pymongo import MongoClient
from neo4j import GraphDatabase
from datetime import datetime

app = Flask(__name__)
CORS(app)
#creds dos bancos
SUPABASE_URL= os.getenv("SUPABASE_URL", "https://vpjjcuhwcxgzcdthwguw.supabase.co")
SUPABASE_KEY= os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwampjdWh3Y3hnemNkdGh3Z3V3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg5MzE3MTgsImV4cCI6MjA3NDUwNzcxOH0.MUxQ4mwD07P_wEoxxdy55zO695p9zygIHPR2ECMB2y8")
MONGO_URI= os.getenv("MONGO_URI", "mongodb+srv://wecon:1@cluster0.ei2fxgk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
NEO4J_URI= os.getenv("NEO4J_URI", "neo4j+s://4efaccc5.databases.neo4j.io")
NEO4J_USER= os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASS= os.getenv("NEO4J_PASS", "umFciuf3FKNJQscatpJ5fvHvxIYNkgzfuWDtfXOsPFc")
TIMEOUT= 25

SB_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Prefer": "return=representation"
}

mongo = MongoClient(MONGO_URI)
mdb = mongo["wecon"]
neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

def _sb_error(r):
    try: return r.json()
    except: return {"status": r.status_code, "text": r.text}

#clientes metodo get
@app.route('/clientes', methods=['GET'])
def clientes_list():
    try:
        url = f"{SUPABASE_URL}/rest/v1/cliente?select=id,nome,documento,id_endereco"
        r = requests.get(url, headers=SB_HEADERS, timeout=TIMEOUT)
        if not r.ok: return jsonify({"success":False,"error":_sb_error(r)}), r.status_code
        return jsonify({"success":True,"clientes":r.json()})
    except Exception as e:
        return jsonify({"success":False,"error":str(e)}), 500

#clientes metodo post
@app.route('/clientes', methods=['POST'])
def clientes_create():
    try:
        dados = request.json or {}
        r = requests.post(f"{SUPABASE_URL}/rest/v1/cliente", headers=SB_HEADERS, json=dados, timeout=TIMEOUT)
        if not r.ok: return jsonify({"success":False,"error":_sb_error(r)}), r.status_code
        try:
            body = r.json()
            if isinstance(body, list) and body: return jsonify({"success":True,"cliente":body[0]}),201
            if isinstance(body, dict) and body: return jsonify({"success":True,"cliente":body}),201
        except: pass
        loc = r.headers.get("Location")
        if loc:
            sep = "&" if "?" in loc else "?"
            g = requests.get(f"{SUPABASE_URL}{loc}{sep}select=id,nome,documento,id_endereco", headers=SB_HEADERS, timeout=TIMEOUT)
            if g.ok:
                arr = g.json()
                if isinstance(arr, list) and arr: return jsonify({"success":True,"cliente":arr[0]}),201
        g2 = requests.get(f"{SUPABASE_URL}/rest/v1/cliente?select=id,nome,documento,id_endereco&order=id.desc&limit=1", headers=SB_HEADERS, timeout=TIMEOUT)
        if g2.ok:
            arr = g2.json()
            if isinstance(arr,list) and arr: return jsonify({"success":True,"cliente":arr[0]}),201
        return jsonify({"success":True,"cliente":dados}),201
    except Exception as e:
        return jsonify({"success":False,"error":str(e)}), 500

#produtos metodo get
@app.route('/produtos_rdb', methods=['GET'])
def produtos_rdb():
    try:
        url = f"{SUPABASE_URL}/rest/v1/produto?select=id,descricao,tamanho,cor,preco"
        r = requests.get(url, headers=SB_HEADERS, timeout=TIMEOUT)
        if not r.ok: return jsonify({"success":False,"error":_sb_error(r)}), r.status_code
        return jsonify({"success":True,"produtos":r.json()})
    except Exception as e:
        return jsonify({"success":False,"error":str(e)}),500
    
@app.route('/produtos_full', methods=['POST'])
def produtos_full_create():
    try:
        d = request.json or {}
        body_rdb = {
            "descricao": d.get("descricao", "").strip(),
            "tamanho":  d.get("tamanho", "").strip(),
            "cor":      d.get("cor", "").strip(),
            "preco":    float(d.get("preco", 0.0)),
        }
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/produto",
            headers=SB_HEADERS,
            json=body_rdb,
            timeout=TIMEOUT
        )
        if not r.ok:
            return jsonify({"success": False, "stage": "supabase", "error": _sb_error(r)}), r.status_code
        try:
            created = r.json()
            if isinstance(created, list) and created:
                prod = created[0]
            elif isinstance(created, dict) and created:
                prod = created
            else:
                g = requests.get(
                    f"{SUPABASE_URL}/rest/v1/produto?select=id,descricao,tamanho,cor,preco&order=id.desc&limit=1",
                    headers=SB_HEADERS, timeout=TIMEOUT
                )
                g.raise_for_status()
                prod = g.json()[0]
        except Exception as e:
            return jsonify({"success": False, "stage": "parse_supabase", "error": str(e)}), 500

        pid = int(prod["id"])
        
        estoque_doc = {
            "produto_id": pid,
            "descricao":  prod.get("descricao"),
            "tamanho":    prod.get("tamanho"),
            "cor":        prod.get("cor"),
            "categoria":  "Geral",
            "quantidade_estoque": int(d.get("quantidade_estoque", 0)),
            "localizacao": d.get("localizacao", "Prateleira A"),
            "fornecedor": {
                "nome":  (d.get("fornecedor", {}) or {}).get("nome"),
                "contato": (d.get("fornecedor", {}) or {}).get("contato"),
                "tempo_entrega_dias": int((d.get("fornecedor", {}) or {}).get("tempo_entrega_dias", 0)),
            },
            "ultima_atualizacao": datetime.now().isoformat()
        }
        mdb.estoque.update_one({"produto_id": pid}, {"$set": estoque_doc}, upsert=True)

        estoque_doc.pop("_id", None)
        return jsonify({
            "success": True,
            "produto": prod,
            "estoque": estoque_doc
        }), 201

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

#estoque
@app.route('/estoque', methods=['GET'])
def estoque_list():
    try:
        docs = list(mdb.estoque.find({}, {"_id":0}))
        return jsonify({"success":True,"estoque":docs})
    except Exception as e:
        return jsonify({"success":False,"error":str(e)}),500

@app.route('/estoque', methods=['POST'])
def estoque_upsert():
    try:
        d = request.json or {}
        pid = int(d["produto_id"])
        q   = int(d.get("quantidade_estoque",0))
        doc = {
            "produto_id": pid,
            "descricao": d.get("descricao",""),
            "tamanho": d.get("tamanho",""),
            "cor": d.get("cor",""),
            "categoria": d.get("categoria","Geral"),
            "quantidade_estoque": q,
            "localizacao": d.get("localizacao","Prateleira A"),
            "ultima_atualizacao": datetime.now().isoformat()
        }
        mdb.estoque.update_one({"produto_id":pid},{"$set":doc},upsert=True)
        doc.pop("_id", None)
        return jsonify({"success":True,"estoque":doc}),201
    except KeyError as ke:
        return jsonify({"success":False,"error":f"campo faltando: {ke}"}),400
    except Exception as e:
        return jsonify({"success":False,"error":str(e)}),500

@app.route('/estoque/<int:produto_id>', methods=['PUT'])
def estoque_update_qtd(produto_id):
    try:
        q = int((request.json or {}).get("quantidade_estoque"))
        res = mdb.estoque.update_one({"produto_id":produto_id},{"$set":{"quantidade_estoque":q,"ultima_atualizacao":datetime.now().isoformat()}})
        if res.matched_count==0:
            return jsonify({"success":False,"error":"produto não encontrado"}),404
        return jsonify({"success":True,"message":"Estoque atualizado"})
    except Exception as e:
        return jsonify({"success":False,"error":str(e)}),500

@app.route('/estoque/sync_from_rdb', methods=['POST'])
def estoque_sync_from_rdb():
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/produto?select=id,descricao,tamanho,cor,preco", headers=SB_HEADERS, timeout=TIMEOUT)
        if not r.ok: return jsonify({"success":False,"error":_sb_error(r)}), r.status_code
        produtos = r.json()
        created, updated = 0, 0
        for p in produtos:
            pid = int(p["id"])
            cur = mdb.estoque.find_one({"produto_id":pid})
            base = {
                "produto_id": pid,
                "descricao": p.get("descricao",""),
                "tamanho": p.get("tamanho",""),
                "cor": p.get("cor",""),
                "categoria": "Geral",
            }
            if cur is None:
                base.update({
                    "quantidade_estoque": 0,
                    "localizacao":"Prateleira A",
                    "ultima_atualizacao": datetime.now().isoformat()
                })
                mdb.estoque.insert_one(base)
                created += 1
            else:
                upd = {}
                for k in ("descricao","tamanho","cor"):
                    if not cur.get(k) and p.get(k): upd[k]=p[k]
                if upd:
                    upd["ultima_atualizacao"]=datetime.now().isoformat()
                    mdb.estoque.update_one({"produto_id":pid},{"$set":upd})
                    updated += 1
        return jsonify({"success":True,"created":created,"updated":updated,"total":len(produtos)})
    except Exception as e:
        return jsonify({"success":False,"error":str(e)}),500



def _ensure_prod_node(session, pid:int):
    doc = mdb.estoque.find_one({"produto_id":pid}, {"_id":0})
    props = doc or {"produto_id":pid}
    session.run("""
        MERGE (p:Produto {produto_id: $pid})
        SET p.descricao = coalesce($descricao, p.descricao),
            p.tamanho   = coalesce($tamanho,   p.tamanho),
            p.cor       = coalesce($cor,       p.cor),
            p.categoria = coalesce($categoria, p.categoria)
    """, pid=pid,
       descricao=props.get("descricao"),
       tamanho=props.get("tamanho"),
       cor=props.get("cor"),
       categoria=props.get("categoria","Geral")
    )

@app.route('/pedidos', methods=['POST'])
def pedidos_create():
    try:
        d = request.json or {}
        cid = int(d["cliente_id"])
        pid = int(d["produto_id"])
        qtd = max(1, int(d.get("quantidade", 1)))

        r_prod = requests.get(
            f"{SUPABASE_URL}/rest/v1/produto?select=id,descricao,preco&id=eq.{pid}",
            headers=SB_HEADERS, timeout=TIMEOUT
        )
        if not r_prod.ok or not r_prod.json():
            return jsonify({"success": False, "error": "produto não existe no RDB"}), 404
        prod_rdb = r_prod.json()[0]
        preco = float(prod_rdb.get("preco") or 0.0)
        valor_total = float(d.get("valor", preco * qtd))

        doc = mdb.estoque.find_one({"produto_id": pid})
        if not doc:
            return jsonify({"success": False, "error": "produto não existe no estoque (Mongo)"}), 404
        estoque_atual = int(doc.get("quantidade_estoque") or 0)
        if estoque_atual < qtd:
            return jsonify({"success": False, "error": f"estoque insuficiente (atual={estoque_atual}, pedido={qtd})"}), 409

        r_ped = requests.post(
            f"{SUPABASE_URL}/rest/v1/pedido",
            headers=SB_HEADERS,
            json={"id_cliente": cid},
            timeout=TIMEOUT
        )
        if not r_ped.ok:
            return jsonify({"success": False, "stage": "supabase.pedido", "error": _sb_error(r_ped)}), r_ped.status_code

        try:
            created = r_ped.json()
            if isinstance(created, list) and created:
                pedido_row = created[0]
            elif isinstance(created, dict) and created:
                pedido_row = created
            else:
                g = requests.get(
                    f"{SUPABASE_URL}/rest/v1/pedido?select=id,id_cliente&order=id.desc&limit=1",
                    headers=SB_HEADERS, timeout=TIMEOUT
                )
                g.raise_for_status()
                pedido_row = g.json()[0]
        except Exception as e:
            return jsonify({"success": False, "stage": "parse_supabase.pedido", "error": str(e)}), 500

        pedido_id = int(pedido_row["id"])

        r_item = requests.post(
            f"{SUPABASE_URL}/rest/v1/item_pedido",
            headers=SB_HEADERS,
            json={"id_pedido": pedido_id, "id_produto": pid, "quantidade": qtd},
            timeout=TIMEOUT
        )
        if not r_item.ok:
            requests.delete(
                f"{SUPABASE_URL}/rest/v1/pedido?id=eq.{pedido_id}",
                headers=SB_HEADERS, timeout=TIMEOUT
            )
            return jsonify({"success": False, "stage": "supabase.item_pedido", "error": _sb_error(r_item)}), r_item.status_code

        mov = {
            "data": datetime.now().isoformat(),
            "tipo": "saida",
            "quantidade": qtd,
            "motivo": "venda_s1",
            "pedido_id": pedido_id
        }
        upd = mdb.estoque.update_one(
            {"produto_id": pid, "quantidade_estoque": {"$gte": qtd}},
            {"$inc": {"quantidade_estoque": -qtd},
             "$set": {"ultima_atualizacao": datetime.now().isoformat()},
             "$push": {"historico_movimentacao": mov}}
        )
        if upd.matched_count == 0:
            requests.delete(
                f"{SUPABASE_URL}/rest/v1/item_pedido?id_pedido=eq.{pedido_id}&id_produto=eq.{pid}",
                headers=SB_HEADERS, timeout=TIMEOUT
            )
            requests.delete(
                f"{SUPABASE_URL}/rest/v1/pedido?id=eq.{pedido_id}",
                headers=SB_HEADERS, timeout=TIMEOUT
            )
            return jsonify({"success": False, "error": "estoque mudou; não foi possível debitar"}), 409

        with neo4j_driver.session() as s:
            s.run("MERGE (c:Cliente {id:$cid})", cid=cid)
            _ensure_prod_node(s, pid)
            s.run("""
                MATCH (c:Cliente {id:$cid}), (p:Produto {produto_id:$pid})
                CREATE (c)-[:COMPROU {
                    pedido_id:$pedido_id, quantidade:$qtd, valor:$valor, data:datetime()
                }]->(p)
            """, cid=cid, pid=pid, pedido_id=pedido_id, qtd=qtd, valor=valor_total)

        doc2 = mdb.estoque.find_one({"produto_id": pid}, {"_id": 0})

        return jsonify({
            "success": True,
            "pedido_id": pedido_id,
            "item": {"id_produto": pid, "quantidade": qtd, "valor_total": valor_total},
            "estoque_atual": doc2
        }), 201

    except KeyError as ke:
        return jsonify({"success": False, "error": f"campo faltando: {ke}"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    
@app.route('/graph/stats', methods=['GET'])
def graph_stats():
    try:
        with neo4j_driver.session() as s:
            res = s.run("""
                CALL {
                  MATCH (c:Cliente) RETURN count(c) AS clientes
                }
                CALL {
                  MATCH (p:Produto) RETURN count(p) AS produtos
                }
                CALL {
                  MATCH ()-[r:COMPROU]->() RETURN count(r) AS compras
                }
                RETURN clientes, produtos, compras
            """)
            row = res.single()
            return jsonify({"success": True, "stats": dict(row)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/graph/last_edges', methods=['GET'])
def graph_last_edges():
    try:
        limit = int(request.args.get("limit", 10))
        with neo4j_driver.session() as s:
            res = s.run("""
                MATCH (c:Cliente)-[r:COMPROU]->(p:Produto)
                RETURN c.id AS cliente_id, p.produto_id AS produto_id,
                       r.quantidade AS quantidade, r.valor AS valor, r.data AS data,
                       p.descricao AS descricao
                ORDER BY r.data DESC
                LIMIT $limit
            """, limit=limit)
            return jsonify({"success": True, "edges": [dict(x) for x in res]})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/historico/<int:cliente_id>', methods=['GET'])
def historico(cliente_id):
    try:
        with neo4j_driver.session() as s:
            res = s.run("""
                MATCH (c:Cliente {id:$cid})-[r:COMPROU]->(p:Produto)
                RETURN p.produto_id as produto_id, p.descricao as descricao,
                       r.quantidade as quantidade, r.valor as valor, r.data as data
                ORDER BY r.data DESC
            """, cid=cliente_id)

            historico = []
            for r in res:
                row = dict(r)
                if "data" in row and row["data"] is not None:
                    row["data"] = str(row["data"])
                historico.append(row)

            return jsonify({"success": True, "historico": historico})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/graph/bootstrap', methods=['POST'])
def graph_bootstrap():
    try:
        with neo4j_driver.session() as s:
            produtos = list(mdb.estoque.find({}, {"_id":0}))
            for p in produtos:
                s.run("""
                    MERGE (x:Produto {produto_id:$pid})
                    SET x.descricao=$desc, x.tamanho=$tam, x.cor=$cor, x.categoria=$cat
                """, pid=int(p["produto_id"]), desc=p.get("descricao"), tam=p.get("tamanho"),
                     cor=p.get("cor"), cat=p.get("categoria","Geral"))

            s.run("""
                MATCH (a:Produto), (b:Produto)
                WHERE a.produto_id <> b.produto_id AND a.categoria = b.categoria
                MERGE (a)-[:RECOMENDADO_PARA {tipo:'mesma_categoria'}]->(b)
            """)

            s.run("""
                MATCH (c:Cliente)-[:COMPROU]->(p1:Produto)
                MATCH (c)-[:COMPROU]->(p2:Produto)
                WHERE p1 <> p2
                MERGE (p1)-[:RECOMENDADO_PARA {tipo:'co_compra'}]->(p2)
            """)

        return jsonify({"success":True,"message":"grafo (re)construído"})
    except Exception as e:
        return jsonify({"success":False,"error":str(e)}),500

@app.route('/recomendacoes/<int:cliente_id>', methods=['GET'])
def recomendacoes(cliente_id):
    try:
        with neo4j_driver.session() as s:
            res = s.run("""
                MATCH (c:Cliente {id:$cid})-[:COMPROU]->(p1:Produto)
                MATCH (p1)-[r:RECOMENDADO_PARA]->(p2:Produto)
                WHERE NOT (c)-[:COMPROU]->(p2)
                RETURN p2.produto_id as produto_id, p2.descricao as descricao,
                       p2.categoria as categoria, p2.cor as cor, count(*) as score
                ORDER BY score DESC LIMIT 5
            """, cid=cliente_id)
            return jsonify({"success":True,"recomendacoes":[dict(r) for r in res]})
    except Exception as e:
        return jsonify({"success":False,"error":str(e)}),500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
