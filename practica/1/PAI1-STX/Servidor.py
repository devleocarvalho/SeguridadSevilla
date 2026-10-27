import http.server
import json
import math
import os
import time
import uuid
import urllib.parse
from http.cookies import SimpleCookie
from pathlib import Path

import hasher


# ==============================================================================
# 1. ARQUIVOS DE PERSISTÊNCIA E ESTADO DO SERVIDOR
# ==============================================================================
DATA_DIR = Path(__file__).resolve().parent
CREDENTIALS_FILE = DATA_DIR / "credenciales.json"   # Base de dados de usuários e hashes
TRANSACTIONS_FILE = DATA_DIR / "transacciones.json" # Histórico de transferências bancárias
NONCES_FILE = DATA_DIR / "nonces.json"             # Armazena nonces usados para evitar Replay Attack
secret_key = hasher.SECRET_KEY                     # Chave secreta de 32 bytes compartilhada com o cliente
sesiones_activas = set()                           # Conjunto na memória com IDs de sessões ativas

# Inicialização e carregamento do banco de dados JSON
with CREDENTIALS_FILE.open("r", encoding="utf-8") as file_credenciales:
    credenciales = json.load(file_credenciales)
with TRANSACTIONS_FILE.open("r", encoding="utf-8") as file_transacciones:
    transacciones = json.load(file_transacciones)

# Carrega e sanitiza o registro de nonces com suporte à purga temporal anti-DoS
with NONCES_FILE.open("r", encoding="utf-8") as file_nonces:
    nonces_guardados = json.load(file_nonces)

# Estrutura interna de nonces: {nonce_str: timestamp_float}
if isinstance(nonces_guardados, dict):
    nonces_registro = nonces_guardados
elif isinstance(nonces_guardados, list):
    tempo_atual = time.time()
    nonces_registro = {str(n): tempo_atual for n in nonces_guardados}
else:
    nonces_registro = {}


def guardar_json(ruta: Path, datos: object) -> None:
    """Função utilitária para salvar dados de forma legível em arquivo JSON."""
    with ruta.open("w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, indent=4)


def purgar_nonces_expirados() -> None:
    """
    Defesa contra esgotamento de memória/disco (Storage Exhaustion DoS):
    Como qualquer mensagem com timestamp anterior a 60 segundos é rejeitada,
    nonces com mais de 60 segundos podem ser seguramente descartados.
    """
    agora = time.time()
    nonces_para_remover = [
        n for n, ts in nonces_registro.items() if (agora - ts) > 65
    ]
    for n in nonces_para_remover:
        del nonces_registro[n]
    if nonces_para_remover:
        guardar_json(NONCES_FILE, nonces_registro)


# ==============================================================================
# 2. LOGS DE SEGURANÇA E AUDITORIA FORENSE
# ==============================================================================
def log_seguridad(tipo: str, mensagem: str, ip_cliente: str = "") -> None:
    """Registra alertas de segurança formatados para monitoramento em tempo real (Kali Linux)."""
    timestamp_log = time.strftime("%Y-%m-%d %H:%M:%S")
    ip_str = f" [{ip_cliente}]" if ip_cliente else ""
    print(f"\033[91m[SEC-ALERT]\033[0m [{timestamp_log}]{ip_str} \033[1m[{tipo}]\033[0m {mensagem}")


def log_evento(tipo: str, mensagem: str) -> None:
    """Registra eventos operacionais legítimos."""
    timestamp_log = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"\033[92m[INFO]\033[0m [{timestamp_log}] [{tipo}] {mensagem}")


# ==============================================================================
# 3. HANDLER HTTP PRINCIPAL COM DEFESA ATIVA
# ==============================================================================
class Handler(http.server.BaseHTTPRequestHandler):
    # Desativa logging padrão para destacar alertas de segurança
    def log_message(self, format: str, *args: object) -> None:
        pass

    def responder(
        self,
        codigo: int,
        mensaje: str,
        cookie: str = "",
        retry_after: int | None = None,
    ) -> None:
        """
        Envia resposta HTTP com cabeçalhos de segurança contra Clickjacking,
        MIME-Sniffing e Cache de dados sensíveis bancários.
        """
        self.send_response(codigo)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        # Hardening de cabeçalhos HTTP
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        if retry_after is not None:
            self.send_header("Retry-After", str(retry_after))
        if cookie:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()
        self.wfile.write(mensaje.encode("utf-8"))

    def do_POST(self) -> None:
        ip_cliente = self.client_address[0]

        # ----------------------------------------------------------------------
        # PASSO A: Validação e Limite de Tamanho do Payload (Anti-DoS)
        # ----------------------------------------------------------------------
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.responder(400, "Longitud de mensaje no válida.")
            return

        # Limite máximo de 64 KB por requisição para evitar ataques de DoS por memória
        if content_length <= 0 or content_length > 65536:
            log_seguridad("PAYLOAD-INVALIDO", f"Tamanho de payload anormal ({content_length} bytes)", ip_cliente)
            self.responder(400, "El mensaje está vacío o excede el límite permitido.")
            return

        byte_data = self.rfile.read(content_length)

        # ----------------------------------------------------------------------
        # PASSO B: Parsing do corpo (JSON ou urlencoded)
        # ----------------------------------------------------------------------
        try:
            if "application/json" in self.headers.get("Content-Type", ""):
                params = json.loads(byte_data.decode("utf-8"))
                if not isinstance(params, dict):
                    raise ValueError("El cuerpo JSON debe ser un objeto.")
            else:
                valores = urllib.parse.parse_qs(byte_data.decode("utf-8"))
                params = {nombre: valor[0] for nombre, valor in valores.items()}
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
            log_seguridad("MALFORMED-BODY", "Corpo malformado recebido", ip_cliente)
            self.responder(400, "Cuerpo de mensaje no válido.")
            return

        # ----------------------------------------------------------------------
        # PASSO C: CAMADA DE DEFESA CRIPTOGRÁFICA (HMAC, NONCE, TIMESTAMP)
        # ----------------------------------------------------------------------
        signature = self.headers.get("X-Signature", "")
        nonce = self.headers.get("X-Nonce", "")
        timestamp = self.headers.get("X-Timestamp", "")

        # 1. Validação de presença de cabeçalhos de segurança
        if not signature or not nonce or not timestamp:
            log_seguridad("HEADERS-INCOMPLETOS", "Requisição sem headers X-Signature, X-Nonce ou X-Timestamp", ip_cliente)
            self.responder(403, "Mensaje no seguro detectado.")
            return

        # 2. Validação numérica do timestamp
        try:
            timestamp_numero = float(timestamp)
            if not math.isfinite(timestamp_numero):
                raise ValueError
        except ValueError:
            log_seguridad("TIMESTAMP-INVALIDO", f"Timestamp não numérico: '{timestamp}'", ip_cliente)
            self.responder(403, "Mensaje no seguro detectado.")
            return

        # 3. Janela de Frescura Temporal (60 segundos)
        diferenca_tempo = abs(time.time() - timestamp_numero)
        if diferenca_tempo > 60:
            log_seguridad("TIMESTAMP-EXPIRADO", f"Janela de tempo violada ({diferenca_tempo:.2f}s > 60s)", ip_cliente)
            self.responder(403, "Mensaje no seguro detectado.")
            return

        # 4. Defesa Anti-Replay (Detecção de Nonce duplicado)
        purgar_nonces_expirados()
        if nonce in nonces_registro:
            log_seguridad("REPLAY-ATTACK", f"Tentativa de reuso do nonce '{nonce}' detectada!", ip_cliente)
            self.responder(403, "Mensaje no seguro detectado.")
            return

        # 5. Defesa de Integridade e Autenticidade (HMAC-SHA256 em tempo constante)
        mensaje_firmado = byte_data + b"|" + nonce.encode("utf-8") + b"|" + timestamp.encode("utf-8")
        if not hasher.verificar_signature(mensaje_firmado, signature, secret_key):
            log_seguridad("HMAC-INVALIDO", "Firma HMAC incorreta! Possível MitM ou adulteração de dados em trânsito.", ip_cliente)
            self.responder(403, "Mensaje no seguro detectado.")
            return

        # Se passou em todas as verificações, registra o nonce
        nonces_registro[nonce] = time.time()
        guardar_json(NONCES_FILE, nonces_registro)

        # ----------------------------------------------------------------------
        # ENDPOINT 1: /signin (Cadastro de Novo Usuário)
        # ----------------------------------------------------------------------
        if self.path == "/signin":
            usuario = str(params.get("usuario", "")).strip()
            password = str(params.get("password", ""))

            if not usuario or not password:
                self.responder(400, "Usuario y contraseña son obligatorios.")
            elif len(password) < 8:
                self.responder(400, "La contraseña debe tener al menos 8 caracteres.")
            elif usuario in credenciales:
                log_seguridad("SIGNIN-CONFLITO", f"Tentativa de cadastrar usuário já existente '{usuario}'", ip_cliente)
                self.responder(403, "Usuario ya existe.")
            else:
                credenciales[usuario] = hasher.crear_hash_contraseña(password)
                guardar_json(CREDENTIALS_FILE, credenciales)
                log_evento("REGISTRO", f"Novo usuário '{usuario}' registrado com PBKDF2 (600k iter) + Salt de 16B.")
                self.responder(200, "Registro exitoso.")

        # ----------------------------------------------------------------------
        # ENDPOINT 2: /login (Autenticação com Defesa contra Força Bruta & Timing)
        # ----------------------------------------------------------------------
        elif self.path == "/login":
            usuario = str(params.get("usuario", ""))
            password = str(params.get("password", ""))
            datos_usuario = credenciales.get(usuario)

            # DEFESA CONTRA ENUMERAÇÃO DE USUÁRIOS POR TIMING ATTACK:
            # Se o usuário não existir, executa PBKDF2 dummy para gastar o mesmo tempo na CPU!
            if datos_usuario is None:
                hasher.simular_verificacion_tiempo_constante(password)
                log_seguridad("LOGIN-FALHA", f"Tentativa de login com usuário inexistente '{usuario}'", ip_cliente)
                self.responder(401, "Credenciales incorrectas.")

            # DEFESA CONTRA FORÇA BRUTA (ACCOUNT LOCKOUT):
            elif hasher.cuenta_bloqueada(datos_usuario):
                guardar_json(CREDENTIALS_FILE, credenciales)
                log_seguridad("FORCA-BRUTA-BLOQUEADA", f"Acesso negado: Conta '{usuario}' está bloqueada temporariamente!", ip_cliente)
                self.responder(429, "Cuenta bloqueada temporalmente.", retry_after=hasher.TIEMPO_BLOQUEO)

            # VALIDAÇÃO DE SENHA (TEMPO CONSTANTE):
            elif hasher.verificar_contraseña(password, datos_usuario):
                guardar_json(CREDENTIALS_FILE, credenciales)
                id_sesion = str(uuid.uuid4())
                sesiones_activas.add(id_sesion)
                log_evento("LOGIN-SUCESSO", f"Usuário '{usuario}' autenticado com sucesso. Sessão emitida.")
                self.responder(
                    200,
                    "Inicio de sesión exitoso.",
                    f"session_id={id_sesion}; Path=/; HttpOnly; SameSite=Strict",
                )
            else:
                # Senha incorreta: contador de erros incrementado
                guardar_json(CREDENTIALS_FILE, credenciales)
                erros = datos_usuario[2]
                if erros >= hasher.MAX_INTENTOS:
                    log_seguridad(
                        "FORCA-BRUTA-DISPARADA",
                        f"Limite de {hasher.MAX_INTENTOS} erros atingido para '{usuario}'! Conta congelada por {hasher.TIEMPO_BLOQUEO}s.",
                        ip_cliente,
                    )
                    self.responder(429, "Cuenta bloqueada temporalmente.", retry_after=hasher.TIEMPO_BLOQUEO)
                else:
                    log_seguridad(
                        "LOGIN-ERRO",
                        f"Tentativa de login incorreta para '{usuario}' ({erros}/{hasher.MAX_INTENTOS})",
                        ip_cliente,
                    )
                    self.responder(401, "Credenciales incorrectas.")

        # ----------------------------------------------------------------------
        # ENDPOINT 3: /logout (Encerramento de Sessão Seguro)
        # ----------------------------------------------------------------------
        elif self.path == "/logout":
            cookie_value = None
            cookie = self.headers.get("Cookie")
            if cookie:
                data_cookie = SimpleCookie()
                data_cookie.load(cookie)
                if "session_id" in data_cookie:
                    cookie_value = data_cookie["session_id"].value

            if cookie_value not in sesiones_activas:
                log_seguridad("LOGOUT-INVALIDO", "Tentativa de logout sem sessão ativa", ip_cliente)
                self.responder(403, "No hay una sesión activa.")
            else:
                sesiones_activas.discard(cookie_value)
                log_evento("LOGOUT", "Sessão invalidada com sucesso no servidor.")
                self.responder(
                    200,
                    "Sesión cerrada correctamente.",
                    "session_id=; Path=/; HttpOnly; SameSite=Strict; Max-Age=0",
                )

        # ----------------------------------------------------------------------
        # ENDPOINT 4: /transfer (Transferência Bancária com Idempotência e Anti-Fraude)
        # ----------------------------------------------------------------------
        elif self.path == "/transfer":
            cookie_value = None
            cookie = self.headers.get("Cookie")
            if cookie:
                data_cookie = SimpleCookie()
                data_cookie.load(cookie)
                if "session_id" in data_cookie:
                    cookie_value = data_cookie["session_id"].value

            # 1. Defesa de Autorização: Cookie de Sessão Válido Obrigatório
            if cookie_value not in sesiones_activas:
                log_seguridad("ACESSO-NAO-AUTORIZADO", "Tentativa de transferência sem sessão autenticada!", ip_cliente)
                self.responder(403, "Inicie sesión antes de realizar una transferencia.")
                return

            tx_id = str(params.get("tx_id", "")).strip()
            origin_account = str(params.get("origin_account", "")).strip()
            destination_account = str(params.get("destination_account", "")).strip()
            amount_raw = params.get("amount", "")
            currency = str(params.get("currency", "")).strip().upper()

            try:
                transaction_timestamp = float(params.get("timestamp", timestamp_numero))
                if not math.isfinite(transaction_timestamp):
                    raise ValueError
            except (TypeError, ValueError):
                self.responder(400, "Timestamp de transacción no válido.")
                return

            # 2. Defesa contra Injeção de Valores Negativos ou Inválidos (Fraude Financeira)
            try:
                amount_num = float(amount_raw)
                if amount_num <= 0 or not math.isfinite(amount_num):
                    raise ValueError
            except (TypeError, ValueError):
                log_seguridad("VALOR-INVALIDO", f"Valor de transferência não permitido: '{amount_raw}'", ip_cliente)
                self.responder(400, "La cantidad a transferir debe ser un número positivo mayor que 0.")
                return

            # 3. Defesa contra Autotransferência
            if origin_account == destination_account:
                log_seguridad("CONTAS-IGUAIS", "Conta de origem e destino idênticas", ip_cliente)
                self.responder(400, "La cuenta de origen y de destino no pueden ser iguales.")
                return

            # 4. Validação de Presença dos Campos
            if not tx_id or not origin_account or not destination_account or not currency:
                self.responder(400, "Faltan datos obligatorios de la transferencia.")
                return

            # 5. Defesa contra Gasto Duplo (Double Spending / Idempotência por tx_id)
            if tx_id in transacciones:
                log_seguridad("DOUBLE-SPENDING", f"Tentativa de reuso de tx_id duplicado '{tx_id}'", ip_cliente)
                self.responder(403, "Transacción duplicada.")
                return

            # Registra transação aprovada
            transacciones[tx_id] = [
                origin_account,
                destination_account,
                amount_num,
                currency,
                transaction_timestamp,
            ]
            guardar_json(TRANSACTIONS_FILE, transacciones)
            log_evento(
                "TRANSFERENCIA-CONCLUIDA",
                f"Transferência [{tx_id[:8]}] {amount_num} {currency} de {origin_account} para {destination_account}.",
            )
            self.responder(200, "Transacción exitosa.")

        else:
            self.responder(404, "Ruta no encontrada.")


# ==============================================================================
# 4. INICIALIZAÇÃO DO SERVIDOR COM DEFESA ATIVA
# ==============================================================================
if __name__ == "__main__":
    host = "127.0.0.1"
    port = int(
        os.environ.get("SECBANK_SERVER_PORT", os.environ.get("SECBANK_PORT", "8080"))
    )
    print("\n" + "=" * 70)
    print("  SERVIDOR SECBANK ATIVO COM MOTOR DEFENSIVO")
    print(f"  Escutando em: http://{host}:{port}")
    print("  Defesas ativas:")
    print("  [+] HMAC-SHA256 (Integridade & Autenticidade)")
    print("  [+] Nonce Unívoco + Purga Temporal (Anti-Replay & Anti-Exhaustion)")
    print("  [+] Janela de Frescura de 60s (Anti-Delay Attack)")
    print("  [+] PBKDF2 600.000 iterações + Salt 16B (Anti-GPU Brute Force)")
    print("  [+] Account Lockout 3 tentativas / 300s (Anti-Dictionary Attack)")
    print("  [+] Resposta em Tempo Constante (Anti-User Enumeration Timing Attack)")
    print("  [+] Idempotência por UUIDv4 tx_id (Anti-Double Spending)")
    print("  [+] Sessões HttpOnly com SameSite=Strict (Anti-Hijacking)")
    print("=" * 70 + "\n")
    try:
        http.server.HTTPServer((host, port), Handler).serve_forever()
    except KeyboardInterrupt:
        print("\nServidor finalizado pelo operador.")
