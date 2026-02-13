import sys
from src.ui.app import App

def main():
    try:
        app = App()
        app.mainloop()
    except Exception as e:
        print(f"Erro fatal na inicialização do v1 gem: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()