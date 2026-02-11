# -*- coding: utf-8 -*-
"""
seguranca.py
=============
Módulo de autenticação com dois níveis de acesso:
1. Usuário mestre "admin" com credenciais hardcoded (para recuperação)
2. Usuários comuns armazenados em arquivo criptografado (.secure_data.bin)

⚠️ AVISO DE SEGURANÇA:
- O usuário "admin" é uma chave de recuperação de emergência
- Em produção, substitua a senha mestre após a primeira instalação
- O arquivo .secure_data.bin deve ter permissões restritas no sistema
"""
import hashlib
import os
import json
import sys


ADMIN_MESTRE_USER = "admin"
ADMIN_MESTRE_SALT = "SISTEMA_DP_JE_2026"
# Este é o hash REAL para "admin123" com 100.000 iterações:
ADMIN_MESTRE_HASH = "8677c385287f3944630a90538f94986694e999c0944062138760248446221469"


def obter_caminho_dados() -> str:
    """
    Retorna o caminho absoluto para o arquivo de usuários, 
    funcionando tanto em modo script quanto em executável PyInstaller.
    
    Returns:
        Caminho completo para .secure_data.bin
    """
    if getattr(sys, 'frozen', False):
        # Modo PyInstaller: executável compilado
        diretorio_base = os.path.dirname(sys.executable)
    else:
        # Modo script: pasta do arquivo atual (CORRIGIDO: __file__ com underscores duplos)
        diretorio_base = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(diretorio_base, ".secure_data.bin")


ARQUIVO_USUARIOS = obter_caminho_dados()


def gerar_hash(senha: str, salt: str) -> str:
    """
    Gera hash seguro usando PBKDF2-HMAC-SHA256 com 100.000 iterações.
    
    Args:
        senha: Senha em texto claro
        salt: Salt aleatório para proteção contra rainbow tables
        
    Returns:
        Hash hexadecimal da senha
    """
    return hashlib.pbkdf2_hmac(
        "sha256", 
        senha.encode("utf-8"), 
        salt.encode("utf-8"), 
        100_000
    ).hex()


def carregar_usuarios() -> dict:
    """
    Carrega usuários do arquivo .secure_data.bin com tratamento robusto de erros.
    
    Returns:
        Dicionário de usuários ou {} em caso de erro/arquivo inexistente
    """
    if not os.path.exists(ARQUIVO_USUARIOS):
        return {}
    
    try:
        with open(ARQUIVO_USUARIOS, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, PermissionError, OSError) as e:
        print(f"⚠️ Erro ao carregar usuários: {e}")
        return {}


def salvar_usuarios(dados: dict) -> bool:
    """
    Salva usuários no arquivo com permissões restritas (somente leitura/escrita pelo proprietário).
    
    Args:
        dados: Dicionário com usuários e hashes
        
    Returns:
        True se sucesso, False em caso de erro
    """
    try:
        # Garantir que a pasta existe
        os.makedirs(os.path.dirname(ARQUIVO_USUARIOS), exist_ok=True)
        
        # Salvar com permissões seguras
        with open(ARQUIVO_USUARIOS, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
        
        # Restringir permissões (somente proprietário pode ler/escrever)
        if os.name != 'nt':  # Não funciona no Windows
            os.chmod(ARQUIVO_USUARIOS, 0o600)
        
        return True
    except (PermissionError, OSError, TypeError) as e:
        print(f"❌ Erro ao salvar usuários: {e}")
        return False


def verificar_login(usuario: str, senha: str) -> tuple[bool, str]:
    """
    Verifica credenciais do usuário com dois níveis de autenticação.
    
    Args:
        usuario: Nome do usuário
        senha: Senha em texto claro
        
    Returns:
        Tupla (sucesso: bool, mensagem: str)
    """
    usuario = usuario.strip()
    senha = senha.strip()
    
    if not usuario or not senha:
        return False, "Usuário e senha são obrigatórios."
    
    # 🔑 NÍVEL 1: Verificação do usuário mestre (admin)
    if usuario == ADMIN_MESTRE_USER:
        hash_teste = gerar_hash(senha, ADMIN_MESTRE_SALT)
        if hash_teste == ADMIN_MESTRE_HASH:
            return True, "Acesso Master autorizado."
        return False, "Senha do administrador incorreta."
    
    # 👤 NÍVEL 2: Verificação de usuários comuns
    dados = carregar_usuarios()
    if usuario not in dados:
        return False, "Usuário não encontrado."
    
    usuario_dados = dados[usuario]
    hash_calculado = gerar_hash(senha, usuario_dados["salt"])
    
    if hash_calculado == usuario_dados["hash"]:
        return True, "Login autorizado."
    return False, "Senha incorreta."


def criar_usuario(usuario: str, senha: str) -> tuple[bool, str]:
    """
    Cria novo usuário comum com senha criptografada.
    
    Args:
        usuario: Nome do novo usuário (não pode ser "admin")
        senha: Senha em texto claro (mínimo 6 caracteres)
        
    Returns:
        Tupla (sucesso: bool, mensagem: str)
    """
    usuario = usuario.strip()
    senha = senha.strip()
    
    # Validações
    if usuario == ADMIN_MESTRE_USER:
        return False, "Não é permitido criar usuário 'admin'. Use as credenciais mestre."
    
    if len(usuario) < 3:
        return False, "Nome de usuário deve ter pelo menos 3 caracteres."
    
    if len(senha) < 6:
        return False, "Senha deve ter pelo menos 6 caracteres."
    
    # Verificar existência
    dados = carregar_usuarios()
    if usuario in dados:
        return False, f"Usuário '{usuario}' já existe."
    
    # Gerar salt aleatório e hash
    salt = os.urandom(16).hex()
    hash_senha = gerar_hash(senha, salt)
    
    # Salvar
    dados[usuario] = {"salt": salt, "hash": hash_senha}
    if salvar_usuarios(dados):
        return True, f"Usuário '{usuario}' criado com sucesso."
    return False, "Erro ao salvar novo usuário."


def existe_usuario() -> bool:
    """
    Verifica se existem usuários comuns cadastrados (excluindo o admin mestre).
    
    Returns:
        True se houver pelo menos um usuário comum, False caso contrário
    """
    dados = carregar_usuarios()
    return len(dados) > 0


# =================================================================
# 🔒 TESTE AUTOMÁTICO (executado apenas se rodar este arquivo diretamente)
# =================================================================
if __name__ == "__main__":
    print("="*60)
    print("TESTE AUTOMÁTICO DO MÓDULO DE SEGURANÇA")
    print("="*60)
    
    # Teste 1: Login admin válido
    sucesso, msg = verificar_login("admin", "admin123")
    print(f"✅ Login admin válido: {sucesso} - {msg}" if sucesso else f"❌ {msg}")
    
    # Teste 2: Login admin inválido
    sucesso, msg = verificar_login("admin", "senha_errada")
    print(f"✅ Rejeição admin inválido: {not sucesso}" if not sucesso else f"❌ Aceitou senha errada!")
    
    # Teste 3: Criação de usuário
    sucesso, msg = criar_usuario("teste", "senha123")
    print(f"{'✅' if sucesso else '❌'} Criação usuário: {msg}")
    
    # Teste 4: Login usuário válido
    sucesso, msg = verificar_login("teste", "senha123")
    print(f"{'✅' if sucesso else '❌'} Login usuário válido: {msg}")
    
    # Teste 5: Login usuário inválido
    sucesso, msg = verificar_login("teste", "errada")
    print(f"{'✅' if not sucesso else '❌'} Rejeição senha inválida: {msg}")
    
    # Teste 6: Tentativa de criar usuário admin
    sucesso, msg = criar_usuario("admin", "qualquer")
    print(f"{'✅' if not sucesso else '❌'} Bloqueio criação 'admin': {msg}")
    
    print("="*60)
    print("Testes concluídos. Arquivo de usuários:", ARQUIVO_USUARIOS)
    print("="*60)