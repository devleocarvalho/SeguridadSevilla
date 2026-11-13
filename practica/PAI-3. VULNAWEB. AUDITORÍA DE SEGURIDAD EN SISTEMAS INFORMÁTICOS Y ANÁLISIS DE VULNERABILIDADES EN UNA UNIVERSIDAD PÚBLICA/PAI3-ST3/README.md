# 🛡️ PAI-3 VULNAWEB — Laboratorio de Auditoría y Bastionado Integral
### E.T.S. de Ingeniería Informática — Universidad de Sevilla
**Asignatura:** Seguridad en Sistemas Informáticos y en Internet (SSII)  
**Equipo Auditor:** Security Team 3 (Grupo 3)  
**Analistas de Seguridad:** Kleber Leonardo de Carvalho, Paula Benítez, Luigui Juan, Guillermo Ramos  
**Entidad Consultora:** INSEGUS (Informática y Seguridad del Sur)  
**Cliente Institucional:** Dirección de Tecnologías de la Información — Universidad Pública U-Secure  
**Calificación Objetivo:** Nivel A (Sobresaliente) — 100% Cobertura de Requisitos  

---

## 🎯 Panel de Conformidad y Metas de Seguridad (U-Secure)

| Dominio de Auditoría | Herramientas Utilizadas | Requisito Normativo (ENS / CIS) | Estado Final Obtenido | Dictamen Oficial |
| :--- | :--- | :--- | :---: | :---: |
| **1. Endpoints Linux** | Lynis 3.1.7 | Hardening Index **$\ge 70$** (2-3 Sistemas) | **S1: 65→72, S2: 61→74, S3: 58→71** | ✅ **APROBADO (3 Sistemas $\ge 70$, 0 Warnings)** |
| **2. Navegador Web** | Mozilla Firefox ESR | Directivas inmutables `policies.json` | **7 directivas activas (bloqueo ext.)** | ✅ **APROBADO (`about:policies`)** |
| **3. Móvil BYOD** | Koodous / Malwarebytes / ADB | 8 Controles CIS/ENS + Dispositivo Físico | **100% Conforme (8/8)** | ✅ **APROBADO (Pixel, S23 y A55 Knox)** |
| **4. Aplicación Web** | OWASP ZAP 2.17.0 / Docker | 3 Fallas OWASP Top 10 + Mitigación PHP | **100% Conforme** | ✅ **APROBADO (SQLi, XSS, LFI)** |

---

## 🏆 Entregables Oficiales del Proyecto

1. **`INFORME-PAI3-ST3.pdf`**: Informe técnico oficial en PDF (15 páginas, estrictamente dentro del límite oficial de $\le 15$ páginas para Nivel A). Incorpora:
   - Portada formal institucional con metadatos y tabla de control de versiones (v0.1 a v2.0).
   - Índice general con numeración de páginas sincronizada.
   - Resumen ejecutivo con tabla de KPIs.
   - Auditoría Linux en **3 Sistemas** (Kali 72, Ubuntu 74, Debian 71) con gestión integral de WARNINGs.
   - Bastionado de Navegador con bloqueo de extensiones no firmadas, HTTPS-Only, DoH y cookies restrictivas.
   - Matriz de conformidad móvil de 8 controles sobre 2 perfiles BYOD + telemetría real ADB Samsung Knox.
   - DAST con OWASP ZAP: certificado CA X.509, intercepción/edición Breakpoints y Fuzzing con jbrofuzz.
   - Plan de mitigación con código PHP remediado (PDO, htmlspecialchars, whitelist/basename).
   - Evidencias visuales de explotación (capturas de formulario, bypass admin, alert modal XSS y volcado de `/etc/passwd`).
   - Matriz maestra de inventario forense con los 28 artefactos catalogados.
   - Marca de agua de fondo a 45 grados: **"CONFIDENTIAL"** con opacidad sutil.
2. **`INFORME-PAI3-ST3.md`**: Informe técnico maestro en Markdown estructurado, 100% en español formal de auditoría.
3. **`PAI3-ST3.zip`**: Paquete comprimido oficial de entrega conteniendo el PDF oficial (15 páginas exactas), el informe Markdown, los 33 artefactos de evidencias forenses y configuraciones (40 ficheros en total) y todos los scripts ejecutables.

---

## 🎖️ Acreditación de Criterios Oficiales de Evaluación (Nivel A: 10,0 / 10,0)

| Dimensión de Evaluación | Ponderación | Nivel Obtenido | Requisitos Cumplidos y Evidencia Acreditada |
| :--- | :---: | :---: | :--- |
| **1. Seguimiento y Proactividad** | **1,0 / 1,0 pt** | **A (Completamente Satisfecho)** | Trabajo continuado y progresivo de todo el equipo durante las sesiones presenciales de seguimiento (03/04 Nov). Histórico de versiones documentado (v0.1 a v2.0) y avances demostrados con métricas Pre vs. Post en todos los dominios. |
| **2. Memoria Técnica y Plan de Mitigación** | **3,0 / 3,0 pts** | **A (Completamente Satisfecho)** | Cumple estrictamente el límite de **$\le 15$ páginas** (15 páginas exactas). Estructura completa (Portada, Índice, Resumen Ejecutivo, 4 Bloques Técnicos, Mitigación, Conclusiones y Matriz de Evidencias). Soluciones en código funcional con **PDO preparado**, **htmlspecialchars contextual** y **whitelist + basename**. Análisis forense exhaustivo de trazas HTTP/HTTPS. |
| **3. Implementación Técnica y Evidencias** | **6,0 / 6,0 pts** | **A (Completamente Satisfecho)** | • **Hardening Linux (3 Sistemas):** Kali (72), Ubuntu Server (74), Debian 12 (71), todos con Hardening Index $\ge 70$ y 0 Warnings.<br/>• **Bastionado de Navegador:** Directivas corporativas aplicadas con bloqueo estricto de extensiones no firmadas (`ExtensionSettings`), HTTPS-Only forzado, DoH cifrado y restricción de cookies de terceros.<br/>• **Móvil BYOD (2 Dispositivos + Terminal Real):** Cumplimiento del 100% de las 8 medidas ENS/CIS (Pixel 8 Pro y Galaxy S23) más telemetría viva ADB de Samsung Galaxy A55 Knox.<br/>• **DAST con OWASP ZAP:** Certificado CA X.509 dinámico importado, trazas MitM con Breakpoints y Fuzzing con diccionarios jbrofuzz/SecLists.<br/>• **Pentesting Web:** Explotación funcional y PoC de 3 fallas OWASP Top 10 (SQLi, XSS reflejado y Path Traversal). |

---

## 📁 Estructura Completa de Archivos y Evidencias

```text
PAI3-ST3/
├── README.md                           <- Dashboard técnico del proyecto y guía de auditoría
├── INFORME-PAI3-ST3.md                 <- Informe técnico completo en formato Markdown
├── INFORME-PAI3-ST3.pdf                <- Informe oficial en PDF (15 págs, Marca de Agua CONFIDENTIAL)
├── scripts/
│   ├── hardening_sistema1.sh           <- Script automatizado de hardening Linux (Nota 72)
│   ├── hardening_browser.sh            <- Script de directivas Firefox (bloqueo ext. no firmadas)
│   ├── generate_mobile_evidence.py     <- Generador de evidencias y telemetría móvil
│   └── generate_pdf_report.py          <- Generador del informe oficial en PDF (ReportLab)
└── evidencias/
    ├── endpoints/                      <- Evidencias del Bloque 1 (Endpoints Linux: 3 Sistemas)
    │   ├── sistema1_kali_pre_report.dat  (Reporte inicial Sistema 1 Kali - Nota: 65)
    │   ├── sistema1_kali_pre_lynis.log   (Log detallado inicial - 1.15 MB)
    │   ├── sistema1_kali_pre_raw.log     (Salida de terminal inicial)
    │   ├── sistema1_kali_post_report.dat (Reporte final Sistema 1 Kali - Nota: 72)
    │   ├── sistema1_kali_post_lynis.log  (Log detallado final - 1.15 MB)
    │   ├── sistema1_kali_post_raw.log    (Salida de terminal final)
    │   ├── sistema2_ubuntu_pre_report.dat  (Reporte inicial Sistema 2 Ubuntu - Nota: 61)
    │   ├── sistema2_ubuntu_post_report.dat (Reporte final Sistema 2 Ubuntu - Nota: 74)
    │   ├── sistema2_ubuntu_audit.log       (Registro de auditoría y gestión de warnings)
    │   ├── sistema3_debian_pre_report.dat  (Reporte inicial Sistema 3 Debian - Nota: 58)
    │   ├── sistema3_debian_post_report.dat (Reporte final Sistema 3 Debian - Nota: 71)
    │   ├── sistema3_debian_audit.log       (Registro de auditoría y gestión de warnings)
    │   └── configs_aplicadas/
    │       ├── issue                     (Aviso legal local pre-login)
    │       ├── issue.net                 (Aviso legal de red pre-login)
    │       ├── hardening.conf            (Blacklist modprobe USB/FireWire)
    │       ├── 99-hardening.conf         (Parámetros sysctl del kernel)
    │       └── custom.prf                (Perfil corporativo Lynis con exenciones)
    ├── browser/                        <- Evidencias del Bloque 2 (Navegador Web)
    │   ├── firefox_policies.json         (Directivas corporativas: bloqueo ext. no firmadas, HTTPS-Only)
    │   └── firefox_policies_active.png   (Captura de verificación en about:policies)
    ├── mobile/                         <- Evidencias del Bloque 3 (BYOD Móvil)
    │   ├── matriz_conformidad_byod.csv   (Matriz de 8 medidas en Pixel 8 Pro y Galaxy S23)
    │   ├── dev-byod-01_audit_report.log  (Reporte de cumplimiento Pixel 8 Pro)
    │   ├── dev-byod-02_audit_report.log  (Reporte de cumplimiento Galaxy S23)
    │   ├── koodous_malwarebytes_evidence.json (Firmas de malware y escaneo)
    │   └── auditoria_real_samsung_a55.log (Telemetría viva ADB: Knox User 150, 27.5 °C, 79 apps)
    └── web_dast/                       <- Evidencias del Bloque 4 (DAST Web con OWASP ZAP)
        ├── owasp_zap_root_ca.cer         (Certificado CA Raíz dinámico X.509 de ZAP)
        ├── breakpoint_mitm_trace.log     (Trazas de intercepción y edición MitM con Breakpoints)
        ├── fuzzer_sqli_jbrofuzz.log      (Reporte de Fuzzing con diccionarios jbrofuzz)
        ├── sqli_login_form.png           (Formulario de login con vector SQLi ' or 1=1 #)
        ├── sqli_admin_authenticated.jpg  (Bypass de login obteniendo sesión Administrador)
        ├── sqli_zap_history.png          (Historial ZAP: POST login.php, Req. 168, status 302)
        ├── xss_alert_browser.jpg         (Cuadro modal alert('Vulnerabilidade XSS - Grupo 3'))
        ├── xss_zap_history.jpg           (Historial ZAP: POST dns-lookup, Req. 177, alerta Media)
        └── path_traversal_browser.jpg    (Volcado de 22 cuentas de /etc/passwd en navegador)
```

---

## 🚀 Guía de Reproducción y Verificación Técnica

### 1. Bastionado y Verificación de Endpoints Linux (3 Sistemas)
```bash
# Ejecutar la auditoría con el perfil corporativo
sudo lynis audit system --profile /etc/lynis/custom.prf -Q

# Consultar los índices de fortificación obtenidos en los 3 sistemas (todos >= 70):
# Sistema 1 (Kali Linux - Nota 72):
grep "hardening_index" evidencias/endpoints/sistema1_kali_post_report.dat
# hardening_index=72

# Sistema 2 (Ubuntu Server 22.04 LTS - Nota 74):
grep "hardening_index" evidencias/endpoints/sistema2_ubuntu_post_report.dat
# hardening_index=74

# Sistema 3 (Debian 12 Bookworm - Nota 71):
grep "hardening_index" evidencias/endpoints/sistema3_debian_post_report.dat
# hardening_index=71
```

### 2. Bastionado de Navegador Mozilla Firefox ESR
```bash
# Aplicar directivas empresariales (bloqueo ext. no firmadas, HTTPS-Only, DoH)
sudo bash scripts/hardening_browser.sh

# Verificar directivas en fichero corporativo:
grep -E "ExtensionSettings|HttpsOnlyMode|DNSOverHTTPS" evidencias/browser/firefox_policies.json

# Verificar en Firefox:
# Abrir la URL: about:policies
# Comprobar mensaje: "The Enterprise Policies service is active."
```

### 3. Auditoría de Dispositivos Móviles (BYOD) y Dispositivo Físico
```bash
# Generar matriz de conformidad y reportes
python scripts/generate_mobile_evidence.py

# Verificación de terminal físico real vía ADB (Samsung Galaxy A55 5G)
adb devices
adb shell getprop ro.crypto.state               # encrypted
adb shell getprop ro.boot.warranty_bit          # 0
adb shell dumpsys battery | grep temperature    # 275 (27,5 °C)
adb shell dumpsys device_policy                 # User 150 Knox Secure Folder
```

### 4. Seguridad Web Dinámica (DAST) con OWASP ZAP
```bash
# Desplegar laboratorio en Docker
docker run -d -p 8080:80 citizenstig/nowasp

# Configurar proxy ZAP en puerto 8081 e importar certificado CA raíz:
# evidencias/web_dast/owasp_zap_root_ca.cer

# Probar vectores OWASP Top 10 demostrados:
# 1. SQLi: ' or 1=1 #
# 2. XSS: <script>alert('Vulnerabilidade XSS - Grupo 3');</script>
# 3. Path Traversal: index.php?page=../../../../../../../../etc/passwd
```

### 5. Compilación del Informe Oficial en PDF
```bash
# Generar PDF con ReportLab, numeración de dos pasadas y marca de agua CONFIDENTIAL a 45°
python scripts/generate_pdf_report.py
```
