import urllib.request
import urllib.parse
import json
from http.cookiejar import CookieJar
import os
from urllib.parse import urlsplit
import time
import uuid
import hasher

# ==============================================================================
# 1. GERENCIAMENTO DE COOKIES DE SESSÃO
# ==============================================================================
# CookieJar armazena automaticamente os cookies recebidos do servidor (como session_id)
# e os anexa em todas as próximas requisições feitas pelo urllib.
cookies = CookieJar()


# ==============================================================================
# 2. CONFIGURAÇÃO DE PROXY (BURP SUITE / MAN-IN-THE-MIDDLE)
# ==============================================================================
class BurpProxyHandler(urllib.request.ProxyHandler):
    """
    Handler customizado para desviar o tráfego HTTP local (127.0.0.1) para o Burp Suite.
    Por padrão, o urllib ignora proxies para endereços 'localhost'/'127.0.0.1'.
    Esta classe força as requisições a passarem pelo Burp para permitir interceptação de tráfego.
    """
    def proxy_open(self, req, proxy, proxy_type):
        if proxy_type != "http":
            raise ValueError("Este teste usa somente o proxy HTTP do Burp.")

        partes_proxy = urlsplit(proxy)
        if partes_proxy.scheme != "http" or not partes_proxy.netloc:
            raise ValueError(
                "Use o proxy HTTP do Burp, por exemplo http://127.0.0.1:8082"
            )

        servidor_original = req.host
        req.add_unredirected_header("Host", servidor_original)
        req.set_proxy(partes_proxy.netloc, "http")
        return None


# Se a variável SECBANK_BURP_PROXY estiver configurada no sistema, ativa o proxy do Burp.
burp_proxy = os.environ.get("SECBANK_BURP_PROXY")
if burp_proxy:
    opener = urllib.request.build_opener(
        BurpProxyHandler({"http": burp_proxy}),
        urllib.request.HTTPCookieProcessor(cookies),
    )
else:
    # Caso contrário, utiliza apenas o processador automático de cookies
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cookies)
    )
urllib.request.install_opener(opener)

# ==============================================================================
# 3. ENDEREÇOS E ROTAS DO SERVIDOR
# ==============================================================================
client_port = os.environ.get(
    "SECBANK_SERVER_PORT",
    os.environ.get("SECBANK_CLIENT_PORT", os.environ.get("SECBANK_PORT", "8080")),
)
base_URL = f"http://127.0.0.1:{client_port}"
signin_URL = f"{base_URL}/signin"
login_URL = f"{base_URL}/login"
transfer_URL = f"{base_URL}/transfer"
logout_URL = f"{base_URL}/logout"

# Chave secreta compartilhada para geração das assinaturas HMAC
secret_key = hasher.SECRET_KEY


# ==============================================================================
# 4. LOOP PRINCIPAL INTERATIVO DE COMANDOS
# ==============================================================================
print("Comandos disponíveis: signin | login | transfer | logout | exit")
while True:
    console_text = input()

    # --------------------------------------------------------------------------
    # COMANDO: SIGNIN (Cadastro de novo usuário)
    # --------------------------------------------------------------------------
    if console_text == "signin":
        print("Nuevo Usuario: ")
        usuario = input()
        print("Contraseña: ")
        password = input()

        # Codifica os dados do formulário em formato application/x-www-form-urlencoded
        datos = urllib.parse.urlencode({'usuario': usuario, 'password': password}).encode('utf-8')
        
        # 1. NONCE: Identificador único aleatório para esta requisição (UUIDv4)
        nonce = str(uuid.uuid4())
        
        # 2. TIMESTAMP: Momento exato em que a mensagem foi criada
        timestamp = str(time.time())

        # 3. ASSINATURA HMAC:
        # Assina conjuntamente: DADOS + NONCE + TIMESTAMP usando a chave secreta.
        # Qualquer tentativa de alterar um deles invalida a assinatura.
        mensagem_para_assinar = datos + b"|" + nonce.encode('utf-8') + b"|" + timestamp.encode('utf-8')
        assinatura = hasher.crear_hash_signature(mensagem_para_assinar, secret_key)

        headers = {
            "X-Signature": assinatura,
            "X-Nonce": nonce,
            "X-Timestamp": timestamp
        }

        req_login = urllib.request.Request(signin_URL, data=datos, headers=headers, method='POST')
        try:
            with urllib.request.urlopen(req_login) as respuesta:
                print("Respuesta Sign In:", respuesta.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            mensaje_error = e.read().decode('utf-8')
            print(f"Error en login ({e.code}): {mensaje_error}")
        except Exception as e:
            print("Error en login:", e)

    # --------------------------------------------------------------------------
    # COMANDO: LOGIN (Autenticação e obtenção do cookie de sessão)
    # --------------------------------------------------------------------------
    elif console_text == "login" and cookies.__len__() == 0:
        print("Usuario: ")
        usuario = input()
        print("Contraseña: ")
        password = input()

        datos = urllib.parse.urlencode({'usuario': usuario, 'password': password}).encode('utf-8')
        nonce = str(uuid.uuid4())
        timestamp = str(time.time())

        # Cria a assinatura protegendo corpo, nonce e timestamp
        mensagem_para_assinar = datos + b"|" + nonce.encode('utf-8') + b"|" + timestamp.encode('utf-8')
        headers = {
            "X-Signature": hasher.crear_hash_signature(mensagem_para_assinar, secret_key),
            "X-Nonce": nonce,
            "X-Timestamp": timestamp
        }

        req_login = urllib.request.Request(login_URL, data=datos, headers=headers, method='POST')
        try:
            with urllib.request.urlopen(req_login) as resposta:
                print("Respuesta Login:", resposta.read().decode('utf-8'))
        
                # O CookieJar já capturou o cabeçalho Set-Cookie automaticamente
                print("\nCookies guardadas localmente:")
                for cookie in cookies:  
                    print(f"- {cookie.name}: {cookie.value}")
        except urllib.error.HTTPError as e:
            mensaje_error = e.read().decode('utf-8')
            print(f"Error en login ({e.code}): {mensaje_error}")
        except Exception as e:
            print("Error en login:", e)

    # --------------------------------------------------------------------------
    # COMANDO: TRANSFER (Transferência bancária autenticada)
    # --------------------------------------------------------------------------
    elif console_text == "transfer":
        # tx_id: Identificador único da transação financeira para prevenir duplicações
        tx_id = str(uuid.uuid4())
        print("Cuenta de Origen: ")
        origin_account = input()
        print("Cuenta de Destio: ")
        destination_account = input()
        print("Cantidad: ")
        amount = input()
        print("Moneda: ")
        currency = input()
        
        nonce = str(uuid.uuid4())
        timestamp = str(time.time())

        # Monta o corpo da mensagem em formato JSON
        datos = json.dumps({
            'tx_id': tx_id,
            'origin_account': origin_account,
            'destination_account': destination_account,
            'amount': float(amount),
            'currency': currency,
            'timestamp': float(timestamp)
        }).encode('utf-8')

        # Assina o corpo JSON + nonce + timestamp
        mensagem_para_assinar = datos + b"|" + nonce.encode('utf-8') + b"|" + timestamp.encode('utf-8')
        headers = {
            "Content-Type": "application/json",
            "X-Signature": hasher.crear_hash_signature(mensagem_para_assinar, secret_key),
            "X-Nonce": nonce,
            "X-Timestamp": timestamp
        }

        # O urllib injetará automaticamente o cabeçalho 'Cookie: session_id=...'
        req_transferencia = urllib.request.Request(
            transfer_URL, data=datos, headers=headers, method='POST'
        )
        try:
            with urllib.request.urlopen(req_transferencia) as resposta:
                print("Respuesta Transferencia:", resposta.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            mensaje_error = e.read().decode('utf-8')
            print(f"Error en transferencia ({e.code}): {mensaje_error}")
        except Exception as e:
            print("Error en transferencia:", e)

    # --------------------------------------------------------------------------
    # COMANDO: LOGOUT (Invalida a sessão no servidor e limpa os cookies locais)
    # --------------------------------------------------------------------------
    elif console_text == "logout":
        if len(cookies) == 0:
            print("Nenhuma sessão ativa. Faça login primeiro.")
            continue

        datos = b"logout=1"
        nonce = str(uuid.uuid4())
        timestamp = str(time.time())
        mensagem_para_assinar = datos + b"|" + nonce.encode("utf-8") + b"|" + timestamp.encode("utf-8")
        headers = {
            "X-Signature": hasher.crear_hash_signature(mensagem_para_assinar, secret_key),
            "X-Nonce": nonce,
            "X-Timestamp": timestamp,
        }
        req_logout = urllib.request.Request(
            logout_URL, data=datos, headers=headers, method="POST"
        )
        try:
            with urllib.request.urlopen(req_logout) as resposta:
                print("Respuesta Logout:", resposta.read().decode("utf-8"))
                # Limpa o repositório local de cookies após confirmação do servidor
                cookies.clear()
        except urllib.error.HTTPError as e:
            mensaje_error = e.read().decode("utf-8")
            print(f"Error en logout ({e.code}): {mensaje_error}")
        except Exception as e:
            print("Error en logout:", e)

    # --------------------------------------------------------------------------
    # COMANDO: EXIT (Encerra o cliente)
    # --------------------------------------------------------------------------
    elif console_text == "exit":
        print("Bye bye!")
        break

    console_text = None