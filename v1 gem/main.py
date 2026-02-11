# Arquivo: main.py
import tkinter as tk
from interface import SistemaDPApp
from tela_login import LoginApp


def abrir_sistema_principal(usuario_logado):
    root_sistema = tk.Tk()
    app = SistemaDPApp(root_sistema, usuario_logado) 
    root_sistema.mainloop()

if __name__ == "__main__":
    root_login = tk.Tk()
    app_login = LoginApp(root_login, on_success_callback=abrir_sistema_principal)
    root_login.mainloop()