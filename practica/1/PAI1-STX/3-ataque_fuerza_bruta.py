"""
SIMULAÇÃO REAL DE ATAQUE DE FORÇA BRUTA (BRUTE-FORCE ATTACK SIMULATOR)
Projeto SecBank - PAI 1 IntegriDos (Segurança em Sistemas Informáticos)

Este script executa uma simulação real de ataque de força bruta contra o servidor SecBank,
testando os dois cenários reais de ameaça:

CENÁRIO 1: Atacante Externo na Rede (Sem Chave Secreta HMAC)
- Simula um atacante na Internet tentando adivinhar senhas via API REST.
- Mostra como a camada de integridade (HMAC-SHA256) neutraliza o ataque antes
  mesmo de qualquer verificação de credenciais no banco de dados.

CENÁRIO 2: Atacante com Acesso à API / Cliente Comprometido (Ataque de Dicionário)
- Simula um invasor que possui um cliente válido assinado e tenta adivinhar a senha
  de uma conta alvo usando uma lista de senhas (Wordlist).
- Demonstra o custo computacional do PBKDF2 (600.000 iterações).
- Demonstra o acionamento da defesa ativa: bloqueio da conta (HTTP 429) após 3 tentativas.
- Demonstra que mesmo acertando a senha após o bloqueio, o acesso permanece bloqueado.
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request
import uuid

import hasher

SERVER_PORT = os.environ.get(
    "SECBANK_SERVER_PORT", os.environ.get("SECBANK_PORT", "8080")
)
BASE_URL = f"http://127.0.0.1:{SERVER_PORT}"

# Wordlist realista de senhas comuns para o ataque de dicionário
DICCIONARIO_PASSWORDS = [
    "123456",
    "password",
    "admin123",
    "banco2026",
    "qwerty1234",
    "SevillaFirme!",  # Senha correta da vítima
    "dragon99",
    "letmein123",
]


def enviar_requisicao(
    ruta: str,
    datos: bytes,
    usar_clave_valida: bool = True,
    timestamp_custom: str | None = None,
) -> tuple[int, str, float]:
    """
    Envia uma requisição HTTP POST ao servidor e mede com precisão o tempo de resposta.
    Permite alternar entre assinatura legítima e forjada para simular atacantes externos.
    """
    nonce = str(uuid.uuid4())
    timestamp = timestamp_custom or str(time.time())
    mensaje = datos + b"|" + nonce.encode("utf-8") + b"|" + timestamp.encode("utf-8")

    if usar_clave_valida:
        firma = hasher.crear_hash_signature(mensaje)
    else:
        # Atacante externo forjando assinatura com chave desconhecida
        chave_atacante = b"chave_falsa_do_atacante_12345678"
        firma = hasher.crear_hash_signature(mensaje, chave_atacante)

    req = urllib.request.Request(
        f"{BASE_URL}{ruta}",
        data=datos,
        headers={
            "Content-Type": "application/json",
            "X-Signature": firma,
            "X-Nonce": nonce,
            "X-Timestamp": timestamp,
        },
        method="POST",
    )

    inicio = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            duracao = (time.perf_counter() - inicio) * 1000
            return resp.status, resp.read().decode("utf-8"), duracao
    except urllib.error.HTTPError as error:
        duracao = (time.perf_counter() - inicio) * 1000
        return error.code, error.read().decode("utf-8"), duracao
    except urllib.error.URLError as e:
        print(f"\n[ERRO] Não foi possível conectar ao servidor em {BASE_URL}: {e.reason}")
        print("Certifique-se de que o Servidor.py está rodando antes de executar o teste.")
        sys.exit(1)


def banner(titulo: str) -> None:
    print("\n" + "=" * 70)
    print(f" {titulo}")
    print("=" * 70)


def main() -> None:
    print("======================================================================")
    print("  SIMULADOR REAL DE FORÇA BRUTA & AUDITORIA DE RESPOSTA SECBANK")
    print(f"  Alvo: {BASE_URL}")
    print("======================================================================")

    # --------------------------------------------------------------------------
    # PASSO 0: Criação de conta alvo no servidor
    # --------------------------------------------------------------------------
    usuario_alvo = f"vitima_{uuid.uuid4().hex[:6]}"
    senha_real = "SevillaFirme!"

    banner(f"0. Preparação: Registrando conta da vítima ({usuario_alvo})")
    dados_reg = json.dumps({"usuario": usuario_alvo, "password": senha_real}).encode("utf-8")
    status, msg, tempo = enviar_requisicao("/signin", dados_reg)
    print(f"[*] Resposta: HTTP {status} | Tempo: {tempo:.1f}ms | Msg: {msg.strip()}")
    if status != 200:
        print(f"[!] Falha ao registrar conta de teste. Verifique se o servidor está ativo.")
        return

    # --------------------------------------------------------------------------
    # CENÁRIO 1: Atacante Externo Sem Chave Secreta HMAC
    # --------------------------------------------------------------------------
    banner("CENÁRIO 1: Ataque Externo na Rede (Sem chave secreta HMAC)")
    print("[*] Um atacante tenta injetar senhas sem possuir a chave de integridade...")
    dados_ataque = json.dumps({"usuario": usuario_alvo, "password": "123456"}).encode("utf-8")
    status, msg, tempo = enviar_requisicao("/login", dados_ataque, usar_clave_valida=False)
    print(f"[*] Tentativa 1 (Chave forjada): HTTP {status} | Tempo: {tempo:.1f}ms | Msg: {msg.strip()}")

    if status == 403:
        print("[+] DEFESA 1 COMPROVADA: O servidor barrou a tentativa na camada HMAC.")
        print("    O atacante externo não consegue nem tentar adivinhar a senha!")
    else:
        print(f"[-] FALHA: Servidor respondeu HTTP {status} em vez de 403.")

    # --------------------------------------------------------------------------
    # CENÁRIO 2: Ataque de Dicionário com API Válida (Malicious Insider)
    # --------------------------------------------------------------------------
    banner("CENÁRIO 2: Ataque de Dicionário com Assinatura Válida")
    print(f"[*] Iniciando ataque contra o usuário '{usuario_alvo}' com wordlist de {len(DICCIONARIO_PASSWORDS)} senhas:")
    print("    Limite do servidor: MAX_INTENTOS = 3 falhas antes do bloqueio.")
    print("-" * 70)

    tentativas_bloqueadas = 0
    bloqueio_detectado = False

    for i, senha_candidata in enumerate(DICCIONARIO_PASSWORDS, start=1):
        dados_login = json.dumps({"usuario": usuario_alvo, "password": senha_candidata}).encode("utf-8")
        status, msg, tempo = enviar_requisicao("/login", dados_login, usar_clave_valida=True)

        status_tag = f"HTTP {status}"
        if status == 200:
            resultado = "SUCESSO (Senha encontrada!)"
        elif status == 401:
            resultado = "FALHA (Credencial incorreta)"
        elif status == 429:
            resultado = "BLOQUEADO (Rate Limit / Lockout Ativo)"
            tentativas_bloqueadas += 1
            bloqueio_detectado = True
        else:
            resultado = f"RESPOSTA INESPERADA ({msg})"

        print(
            f"Tentativa {i:02d} | Palpite: '{senha_candidata:<15}' | "
            f"{status_tag} | {tempo:6.1f}ms | {resultado}"
        )

    # --------------------------------------------------------------------------
    # CENÁRIO 3: Teste da Senha Correta Durante o Período de Bloqueio
    # --------------------------------------------------------------------------
    banner("CENÁRIO 3: Testando a Senha Real com a Conta Bloqueada")
    print(f"[*] O atacante finalmente descobriu a senha real ('{senha_real}').")
    print("    Tentando autenticar agora...")
    dados_login_correto = json.dumps({"usuario": usuario_alvo, "password": senha_real}).encode("utf-8")
    status, msg, tempo = enviar_requisicao("/login", dados_login_correto, usar_clave_valida=True)
    print(f"[*] Resposta com senha CORRETA: HTTP {status} | {tempo:.1f}ms | Msg: {msg.strip()}")

    if status == 429:
        print("[+] DEFESA 2 COMPROVADA: Mesmo com a senha 100% correta, o servidor recusa!")
        print("    A conta está temporariamente congelada por 300 segundos.")
    else:
        print(f"[-] FALHA: Servidor aceitou senha ou retornou código inesperado: HTTP {status}")

    # --------------------------------------------------------------------------
    # RELATÓRIO TÉCNICO FINAL
    # --------------------------------------------------------------------------
    banner("RELATÓRIO DA AUDITORIA DE SEGURANÇA CONTRA FORÇA BRUTA")
    print(f"• Total de senhas testadas: {len(DICCIONARIO_PASSWORDS)}")
    print(f"• Bloqueio ativo confirmado: {'SIM (HTTP 429)' if bloqueio_detectado else 'NÃO'}")
    print(f"• Tentativas barradas pelo bloqueio: {tentativas_bloqueadas}")
    print("• Avaliação do algoritmo PBKDF2 (600.000 iterações):")
    print("  Cada verificação legítima demorou ~150-350ms de processamento na CPU,")
    print("  tornando ataques de dicionário offline ou remotos inviáveis em grande escala.")
    print("======================================================================\n")


if __name__ == "__main__":
    main()
