#!/bin/bash
# ==============================================================================
# PROYECTO PAI-3: BASTIONADO DE NAVEGADOR WEB (FIREFOX ESR)
# EQUIPO AUDITOR: GRUPO 3 (INSEGUS / UNIVERSIDAD U-SECURE)
# ==============================================================================
# Aplica directivas corporativas rigurosas en Firefox mediante policies.json:
# - HTTPS-Only Mode forzado
# - Bloqueo de extensiones no autorizadas y no firmadas (ExtensionSettings)
# - Restricción estricta de cookies de terceros (reject-foreign)
# - DNS over HTTPS (DoH Cloudflare cifrado)
# - Desactivación de Telemetría y gestor de contraseñas (anti-InfoStealers)
# - Desactivación de WebRTC (anti-fuga de IP local)
# ==============================================================================

set -e

echo "[+] 1. Creando directorios de directivas corporativas..."
mkdir -p /etc/firefox/policies
mkdir -p /usr/share/firefox-esr/distribution
mkdir -p /usr/lib/firefox-esr/distribution

echo "[+] 2. Generando policies.json corporativo..."
cat << 'EOF' > /etc/firefox/policies/policies.json
{
  "policies": {
    "DisableTelemetry": true,
    "DisableFirefoxStudies": true,
    "DisablePocket": true,
    "DisableFeedbackCommands": true,
    "DisableSystemAddonUpdate": true,
    "DisableSetDesktopBackground": true,
    "OfferToSaveLogins": false,
    "PasswordManagerEnabled": false,
    "PrimaryPassword": false,
    "PromptForDownloadLocation": true,
    "NetworkPrediction": false,
    "DNSOverHTTPS": {
      "Enabled": true,
      "ProviderURL": "https://cloudflare-dns.com/dns-query",
      "Locked": true
    },
    "HttpsOnlyMode": "force_enabled",
    "ExtensionSettings": {
      "*": {
        "installation_mode": "blocked",
        "blocked_install_message": "Instalación de extensiones bloqueada por directiva corporativa de U-Secure. Solo se permiten complementos oficiales homologados y firmados."
      }
    },
    "InstallAddonsPermission": {
      "Default": false
    },
    "EnableTrackingProtection": {
      "Value": true,
      "Locked": true,
      "Cryptomining": true,
      "Fingerprinting": true,
      "EmailTracking": true
    },
    "Cookies": {
      "Behavior": "reject-foreign",
      "Locked": true
    },
    "SanitizeOnShutdown": {
      "Cache": true,
      "Cookies": false,
      "History": false,
      "Sessions": false,
      "SiteSettings": false,
      "Locked": true
    },
    "Preferences": {
      "xpinstall.signatures.required": {
        "Value": true,
        "Status": "locked"
      },
      "media.peerconnection.enabled": {
        "Value": false,
        "Status": "locked"
      },
      "privacy.firstparty.isolate": {
        "Value": true,
        "Status": "locked"
      },
      "geo.enabled": {
        "Value": false,
        "Status": "locked"
      },
      "dom.battery.enabled": {
        "Value": false,
        "Status": "locked"
      }
    }
  }
}
EOF

# Copia a las carpetas de distribucion de Firefox-ESR en Kali Linux / Debian / Ubuntu
cp /etc/firefox/policies/policies.json /usr/share/firefox-esr/distribution/policies.json
cp /etc/firefox/policies/policies.json /usr/lib/firefox-esr/distribution/policies.json 2>/dev/null || true

echo "[+] 3. Asignando permisos restringidos..."
chmod 644 /etc/firefox/policies/policies.json
chmod 644 /usr/share/firefox-esr/distribution/policies.json

echo "[+] ¡Directivas de Firefox aplicadas con éxito!"
echo "[+] Abra Firefox y acceda a 'about:policies' para verificar las reglas activas."
