# 🎓 GUIA DE APRESENTAÇÃO E DEFESA ORAL (ROTEIRO DE ALTA PERFORMANCE)
## Projeto BYODSEC: Road Warrior VPN SSL/TLS 1.3 con mTLS
**Universidad de Sevilla — E.T.S. Ingeniería Informática**  
**Asignatura:** Seguridad en Sistemas Informáticos y en Internet (PAI 2)  
**Equipo:** Security Team 3 (Grupo 3)  
**Calificación Objetivo:** Sobresaliente / Matrícula de Honor (Grade A - 100% Requisitos)

---

## ⏱️ Cronograma Minuto a Minuto (Pitch de 10 Minutos)

| Tempo | Seção | Objetivo Principal | Recurso Visual / Demonstração |
| :---: | :--- | :--- | :--- |
| **00:00 - 01:30** | **1. O Problema Real do BYOD** | Mostrar por que o teletrabalho sem segurança mTLS expõe a universidade ao colapso. | Slide 1 / Diagrama 1 (Topologia) |
| **01:30 - 03:30** | **2. A Arquitetura em Duas Camadas** | Explicar a separação: Transporte (Dispositivo) vs Aplicação (Pessoa). | Diagrama 2 (Handshake TLS 1.3) |
| **03:30 - 06:30** | **3. Demonstração Prática ao Vivo** | Executar os 3 testes capitais (Ataque sem cert, Ataque Rogue CA e Conexão Legítima com RBAC). | Terminal Kali Linux vs Windows Server |
| **06:30 - 08:30** | **4. Criptoanálise & Benchmark** | Provar matematicamente a invulnerabilidade (Hashcat) e estabilidade com 300 sessões. | Tabela de Benchmark & Hashcat |
| **08:30 - 10:00** | **5. Conclusão & Conformidade Legal** | Fechar com conformidade legal (RGPD, ENS e NIST SP 800-113). | Slide Final / Pergunta da Banca |

---

## 🎙️ Script de Apresentação (O que Falar em Cada Momento)

### 1. Introdução: O Contexto e a Falha dos Modelos Tradicionais (00:00 - 01:30)
> *"Bom dia a todos os membros da banca avaliadora e colegas. Hoje apresentamos o projeto BYODSEC, desenvolvido pelo Security Team 3.*  
> *Com a expansão do teletrabalho, professores (PDI), técnicos (PTGAS) e pesquisadores passaram a acessar sistemas acadêmicos confidenciais a partir de seus computadores pessoais em redes públicas e domésticas desprotegidas.*  
> *O modelo clássico de VPN comercial depende exclusivamente de **usuário e senha**. No mundo corporativo atual, isso é insuficiente: se um docente cair em um phishing ou reutilizar uma senha vazada, a rede interna da universidade é imediatamente comprometida.*  
> *A nossa missão foi projetar uma pasarela Road Warrior de segurança máxima que implementa **Zero Trust**: nós nunca confiamos na rede, nunca confiamos em senhas isoladas, e exigimos validação criptográfica bidirecional de ponta a ponta."*

---

### 2. A Solução: Arquitetura em Duas Camadas e TLS 1.3 Estrito (01:30 - 03:30)
*(Mostre o Diagrama 1 e o Diagrama 2 na tela)*

> *"Para solucionar esse desafio de forma irrevogável, adotamos três decisões de engenharia de segurança:*  
> 1. * **TLS 1.3 Nativo e Estrito (RS2):** Desabilitamos por completo SSLv3, TLS 1.0, 1.1 e 1.2. Isso elimina ataques históricos de downgrade como POODLE e garante suítes autenticadas com AEAD (`TLS_AES_256_GCM_SHA384`) e curvas modernas Curve25519 para Secreto Perfeito para a Frente (PFS).*  
> 2. * **Portão 1 - Autenticação Mutua no Transporte (mTLS - RF1/RS1):** Implementamos nossa própria Autoridade Certificadora Raiz institucional (*U-Secure Root CA v1.3*). A pasarela exige `ssl.CERT_REQUIRED`. Nenhum pacote de dados é aceito se o computador não apresentar um certificado digital X.509 v3 assinado pela universidade.*  
> 3. * **Portão 2 - Autenticação de Usuário e Device Binding (RF2):** Uma vez aberto o túnel criptografado, o usuário precisa autenticar com sua senha, protegida com **PBKDF2-HMAC-SHA256 e 600.000 iterações**. Além disso, o servidor verifica em tempo constante se o dono do certificado é exatamente a mesma pessoa que fez login, impedindo usurpação de identidade."*

---

### 3. Demonstração ao Vivo no Terminal (03:30 - 06:30)
*(Este é o momento de maior impacto. Mostre a tela dividida: Kali Linux de um lado, Servidor Windows do outro)*

#### Passo 1: O Reconhecimento com Nmap
* Execute no Kali:
  ```bash
  nmap -p 8443 --script ssl-enum-ciphers vpn.usecure.edu.es
  ```
* **Fala:** *"Observem o escaneamento do Nmap: o servidor responde apenas com TLS 1.3, classificação máxima A e curvas elípticas modernas. Nenhuma versão antiga é aceita."*

#### Passo 2: O Ataque Sem Certificado (O Intruso Comum)
* Execute no Kali:
  ```bash
  openssl s_client -connect vpn.usecure.edu.es:8443 -tls1_3
  ```
* **Fala:** *"Um atacante tenta se conectar sem o certificado do dispositivo. O servidor Windows corta a conexão instantaneamente no handshake com o alerta fatal número 116 (`certificate required`). O atacante não consegue trocar 1 byte de dados."*

#### Passo 3: O Ataque com Certificado Falso (Rogue CA)
* Execute no Kali:
  ```bash
  openssl s_client -connect vpn.usecure.edu.es:8443 -tls1_3 -cert hacker.crt -key hacker.key
  ```
* **Fala:** *"Mesmo que o atacante crie seu próprio certificado autoassinado, o handshake falha no ato com alerta fatal número 48 (`unknown ca`). Somente a Root CA da universidade tem autoridade criptográfica."*

#### Passo 4: Conexão Legítima e Demonstração de RBAC
* Execute no Kali:
  ```bash
  python3 vpn_client.py --user carmen_pdi --host 192.168.1.21
  ```
* Digite a senha: `CarmenSecurePass2026!#PDI`
* Selecione a opção **`[1] Webmail`**: *"Vemos a caixa postal interna do PDI com e-mails reais."*
* Selecione a opção **`[3] Sistemas Administrativos (PTGAS)`**:
  * **O Terminal responderá:** `403 Forbidden: El rol 'PDI' no tiene privilegios para acceder a este servicio.`
* **Fala:** *"Vejam este ponto crucial: mesmo autenticada e com certificado válido, a professora Carmen não pode ver a folha de pagamento administrativa. O sistema aplica Controle de Acesso Baseado em Perfis (RBAC) com isolamento estrito."*
* Selecione **`[6] Desconectar`**:
* **Fala:** *"O desmonte é seguro (RF4): o IP virtual `10.8.0.10` é devolvido ao pool e as chaves de sessão efêmeras são imediatamente destruídas da memória RAM."*

---

### 4. Criptoanálise com Hashcat e Teste de Carga de 300 Usuários (06:30 - 08:30)
*(Apresente as tabelas do relatório)*

1. **Auditoria com Hashcat:**
   > *"No módulo CAI 1, comprovamos que chaves fracas de 32 bits eram quebradas em 1 hora e 10 minutos pelo Hashcat. No nosso projeto PAI 2, graças ao PBKDF2 com 600.000 iterações e sal de 128 bits, seriam necessários **3,8 × 10¹⁴ anos** em um cluster GPU moderno. Mas o ponto fundamental de arquitetura é: **mesmo que a senha fosse descoberta, o atacante ainda não entraria**, porque precisaria fisicamente da chave privada RSA de 2048 bits do notebook do usuário."*
2. **Benchmark de Carga com 300 Sessões Simultâneas (RS3):**
   > *"Submetemos o gateway a um teste de estresse real com 300 conexões concorrentes. A taxa de sucesso foi de **100% (0 quedas)**, com consumo moderado de CPU (estabilizado em 24%) e alocação de memória de apenas 120 KB por sessão TLS, comprovando a escalabilidade para toda a comunidade universitária."*

---

### 5. Conclusão e Fechamento (08:30 - 10:00)
> *"Para concluir, o projeto BYODSEC atende a 100% dos requisitos funcionais e de segurança da disciplina e cumpre as normas do **Esquema Nacional de Seguridad (ENS - RD 311/2022)**, do **RGPD** e do **NIST SP 800-113**.  
> Entregamos o código completo, os scripts de ataque, as trazas PCAP analisadas no Wireshark, a memória técnica em 14 páginas e os diagramas editáveis.  
> Estamos à disposição da banca para responder a quaisquer perguntas. Muito obrigado!"*

---

## 🎯 FAQ da Banca: Respostas Prontas para Perguntas Difíceis

### P1: "Por que vocês desabilitaram o TLS 1.2 e usaram exclusivamente TLS 1.3?"
* **Resposta Técnica:** *"O TLS 1.2 ainda permite algoritmos obsoletos (como RSA key exchange sem PFS e cifras CBC suscetíveis a ataques como Lucky13). O TLS 1.3 removeu completamente esses vetores, reduziu o handshake para apenas 1 Round-Trip Time (1-RTT) e garante nativamente Perfect Forward Secrecy (PFS) e cifras AEAD modernas."*

### P2: "O que acontece se o laptop da professora for roubado?"
* **Resposta Técnica:** *"O sistema possui proteção em duas camadas. Mesmo que o ladrão tenha o computador e o certificado, ele não possui a senha corporativa (que é derivada com PBKDF2 com 600.000 iterações). Além disso, a Root CA institucional pode revogar imediatamente o número de série do certificado através da CRL (Certificate Revocation List), invalidando o acesso antes que qualquer tentativa ocorra."*

### P3: "Por que o Wireshark mostra Application Data de 1.445 bytes durante o handshake se a conexão ainda nem foi autenticada?"
* **Resposta Técnica:** *"Essa é uma das grandes inovações de privacidade do TLS 1.3 (RFC 8446). No TLS 1.2 os certificados eram enviados em texto claro. No TLS 1.3, logo após o `ServerHello`, as chaves efêmeras já são derivadas e as mensagens `EncryptedExtensions`, `Certificate` e `CertificateRequest` viajam criptografadas como registros `Application Data`. Um espião na rede não consegue nem mesmo ler o nome da universidade ou do cliente."*

### P4: "Como o sistema impede um ataque de pasarela falsa (Evil Twin)?"
* **Resposta Técnica:** *"O cliente BYOD possui em seu disco a cópia confiável da Root CA da universidade (`certs/ca.crt`). Se um atacante levantar uma VPN falsa com outro certificado, o cliente detecta a quebra de cadeia de custódia e aborta a conexão antes de transmitir qualquer credencial, emitindo o erro `certificate verify failed`."*

### P5: "Como foi comprovada a imunidade contra Timing Attacks?"
* **Resposta Técnica:** *"Na verificação da senha e na comparação de hashes em `database.py`, utilizamos estritamente a função `secrets.compare_digest`. Ela executa a comparação de strings em tempo computacional constante, independentemente de quantos caracteres estejam certos ou errados, eliminando canais laterais de medição de latência de CPU."*
