# DEPARTAMENTO DE LENGUAJES Y SISTEMAS INFORMÁTICOS
## E.T.S. INGENIERÍA INFORMÁTICA — UNIVERSIDAD DE SEVILLA
**Asignatura:** Seguridad en Sistemas Informáticos y en Internet  
**Convocatoria:** Curso Académico 2026 / 2027  
**Expediente Técnico:** CAI 2 — Parte 1 (Cifrado de Radiografías y Análisis Forense VeraCrypt)  

---

### METADATOS OFICIALES DEL ENCARGO DE CONSULTORÍA

| Metadato Institucional | Detalle de Registro |
| :--- | :--- |
| **Entidad Destinataria** | Dirección Gerencia, Dirección de Seguridad y CISO — Entidad Hospitalaria |
| **Equipo Auditor Responsable** | **Security Team 3 (Grupo 3)** |
| **Consultores / Analistas** | • **Kleber Leonardo de Carvalho** (Consultor Principal en Criptografía Aplicada)<br>• **Luigui Juan Guillermo Ramos** (Consultor de Seguridad Defensiva y Análisis Forense)<br>• **Paula Benítez** (Consultora de Auditoría y Cumplimiento Normativo) |
| **Fecha de Emisión Oficial** | Octubre de 2026 |
| **Identificador del Entregable** | `ST-3-CAI2A.pdf` (Informe Principal) / `ST-3-CAI2A.zip` (Paquete de Auditoría) |
| **Clasificación del Documento** | **CONFIDENCIAL / USO INTERNO (RESTRICTED TLP:AMBER+)** *(Anexo en TLP:RED)* |
| **Estado de Conformidad** | **Dictamen Favorable — Pruebas Empíricas Superadas y Recuperación Forense 100% Exitosa** |

---

### CONTROL DE VERSIONES DEL DOCUMENTO

| Versión | Fecha | Autor(es) | Resumen de Modificaciones y Alcance |
| :---: | :---: | :---: | :--- |
| **0.1** | 07/10/2026 | Security Team 3 | Análisis de requisitos del sistema hospitalario, marco RGPD/ENS y diseño de pruebas. |
| **0.5** | 08/10/2026 | Security Team 3 | Ensayos de cifrado OpenSSL, análisis de modos/padding y evidencia gráfica en modo ECB. |
| **1.0** | 09/10/2026 | Security Team 3 | Auditoría Hashcat de `drive.vc`, recuperación de clave, montaje FAT12 y redacción final. |

---

## 1. Resumen Ejecutivo

### 1.1. Contexto Operativo y Calificación del Riesgo Legal y Técnico
La entidad hospitalaria auditada opera un complejo asistencial multisede cuyos sistemas transmiten y almacenan datos médicos sin cifrado alguno, tanto en reposo como durante el traslado físico de soportes y comunicación por red interna. Esta deficiencia tipifica un sistema no confiable (*untrustworthy*), conculcando de manera flagrante el **Reglamento General de Protección de Datos (RGPD, Arts. 9 y 32)**, la **Ley Orgánica 3/2018 (LOPDGDD)** y el **Esquema Nacional de Seguridad (ENS - RD 311/2022)**. 

El tratamiento indebido de datos de salud (categoría especial de datos de alta sensibilidad) expone a la entidad a sanciones de la Agencia Española de Protección de Datos (AEPD) de hasta **20 millones de euros o el 4% de su facturación anual global**, además de la paralización de sus servicios y un gravísimo daño reputacional.

### 1.2. Respuesta Sintética a la Consulta a): Cifrado Masivo de Radiografías
1. **Refutación de AES-128-CBC:** Se desaconseja de manera taxativa ceñirse a claves de 128 bits. La custodia de datos de salud debe prolongarse durante décadas (>30 años según la Ley 41/2002 de autonomía del paciente), y el algoritmo cuántico de Grover reduce el espacio efectivo de una clave simétrica de $N$ a $N/2$ bits, degradando AES-128 a solo 64 bits de seguridad efectiva. Al contar los procesadores modernos con aceleración hardware (**Intel AES-NI**), la sobrecarga computacional de migrar a AES-256 es insignificante (inferior a **0.55 ms**).
2. **Ranking Oficial Dictaminado:** 
   * **1º AES-256-CBC:** Máxima solidez criptográfica post-cuántica y compatibilidad estándar con sistemas PACS/DICOM.
   * **2º ChaCha20:** Cifrador de flujo de 256 bits con **0 bytes de overhead espacial** (sin padding) e ideal para terminales móviles y tablets clínicas que carecen de instrucciones dedicadas AES-NI.
   * **3º Camellia-256-CBC:** Cifrador de bloque estándar internacional ISO/IEC, ideal para diversificación criptográfica independiente de AES.
3. **Descarte Crítico de ECB:** Se demuestra pericialmente que el modo *Electronic Codebook* (ECB) fugaría de manera nítida la silueta anatómica del tórax y órganos del paciente, violando el criterio prioritario de confidencialidad absoluta.
4. **Procedimiento Operativo:** Uso de OpenSSL con relleno **PKCS#7**, vector de inicialización (IV) criptográficamente seguro y derivación mediante **PBKDF2 con 100.000 iteraciones** (`-pbkdf2 -iter 100000`). Verificación de integridad garantizada mediante huellas **SHA-256** o cifrado autenticado **AEAD** (AES-GCM / ChaCha20-Poly1305).

### 1.3. Respuesta Sintética a la Consulta b): Seguridad en VeraCrypt y Recuperación Forense
1. **Generación Segura en VeraCrypt:** Implementación de cascadas multicapa (**Serpent-Twofish-AES**), modo sectorial **XTS** (clave doble de 512 bits), multiplicación de iteraciones PBKDF2 fijando **PIM > 1000**, obligatoriedad de **Keyfiles** (archivos de clave de 64 bytes de alta entropía) y uso de **Contenedores Ocultos** (*Hidden Volumes*) para garantizar negación plausible (*plausible deniability*).
2. **Resolución de la Contraseña de `drive.vc`:** A partir del patrón recordado por el cliente, se delimitó el espacio a **52.000 combinaciones posibles**. Mediante un ataque por máscara acelerado por GPU con **Hashcat (modo 29421)** a 513 H/s, se descubrió la contraseña en apenas **48 segundos**:
   $$\mathbf{abcd..Hb0167}$$
3. **Rescate de la Información Confidencial:** Descifrados los 1.536 sectores del volumen formateado en FAT12, se extrajo el archivo confidencial `/TopSecret/calendario-escolar-2026-27.pdf` (67.714 bytes), resguardado en el Anexo Técnico Confidencial.

---

## 2. Consultoría Apartado a): Selección y Evaluación Criptográfica para Radiografías

### 2.1. Análisis Crítico y Refutación de la Propuesta de los Técnicos (AES-128-CBC)
Los técnicos de la entidad hospitalaria propusieron adoptar `AES-128-CBC` bajo el argumento de su "facilidad de uso y eficiencia". El equipo consultor rechaza formalmente esta propuesta por tres fundamentos técnicos insoslayables:

1. **Período de Conservación de Historias Clínicas (Ley 41/2002 y RGPD):** Las radiografías y diagnósticos médicos deben custodiarse entre 20 y 30 años como mínimo tras el alta médica, y mantenerse confidenciales durante toda la vida del paciente. El umbral de seguridad de 128 bits no es viable para ese horizonte temporal ante el avance computacional.
2. **Resistencia Criptoanalítica y Computación Cuántica (Algoritmo de Grover):** La computación cuántica reduce la seguridad de una clave simétrica de $N$ bits a $N/2$ bits. Una clave de 128 bits se reduce a $2^{64}$ operaciones, situándola en el rango de factibilidad de ataque por grandes adversarios. En cambio, **AES-256 conserva un margen post-cuántico de 128 bits ($2^{128}$ operaciones)**, inexpugnable.
3. **Impacto Computacional Residual por AES-NI:** En CPUs modernas (Intel Xeon/Core, AMD EPYC/Ryzen), el cifrado AES se computa por instrucciones integradas en el silicio (AES-NI). Los ensayos empíricos demuestran que la diferencia temporal entre cifrar en 128 bits vs 256 bits es de apenas **0.55 ms** (+10%), un coste computacional totalmente despreciable que no justifica en absoluto reducir la seguridad a la mitad.

### 2.2. Evaluación y Descarte Técnico de Algoritmos Conocidos por el Cliente

| Algoritmo / Modo | Evaluación Técnica y Vulnerabilidades Asociadas | Dictamen Pericial |
| :--- | :--- | :--- |
| **RSA-2048** | Cifrado asimétrico. Estructuralmente restringido a bloques inferiores a la clave (máx. 245 bytes con PKCS#1 v1.5 o 214 bytes con OAEP). Cifrar imágenes de 1.5 MB requeriría miles de exponenciaciones modulares extremadamente lentas, inviabilizando su uso masivo en archivos. | **RECHAZADO TAJANTEMENTE**<br>*(Inviable para masas de datos)* |
| **Blowfish / CAST5** | Cifradores de bloque de 1ª generación con tamaño de bloque de **64 bits (8 bytes)**. Vulnerables al ataque **Sweet32** (colisión por paradoja del cumpleaños tras transferir apenas $\approx 32\text{ GB}$ bajo el mismo contexto). | **RECHAZADO**<br>*(Bloque obsoleto de 64 bits)* |
| **Modo ECB**<br>(`aes-ecb`, `camellia-ecb`, `serpent-ecb`) | *Electronic Codebook*: Cifra cada bloque de 16 bytes de manera autónoma sin vector de inicialización. Bloques idénticos de texto claro generan bloques cifrados idénticos, preservando los contornos y patrones espaciales de la imagen médica. | **RECHAZADO CRÍTICAMENTE**<br>*(Violación flagrante del Criterio 1)* |
| **Modos CFB / OFB** | Modos de realimentación. OFB no admite paralelización en descifrado; CFB propaga errores de canal y ambos presentan rendimientos netamente inferiores frente a CBC y ChaCha20. | **DESACONSEJADO**<br>*(Superado tecnológicamente)* |
| **Serpent-128** | Cifrador con altísimo margen de seguridad pero sin instrucciones de aceleración en hardware en la mayoría de CPUs hospitalarias, ofreciendo menor velocidad que AES. | **SECUNDARIO** |

### 2.3. Demostración Empírica de la Fuga de Información en Modo ECB vs Modo CBC

Para demostrar visualmente y de forma irrefutable al Gerente y al CISO por qué el **Criterio 1 (Garantía de no inteligibilidad por terceros)** veta de forma absoluta el modo ECB (*Electronic Codebook*), el equipo consultor diseñó un ensayo pericial replicable en **Kali Linux** sobre una radiografía torácica clínica (`radiografia_tamano1_500KB.bmp`):

#### 1. Fundamento Técnico de la Vulnerabilidad
El formato BMP (*Bitmap*) almacena los datos de la imagen de forma pura y sin compresión: consta de una **cabecera fija de 54 bytes** (que contiene la firma `BM`, dimensiones de ancho/alto y profundidad de color) seguida inmediatamente por la matriz de píxeles sin comprimir. Al cifrar una radiografía médica (donde grandes regiones anatómicas como los campos pulmonares, huesos o el fondo negro presentan secuencias de píxeles idénticas):
* **En Modo ECB:** Procesa bloques de 16 bytes de forma totalmente independiente sin Vector de Inicialización (IV). Por tanto:
  $$P_i = P_j \implies C_i = C_j$$
  Bloques idénticos de texto plano generan exactamente los mismos bloques cifrados. La correlación espacial de los datos se preserva intacta.
* **En Modo CBC / ChaCha20:** Cada bloque de entrada se combina mediante una operación XOR con el bloque cifrado precedente ($C_i = E_K(P_i \oplus C_{i-1})$). Esto desata el **efecto avalancha**: la modificación de un solo bit en la entrada altera aproximadamente el 50% de los bits del texto cifrado, produciendo ruido estocástico puro sin patrón alguno (entropía $\approx 7.999\text{ bits/byte}$).

#### 2. Procedimiento de Ejecución Forense en Kali Linux
Para hacer visible la fuga de información sin descifrar la clave, se cifró la muestra en ambos modos y se reconstruyó la cabecera BMP estándar de 54 bytes para permitir a los visores de imagen renderizar los datos cifrados:

```bash
# Paso 1: Cifrado en modo inseguro ECB (Electronic Codebook)
openssl enc -aes-256-ecb -e \
  -in radiografia_tamano1_500KB.bmp \
  -out radiografia_ecb.enc \
  -pass pass:"ClaveSecretaHospitalaria" -pbkdf2

# Paso 2: Cifrado en modo seguro CBC (Cipher Block Chaining)
openssl enc -aes-256-cbc -e \
  -in radiografia_tamano1_500KB.bmp \
  -out radiografia_cbc.enc \
  -pass pass:"ClaveSecretaHospitalaria" -pbkdf2

# Paso 3: Extracción pericial de los 54 bytes de la cabecera original BMP
head -c 54 radiografia_tamano1_500KB.bmp > cabecera_bmp.bin

# Paso 4: Reconstrucción de imágenes visuales combinando cabecera y cuerpo cifrado
cat cabecera_bmp.bin radiografia_ecb.enc > evidencia_visual_ecb.bmp
cat cabecera_bmp.bin radiografia_cbc.enc > evidencia_visual_cbc.bmp
```

#### 3. Dictamen Pericial del Resultado Visual
* **Evidencia en `evidencia_visual_ecb.bmp`:** Al abrir la imagen resultante, **la silueta de las costillas, la caja torácica, la clavícula y la silueta cardíaca del paciente se distinguen con total nitidez a simple vista**, así como marcas textuales del equipo de rayos X. Un atacante pasivo en la red hospitalaria obtendría un diagnóstico visual completo sin necesidad de romper la clave criptográfica.
* **Evidencia en `evidencia_visual_cbc.bmp`:** La imagen resultante es una trama estática de ruido blanco sin ningún contorno discernible, certificando el cumplimiento del Criterio 1.

### 2.4. Modos de Bloque, Esquema de Padding y Tamaño de Clave Recomendados
1. **Modo de Operación de Bloque:** **CBC (Cipher Block Chaining)**. Requiere un Vector de Inicialización (IV) de 16 bytes (128 bits) impredecible y generado mediante un generador criptográficamente seguro (CSPRNG).
2. **Esquema de Relleno (Padding):** **PKCS#7 (RFC 5652)**. Añade entre 1 y 16 bytes para alinear el tamaño del archivo al bloque de 128 bits. Al descifrar, el algoritmo valida y retira el relleno estrictamente.
3. **Cifrador de Flujo Alternativo (ChaCha20):** Al ser un cifrador de flujo, **no utiliza padding**. El archivo cifrado tiene exactamente el mismo tamaño en bytes que el original (**0 bytes de sobrecarga espacial**).
4. **Tamaño de Clave:** Claves simétricas de **256 bits (32 bytes)** para los tres algoritmos, alineadas con los esquemas del NIST y el Esquema Nacional de Seguridad (ENS).

### 2.5. Especificación Técnica de Procedimientos en OpenSSL y Parámetros Seguros

Para garantizar la máxima robustez operativa, los comandos oficiales son los siguientes:

```bash
# 1. Cifrado con AES-256-CBC (Derivación PBKDF2 robusta con 100.000 rondas y Salt CSPRNG)
openssl enc -aes-256-cbc -e -in radiografia.bmp -out radiografia_aes.enc \
  -pass pass:"ClaveMaestraHospitalaria2026!#" -pbkdf2 -iter 100000

# 2. Cifrado con ChaCha20 (Cifrador de flujo de 256 bits con 0 bytes de overhead espacial)
openssl enc -chacha20 -e -in radiografia.bmp -out radiografia_chacha.enc \
  -pass pass:"ClaveMaestraHospitalaria2026!#" -pbkdf2 -iter 100000

# 3. Cifrado con Camellia-256-CBC (Cifrador de bloque estándar ISO/IEC 18033-3)
openssl enc -camellia-256-cbc -e -in radiografia.bmp -out radiografia_camellia.enc \
  -pass pass:"ClaveMaestraHospitalaria2026!#" -pbkdf2 -iter 100000

# Descifrado y recuperación íntegra del archivo original
openssl enc -aes-256-cbc -d -in radiografia_aes.enc -out radiografia_recuperada.bmp \
  -pass pass:"ClaveMaestraHospitalaria2026!#" -pbkdf2 -iter 100000
```

> **Justificación de Parámetros de Seguridad:**
> * `-pbkdf2`: Fuerza la función de derivación basada en contraseña estándar (RFC 8018), suprimiendo el algoritmo legado vulnerable de OpenSSL (EVP KDF).
> * `-iter 100000`: Eleva a 100.000 las rondas de HMAC-SHA256, frenando ataques de fuerza bruta mediante diccionarios.
> * **Salt Aleatorio:** OpenSSL antepone automáticamente 8 bytes de salt (`Salted__...`), neutralizando por completo el uso de *Rainbow Tables*.

### 2.6. Metodología de Comprobación de Integridad y Autenticidad de los Ficheros

1. **Nivel 1 — Verificación por Hash Criptográfico (SHA-256):**
   Antes de transmitir el archivo, el emisor genera la huella digital:
   ```bash
   sha256sum radiografia.bmp > control_integridad.sha256
   ```
   En la estación médica receptora, tras el descifrado, se comprueba:
   ```bash
   sha256sum -c control_integridad.sha256
   # Respuesta esperada: radiografia.bmp: OK
   ```

   **Evidencia Pericial Real Obtenida en el Laboratorio (Kali Linux):**
   ```text
   $ sha256sum radiografia_tamano1_500KB.bmp
   aa167dcae3e34e36cf438f6449272c3ee9496c3d930121f1ac26658507e61687  radiografia_tamano1_500KB.bmp

   $ sha256sum recuperada.bmp
   aa167dcae3e34e36cf438f6449272c3ee9496c3d930121f1ac26658507e61687  recuperada.bmp

   --> DICTAMEN FORENSE: Coincidencia bit a bit al 100%. Integridad certificada matemáticamente.
   ```

2. **Nivel 2 — Cifrado Autenticado AEAD (Recomendación Avanzada):**
   Para entornos de producción se recomienda evolucionar a esquemas **AEAD (Authenticated Encryption with Associated Data)** como **AES-256-GCM** o **ChaCha20-Poly1305**. Estos esquemas integran una etiqueta de autenticación (*Authentication Tag* de 128 bits). Si un atacante modifica un solo bit del archivo en tránsito, la rutina de descifrado aborta instantáneamente, impidiendo que datos corrompidos lleguen al facultativo.

---

## 3. Diseño Experimental, Resultados Empíricos y Ranking de Preferencias

### 3.1. Caracterización del Parque Radiológico Hospitalario
A partir de la gráfica de distribución de la entidad hospitalaria, se modela el volumen de radiografías digitales:

* **100 KB (18%):** Odontología y radiología simple.
* **500 KB (24%):** Extremidades y tórax simple (**MUESTRA TAMAÑO 1: < 1000 KB**).
* **1000 KB (46%):** Estudios torácicos de resolución media.
* **1500 KB (12%):** Tomografías y escáneres de alta definición (**MUESTRA TAMAÑO 2: > 1000 KB**).

Se eligen dos muestras reales de ensayo:
* **Tamaño 1 (< 1000 KB):** Muestra clínica de 500 KB (512.174 bytes = 0.4884 MB).
* **Tamaño 2 (> 1000 KB):** Muestra clínica de 1500 KB (1.536.000 bytes = 1.4648 MB).

### 3.2. Pruebas Experimentales y Tablas Oficiales de Rendimiento

A continuación se presentan las mediciones empíricas obtenidas directamente en el entorno de auditoría **Kali Linux**, contrastando el comportamiento de los tres algoritmos candidatos frente a la propuesta base de los técnicos:

#### 1. Telemetría Pericial en Tiempo Real (Consola Kali Linux)
```text
[Ensayo Cifrado Tamaño 1 - 500 KB]
- AES-256-CBC:      real 0.01s (user 0.00s, sys 0.01s, cpu 86%)  --> ~10 ms
- ChaCha20:         real 0.01s (user 0.00s, sys 0.00s, cpu 92%)  --> ~10 ms
- Camellia-256-CBC: real 0.01s (user 0.01s, sys 0.01s, cpu 92%)  --> ~10 ms
- Base AES-128-CBC: real 0.01s (user 0.00s, sys 0.00s, cpu 92%)  --> ~10 ms

[Ensayo Cifrado Tamaño 2 - 1500 KB]
- AES-256-CBC:      real 0.01s (user 0.00s, sys 0.00s, cpu 95%)  --> ~10 ms
- ChaCha20:         real 0.01s (user 0.00s, sys 0.00s, cpu 95%)  --> ~10 ms
- Camellia-256-CBC: real 0.02s (user 0.02s, sys 0.00s, cpu 97%)  --> ~20 ms (EL DOBLE)
- Base AES-128-CBC: real 0.01s (user 0.00s, sys 0.00s, cpu 96%)  --> ~10 ms

[Ensayo Descifrado Tamaño 1 - 500 KB]
- AES-256-CBC:      real 0.01s (user 0.00s, sys 0.00s, cpu 92%)  --> ~10 ms
- ChaCha20:         real 0.00s (user 0.00s, sys 0.00s, cpu 94%)  --> < 5 ms (MÁXIMA EFICIENCIA)
- Camellia-256-CBC: real 0.01s (user 0.01s, sys 0.00s, cpu 97%)  --> ~10 ms
```

#### TABLA 1: EXPERIMENTOS DE CIFRADO (Medias Consolidadas)

| Tamaño de Imagen | Alg1: AES-256-CBC (ms) | Alg1: AES-256-CBC (MB) | Alg2: ChaCha20 (ms) | Alg2: ChaCha20 (MB) | Alg3: Camellia-256-CBC (ms) | Alg3: Camellia-256-CBC (MB) | Alg. Base: AES-128-CBC (ms) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Tamaño 1** (< 1000 KB / 500 KB) | 4.46 ms (~0.01s) | 0.4884 MB | 4.52 ms (~0.01s) | 0.4884 MB | 7.69 ms (~0.01s) | 0.4884 MB | 3.97 ms (~0.01s) |
| **Tamaño 2** (> 1000 KB / 1500 KB) | 5.61 ms (~0.01s) | 1.4649 MB | 4.91 ms (~0.01s) | 1.4648 MB | 13.15 ms (~0.02s) | 1.4649 MB | 5.06 ms (~0.01s) |

#### TABLA 2: EXPERIMENTOS DE DESCIFRADO

| Tamaño de Imagen | Alg1: AES-256-CBC (ms) | Alg1: AES-256-CBC (MB) | Alg2: ChaCha20 (ms) | Alg2: ChaCha20 (MB) | Alg3: Camellia-256-CBC (ms) | Alg3: Camellia-256-CBC (MB) | Alg. Base: AES-128-CBC (ms) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Tamaño 1** (< 1000 KB / 500 KB) | 3.93 ms (~0.01s) | 0.4884 MB | 0.00s (< 5 ms) | 0.4884 MB | 7.95 ms (~0.01s) | 0.4884 MB | 3.86 ms (~0.01s) |
| **Tamaño 2** (> 1000 KB / 1500 KB) | 4.89 ms (~0.01s) | 1.4648 MB | 6.18 ms (~0.01s) | 1.4648 MB | 12.82 ms (~0.02s) | 1.4648 MB | 5.39 ms (~0.01s) |

#### Análisis de Complejidad Temporal y Espacial:
* **Complejidad Temporal:** Los resultados en Kali Linux corroboran la hipótesis inicial: tanto `AES-256-CBC` como `ChaCha20` procesan el archivo pesado en apenas 0.01s (10 ms), idéntico a AES-128. En la rutina de descifrado, `ChaCha20` sobresale registrando **0.00s (< 5 ms)** gracias a su diseño de flujo simétrico optimizado en registros de CPU. En contraste, `Camellia-256-CBC` tarda el doble (0.02s / ~13-20 ms) en el fichero de 1500 KB al no beneficiarse de instrucciones aceleradas por hardware en el silicio.
* **Complejidad Espacial:**
  * **ChaCha20:** **0 bytes de overhead espacial**. Mantiene el tamaño idéntico al original al ser un cifrador de flujo sin padding.
  * **AES-256-CBC y Camellia-256-CBC:** Añaden de 2 a 16 bytes de relleno PKCS#7 (+0.001% en 1500 KB), con impacto nulo en el almacenamiento hospitalario.

### 3.3. Ranking Oficial de Preferencias Justificado

| Posición | Algoritmo Seleccionado | Dictamen y Justificación Criptográfica |
| :---: | :---: | :--- |
| **1º** | **AES-256-CBC** | **RECOMENDACIÓN PRINCIPAL.** Máxima solidez post-cuántica a largo plazo (>30 años), aceleración por hardware nativa en servidores (Intel/AMD AES-NI) y compatibilidad absoluta con el estándar médico PACS/DICOM. |
| **2º** | **ChaCha20** | **SEGUNDA PREFERENCIA (Ideal para Movilidad).** Complejidad espacial perfecta (+0 bytes de sobrecarga), inmune a ataques de canal lateral por tiempos de tabla y altísima velocidad en tablets clínicas y dispositivos móviles sin AES-NI. |
| **3º** | **Camellia-256-CBC** | **TERCERA PREFERENCIA (Diversidad Criptográfica).** Cifrador estándar ISO/IEC de 256 bits avalado por el proyecto europeo NESSIE, como alternativa independiente a AES ante hipotéticas fallas en su diseño SPN. |

---

## 4. Consultoría Apartado b): Seguridad en VeraCrypt y Proceso Forense

### 4.1. Directrices de Ingeniería para Contenedores VeraCrypt de Máxima Seguridad
Para salvaguardar la información de máxima confidencialidad en puestos con Windows 11, se instruye la siguiente configuración:

1. **Cifradores Disponibles:**
   * *Cifradores Simples:* AES (Rijndael, 256 bits), Serpent (256 bits), Twofish (256 bits), Camellia (256 bits), Kuznyechik (256 bits).
   * *Cascadas Multicapa:* Cifrado encadenado con claves independientes:
     * Bicapa: *AES-Twofish*, *Camellia-Kuznyechik*, *Twofish-Serpent*, *Serpent-AES*.
     * Tricapa: **Serpent-Twofish-AES** (máximo nivel de blindaje defensivo concebible).
2. **Modo de Operación Sectorial:** **XTS (IEEE 1619)** con clave doble de 512 bits (256 bits para cifrado y 256 bits para tweak sectorial).
3. **Funciones Hash / PRF de Derivación:** SHA-512 (500.000 iteraciones por defecto), Whirlpool, SHA-256 o Streebog.
4. **Configuración de Máxima Seguridad Recomendada:**
   * **Uso de Cascada (Serpent-Twofish-AES):** Si un algoritmo sufre una debilidad teórica, los datos permanecen blindados por las otras dos capas.
   * **Multiplicación de Iteraciones (PIM > 1000):** Eleva las rondas de PBKDF2 a millones, inutilizando clusters de cracking por GPU.
   * **Uso Obligatorio de Keyfiles:** Archivo de 64 bytes de ruido pseudoaleatorio (CSPRNG) en un token físico USB/FIDO2. Sin él, el atacante ni siquiera puede iniciar el intento de descifrado.
   * **Contenedor Oculto (*Hidden Volume*):** Aporta negación plausible (*plausible deniability*), ocultando el contenedor real dentro del espacio libre de un volumen señuelo.

### 4.2. Auditoría Forense y Proceso de Recuperación del Contenedor `drive.vc`
El Gerente solicitó asistencia pericial para acceder a un contenedor de 1.0 MB (`drive.vc`) cuya contraseña fue extraviada tras crearse con las opciones por defecto de VeraCrypt en Windows 11.

#### 1. Inspección Estructural de la Cabecera
Con el analizador forense de volúmenes se identificó la arquitectura técnica:
```text
VERACRYPT header information for drive.vc:
Version:        5 (Formato estándar VeraCrypt 1.24+)
Sector size:    512 bytes
Volume size:    786432 bytes (768 KB de área útil de datos)
MK offset:      131072 bytes (128 KB de cabecera cifrada)
PBKDF2 hash:    sha512 (500.000 iteraciones por defecto)
Cipher chain:   aes (AES-256) | Cipher mode: xts-plain64 (MK: 512 bits)
```

#### 2. Delimitación Matemática del Espacio de Búsqueda
El cliente recordó la estructura de la contraseña:
* Comienza por: `abcd..H` (7 caracteres literales fijos).
* Siguiente carácter: Una letra del abecedario (`[a-zA-Z]`, 52 posibilidades).
* Siguiente carácter: El dígito cero (`0`, 1 opción fija).
* Tres caracteres finales: 3 dígitos numéricos (`[0-9]{3}`, 1.000 opciones).
* Longitud total: Exactamente **12 caracteres** ($7 + 1 + 1 + 3 = 12$).

El espacio total de combinaciones es críticamente reducido:
$$S = 52 \times 1 \times 1000 = \mathbf{52.000\text{ combinaciones posibles}}$$

#### 3. Auditoría por Fuerza Bruta con Hashcat
Se extrajo la cabecera mediante el script oficial `veracrypt2hashcat.py` y se configuró Hashcat v7.1.2 acelerado por GPU:
* **Modo Hash:** `29421` (VeraCrypt SHA512 + XTS 512 bit, volumen estándar moderno).
* **Modo de Ataque:** `-a 3` (Ataque por máscara).
* **Máscara:** `abcd..H?10?d?d?d` con juego de caracteres personalizado `-1 ?l?u`.

```text
========================= TRAZA DE AUDITORÍA HASHCAT =========================
Session..........: hashcat | Status: Cracked
Hash.Mode........: 29421 (VeraCrypt SHA512 + XTS 512 bit)
Time.Started.....: Fri Oct  9 11:31:07 2026 (48 secs)
Speed.#01........: 513 H/s (GPU: NVIDIA GeForce RTX 3050 Laptop GPU)
Progress.........: 24576/52000 (47.26%)
Contraseña hallada: abcd..Hb0167
==============================================================================
```

> **Dictamen de Vulnerabilidad:**
> La contraseña fue descubierta en **solo 48 segundos** tras evaluar únicamente el 47.26% del espacio. La contraseña legítima de desbloqueo es: **`abcd..Hb0167`**.

### 4.3. Reconstrucción Forense del Volumen, Montaje y Extracción del Contenido
Recuperada la credencial, se desarrolló un script pericial en Python (`script_recuperacion_forense.py`) que opera en espacio de usuario sin requerir controladores de kernel:

1. **Derivación de Clave de Cabecera:** PBKDF2-HMAC-SHA512 con salt de 64 bytes y 500.000 rondas.
2. **Descifrado de Cabecera:** Cabecera de 448 bytes descifrada con AES-XTS, validando la firma mágica `VERA`.
3. **Extracción de la Master Key XTS:** Extraídos los 64 bytes de la clave maestra en el offset 192:
   ```text
   f440cf2b946b29ae45397d48eaba7f42674915ab9f8e511eb6a29e817a964084d776a9546235c8e4920d5cd6b8cc155f156fae459474679e3a632ab77a82bf20
   ```
4. **Descifrado de Sectores XTS:** Descifrado sector a sector de los 1.536 sectores del área de datos (offset 131.072 bytes) con tweak sectorial secuencial base 256 ($\text{sec\_num} = 256 + i$).
5. **Montaje y Extracción FAT12:** Se generó la imagen descifrada `volumen_descifrado.img`. Mediante herramientas de análisis de sistemas de archivos FAT12, se extrajo el archivo confidencial:
   * **Ruta en el contenedor:** `/TopSecret/calendario-escolar-2026-27.pdf`
   * **Tamaño:** 67.714 bytes.
   * **Huella SHA-256:** `0173f85f02f5b6346cf275a2f16a292f263e7f70e0ed1cc5af7b86e644493479`.

---

## 5. Oportunidad de Negocio y Propuesta de Servicios de Continuidad

El incidente diagnosticado revela la urgente necesidad de implementar un modelo de seguridad gestionada en la entidad hospitalaria. El **Security Team 3** presenta su Catálogo de Servicios de Ciberseguridad Sanitaria Avanzada:

| Línea de Servicio | Alcance Técnico y Valor Asistencial |
| :--- | :--- |
| **1. Pasarela Criptográfica DICOM (Crypto-PACS)** | Despliegue de un daemon automatizado para cifrado transparente de radiografías en tránsito y reposo mediante AES-256-GCM. |
| **2. Auditoría y Adecuación ENS y RGPD en Salud** | Certificación de conformidad con el Esquema Nacional de Seguridad (RD 311/2022) y blindaje jurídico ante expedientes de la AEPD. |
| **3. Gestión Centralizada de Secretos y Tokens FIDO2** | Implantación de PKI institucional, contenedores cifrados con Keyfiles en hardware y supresión de contraseñas débiles. |
| **4. CSIRT Hospitalario 24/7 (Respuesta a Incidentes)** | Monitorización continua de incidentes, análisis forense digital y soporte pericial inmediato ante fugas de información clínica. |

---

## 6. Bibliografía y Referencias Normativas

1. **Reglamento General de Protección de Datos (RGPD) — Reglamento (UE) 2016/679.** Artículos 9 (*Categorías especiales de datos*) y 32 (*Seguridad del tratamiento*).
2. **Ley Orgánica 3/2018 (LOPDGDD)** de Protección de Datos Personales y garantía de los derechos digitales.
3. **Ley 41/2002**, de 14 de noviembre, básica reguladora de la autonomía del paciente y de derechos y obligaciones en materia de información y documentación clínica.
4. **Real Decreto 311/2022:** Esquema Nacional de Seguridad (ENS) en el ámbito de la administración pública.
5. **NIST Special Publication 800-38A:** *Recommendation for Block Cipher Modes of Operation*. National Institute of Standards and Technology.
6. **NIST FIPS PUB 197:** *Advanced Encryption Standard (AES)*. Federal Information Processing Standards.
7. **RFC 8439:** *ChaCha20 and Poly1305 for IETF Protocols*. Internet Engineering Task Force.
8. **RFC 5652:** *Cryptographic Message Syntax (CMS) — PKCS#7 Padding Scheme*.
9. **VeraCrypt Documentation:** *VeraCrypt Volume Format Specification & Technical Architecture*. IDRIX, 2026.
10. **HASHCAT Project:** *Advanced Password Recovery Utility v7.1.2*. Jens Steube et al.

---

## 7. ANEXO TÉCNICO CONFIDENCIAL (Apartado b)
**USO ÚNICO Y EXCLUSIVO DE LA DIRECCIÓN GERENCIA Y EQUIPO DE CIBERSEGURIDAD**

> **CLASIFICACIÓN: ESTRICTAMENTE CONFIDENCIAL (TLP:RED).**  
> La información desglosada en este anexo procede de la intervención pericial autorizada sobre los activos cifrados de la entidad hospitalaria. Su divulgación a terceros está expresamente prohibida.

### 7.1. Credenciales y Elementos Criptográficos Recuperados
* **Identificador del Contenedor Auditado:** `drive.vc` (1.048.576 bytes / 1.0 MB en disco).
* **Hash Criptográfico Extraído para Hashcat (Modo 29421):**
  ```text
  $veracrypt$ade9c4a25cb55592ee35521edc09738924f2ce0916abf7eff1de593b887ba3b71e22d3afdeeddc0a0d0afdb66c7af2f9066d4ec396f55ba9d69cf734644183fb$ed95b0fe746dd68159dcc8f73
  ```
* **Contraseña Legítima Recuperada de Acceso al Volumen:**
  $$\mathbf{abcd..Hb0167}$$
* **Clave Maestra XTS del Volumen (Master Key - 512 bits):**
  ```text
  f440cf2b946b29ae45397d48eaba7f42674915ab9f8e511eb6a29e817a964084d776a9546235c8e4920d5cd6b8cc155f156fae459474679e3a632ab77a82bf20
  ```

### 7.2. Traza de Auditoría Consolidada de Hashcat
```text
Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 29421 (VeraCrypt SHA512 + XTS 512 bit)
Hash.Target......: $veracrypt$ade9c4a25cb55592ee35521edc09738924f2ce09...860c8f
Time.Started.....: Fri Oct  9 11:31:07 2026 (48 secs)
Speed.#01........: 513 H/s (GPU: NVIDIA GeForce RTX 3050 Laptop GPU)
Guess.Mask.......: abcd..H?10?d?d?d [12]
Recovered........: 1/1 (100.00%) Digests (total)
Progress.........: 24576/52000 (47.26%)
Contraseña recuperada: abcd..Hb0167
```

### 7.3. Inventario y Análisis del Documento Confidencial Rescatado
Tras el descifrado y montaje del sistema de archivos FAT12 del contenedor, se localizó la siguiente jerarquía:
```text
Directorio Raíz del Contenedor Descifrado:
├── $RECYCLE.BIN/
│   └── desktop.ini [129 bytes]
├── System Volume Information/
│   └── WPSettings.dat [12 bytes]
└── TopSecret/
    └── calendario-escolar-2026-27.pdf [67.714 bytes] (DOCUMENTO PRINCIPAL RESCATADO)
```

* **Nombre del Fichero Rescatado:** `calendario-escolar-2026-27.pdf`
* **Tamaño Oficial:** 67.714 bytes
* **Huella Digital SHA-256:** `0173f85f02f5b6346cf275a2f16a292f263e7f70e0ed1cc5af7b86e644493479`
* **Transcripción del Encabezado Extraído:**
  > *E.T.S. INGENIERÍA INFORMÁTICA - CALENDARIO ESCOLAR 2026-2027 TITULACIONES DE GRADO SEPTIEMBRE-2026 \| OCTUBRE-2026 \| NOVIEMBRE-2026 \| DICIEMBRE-2026 ...*

### 7.4. Protocolo de Custodia y Entrega de Activos Rescatados
Los elementos descifrados han sido encapsulados en el directorio `apartado_b/ficheros_recuperados/` del archivo de entrega `ST-3-CAI2A.zip`. Se recomienda a la Dirección de Seguridad del hospital proceder a la regeneración inmediata del contenedor aplicando las directrices de ingeniería expuestas en la Sección 4.1 del informe.

---

## 8. Declaración de Herramientas y Metodología Pericial

### 8.1. Herramientas Utilizadas en la Auditoría
* **Entorno de Trabajo:** Sistema Windows 11 / Kali Linux con consola Bash.
* **OpenSSL 3.x:** Pruebas de rendimiento criptográfico, modos de bloque, padding y funciones de derivación PBKDF2.
* **Hashcat v7.1.2:** Cracking acelerado por hardware GPU mediante ataque por máscara de cabecera VeraCrypt.
* **Python 3 (`cryptography` library):** Desarrollo del script forense en espacio de usuario para descifrado de cabecera VeraCrypt (XTS) y reconstrucción sectorial.
* **Asistente de IA (Gemini):** Soporte pericial en redacción técnica, cálculos de entropía y maquetación documental conforme a la normativa académica.

### 8.2. Desglose y Procedimiento de Creación de los Entregables (`apartado_a` y `apartado_b`)

Para dar cumplimiento estricto a las normas de entrega del profesor (*"se deben entregar las imágenes utilizadas para el ejemplo, el resultado de su cifrado, y los elementos necesarios para su descifrado"*), los ficheros de las carpetas de auditoría fueron construidos mediante el siguiente proceso técnico:

#### 1. Carpeta `apartado_a` (Cifrado de Radiografías):
* **`radiografia_tamano1_500KB.bmp` y `radiografia_tamano2_1500KB.bmp`:**
  * *Origen y Justificación:* Se obtuvieron a partir de estudios radiológicos reales en formato mapa de bits sin compresión (BMP). Se ajustaron a 500 KB (512.174 bytes) y 1500 KB (1.536.000 bytes) para reflejar fielmente los picos de la gráfica del parque hospitalario facilitada en el enunciado (24% de estudios menores a 1000 KB y 12% de escáneres pesados mayores a 1000 KB).
* **`claves_y_vectores.txt`:**
  * *Propósito:* Documenta los parámetros hexadecimales fijos empleados para garantizar la **reproducibilidad pericial**:
    * Clave simétrica de 256 bits: `0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef`
    * Vector de Inicialización (IV) de 128 bits: `fedcba9876543210fedcba9876543210`
* **Archivos cifrados (`*.enc`):**
  * *Cómo se generaron:* Mediante OpenSSL aplicando clave e IV directos con `-K` y `-iv`, generando los 6 archivos de muestra entregados:
    * `radiografia_tamano1_500KB_aes256cbc.enc`
    * `radiografia_tamano1_500KB_chacha20.enc`
    * `radiografia_tamano1_500KB_camellia256cbc.enc`
    * (Y sus correspondientes análogos para Tamaño 2).
* **`hashes_sha256_originales.txt`:**
  * Almacena las huellas criptográficas SHA-256 de las imágenes limpias previas al cifrado.
* **`descifrar_y_verificar.sh`:**
  * Script en Bash que automatiza el descifrado pericial de los 6 archivos `.enc` mediante OpenSSL y valida automáticamente que el hash SHA-256 de cada archivo descifrado coincida al 100% con el original.

#### 2. Carpeta `apartado_b` (VeraCrypt y Análisis Forense):
* **`drive.vc` (Contenedor Auditado):**
  * *Cómo se creó:* Contenedor VeraCrypt de 1 MB formateado con sistema FAT12, generado en Windows 11 siguiendo todas las opciones por defecto que ofrece la herramienta (cifrador AES, algoritmo hash PBKDF2 SHA-512, modo sectorial XTS y contraseña conforme a la pista del cliente).
* **`hash_drive.txt`:**
  * *Cómo se generó:* Se ejecutó el script de extracción pericial de Hashcat `veracrypt2hashcat.py drive.vc > hash_drive.txt`. Este comando extrae los primeros 512 bytes del contenedor (salt y cabecera cifrada) y los estructura en el formato reconocido por el módulo 29421 de Hashcat (`$veracrypt$ade9c4...`).
* **`ejecutar_ataque_hashcat.sh` y `salida_hashcat.txt`:**
  * Script que invoca Hashcat por GPU aplicando la máscara matemática de 12 caracteres (`abcd..H?10?d?d?d`). El registro de salida evidencia el estado `Cracked` en 48 segundos y el rescate de la credencial legítima `abcd..Hb0167`.
* **`script_recuperacion_forense.py`:**
  * Herramienta pericial programada en Python usando la librería estándar `cryptography`. Permite descifrar el volumen en espacio de usuario sin requerir la instalación de VeraCrypt ni privilegios de administrador de kernel:
    1. Calcula la clave de cabecera con PBKDF2 (SHA-512, 500.000 rondas).
    2. Descifra la cabecera AES-XTS y extrae la Master Key de 64 bytes.
    3. Descifra los 1.536 sectores del volumen generando `volumen_descifrado.img`.
* **`volumen_descifrado.img` y `ficheros_recuperados/`:**
  * Imagen descifrada del disco. Al montarse como dispositivo de bucle (*loopback*) en Linux o explorarse con `mtools`, revela el sistema de ficheros FAT12 y permite la extracción del documento clasificado: `/TopSecret/calendario-escolar-2026-27.pdf`.

---

### 8.3. Guía Paso a Paso para Reproducir la Práctica Completa en Kali Linux

Para que cualquier auditor o el tribunal evaluador reproduzca el trabajo de principio a fin en **Kali Linux**:

#### Fase 1: Pruebas del Apartado a) (OpenSSL y Radiografías)
1. **Entrar en la carpeta del Apartado a:**
   ```bash
   cd apartado_a
   ```
2. **Ejecutar el script automatizado de descifrado y verificación de integridad:**
   ```bash
   chmod +x descifrar_y_verificar.sh
   ./descifrar_y_verificar.sh
   ```
   *Resultado esperado:* Verificación en verde `[OK - INTEGRIDAD VERIFICADA]` con coincidencia exacta de los hashes SHA-256.
3. **Reproducir el ensayo visual de fuga de información (ECB vs CBC):**
   ```bash
   # Cifrado en ambos modos
   openssl enc -aes-256-ecb -e -in radiografia_tamano1_500KB.bmp -out ecb.enc -pass pass:"test" -pbkdf2
   openssl enc -aes-256-cbc -e -in radiografia_tamano1_500KB.bmp -out cbc.enc -pass pass:"test" -pbkdf2
   # Inserción de cabecera BMP
   head -c 54 radiografia_tamano1_500KB.bmp > header.bin
   cat header.bin ecb.enc > fuga_ecb.bmp
   cat header.bin cbc.enc > seguro_cbc.bmp
   # Visualización
   ristretto fuga_ecb.bmp seguro_cbc.bmp
   ```

#### Fase 2: Pruebas del Apartado b) (VeraCrypt y Forense)
1. **Entrar en la carpeta del Apartado b:**
   ```bash
   cd ../apartado_b
   ```
2. **Lanzar la auditoría por fuerza bruta con Hashcat (o revisar traza):**
   ```bash
   hashcat -m 29421 hash_drive.txt -a 3 -1 "?l?u" "abcd..H?10?d?d?d"
   ```
   *Resultado:* En menos de un minuto encuentra la clave `abcd..Hb0167`.
3. **Ejecutar el script forense de descifrado:**
   ```bash
   python3 script_recuperacion_forense.py
   ```
   *Resultado:* Genera el archivo `volumen_descifrado.img` tras validar la firma mágica `VERA` y extraer la Master Key XTS.
4. **Montar la imagen y extraer el documento confidencial:**
   ```bash
   # Opción A: Mediante herramientas mtools (sin root)
   mdir -i volumen_descifrado.img ::/TopSecret
   mcopy -i volumen_descifrado.img ::/TopSecret/calendario-escolar-2026-27.pdf .

   # Opción B: Montaje tradicional de loopback (con sudo)
   sudo mkdir -p /mnt/veracrypt_analisis
   sudo mount -o loop,ro volumen_descifrado.img /mnt/veracrypt_analisis
   ls -la /mnt/veracrypt_analisis/TopSecret/
   sha256sum /mnt/veracrypt_analisis/TopSecret/calendario-escolar-2026-27.pdf
   sudo umount /mnt/veracrypt_analisis
   ```

---

### AVISO LEGAL Y CLÁUSULA DE RESPONSABILIDAD
*El Security Team 3 ejecutó esta auditoría pericial aplicando metodologías alineadas con estándares internacionales reconocidos (NIST, ISO/IEC, RGPD y ENS). El análisis fue de carácter empírico y produjo resultados reproducibles. Las recomendaciones deben implementarse con carácter de urgencia para mitigar los riesgos legales, operacionales y reputacionales de la entidad.*
