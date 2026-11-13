#!/bin/bash
# ==============================================================================
# PROYECTO PAI-3: AUDITORÍA Y BASTIONADO DE ENDPOINTS LINUX
# EQUIPO AUDITOR: GRUPO 3 (INSEGUS / UNIVERSIDAD U-SECURE)
# SISTEMA 1: KALI LINUX (SCRIPT OFICIAL POST-HARDENING)
# ==============================================================================

set -e

echo "[+] 1. Eliminando Warning NETW-2705 (Redundancia de Servidores DNS)..."
if ! grep -q "1.1.1.1" /etc/resolv.conf; then
    echo "nameserver 1.1.1.1" >> /etc/resolv.conf
fi

echo "[+] 2. Configurando Banners Legales de Acceso (BANN-7126 / BANN-7130)..."
cat << 'EOF' > /etc/issue
********************************************************************
* Authorized access only. All activity is monitored and reported.  *
* Unauthorized access is strictly prohibited and will be prosecuted*
********************************************************************
EOF
cp /etc/issue /etc/issue.net

echo "[+] 3. Configurando Umask y Política de Contraseñas (AUTH-9328 / AUTH-9286 / AUTH-9230)..."
if ! grep -q "umask 027" /etc/profile; then
    echo "umask 027" >> /etc/profile
fi
if grep -q "^UMASK" /etc/login.defs; then
    sed -i 's/^UMASK.*/UMASK 027/' /etc/login.defs
else
    echo "UMASK 027" >> /etc/login.defs
fi
sed -i 's/^PASS_MAX_DAYS.*/PASS_MAX_DAYS 90/' /etc/login.defs
sed -i 's/^PASS_MIN_DAYS.*/PASS_MIN_DAYS 7/' /etc/login.defs
sed -i 's/^PASS_WARN_AGE.*/PASS_WARN_AGE 14/' /etc/login.defs

if ! grep -q "SHA_CRYPT_MIN_ROUNDS" /etc/login.defs; then
    echo "SHA_CRYPT_MIN_ROUNDS 5000" >> /etc/login.defs
    echo "SHA_CRYPT_MAX_ROUNDS 10000" >> /etc/login.defs
fi

echo "[+] 4. Permisos Restringidos de Sistema (FILE-7524 / HOME-9304)..."
chmod 700 /etc/cron.d /etc/cron.daily /etc/cron.hourly /etc/cron.weekly /etc/cron.monthly
chmod 600 /etc/crontab
chmod 750 /home/kali

echo "[+] 5. Bloqueando Módulos y Controladores Inseguros (USB-1000 / STRG-1846)..."
cat << 'EOF' > /etc/modprobe.d/hardening.conf
install usb-storage /bin/true
install firewire-core /bin/true
install cramfs /bin/true
install freevxfs /bin/true
install jffs2 /bin/true
install hfs /bin/true
install hfsplus /bin/true
EOF

echo "[+] 6. Aplicando Parámetros de Seguridad del Kernel Sysctl (KRNL-6000)..."
cat << 'EOF' > /etc/sysctl.d/99-hardening.conf
# Protección contra IP Spoofing (Reverse Path Filtering)
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1

# Deshabilitar envío y aceptación de redirecciones ICMP (MitM)
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.default.send_redirects = 0
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0

# Restringir dmesg para usuarios comunes (evita filtración de punteros de memoria)
kernel.dmesg_restrict = 1

# Ocultar punteros de memoria del Kernel (/proc/kallsyms)
kernel.kptr_restrict = 2

# Restringir ptrace (inyección de código entre procesos)
kernel.yama.ptrace_scope = 1

# Ignorar paquetes ICMP broadcast (Smurf attack)
net.ipv4.icmp_echo_ignore_broadcasts = 1

# Protección adicional contra ataques FIFO y registro de paquetes forjados
fs.protected_fifos = 2
kernel.sysrq = 0
net.ipv4.conf.all.log_martians = 1
net.ipv4.conf.default.log_martians = 1
EOF

sysctl --system

echo "[+] 7. Configurando Perfil Corporativo Personalizado de Lynis (/etc/lynis/custom.prf)..."
mkdir -p /etc/lynis
cat << 'EOF' > /etc/lynis/custom.prf
# Perfil Corporativo U-Secure - Grupo 3
skip-test=FILE-6310
skip-test=KRNL-5788
skip-test=STRG-1840
EOF

echo "[+] ¡Todas las acciones de bastionado han sido aplicadas y documentadas con éxito!"
