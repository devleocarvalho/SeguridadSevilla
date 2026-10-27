import base64
import hashlib
import hmac
import os
import secrets
import time
from pathlib import Path

# ==============================================================================
# 1. GERENCIAMENTO DA CHAVE SECRETA (HMAC SECRET KEY)
# ==============================================================================
# A chave secreta é compartilhada exclusivamente entre o cliente e o servidor.
# Ela é usada para assinar as requisições via HMAC e garantir que ninguém no
# meio do caminho (ataque Man-in-the-Middle) consiga adulterar os dados.
KEY_FILE = Path(__file__).resolve().with_name("secret.key")
try:
    # 'xb' abre em modo exclusivo de escrita binária (falha se o arquivo já existir).
    # Se não existir, gera uma chave criptográfica forte de 32 bytes (256 bits).
    with KEY_FILE.open("xb") as file_key:
        SECRET_KEY = secrets.token_bytes(32)
        file_key.write(SECRET_KEY)
except FileExistsError:
    # Se já existir, lê a chave existente para manter a mesma entre execuções.
    SECRET_KEY = KEY_FILE.read_bytes()

# Para HMAC-SHA256, a chave deve ter pelo menos 32 bytes para máxima segurança.
if len(SECRET_KEY) < 32:
    raise ValueError("La clave HMAC debe tener al menos 32 bytes.")

# ==============================================================================
# 2. POLÍTICA DE DEFESA CONTRA FORÇA BRUTA (ACCOUNT LOCKOUT)
# ==============================================================================
MAX_INTENTOS = 3       # Número máximo de erros permitidos antes do bloqueio
TIEMPO_BLOQUEO = 300   # Tempo de bloqueio em segundos (5 minutos)


# ==============================================================================
# 3. GERAÇÃO DE HASH DE SENHA SEGURO (PBKDF2 + SALT)
# ==============================================================================
def crear_hash_contraseña(contraseña: str) -> list:
    """
    Gera um hash seguro para uma nova senha usando PBKDF2-HMAC-SHA256.
    
    Por que não usar MD5 ou SHA-256 direto?
    - Funções rápidas como MD5/SHA-256 permitem testar bilhões de senhas por segundo.
    - PBKDF2 é uma KDF (Key Derivation Function) "lenta", desenhada para inviabilizar
      ataques de força bruta e dicionário com GPUs.
    
    O que é o SALT?
    - Um conjunto de 16 bytes aleatórios únicos para este usuário.
    - Evita 'Rainbow Tables' (tabelas pré-computadas) e impede que dois usuários
      com a mesma senha tenham o mesmo hash salvo.
    """
    salt = os.urandom(16)  # Gera 16 bytes criptograficamente aleatórios

    # Executa 600.000 iterações de HMAC-SHA256 (recomendação OWASP)
    hash_resultado = hashlib.pbkdf2_hmac(
        "sha256",
        contraseña.encode("utf-8"),
        salt,
        600000,
    )
    
    # Estrutura salva no credenciales.json:
    # [0] Hash da senha codificado em Base64
    # [1] Salt único codificado em Base64
    # [2] Contador de tentativas consecutivas incorretas (inicia em 0)
    # [3] Timestamp de quando a conta foi bloqueada (inicia como None)
    return [
        base64.b64encode(hash_resultado).decode("ascii"),
        base64.b64encode(salt).decode("ascii"),
        0,
        None,
    ]


# ==============================================================================
# 4. VERIFICAÇÃO DE BLOQUEIO DE CONTA
# ==============================================================================
def cuenta_bloqueada(datos_usuario: list) -> bool:
    """
    Verifica se a conta do usuário está atualmente bloqueada por excesso de tentativas.
    """
    # Se o timestamp de bloqueio for None, a conta nunca foi bloqueada (ou já foi resetada).
    if datos_usuario[3] is None:
        return False

    # Se ainda não passaram 300 segundos (TIEMPO_BLOQUEO), a conta continua bloqueada.
    if time.time() - datos_usuario[3] < TIEMPO_BLOQUEO:
        return True

    # Se o tempo já expirou, desbloqueia automaticamente e reseta os contadores.
    datos_usuario[2] = 0
    datos_usuario[3] = None
    return False


# ==============================================================================
# 5. VERIFICAÇÃO DA SENHA DE LOGIN
# ==============================================================================
def verificar_contraseña(contraseña_ingresada: str, datos_usuario: list) -> bool:
    """
    Valida a senha digitada pelo usuário contra o hash armazenado.
    Utiliza comparação em tempo constante para mitigar Timing Attacks.
    """
    # Se a conta estiver bloqueada, rejeita imediatamente
    if cuenta_bloqueada(datos_usuario):
        return False

    # Recalcula o hash usando a senha digitada e o SALT ORIGINAL recuperado do usuário
    nuevo_hash = hashlib.pbkdf2_hmac(
        "sha256",
        contraseña_ingresada.encode("utf-8"),
        base64.b64decode(datos_usuario[1]),  # Decodifica o salt de Base64
        600000,
    )

    # hmac.compare_digest: COMPARAÇÃO EM TEMPO CONSTANTE
    # Comparações normais (ex: 'a == b') param no primeiro caractere diferente,
    # permitindo que um invasor descubra a senha medindo o tempo de resposta em microssegundos.
    # compare_digest sempre leva o mesmo tempo independente de onde difere.
    if hmac.compare_digest(nuevo_hash, base64.b64decode(datos_usuario[0])):
        # Senha correta: zera as tentativas de erro
        datos_usuario[2] = 0
        datos_usuario[3] = None
        return True

    # Senha incorreta: incrementa o contador de erros
    datos_usuario[2] += 1
    if datos_usuario[2] >= MAX_INTENTOS:
        # Atingiu o limite (3 tentativas): registra o timestamp do bloqueio
        datos_usuario[3] = time.time()
    return False


# ==============================================================================
# 5.1. DEFESA CONTRA TIMING ATTACK DE ENUMERAÇÃO DE USUÁRIOS
# ==============================================================================
_DUMMY_SALT = b"\x00" * 16
_DUMMY_HASH = hashlib.pbkdf2_hmac(
    "sha256", b"dummy_password_timing_protection", _DUMMY_SALT, 600000
)


def simular_verificacion_tiempo_constante(contraseña_ingresada: str) -> None:
    """
    Executa a derivação PBKDF2 pesada (600.000 iterações) mesmo quando o usuário NÃO existe.
    Isso impede que atacantes descubram quais contas existem no sistema através
    de Timing Attack (diferença entre 1ms para conta inexistente e centenas de ms para existente).
    """
    nuevo_hash = hashlib.pbkdf2_hmac(
        "sha256",
        contraseña_ingresada.encode("utf-8"),
        _DUMMY_SALT,
        600000,
    )
    hmac.compare_digest(nuevo_hash, _DUMMY_HASH)


# ==============================================================================
# 6. ASSINATURA DIGITAL DAS REQUISIÇÕES (HMAC-SHA256)
# ==============================================================================
def crear_hash_signature(data: bytes, secret_key: bytes = SECRET_KEY) -> str:
    """
    Gera a assinatura HMAC-SHA256 de um conjunto de dados binários usando a chave secreta.
    Qualquer alteração em 1 único bit dos dados resultará em uma assinatura totalmente diferente.
    """
    return hmac.new(secret_key, data, hashlib.sha256).hexdigest()


def verificar_signature(
    data: bytes, signature: str, secret_key: bytes = SECRET_KEY
) -> bool:
    """
    Verifica se a assinatura recebida bate com a calculada localmente.
    Também usa compare_digest para prevenir Timing Attacks na validação da assinatura.
    """
    firma_esperada = crear_hash_signature(data, secret_key)
    return hmac.compare_digest(firma_esperada, signature)

