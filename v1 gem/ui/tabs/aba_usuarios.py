import tkinter as tk
from tkinter import ttk, messagebox
import seguranca

class AbaUsuarios(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        # --- LADO ESQUERDO: CADASTRO ---
        frm_add = ttk.LabelFrame(self, text="Cadastrar Novo Usuário", padding=20)
        frm_add.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        ttk.Label(frm_add, text="Login:").pack(anchor="w")
        self.ent_novo_user = ttk.Entry(frm_add, width=30)
        self.ent_novo_user.pack(pady=(5, 15))

        ttk.Label(frm_add, text="Senha:").pack(anchor="w")
        self.ent_nova_senha = ttk.Entry(frm_add, width=30, show="*")
        self.ent_nova_senha.pack(pady=(5, 20))

        ttk.Button(frm_add, text="CADASTRAR", command=self.salvar_usuario).pack(fill=tk.X)

        # --- LADO DIREITO: LISTAGEM ---
        frm_lista = ttk.LabelFrame(self, text="Usuários Ativos", padding=20)
        frm_lista.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        columns = ("usuario", "tipo")
        self.tree = ttk.Treeview(frm_lista, columns=columns, show="headings")
        self.tree.heading("usuario", text="NOME DE USUÁRIO")
        self.tree.heading("tipo", text="NÍVEL DE ACESSO")
        self.tree.pack(fill=tk.BOTH, expand=True)

        ttk.Button(frm_lista, text="REMOVER SELECIONADO", command=self.remover_usuario).pack(pady=10)
        self.atualizar_tabela()

    def atualizar_tabela(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        # Admin Mestre (Sempre presente)
        self.tree.insert("", "end", values=("admin", "ADMINISTRADOR MESTRE"))
        # Usuários Comuns
        for user in seguranca.listar_usuarios():
            self.tree.insert("", "end", values=(user, "OPERADOR"))

    def salvar_usuario(self):
        u = self.ent_novo_user.get().strip()
        s = self.ent_nova_senha.get().strip()
        if not u or not s:
            messagebox.showwarning("Erro", "Preencha usuário e senha.")
            return
        
        sucesso, msg = seguranca.criar_usuario(u, s)
        if sucesso:
            messagebox.showinfo("Sucesso", msg)
            self.ent_novo_user.delete(0, tk.END)
            self.ent_nova_senha.delete(0, tk.END)
            self.atualizar_tabela()
        else:
            messagebox.showerror("Erro", msg)

    def remover_usuario(self):
        sel = self.tree.selection()
        if not sel: return
        
        usuario = self.tree.item(sel)["values"][0]
        if messagebox.askyesno("Confirmar", f"Deseja remover o acesso de {usuario}?"):
            sucesso, msg = seguranca.deletar_usuario(usuario)
            if sucesso:
                messagebox.showinfo("Sucesso", msg)
                self.atualizar_tabela()
            else:
                messagebox.showerror("Erro", msg)