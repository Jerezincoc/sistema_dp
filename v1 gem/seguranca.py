import hashlib
import os
import json
import sys

ADMIN_MESTRE_USER = "admin"
ADMIN_MESTRE_HASH = "d94a12b9016f0f5f9c0b5d5c5f2d0ba10791cfdee62c034bc2d7adf8a88d2150"
ADMIN_MESTRE_SALT = "SISTEMA_DP_JE"

def obter_caminho_dados():
    if getattr(sys, 'frozen', False):
        diretorio_base = os.path.dirname(sys.executable)
    else:
        diretorio_base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(diretorio_base, ".secure_data.bin")

ARQUIVO_USUARIOS = obter_caminho_dados()

def carregar_usuarios():
    if not os.path.exists(ARQUIVO_USUARIOS): return {}
    try:
        with open(ARQUIVO_USUARIOS, "r") as f: return json.load(f)
    except: return {}

def salvar_usuarios(dados):
    with open(ARQUIVO_USUARIOS, "w") as f: json.dump(dados, f, indent=4)

def gerar_hash(senha, salt):
    return hashlib.pbkdf2_hmac("sha256", senha.encode(), salt.encode(), 100_000).hex()

# --- FUNÇÕES PRINCIPAIS ---

def verificar_login(usuario, senha):
    # 1. VERIFICA SE É O ADMIN MESTRE (O que está no código)
    if usuario == ADMIN_MESTRE_USER:
        hash_teste = gerar_hash(senha, ADMIN_MESTRE_SALT)
        if hash_teste == ADMIN_MESTRE_HASH:
            return True, "Acesso Master Autorizado."
    
    # 2. SE NÃO FOR, PROCURA NO ARQUIVO .BIN (Usuários comuns)
    dados = carregar_usuarios()
    if usuario in dados:
        salt_salvo = dados[usuario]["salt"]
        hash_salvo = dados[usuario]["hash"]
        if gerar_hash(senha, salt_salvo) == hash_salvo:
            return True, "Login autorizado."
            
    return False, "Usuário ou senha incorretos."

def criar_usuario(usuario, senha):
    """Cria usuários comuns que ficam no .bin"""
    dados = carregar_usuarios()
    if usuario == ADMIN_MESTRE_USER or usuario in dados:
        return False, "Usuário já existe."

    salt = os.urandom(16).hex()
    hash_senha = gerar_hash(senha, salt)
    dados[usuario] = {"salt": salt, "hash": hash_senha}
    salvar_usuarios(dados)
    return True, "Usuário criado com sucesso."

def existe_usuario():
    # Como o Admin Mestre sempre existe no código, essa função sempre retorna True
    return True
def listar_usuarios():
    """Retorna uma lista com os nomes de todos os usuários comuns."""
    dados = carregar_usuarios()
    return list(dados.keys())

def deletar_usuario(usuario):
    """Remove um usuário do arquivo .bin"""
    if usuario == ADMIN_MESTRE_USER:
        return False, "O Administrador Mestre não pode ser removido."
    
    dados = carregar_usuarios()
    if usuario in dados:
        del dados[usuario]
        salvar_usuarios(dados)
        return True, f"Usuário {usuario} removido com sucesso."
    return False, "Usuário não encontrado."