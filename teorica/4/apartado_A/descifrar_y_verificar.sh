#!/usr/bin/env bash
# Script automatizado de descifrado y verificación de integridad para el Apartado a)
# Security Team 3 - ETSII Universidad de Sevilla

set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KEY="0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
IV="fedcba9876543210fedcba9876543210"

echo "========================================================================"
echo "[Security Team 3] INICIANDO PROCESO DE DESCIFRADO Y VERIFICACIÓN"
echo "========================================================================"

mkdir -p "$DIR/descifrados"

decrypt_and_check() {
    local alg_name="$1"
    local openssl_alg="$2"
    local enc_file="$3"
    local orig_file="$4"
    local out_file="$DIR/descifrados/$(basename "$enc_file" .enc)_recuperado.bmp"
    
    echo -n "[*] Descifrando $(basename "$enc_file") con $alg_name... "
    openssl enc "$openssl_alg" -d -in "$enc_file" -out "$out_file" -K "$KEY" -iv "$IV"
    
    local orig_hash=$(sha256sum "$orig_file" | awk '{print $1}')
    local dec_hash=$(sha256sum "$out_file" | awk '{print $1}')
    
    if [ "$orig_hash" == "$dec_hash" ]; then
        echo -e "\033[0;32m[OK - INTEGRIDAD VERIFICADA]\033[0m"
        echo "    SHA-256: $dec_hash"
    else
        echo -e "\033[0;31m[ERROR - CORRUPCIÓN DETECTADA]\033[0m"
        exit 1
    fi
}

echo "--- DESCIFRADO TAMAÑO 1 (< 1000 KB: 500 KB) ---"
decrypt_and_check "AES-256-CBC" "-aes-256-cbc" "$DIR/radiografia_tamano1_500KB_aes256cbc.enc" "$DIR/radiografia_tamano1_500KB.bmp"
decrypt_and_check "ChaCha20" "-chacha20" "$DIR/radiografia_tamano1_500KB_chacha20.enc" "$DIR/radiografia_tamano1_500KB.bmp"
decrypt_and_check "Camellia-256-CBC" "-camellia-256-cbc" "$DIR/radiografia_tamano1_500KB_camellia256cbc.enc" "$DIR/radiografia_tamano1_500KB.bmp"

echo ""
echo "--- DESCIFRADO TAMAÑO 2 (> 1000 KB: 1500 KB) ---"
decrypt_and_check "AES-256-CBC" "-aes-256-cbc" "$DIR/radiografia_tamano2_1500KB_aes256cbc.enc" "$DIR/radiografia_tamano2_1500KB.bmp"
decrypt_and_check "ChaCha20" "-chacha20" "$DIR/radiografia_tamano2_1500KB_chacha20.enc" "$DIR/radiografia_tamano2_1500KB.bmp"
decrypt_and_check "Camellia-256-CBC" "-camellia-256-cbc" "$DIR/radiografia_tamano2_1500KB_camellia256cbc.enc" "$DIR/radiografia_tamano2_1500KB.bmp"

echo ""
echo "========================================================================"
echo "[ÉXITO] Todos los ficheros han sido descifrados e integrados al 100%."
echo "========================================================================"
