#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script Forense de Descifrado y Extracción para Contenedores VeraCrypt
Security Team 3 - E.T.S.I.I. Universidad de Sevilla
"""

import struct
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

def decrypt_veracrypt_volume(vc_path, password, out_img_path):
    print(f"[*] Leyendo contenedor: {vc_path}")
    with open(vc_path, 'rb') as f:
        vc_bytes = f.read()

    header = vc_bytes[:512]
    salt = header[:64]
    enc_header_data = header[64:512]

    print("[*] Derivando clave de cabecera con PBKDF2-HMAC-SHA512 (500.000 iteraciones)...")
    hdr_key = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 500000, dklen=64)

    print("[*] Descifrando cabecera con AES-XTS...")
    hdr_cipher = Cipher(algorithms.AES(hdr_key), modes.XTS(b'\x00' * 16), backend=default_backend())
    dec_header = hdr_cipher.decryptor().update(enc_header_data)

    magic = dec_header[:4]
    if magic != b'VERA':
        raise ValueError(f"Fallo al descifrar cabecera. Magic encontrado: {magic}")
    print(f"[+] Cabecera descifrada correctamente! Magic: {magic.decode('ascii')}")

    # Extraer metadatos
    hdr_ver = struct.unpack('>H', dec_header[4:6])[0]
    prog_ver = struct.unpack('>H', dec_header[6:8])[0]
    data_offset = struct.unpack('>Q', dec_header[44:52])[0]
    data_size = struct.unpack('>Q', dec_header[52:60])[0]
    sector_size = struct.unpack('>I', dec_header[64:68])[0]
    master_key = dec_header[192:192+64]

    print(f"    - Version de cabecera: {hdr_ver}")
    print(f"    - Version de programa: {hex(prog_ver)}")
    print(f"    - Offset de datos: {data_offset} bytes")
    print(f"    - Tamano de datos: {data_size} bytes ({data_size/1024} KB)")
    print(f"    - Tamano de sector: {sector_size} bytes")
    print(f"    - Clave Maestra (MK Hex): {master_key.hex()}")

    num_sectors = data_size // sector_size
    base_sector = data_offset // sector_size
    print(f"[*] Descifrando {num_sectors} sectores XTS-plain64 con sector base {base_sector}...")

    decrypted_img = bytearray()
    for i in range(num_sectors):
        sec_num = base_sector + i
        tweak = struct.pack('<Q', sec_num) + b'\x00' * 8
        c = Cipher(algorithms.AES(master_key), modes.XTS(tweak), backend=default_backend())
        sec_enc = vc_bytes[data_offset + i * sector_size : data_offset + (i + 1) * sector_size]
        decrypted_img.extend(c.decryptor().update(sec_enc))

    with open(out_img_path, 'wb') as f:
        f.write(decrypted_img)
    print(f"[+] Imagen de volumen descifrada guardada en: {out_img_path}")

if __name__ == '__main__':
    decrypt_veracrypt_volume('drive.vc', 'abcd..Hb0167', 'volumen_descifrado.img')
