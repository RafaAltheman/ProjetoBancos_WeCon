import tkinter as tk
from tkinter import ttk, messagebox
import requests, os, json, threading
from datetime import datetime

class SistemaGestao:
    def __init__(self, root):
        self.root = root
        self.root.title("WeCon")
        self.root.geometry("1000x700")
        self.s2_url = os.getenv("S2_URL", "http://localhost:5000")
        self.log_requisicoes = []
        self._build_ui()

    def call_api(self, metodo, endpoint, dados=None, on_done=None):
        def worker():
            try:
                url = f"{self.s2_url}{endpoint}"
                if metodo == "GET":
                    resp = requests.get(url, timeout=30)
                elif metodo == "POST":
                    resp = requests.post(url, json=dados, timeout=30)
                elif metodo == "PUT":
                    resp = requests.put(url, json=dados, timeout=30)
                else:
                    raise ValueError("método inválido")
                try:
                    body = resp.json()
                except Exception:
                    body = {"raw": resp.text}

                log = {
                    "timestamp": datetime.now().isoformat(),
                    "metodo": metodo,
                    "endpoint": endpoint,
                    "dados": dados,
                    "resposta": body,
                    "status": resp.status_code
                }
                self.log_requisicoes.append(log)
                result = body if resp.status_code < 400 else {"success": False, "status": resp.status_code, "error": body}
            except Exception as e:
                result = {"success": False, "error": str(e)}
            if on_done:
                self.root.after(0, lambda: on_done(result))
        threading.Thread(target=worker, daemon=True).start()

    def _build_ui(self):
        top = ttk.Frame(self.root); top.pack(fill='x', padx=10, pady=5)
        ttk.Label(top, text=f"S2 URL: {self.s2_url}", foreground="#555").pack(side='left')

        nb = ttk.Notebook(self.root); nb.pack(fill='both', expand=True, padx=10, pady=10)

        frm_cli    = ttk.Frame(nb); nb.add(frm_cli, text="Clientes")
        frm_prod   = ttk.Frame(nb); nb.add(frm_prod, text="Produtos (RDB)")
        frm_stock  = ttk.Frame(nb); nb.add(frm_stock, text="Estoque (Mongo)")
        frm_ped    = ttk.Frame(nb); nb.add(frm_ped, text="Pedidos/Neo4j")
        frm_hist   = ttk.Frame(nb); nb.add(frm_hist, text="Histórico/Recomendações")
        frm_log    = ttk.Frame(nb); nb.add(frm_log, text="Log")

        self._tab_clientes(frm_cli)
        self._tab_produtos(frm_prod)
        self._tab_estoque(frm_stock)
        self._tab_pedidos(frm_ped)
        self._tab_hist(frm_hist)
        self._tab_log(frm_log)

    def _tab_clientes(self, parent):
        box = ttk.LabelFrame(parent, text="Cadastrar Cliente"); box.pack(fill='x', padx=6, pady=6)
        ttk.Label(box, text="Nome").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        ttk.Label(box, text="Documento").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        ttk.Label(box, text="Endereço ID").grid(row=2, column=0, padx=5, pady=5, sticky='e')

        self.e_cli_nome = ttk.Entry(box, width=40); self.e_cli_nome.grid(row=0, column=1, padx=5, pady=5)
        self.e_cli_doc  = ttk.Entry(box, width=40); self.e_cli_doc.grid(row=1, column=1, padx=5, pady=5)
        self.e_cli_end  = ttk.Entry(box, width=40); self.e_cli_end.grid(row=2, column=1, padx=5, pady=5); self.e_cli_end.insert(0,"1")

        ttk.Button(box, text="Cadastrar", command=self._cadastrar_cliente).grid(row=3, column=0, columnspan=2, pady=6)

        lst = ttk.LabelFrame(parent, text="Clientes"); lst.pack(fill='both', expand=True, padx=6, pady=6)
        self.tree_cli = ttk.Treeview(lst, columns=("id","nome","doc","end"), show='headings', height=12)
        
        for c,t in zip(("id","nome","doc","end"),("ID","Nome","Documento","Endereço ID")):
            self.tree_cli.heading(c,text=t); self.tree_cli.column(c,anchor='center',width=140)
            
        self.tree_cli.pack(fill='both', expand=True, padx=5, pady=5)
        ttk.Button(lst, text="Atualizar", command=self._load_clientes).pack(pady=4)
        self._load_clientes()

    def _cadastrar_cliente(self):
        try:
            data={"nome":self.e_cli_nome.get().strip(),"documento":self.e_cli_doc.get().strip(),"id_endereco":int(self.e_cli_end.get().strip())}
        except:
            messagebox.showerror("Erro","Endereço ID deve ser inteiro"); return
        def ok(res):
            if res.get("success", True):
                messagebox.showinfo("OK","Cliente cadastrado!")
                self._load_clientes()
                self.e_cli_nome.delete(0,tk.END); self.e_cli_doc.delete(0,tk.END)
            else:
                messagebox.showerror("Erro", f"{res.get('error')}")
        self.call_api("POST","/clientes",data,ok)

    def _load_clientes(self):
        def ok(res):
            if res.get("success", True):
                for i in self.tree_cli.get_children(): self.tree_cli.delete(i)
                for c in res.get("clientes",[]):
                    self.tree_cli.insert('', 'end', values=(c.get("id"),c.get("nome"),c.get("documento"),c.get("id_endereco")))
            else:
                messagebox.showerror("Erro", f"{res.get('error')}")
        self.call_api("GET","/clientes",on_done=ok)

    def _tab_produtos(self, parent):
        tips = ttk.Frame(parent); tips.pack(fill='x', padx=6, pady=4)
        ttk.Label(
            tips,
            text="Produtos são criados no supabase. Este formulário também cria o estoque no Mongo.",
            foreground="#555"
        ).pack(side='left')

        form = ttk.LabelFrame(parent, text="Cadastrar Produto + Estoque")
        form.pack(fill='x', padx=6, pady=6)

        # RDB
        ttk.Label(form, text="Descrição").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        ttk.Label(form, text="Tamanho").grid(row=0, column=2, padx=5, pady=5, sticky='e')
        ttk.Label(form, text="Cor").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        ttk.Label(form, text="Preço (R$)").grid(row=1, column=2, padx=5, pady=5, sticky='e')

        self.e_prod_desc = ttk.Entry(form, width=28); self.e_prod_desc.grid(row=0, column=1, padx=5, pady=5)
        self.e_prod_tam  = ttk.Entry(form, width=12); self.e_prod_tam.grid(row=0, column=3, padx=5, pady=5)
        self.e_prod_cor  = ttk.Entry(form, width=12); self.e_prod_cor.grid(row=1, column=1, padx=5, pady=5)
        self.e_prod_pre  = ttk.Entry(form, width=12); self.e_prod_pre.grid(row=1, column=3, padx=5, pady=5)

        # Estoque
        ttk.Label(form, text="Quantidade").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        ttk.Label(form, text="Localização").grid(row=2, column=2, padx=5, pady=5, sticky='e')
        ttk.Label(form, text="Fornecedor - Nome").grid(row=3, column=0, padx=5, pady=5, sticky='e')
        ttk.Label(form, text="Fornecedor - Contato").grid(row=3, column=2, padx=5, pady=5, sticky='e')
        ttk.Label(form, text="Fornecedor - Prazo (dias)").grid(row=4, column=0, padx=5, pady=5, sticky='e')

        self.e_st_qtd_new = ttk.Entry(form, width=12); self.e_st_qtd_new.grid(row=2, column=1, padx=5, pady=5)
        self.e_st_loc_new = ttk.Entry(form, width=12); self.e_st_loc_new.grid(row=2, column=3, padx=5, pady=5)
        self.e_forn_nome  = ttk.Entry(form, width=28); self.e_forn_nome.grid(row=3, column=1, padx=5, pady=5)
        self.e_forn_cont  = ttk.Entry(form, width=18); self.e_forn_cont.grid(row=3, column=3, padx=5, pady=5)
        self.e_forn_prazo = ttk.Entry(form, width=12); self.e_forn_prazo.grid(row=4, column=1, padx=5, pady=5)

        ttk.Button(form, text="Cadastrar (RDB + Estoque)", command=self._criar_produto_full)\
            .grid(row=5, column=0, columnspan=4, pady=8)

        # --- Lista de produtos (RDB) ---
        frame = ttk.LabelFrame(parent, text="Produtos (RDB)")
        frame.pack(fill='both', expand=True, padx=6, pady=6)

        self.tree_prod = ttk.Treeview(frame, columns=("id","descricao","tam","cor","preco"), show="headings")
        for c,t in zip(("id","descricao","tam","cor","preco"),("ID","Descrição","Tamanho","Cor","Preço")):
            self.tree_prod.heading(c,text=t); self.tree_prod.column(c, width=150, anchor='center')
        self.tree_prod.pack(fill='both', expand=True, padx=5, pady=5)

        ttk.Button(frame, text="Atualizar", command=self._load_produtos_rdb).pack(pady=4)
        self._load_produtos_rdb()


    def _load_produtos_rdb(self):
        def ok(res):
            if res.get("success", True):
                for i in self.tree_prod.get_children(): self.tree_prod.delete(i)
                for p in res.get("produtos", []):
                    self.tree_prod.insert('', 'end', values=(p.get("id"),p.get("descricao"),p.get("tamanho"),p.get("cor"),p.get("preco")))
            else:
                messagebox.showerror("Erro", f"{res.get('error')}")
        self.call_api("GET","/produtos_rdb",on_done=ok)
        
    def _criar_produto_full(self):
        try:
            preco = float(self.e_prod_pre.get().strip() or "0")
        except:
            messagebox.showerror("Erro", "Preço inválido"); return
        try:
            qtd = int(self.e_st_qtd_new.get().strip() or "0")
        except:
            messagebox.showerror("Erro", "Quantidade inválida"); return
        try:
            prazo = int(self.e_forn_prazo.get().strip() or "0")
        except:
            messagebox.showerror("Erro", "Prazo do fornecedor inválido"); return

        data = {
            "descricao": self.e_prod_desc.get().strip(),
            "tamanho": self.e_prod_tam.get().strip(),
            "cor": self.e_prod_cor.get().strip(),
            "preco": preco,
            "quantidade_estoque": qtd,
            "localizacao": self.e_st_loc_new.get().strip() or "Prateleira A",
            "fornecedor": {
                "nome": self.e_forn_nome.get().strip() or None,
                "contato": self.e_forn_cont.get().strip() or None,
                "tempo_entrega_dias": prazo
            }
        }

        def ok(res):
            if res.get("success", True):
                messagebox.showinfo("OK", f"Produto criado (ID {res['produto']['id']}) e estoque cadastrado!")
                for w in (self.e_prod_desc, self.e_prod_tam, self.e_prod_cor, self.e_prod_pre,
                        self.e_st_qtd_new, self.e_st_loc_new, self.e_forn_nome, self.e_forn_cont, self.e_forn_prazo):
                    w.delete(0, tk.END)
                self._load_produtos_rdb()
                self._load_estoque()
            else:
                messagebox.showerror("Erro", f"{res.get('error')}")

        self.call_api("POST", "/produtos_full", data, ok)


    def _tab_estoque(self, parent):
        actions = ttk.Frame(parent); actions.pack(fill='x', padx=6, pady=6)
        ttk.Button(actions, text="Sincronizar Estoque (RDB → Mongo)", command=self._sync_estoque).pack(side='left', padx=4)
        ttk.Button(actions, text="Atualizar Lista", command=self._load_estoque).pack(side='left', padx=4)

        form = ttk.LabelFrame(parent, text="Upsert Estoque"); form.pack(fill='x', padx=6, pady=6)
        ttk.Label(form, text="produto_id").grid(row=0,column=0, padx=5,pady=5, sticky='e')
        ttk.Label(form, text="Descrição").grid(row=0,column=2, padx=5,pady=5, sticky='e')
        ttk.Label(form, text="Tamanho").grid(row=1,column=0, padx=5,pady=5, sticky='e')
        ttk.Label(form, text="Cor").grid(row=1,column=2, padx=5,pady=5, sticky='e')
        ttk.Label(form, text="Quantidade").grid(row=2,column=0, padx=5,pady=5, sticky='e')

        self.e_st_pid = ttk.Entry(form, width=12); self.e_st_pid.grid(row=0,column=1, padx=5,pady=5)
        self.e_st_desc= ttk.Entry(form, width=30); self.e_st_desc.grid(row=0,column=3, padx=5,pady=5)
        self.e_st_tam = ttk.Entry(form, width=12); self.e_st_tam.grid(row=1,column=1, padx=5,pady=5)
        self.e_st_cor = ttk.Entry(form, width=12); self.e_st_cor.grid(row=1,column=3, padx=5,pady=5)
        self.e_st_qtd = ttk.Entry(form, width=12); self.e_st_qtd.grid(row=2,column=1, padx=5,pady=5)
        ttk.Button(form, text="Salvar/Atualizar", command=self._upsert_estoque).grid(row=3, column=0, columnspan=4, pady=6)

        lst = ttk.LabelFrame(parent, text="Estoque (Mongo)"); lst.pack(fill='both', expand=True, padx=6, pady=6)
        self.tree_st = ttk.Treeview(lst, columns=("pid","desc","tam","cor","cat","qtd","loc","upd"), show="headings")
        for c,t in zip(("pid","desc","tam","cor","cat","qtd","loc","upd"),
                       ("produto_id","Descrição","Tam","Cor","Categoria","Qtd","Local","Atualizado")):
            self.tree_st.heading(c,text=t); self.tree_st.column(c,anchor='center',width=120)
        self.tree_st.pack(fill='both', expand=True, padx=5, pady=5)
        self._load_estoque()

    def _sync_estoque(self):
        def ok(res):
            if res.get("success", True):
                messagebox.showinfo("OK", f"Sync concluído. criados={res.get('created')} atualizados={res.get('updated')}")
                self._load_estoque()
            else:
                messagebox.showerror("Erro", f"{res.get('error')}")
        self.call_api("POST","/estoque/sync_from_rdb",on_done=ok)

    def _load_estoque(self):
        def ok(res):
            if res.get("success", True):
                for i in self.tree_st.get_children(): self.tree_st.delete(i)
                for d in res.get("estoque", []):
                    self.tree_st.insert('', 'end', values=(
                        d.get("produto_id"), d.get("descricao"), d.get("tamanho"),
                        d.get("cor"), d.get("categoria"), d.get("quantidade_estoque"),
                        d.get("localizacao"), d.get("ultima_atualizacao")
                    ))
            else:
                messagebox.showerror("Erro", f"{res.get('error')}")
        self.call_api("GET","/estoque",on_done=ok)

    def _upsert_estoque(self):
        try:
            data = {
                "produto_id": int(self.e_st_pid.get().strip()),
                "descricao": self.e_st_desc.get().strip(),
                "tamanho": self.e_st_tam.get().strip(),
                "cor": self.e_st_cor.get().strip(),
                "quantidade_estoque": int(self.e_st_qtd.get().strip()),
                "categoria": "Geral",
                "localizacao": "Prateleira A"
            }
        except:
            messagebox.showerror("Erro","produto_id e quantidade devem ser inteiros"); return
        def ok(res):
            if res.get("success", True):
                messagebox.showinfo("OK","Estoque salvo/atualizado")
                self._load_estoque()
            else:
                messagebox.showerror("Erro", f"{res.get('error')}")
        self.call_api("POST","/estoque",data,ok)

    def _tab_pedidos(self, parent):
        box = ttk.LabelFrame(parent, text="Registrar Pedido"); box.pack(fill='x', padx=6, pady=6)
        ttk.Label(box,text="Cliente ID").grid(row=0,column=0, padx=5,pady=5, sticky='e')
        ttk.Label(box,text="produto_id").grid(row=0,column=2, padx=5,pady=5, sticky='e')
        ttk.Label(box,text="Quantidade").grid(row=1,column=0, padx=5,pady=5, sticky='e')
        ttk.Label(box,text="Valor (R$)").grid(row=1,column=2, padx=5,pady=5, sticky='e')

        self.e_pd_c = ttk.Entry(box,width=12); self.e_pd_c.grid(row=0,column=1, padx=5,pady=5)
        self.e_pd_p = ttk.Entry(box,width=12); self.e_pd_p.grid(row=0,column=3, padx=5,pady=5)
        self.e_pd_q = ttk.Entry(box,width=12); self.e_pd_q.grid(row=1,column=1, padx=5,pady=5); self.e_pd_q.insert(0,"1")
        self.e_pd_v = ttk.Entry(box,width=12); self.e_pd_v.grid(row=1,column=3, padx=5,pady=5); self.e_pd_v.insert(0,"0")

        ttk.Button(box,text="Registrar", command=self._registrar_pedido).grid(row=2,column=0,columnspan=4,pady=6)

        gbox = ttk.LabelFrame(parent, text="Grafo"); gbox.pack(fill='x', padx=6, pady=6)
        
        gbox = ttk.LabelFrame(parent, text="Grafo / Conferência"); gbox.pack(fill='x', padx=6, pady=6)
        ttk.Button(gbox, text="Status Neo4j", command=self._graph_stats).pack(side='left', padx=5)
        ttk.Button(gbox, text="Últimas compras", command=self._graph_last_edges).pack(side='left', padx=5)


    def _registrar_pedido(self):
        try:
            data = {
                "cliente_id": int(self.e_pd_c.get()),
                "produto_id": int(self.e_pd_p.get()),
                "quantidade": int(self.e_pd_q.get()),
                "valor": float(self.e_pd_v.get())
            }
        except Exception:
            messagebox.showerror("Erro", "IDs/Quantidade/Valor inválidos")
            return

        def ok(res):
            if res.get("success", True):
                pid = res.get("pedido_id")
                messagebox.showinfo("OK", f"Pedido registrado! ID {pid}")

                self._load_estoque()

                if self.e_h_cid.get().strip():
                    self._load_hist()
            else:
                messagebox.showerror("Erro", f"{res.get('error')}")

        self.call_api("POST", "/pedidos", data, ok)

    def _graph_stats(self):
        def ok(res):
            if res.get("success", True):
                s = res.get("stats", {})
                messagebox.showinfo(
                    "Stats do Grafo",
                    f"Clientes: {s.get('clientes')}\n"
                    f"Produtos: {s.get('produtos')}\n"
                    f"Compras: {s.get('compras')}"
                )
            else:
                messagebox.showerror("Erro", f"{res.get('error')}")
        self.call_api("GET", "/graph/stats", on_done=ok)

    def _graph_last_edges(self):
        def ok(res):
            self.tx_hist.delete(1.0, tk.END)
            if res.get("success", True):
                edges = res.get("edges", [])
                if not edges:
                    self.tx_hist.insert(tk.END, "(sem compras recentes)\n")
                    return
                for e in edges:
                    self.tx_hist.insert(
                        tk.END,
                        f"c{e.get('cliente_id')} comprou {e.get('descricao')} "
                        f"(pid={e.get('produto_id')}) qtd={e.get('quantidade')} "
                        f"R${e.get('valor')} em {e.get('data')}\n"
                    )
            else:
                self.tx_hist.insert(tk.END, f"Erro: {res.get('error')}\n")
        self.call_api("GET", "/graph/last_edges?limit=15", on_done=ok)

    def _tab_hist(self, parent):
        box = ttk.LabelFrame(parent, text="Cliente"); box.pack(fill='x', padx=6, pady=6)
        ttk.Label(box, text="Cliente ID").grid(row=0,column=0, padx=5,pady=5, sticky='e')
        self.e_h_cid = ttk.Entry(box,width=12); self.e_h_cid.grid(row=0,column=1, padx=5,pady=5)
        ttk.Button(box,text="Histórico", command=self._load_hist).grid(row=0,column=2,padx=5)
        ttk.Button(box,text="Recomendações", command=self._load_recs).grid(row=0,column=3,padx=5)

        out = ttk.LabelFrame(parent, text="Resultados"); out.pack(fill='both', expand=True, padx=6, pady=6)
        self.tx_hist = tk.Text(out, height=20); self.tx_hist.pack(fill='both', expand=True, padx=6, pady=6)

    def _load_hist(self):
        try: cid=int(self.e_h_cid.get())
        except: messagebox.showerror("Erro","Cliente ID inválido"); return
        def ok(res):
            self.tx_hist.delete(1.0, tk.END)
            if res.get("success", True):
                arr = res.get("historico",[])
                if not arr: self.tx_hist.insert(tk.END,"(sem compras)\n"); return
                for r in arr:
                    self.tx_hist.insert(tk.END, f"- {r.get('descricao')} (pid={r.get('produto_id')}) qtd={r.get('quantidade')} R${r.get('valor')} em {r.get('data')}\n")
            else:
                self.tx_hist.insert(tk.END, f"Erro: {res.get('error')}\n")
        self.call_api("GET", f"/historico/{cid}", on_done=ok)

    def _load_recs(self):
        try: cid=int(self.e_h_cid.get())
        except: messagebox.showerror("Erro","Cliente ID inválido"); return
        def ok(res):
            self.tx_hist.delete(1.0, tk.END)
            if res.get("success", True):
                arr = res.get("recomendacoes",[])
                if not arr: self.tx_hist.insert(tk.END,"(sem recomendações)\n"); return
                for r in arr:
                    self.tx_hist.insert(tk.END, f"- {r.get('descricao')} (pid={r.get('produto_id')}) cat={r.get('categoria')} cor={r.get('cor')} score={r.get('score')}\n")
            else:
                self.tx_hist.insert(tk.END, f"Erro: {res.get('error')}\n")
        self.call_api("GET", f"/recomendacoes/{cid}", on_done=ok)

    def _tab_log(self, parent):
        self.tx_log = tk.Text(parent, height=24)
        self.tx_log.pack(fill='both', expand=True, padx=6, pady=6)
        btns = ttk.Frame(parent); btns.pack(fill='x', padx=6, pady=6)
        ttk.Button(btns, text="Atualizar Log", command=self._refresh_log).pack(side='left', padx=4)
        ttk.Button(btns, text="Copiar JSON", command=self._copy_log).pack(side='left', padx=4)

    def _refresh_log(self):
        self.tx_log.delete(1.0, tk.END)
        for l in self.log_requisicoes[-150:]:
            status = "deu certo" if 200 <= l["status"] < 300 else "erro"
            self.tx_log.insert(tk.END, f"{status} {l['timestamp']} {l['metodo']} {l['endpoint']} ({l['status']})\n")

    def _copy_log(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(json.dumps(self.log_requisicoes, ensure_ascii=False, indent=2))
        messagebox.showinfo("OK","Log copiado.")

if __name__ == "__main__":
    root = tk.Tk()
    app = SistemaGestao(root)
    root.mainloop()
