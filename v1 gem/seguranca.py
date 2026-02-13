import hashlib
import os
import json
import sys

# --- CONFIGURAÇÕES DO MESTRE ABSOLUTO ---
ADMIN_MESTRE_USER = "admin"
ADMIN_MESTRE_HASH = "d94a12b9016f0f5f9c0b5d5c5f2d0ba10791cfdee62c034bc2d7adf8a88d2150"
ADMIN_MESTRE_SALT = "SISTEMA_DP_JE"

# --- DEFINIÇÃO DE PESOS ---
NIVEIS = {
    "MESTRE": 3,
    "ADMINISTRADOR": 2,
    "OPERADOR": 1,
    "OBSERVADOR": 0
}

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

# --- FUNÇÕES DE VALIDAÇÃO DE ACESSO ---

def verificar_login(usuario, senha):
    """Retorna (Sucesso, Perfil)"""
    # 1. Verificação do Mestre Hardcoded
    if usuario == ADMIN_MESTRE_USER:
        hash_teste = gerar_hash(senha, ADMIN_MESTRE_SALT)
        if hash_teste == ADMIN_MESTRE_HASH:
            return True, "MESTRE"
    
    # 2. Verificação no arquivo .bin
    dados = carregar_usuarios()
    if usuario in dados:
        salt_salvo = dados[usuario]["salt"]
        hash_salvo = dados[usuario]["hash"]
        if gerar_hash(senha, salt_salvo) == hash_salvo:
            return True, dados[usuario].get("perfil", "OBSERVADOR")
            
    return False, None

# --- FUNÇÕES DE GESTÃO (COM HIERARQUIA) ---

def criar_usuario(quem_esta_criando_perfil, novo_usuario, nova_senha, novo_perfil):
    """
    quem_esta_criando_perfil: Perfil de quem está operando o sistema agora.
    Regra: Só cria perfis de nível igual ou inferior, exceto MESTRE.
    """
    dados = carregar_usuarios()
    
    if novo_usuario == ADMIN_MESTRE_USER or novo_usuario in dados:
        return False, "Usuário já existe."

    # VALIDAÇÃO DE HIERARQUIA
    p_criador = NIVEIS.get(quem_esta_criando_perfil, 0)
    p_novo = NIVEIS.get(novo_perfil, 0)

    # Regra: Só Mestre cria outro Mestre
    if novo_perfil == "MESTRE" and quem_esta_criando_perfil != "MESTRE":
        return False, "Apenas um MESTRE pode promover outro MESTRE."

    # Regra Geral: Não pode criar alguém com nível superior ao seu
    if p_novo > p_criador:
        return False, f"Seu nível ({quem_esta_criando_perfil}) não permite criar um ({novo_perfil})."

    salt = os.urandom(16).hex()
    hash_senha = gerar_hash(nova_senha, salt)
    dados[novo_usuario] = {
        "salt": salt, 
        "hash": hash_senha, 
        "perfil": novo_perfil.upper()
    }
    salvar_usuarios(dados)
    return True, f"Usuário {novo_usuario} criado como {novo_perfil}."

def listar_usuarios():
    dados = carregar_usuarios()
    lista = []
    # Adiciona o admin mestre manualmente na visualização
    lista.append({"usuario": "admin", "perfil": "MESTRE"})
    for user, info in dados.items():
        lista.append({"usuario": user, "perfil": info["perfil"]})
    return lista

def deletar_usuario(quem_esta_deletando_perfil, usuario_alvo):
    if usuario_alvo == ADMIN_MESTRE_USER:
        return False, "O Administrador Mestre é intocável."
    
    dados = carregar_usuarios()
    if usuario_alvo not in dados:
        return False, "Usuário não encontrado."

    # Só deleta quem for de nível igual ou inferior
    p_deletador = NIVEIS.get(quem_esta_deletando_perfil, 0)
    p_alvo = NIVEIS.get(dados[usuario_alvo]["perfil"], 0)

    if p_alvo > p_deletador:
        return False, "Você não tem autoridade para remover este usuário."

    del dados[usuario_alvo]
    salvar_usuarios(dados)
    return True, f"Usuário {usuario_alvo} removido."

# --- FUNÇÕES DE PERMISSÃO PARA A INTERFACE ---

def pode_alterar_tabelas_legais(perfil):
    """Regra: Apenas Mestre altera INSS/IRRF"""
    return perfil == "MESTRE"

def pode_gerenciar_rubricas(perfil):
    """Regra: Mestre e Administrador podem mexer nas fórmulas"""
    return NIVEIS.get(perfil, 0) >= 2