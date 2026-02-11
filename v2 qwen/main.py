# -*- coding: utf-8 -*-
"""
main.py
=======
Ponto de entrada seguro do Sistema DP com fluxo de autenticação robusto.
Corrige o problema crítico de múltiplas instâncias Tk() que causava instabilidade.
"""
import tkinter as tk
from tkinter import messagebox
from tela_login import LoginApp
from interface import SistemaDPApp


class AplicacaoPrincipal:
    """
    Gerencia o ciclo de vida completo da aplicação com um único Tk() root.
    Implementa o padrão recomendado pelo Tkinter: uma única instância root + Toplevels.
    """
    
    def __init__(self):
        # ✅ ÚNICA instância Tk() para toda a aplicação
        self.root = tk.Tk()
        self.root.title("Sistema DP 2026 - Login")
        self._centralizar_janela(400, 300)
        
        # Estado atual da aplicação
        self.usuario_logado = None
        self.app_principal = None
        
        # Inicia com tela de login
        self.mostrar_login()
        
        # Tratamento seguro do fechamento da janela
        self.root.protocol("WM_DELETE_WINDOW", self._ao_fechar_aplicacao)
    
    def _centralizar_janela(self, largura, altura):
        """Centraliza a janela na tela do usuário."""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - largura) // 2
        y = (screen_height - altura) // 2
        self.root.geometry(f"{largura}x{altura}+{x}+{y}")
    
    def mostrar_login(self):
        """Exibe a tela de login (destrói interface principal se existir)."""
        # Limpa a janela atual
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Atualiza título da janela
        self.root.title("Sistema DP 2026 - Login")
        self._centralizar_janela(400, 300)
        
        # Instancia a tela de login
        self.login_app = LoginApp(
            self.root, 
            on_success_callback=self._ao_login_sucesso,
            on_cancel_callback=self._ao_cancelar_login
        )
    
    def _ao_login_sucesso(self, usuario):
        """Callback executado após autenticação bem-sucedida."""
        self.usuario_logado = usuario
        
        # Limpa a tela de login
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Atualiza título com usuário logado
        self.root.title(f"Sistema DP 2026 - Usuário: {usuario}")
        self.root.geometry("1000x750")
        self._centralizar_janela(1000, 750)
        
        # Instancia a interface principal
        self.app_principal = SistemaDPApp(self.root, usuario)
    
    def _ao_cancelar_login(self):
        """Callback para cancelamento/fechamento da tela de login."""
        self.root.quit()
    
    def _ao_fechar_aplicacao(self):
        """Tratamento seguro do evento de fechamento da janela."""
        if messagebox.askokcancel("Sair", "Deseja realmente sair do Sistema DP?"):
            self.root.destroy()
    
    def executar(self):
        """Inicia o loop principal da aplicação."""
        self.root.mainloop()


# =================================================================
# 🔐 PONTO DE ENTRADA SEGURO
# =================================================================
if __name__ == "__main__":
    try:
        app = AplicacaoPrincipal()
        app.executar()
    except Exception as e:
        # Fallback para erro catastrófico (ex: módulo login ausente)
        import traceback
        traceback.print_exc()
        print(f"\n❌ ERRO FATAL AO INICIAR O SISTEMA:\n{e}")
        input("\nPressione ENTER para sair...")