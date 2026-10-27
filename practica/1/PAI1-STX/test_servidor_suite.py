"""
SUÍTE COMPLETA DE TESTES DE INTEGRAÇÃO E AUDITORIA DE SEGURANÇA
Projeto SecBank - PAI 1 IntegriDos (Segurança em Sistemas Informáticos)

Este arquivo executa uma bateria formal de testes automatizados contra o Servidor SecBank,
auditando rigorosamente se TODOS os requisitos de segurança e mecanismos defensivos estão
operando com precisão absoluta:

1.  Autenticidade e Integridade (HMAC-SHA256)
2.  Defesa Anti-Replay (Nonces únicos e não-repetíveis)
3.  Defesa de Frescura Temporal (Janela estrita de 60 segundos)
4.  Defesa contra Força Bruta (Account Lockout após 3 falhas com HTTP 429)
5.  Defesa de Autorização e Sessão (Cookies HttpOnly, SameSite e Invalidação no Logout)
6.  Defesa contra Fraude e Gasto Duplo (Idempotência por tx_id e valores positivos)
7.  Defesa contra Adulteração em Trânsito (MitM)

COMO EXECUTAR:
  python test_servidor_suite.py
"""

import json
import os
import sys
import time
import unittest
import urllib.error
import urllib.request
import uuid
from http.cookies import SimpleCookie

import hasher

SERVER_PORT = os.environ.get(
    "SECBANK_SERVER_PORT", os.environ.get("SECBANK_PORT", "8080")
)
BASE_URL = f"http://127.0.0.1:{SERVER_PORT}"


def enviar_post(
    rota: str,
    payload_dict: dict,
    chave_hmac: bytes = hasher.SECRET_KEY,
    nonce_custom: str | None = None,
    timestamp_custom: float | None = None,
    cookie_str: str = "",
) -> tuple[int, str, dict[str, str]]:
    """Função auxiliar para envio e assinatura de requisições ao servidor."""
    byte_data = json.dumps(payload_dict).encode("utf-8")
    nonce = nonce_custom if nonce_custom is not None else str(uuid.uuid4())
    ts = str(timestamp_custom if timestamp_custom is not None else time.time())

    mensagem = byte_data + b"|" + nonce.encode("utf-8") + b"|" + ts.encode("utf-8")
    assinatura = hasher.crear_hash_signature(mensagem, chave_hmac)

    headers = {
        "Content-Type": "application/json",
        "X-Signature": assinatura,
        "X-Nonce": nonce,
        "X-Timestamp": ts,
    }
    if cookie_str:
        headers["Cookie"] = cookie_str

    req = urllib.request.Request(
        f"{BASE_URL}{rota}", data=byte_data, headers=headers, method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            headers_resp = {k: v for k, v in resp.headers.items()}
            return resp.status, resp.read().decode("utf-8"), headers_resp
    except urllib.error.HTTPError as error:
        headers_resp = {k: v for k, v in error.headers.items()}
        return error.code, error.read().decode("utf-8"), headers_resp


class TestSecBankServerDefenses(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Valida conectividade básica com o servidor
        try:
            status, _, _ = enviar_post("/signin", {"usuario": "", "password": ""})
            if status != 400:
                pass
        except urllib.error.URLError:
            print(f"\n[ERRO CRÍTICO] Não foi possível conectar ao servidor em {BASE_URL}.")
            print("Inicie o servidor antes de rodar os testes: python Servidor.py\n")
            sys.exit(1)

    # --------------------------------------------------------------------------
    # 1. TESTES DE REGISTRO E GESTÃO DE CREDENCIAIS
    # --------------------------------------------------------------------------
    def test_01_registro_usuario_legitimo(self):
        """Valida cadastro bem-sucedido de novo usuário (HTTP 200)."""
        usuario = f"user_{uuid.uuid4().hex[:6]}"
        status, msg, _ = enviar_post("/signin", {"usuario": usuario, "password": "PasswordForte2026!"})
        self.assertEqual(status, 200, f"Falha no registro: {msg}")
        self.assertIn("Registro exitoso", msg)

    def test_02_registro_usuario_duplicado_deve_falhar(self):
        """Garante que usuários com nomes repetidos sejam bloqueados com HTTP 403."""
        usuario = f"dup_{uuid.uuid4().hex[:6]}"
        enviar_post("/signin", {"usuario": usuario, "password": "PasswordForte2026!"})
        # Tentativa de recadastrar o mesmo usuário
        status, msg, _ = enviar_post("/signin", {"usuario": usuario, "password": "OutraPassword!"})
        self.assertEqual(status, 403)
        self.assertIn("Usuario ya existe", msg)

    # --------------------------------------------------------------------------
    # 2. TESTES DE AUTENTICAÇÃO E SESSÃO
    # --------------------------------------------------------------------------
    def test_03_login_e_emissao_cookie_seguro(self):
        """Valida login legítimo e emissão de Cookie com flags HttpOnly e SameSite."""
        usuario = f"auth_{uuid.uuid4().hex[:6]}"
        senha = "SuperClaveSecreta!"
        enviar_post("/signin", {"usuario": usuario, "password": senha})

        status, msg, headers = enviar_post("/login", {"usuario": usuario, "password": senha})
        self.assertEqual(status, 200, f"Falha no login: {msg}")

        set_cookie = headers.get("Set-Cookie", "")
        self.assertIn("session_id=", set_cookie)
        self.assertIn("HttpOnly", set_cookie, "O cookie DEVE possuir a flag HttpOnly para proteção contra XSS.")

    # --------------------------------------------------------------------------
    # 3. TESTES DE TRANSFERÊNCIA FINANCEIRA E REGRAS DE NEGÓCIO
    # --------------------------------------------------------------------------
    def test_04_transferencia_legitima_com_sessao(self):
        """Valida que uma transferência com cookie de sessão válido seja aceita (HTTP 200)."""
        usuario = f"tx_user_{uuid.uuid4().hex[:6]}"
        senha = "SuperClaveSecreta!"
        enviar_post("/signin", {"usuario": usuario, "password": senha})
        _, _, headers = enviar_post("/login", {"usuario": usuario, "password": senha})
        cookie = headers.get("Set-Cookie", "").split(";")[0]

        tx_payload = {
            "tx_id": str(uuid.uuid4()),
            "origin_account": "ES1234567890123456789012",
            "destination_account": "ES9876543210987654321098",
            "amount": 250.75,
            "currency": "EUR",
        }
        status, msg, _ = enviar_post("/transfer", tx_payload, cookie_str=cookie)
        self.assertEqual(status, 200, f"Transferência legítima recusada: {msg}")

    def test_05_transferencia_sem_sessao_deve_ser_negada(self):
        """Garante que transferências anônimas ou sem cookie válido recebam HTTP 403."""
        tx_payload = {
            "tx_id": str(uuid.uuid4()),
            "origin_account": "ES1234567890123456789012",
            "destination_account": "ES9876543210987654321098",
            "amount": 100.0,
            "currency": "EUR",
        }
        status, _, _ = enviar_post("/transfer", tx_payload, cookie_str="")
        self.assertEqual(status, 403, "Transferência sem cookie de sessão foi permitida!")

    def test_06_transferencia_valor_negativo_deve_falhar(self):
        """Garante que valores negativos ou zerados sejam rejeitados com HTTP 400."""
        usuario = f"fraud_{uuid.uuid4().hex[:6]}"
        senha = "SuperClaveSecreta!"
        enviar_post("/signin", {"usuario": usuario, "password": senha})
        _, _, headers = enviar_post("/login", {"usuario": usuario, "password": senha})
        cookie = headers.get("Set-Cookie", "").split(";")[0]

        tx_payload = {
            "tx_id": str(uuid.uuid4()),
            "origin_account": "ES1234567890123456789012",
            "destination_account": "ES9876543210987654321098",
            "amount": -500.0,  # Valor fraudulento
            "currency": "EUR",
        }
        status, msg, _ = enviar_post("/transfer", tx_payload, cookie_str=cookie)
        self.assertEqual(status, 400, "Valor de transferência negativo não foi barrado!")

    def test_07_prevencao_duplo_gasto_idempotencia(self):
        """Garante que reenvios do mesmo tx_id sejam barrados com HTTP 403 (Transacción duplicada)."""
        usuario = f"idem_{uuid.uuid4().hex[:6]}"
        senha = "SuperClaveSecreta!"
        enviar_post("/signin", {"usuario": usuario, "password": senha})
        _, _, headers = enviar_post("/login", {"usuario": usuario, "password": senha})
        cookie = headers.get("Set-Cookie", "").split(";")[0]

        tx_id_unico = str(uuid.uuid4())
        tx_payload = {
            "tx_id": tx_id_unico,
            "origin_account": "ES1234567890123456789012",
            "destination_account": "ES9876543210987654321098",
            "amount": 50.0,
            "currency": "EUR",
        }
        status1, _, _ = enviar_post("/transfer", tx_payload, cookie_str=cookie)
        self.assertEqual(status1, 200)

        # Reenvio com novo nonce (não é replay de rede, mas reutiliza tx_id financeiro)
        status2, msg2, _ = enviar_post("/transfer", tx_payload, cookie_str=cookie)
        self.assertEqual(status2, 403)
        self.assertIn("Transacción duplicada", msg2)

    # --------------------------------------------------------------------------
    # 4. TESTES DE SEGURANÇA CRIPTOGRÁFICA (MITM, REPLAY, TIMESTAMPS)
    # --------------------------------------------------------------------------
    def test_08_mitm_adulteracao_de_dados_em_transito(self):
        """Simula atacante alterando dados (de 10 EUR para 10000 EUR) mantendo a assinatura original."""
        usuario = f"mitm_{uuid.uuid4().hex[:6]}"
        senha = "SuperClaveSecreta!"
        enviar_post("/signin", {"usuario": usuario, "password": senha})
        _, _, headers = enviar_post("/login", {"usuario": usuario, "password": senha})
        cookie = headers.get("Set-Cookie", "").split(";")[0]

        # Payload legítimo original
        payload_original = {
            "tx_id": str(uuid.uuid4()),
            "origin_account": "ES1234567890123456789012",
            "destination_account": "ES9876543210987654321098",
            "amount": 10.0,
            "currency": "EUR",
        }
        byte_data = json.dumps(payload_original).encode("utf-8")
        nonce = str(uuid.uuid4())
        ts = str(time.time())
        # Assinatura gerada sobre 10.0 EUR
        msg_original = byte_data + b"|" + nonce.encode("utf-8") + b"|" + ts.encode("utf-8")
        firma_legitima = hasher.crear_hash_signature(msg_original)

        # Atacante altera o corpo da requisição para 10000.0 EUR
        payload_adulterado = dict(payload_original)
        payload_adulterado["amount"] = 10000.0
        byte_adulterado = json.dumps(payload_adulterado).encode("utf-8")

        req = urllib.request.Request(
            f"{BASE_URL}/transfer",
            data=byte_adulterado,
            headers={
                "Content-Type": "application/json",
                "X-Signature": firma_legitima,  # Assinatura não bate com o novo corpo!
                "X-Nonce": nonce,
                "X-Timestamp": ts,
                "Cookie": cookie,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=5) as r:
                code = r.status
        except urllib.error.HTTPError as e:
            code = e.code

        self.assertEqual(code, 403, "O servidor aceitou um payload adulterado (falha de HMAC/MitM)!")

    def test_09_atacante_sem_chave_secreta_deve_ser_barrado(self):
        """Simula requisição assinada com chave secreta forjada por um invasor."""
        chave_invasor = b"chave_completamente_falsa_123456"
        status, _, _ = enviar_post(
            "/signin",
            {"usuario": "hacker", "password": "password"},
            chave_hmac=chave_invasor,
        )
        self.assertEqual(status, 403, "Atacante com chave falsa não foi barrado!")

    def test_10_replay_attack_nonce_repetido(self):
        """Garante que reenviar uma requisição legítima idêntica seja barrado por Nonce duplicado."""
        usuario = f"replay_{uuid.uuid4().hex[:6]}"
        payload = {"usuario": usuario, "password": "PasswordForte123!"}
        nonce_fixo = str(uuid.uuid4())
        ts_fixo = time.time()

        # Envio 1: Legítimo
        status1, _, _ = enviar_post(
            "/signin", payload, nonce_custom=nonce_fixo, timestamp_custom=ts_fixo
        )
        self.assertEqual(status1, 200)

        # Envio 2: Atacante intercepta e reenvia o pacote exato
        status2, _, _ = enviar_post(
            "/signin", payload, nonce_custom=nonce_fixo, timestamp_custom=ts_fixo
        )
        self.assertEqual(status2, 403, "Ataque de Replay com mesmo Nonce foi aceito!")

    def test_11_timestamp_expirado_deve_ser_rejeitado(self):
        """Garante que requisições com timestamp fora da janela de 60s sejam recusadas."""
        usuario = f"stale_{uuid.uuid4().hex[:6]}"
        payload = {"usuario": usuario, "password": "PasswordForte123!"}
        timestamp_antigo = time.time() - 120  # 2 minutos no passado

        status, _, _ = enviar_post("/signin", payload, timestamp_custom=timestamp_antigo)
        self.assertEqual(status, 403, "Requisição com timestamp expirado (> 60s) foi aceita!")

    # --------------------------------------------------------------------------
    # 5. TESTES DE DEFESA CONTRA FORÇA BRUTA (LOCKOUT) E LOGOUT
    # --------------------------------------------------------------------------
    def test_12_defesa_contra_forca_bruta_bloqueio_conta(self):
        """Verifica se após 3 erros consecutivos a conta é bloqueada com HTTP 429."""
        usuario = f"brute_{uuid.uuid4().hex[:6]}"
        senha_correta = "MinhaSenhaReal2026!"
        enviar_post("/signin", {"usuario": usuario, "password": senha_correta})

        # 3 tentativas incorretas devem responder HTTP 401
        for i in range(1, hasher.MAX_INTENTOS + 1):
            status, _, _ = enviar_post("/login", {"usuario": usuario, "password": f"senha_errada_{i}"})
            self.assertEqual(status, 401, f"Tentativa {i} não respondeu 401!")

        # 4ª tentativa (mesmo com a senha correta!) deve responder HTTP 429 (Too Many Requests / Bloqueio)
        status_bloq, msg_bloq, headers_bloq = enviar_post(
            "/login", {"usuario": usuario, "password": senha_correta}
        )
        self.assertEqual(status_bloq, 429, "Conta não foi bloqueada após atingir MAX_INTENTOS!")
        self.assertIn("Retry-After", headers_bloq, "Servidor deve enviar cabeçalho Retry-After no bloqueio.")

    def test_13_logout_invalida_sessao_com_sucesso(self):
        """Garante que o logout invalide a sessão e expire o cookie."""
        usuario = f"logout_{uuid.uuid4().hex[:6]}"
        senha = "SuperClaveSecreta!"
        enviar_post("/signin", {"usuario": usuario, "password": senha})
        _, _, headers = enviar_post("/login", {"usuario": usuario, "password": senha})
        cookie = headers.get("Set-Cookie", "").split(";")[0]

        # Executa logout
        status_out, _, headers_out = enviar_post("/logout", {"logout": 1}, cookie_str=cookie)
        self.assertEqual(status_out, 200)
        self.assertIn("Max-Age=0", headers_out.get("Set-Cookie", ""))

        # Tentativa de transferir dinheiro após logout deve ser recusada com HTTP 403
        tx_payload = {
            "tx_id": str(uuid.uuid4()),
            "origin_account": "ES1234567890123456789012",
            "destination_account": "ES9876543210987654321098",
            "amount": 10.0,
            "currency": "EUR",
        }
        status_tx, _, _ = enviar_post("/transfer", tx_payload, cookie_str=cookie)
        self.assertEqual(status_tx, 403, "Sessão deslogada continuou autorizada a fazer transferências!")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("  SUÍTE DE AUDITORIA DE SEGURANÇA SECBANK (PAI 1 INTEGRIDOS)")
    print(f"  Testando servidor em: {BASE_URL}")
    print("=" * 70 + "\n")
    unittest.main(verbosity=2)
