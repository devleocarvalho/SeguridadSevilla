# -*- coding: utf-8 -*-
"""
Generador del Informe Técnico Oficial en PDF para PAI-3 VULNAWEB (Versión Completa y Argumentada)
Consultora: INSEGUS (Informática y Seguridad del Sur)
Cliente: Universidad Pública U-Secure
Equipo: Security Team 3 (Grupo 3) - ETSII Universidad de Sevilla
"""

import os
import shutil
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        # 1. Marca de agua "CONFIDENTIAL" a 45 grados en el fondo
        self.saveState()
        self.setFont("Helvetica-Bold", 60)
        self.setFillColor(colors.HexColor("#64748B"))
        try:
            self.setFillAlpha(0.08)  # Opacidad sutil y elegante
        except Exception:
            pass
        self.translate(105 * mm, 148 * mm)  # Centro geométrico de A4
        self.rotate(45)
        self.drawCentredString(0, 0, "CONFIDENTIAL")
        self.restoreState()

        if self._pageNumber == 1:
            return  # Portada sin encabezados ni pie formal

        # 2. Encabezado formal de auditoría
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#4A5568"))
        self.drawString(18 * mm, 285 * mm, "INSEGUS Cybersecurity — Auditoría Integral de Seguridad U-Secure (PAI-3)")
        self.drawRightString(192 * mm, 285 * mm, "Security Team 3 | ETSII Sevilla")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(18 * mm, 282 * mm, 192 * mm, 282 * mm)

        # 3. Pie de página formal
        self.line(18 * mm, 15 * mm, 192 * mm, 15 * mm)
        self.drawString(18 * mm, 10 * mm, "CONFIDENCIAL — Comité de Seguridad y Tecnologías de la Información U-Secure")
        page_text = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(192 * mm, 10 * mm, page_text)
        self.restoreState()

def build_pdf():
    output_pdf = r"c:\leo\programacao\Sevilla\emenda\seguranca\practica\3\INFORME-PAI3-ST3.pdf"
    lab_pdf = r"c:\leo\programacao\Sevilla\emenda\seguranca\practica\3\PAI3-ST3\INFORME-PAI3-ST3.pdf"
    
    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm
    )

    styles = getSampleStyleSheet()

    c_primary = colors.HexColor("#1E3A8A")    # Azul corporativo oscuro
    c_secondary = colors.HexColor("#831843")  # Borgoña institucional US
    c_dark = colors.HexColor("#0F172A")       # Texto base
    c_bg_code = colors.HexColor("#F8FAFC")    # Fondo de bloques de código
    c_border = colors.HexColor("#CBD5E1")     # Borde de tablas

    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=23,
        textColor=c_primary,
        alignment=1,
        spaceAfter=10
    )

    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=c_secondary,
        alignment=1,
        spaceAfter=14
    )

    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12.0,
        leading=15.0,
        textColor=c_primary,
        spaceBefore=9,
        spaceAfter=4,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.0,
        leading=13.0,
        textColor=c_secondary,
        spaceBefore=7,
        spaceAfter=3,
        keepWithNext=True
    )

    h3_style = ParagraphStyle(
        'H3',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=c_dark,
        spaceBefore=5,
        spaceAfter=2.5,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=12.2,
        textColor=c_dark,
        spaceAfter=3,
        alignment=4
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=body_style,
        leftIndent=10,
        firstLineIndent=-7,
        spaceAfter=2
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.1,
        leading=10.2,
        textColor=c_primary
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10.2,
        textColor=c_dark
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=10.2,
        textColor=c_dark
    )

    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.0,
        leading=9.0,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=2
    )

    story = []

    # ==================== PORTADA ====================
    story.append(Spacer(1, 18 * mm))
    story.append(Paragraph("INFORME TÉCNICO DE AUDITORÍA DE SEGURIDAD EN SISTEMAS INFORMÁTICOS Y ANÁLISIS DE VULNERABILIDADES WEB", title_style))
    story.append(Paragraph("Proyecto VULNAWEB (PAI 3): Postura de Seguridad Integral (Endpoints, Navegadores, BYOD Móvil y DAST Web) para la Universidad Pública \"U-Secure\"", subtitle_style))
    story.append(HRFlowable(width="90%", thickness=1.5, color=c_secondary, spaceAfter=14))

    meta_data = [
        [Paragraph("<b>Asignatura:</b>", body_style), Paragraph("Seguridad en Sistemas Informáticos y en Internet (SSII)", body_style)],
        [Paragraph("<b>Institución Académica:</b>", body_style), Paragraph("E.T.S. de Ingeniería Informática — Universidad de Sevilla", body_style)],
        [Paragraph("<b>Entidad Consultora:</b>", body_style), Paragraph("INSEGUS (Informática y Seguridad del Sur)", body_style)],
        [Paragraph("<b>Equipo Auditor:</b>", body_style), Paragraph("<b>Security Team 3 (Grupo 3)</b>", body_style)],
        [Paragraph("<b>Analistas de Seguridad:</b>", body_style), Paragraph("Kleber Leonardo de Carvalho, Paula Benítez, Luigui Juan, Guillermo Ramos", body_style)],
        [Paragraph("<b>Destinatario:</b>", body_style), Paragraph("Área de Ciberseguridad / CISO — Universidad Pública U-Secure", body_style)],
        [Paragraph("<b>Fecha de Emisión:</b>", body_style), Paragraph("Noviembre de 2026", body_style)],
        [Paragraph("<b>Versión del Documento:</b>", body_style), Paragraph("2.0 (Versión Final Oficial)", body_style)],
        [Paragraph("<b>Clasificación:</b>", body_style), Paragraph("<font color='#B91C1C'><b>CONFIDENCIAL / USO INTERNO (RESTRICTED TLP:AMBER+)</b></font>", body_style)],
    ]
    meta_table = Table(meta_data, colWidths=[50 * mm, 124 * mm])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('BOX', (0, 0), (-1, -1), 1, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(meta_table)

    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>Control de Versiones del Documento:</b>", h3_style))
    vers_data = [
        [Paragraph("<b>Versión</b>", table_header_style), Paragraph("<b>Fecha</b>", table_header_style), Paragraph("<b>Autor(es)</b>", table_header_style), Paragraph("<b>Resumen de Modificaciones Técnicas</b>", table_header_style)],
        [Paragraph("0.1", code_style), Paragraph("26/10/2026", table_cell_style), Paragraph("Security Team 3", table_cell_style), Paragraph("Definición del alcance técnico y matriz de auditoría según PAI-3.", table_cell_style)],
        [Paragraph("0.5", code_style), Paragraph("27/10/2026", table_cell_style), Paragraph("Security Team 3", table_cell_style), Paragraph("Auditoría base de endpoints Linux (Lynis), script de hardening y validación ≥ 70.", table_cell_style)],
        [Paragraph("0.8", code_style), Paragraph("03/11/2026", table_cell_style), Paragraph("Security Team 3", table_cell_style), Paragraph("Directivas corporativas de navegador (policies.json), auditoría BYOD móvil.", table_cell_style)],
        [Paragraph("1.0", code_style), Paragraph("03/11/2026", table_cell_style), Paragraph("Security Team 3", table_cell_style), Paragraph("Despliegue DAST con ZAP, fuzzing Top 10 (SQLi, XSS, LFI) y código seguro PHP.", table_cell_style)],
        [Paragraph("2.0", code_style), Paragraph("04/11/2026", table_cell_style), Paragraph("Security Team 3", table_cell_style), Paragraph("Telemetría en terminal real Samsung A55 Knox, Breakpoints MitM, matrices de evidencias y dictamen final.", table_cell_style)],
    ]
    t_vers = Table(vers_data, colWidths=[16 * mm, 22 * mm, 32 * mm, 104 * mm])
    t_vers.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
    ]))
    story.append(t_vers)
    story.append(PageBreak())

    # ==================== ÍNDICE DE CONTENIDOS ====================
    story.append(Paragraph("ÍNDICE GENERAL DE CONTENIDOS", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=8))

    index_data = [
        [Paragraph("<b>1. Resumen Ejecutivo</b>", body_style), Paragraph("<b>Pág. 3</b>", body_style)],
        [Paragraph("<b>2. Auditoría y Bastionado de Sistemas Informáticos (Endpoints Linux)</b>", body_style), Paragraph("<b>Pág. 4</b>", body_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;2.1. Descripción de los Sistemas y Herramientas (Lynis 3.1.7)", body_style), Paragraph("Pág. 4", body_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;2.2. Diagnóstico Inicial y Justificación de Hallazgos (Índice 65 / Warnings)", body_style), Paragraph("Pág. 4", body_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;2.3. Acciones Correctoras y Fundamentación de Parámetros del Kernel", body_style), Paragraph("Pág. 4", body_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;2.4. Resultados Post-Bastionado (Índice 72 / Aprobado)", body_style), Paragraph("Pág. 4", body_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;2.5. Cuadro Comparativo Detallado de Controles Lynis", body_style), Paragraph("Pág. 5", body_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;2.6. Matriz de Trazabilidad de Hallazgos y Rutas de Evidencias (Endpoints)", body_style), Paragraph("Pág. 5", body_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;2.7. Conclusiones del Bastionado de Endpoints Linux", body_style), Paragraph("Pág. 5", body_style)],
        [Paragraph("<b>3. Análisis y Bastionado de Navegador Web (Firefox ESR)</b>", body_style), Paragraph("<b>Pág. 6</b>", body_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;3.1. Descripción del Sistema y Vectores de Amenaza (InfoStealers, WebRTC)", body_style), Paragraph("Pág. 6", body_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;3.2. Directivas Corporativas Aplicadas (policies.json)", body_style), Paragraph("Pág. 6", body_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;3.3. Plan de Pruebas y Evidencias Visuales (about:policies)", body_style), Paragraph("Pág. 6", body_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;3.4. Matriz de Trazabilidad de Hallazgos y Rutas de Evidencias (Navegador)", body_style), Paragraph("Pág. 7", body_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;3.5. Conclusiones del Bastionado de Navegadores Web", body_style), Paragraph("Pág. 7", body_style)],
        [Paragraph("<b>4. Auditoría de Seguridad en Dispositivos Móviles (BYOD)</b>", body_style), Paragraph("<b>Pág. 8</b>", body_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;4.1. Entorno de Uso Mixto y Modelo Zero Trust en Terminales Personales", body_style), Paragraph("Pág. 8", body_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;4.2. Matriz de Conformidad de las 8 Medidas de Seguridad Corporativas", body_style), Paragraph("Pág. 8", body_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;4.3. Validación Empírica en Dispositivo Físico Real (Samsung Galaxy A55 5G con Knox)", body_style), Paragraph("Pág. 9", body_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;4.4. Matriz de Trazabilidad de Hallazgos y Rutas de Evidencias (Móvil)", body_style), Paragraph("Pág. 10", body_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;4.5. Conclusiones de la Auditoría Móvil y Entorno BYOD", body_style), Paragraph("Pág. 10", body_style)],
        [Paragraph("<b>5. Auditoría de Seguridad Web DAST y Plan de Mitigación</b>", body_style), Paragraph("<b>Pág. 11</b>", body_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;5.1. Despliegue del Laboratorio en Docker (Mutillidae II)", body_style), Paragraph("Pág. 11", body_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;5.2. Despliegue de Proxy y Cadena Criptográfica CA Raíz Dinámica X.509", body_style), Paragraph("Pág. 11", body_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;5.3. Intercepción y Edición en Vivo mediante Breakpoints (MitM)", body_style), Paragraph("Pág. 11", body_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;5.4. Fuzzing Automatizado con Diccionarios de Inyección (jbrofuzz / SecLists)", body_style), Paragraph("Pág. 11", body_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;5.5. Explotación Demostrada y Análisis de 3 Vulnerabilidades OWASP Top 10", body_style), Paragraph("Pág. 12", body_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;5.6. Matriz de Trazabilidad de Hallazgos y Rutas de Evidencias (Web DAST)", body_style), Paragraph("Pág. 13", body_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;5.7. Plan de Mitigación en Código Seguro PHP (PDO, htmlspecialchars, Whitelist)", body_style), Paragraph("Pág. 13", body_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;5.8. Conclusiones de la Auditoría Web DAST", body_style), Paragraph("Pág. 14", body_style)],
        [Paragraph("<b>6. Conclusiones Globales y Dictamen Institucional</b>", body_style), Paragraph("<b>Pág. 14</b>", body_style)],
        [Paragraph("<b>7. Referencias Normativas y Estándares Técnicos</b>", body_style), Paragraph("<b>Pág. 14</b>", body_style)],
        [Paragraph("<b>8. Matriz Maestra de Inventario y Trazabilidad de Evidencias (PAI3-ST3.zip)</b>", body_style), Paragraph("<b>Pág. 14-15</b>", body_style)],
    ]
    t_index = Table(index_data, colWidths=[148 * mm, 26 * mm])
    t_index.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor("#F1F5F9")),
        ('TOPPADDING', (0, 0), (-1, -1), 1.8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.8),
    ]))
    story.append(t_index)
    story.append(PageBreak())

    # ==================== 1. RESUMEN EJECUTIVO ====================
    story.append(Paragraph("1. RESUMEN EJECUTIVO", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=8))

    story.append(Paragraph(
        "Por encargo formal del Rectorado y la Dirección de Tecnologías de la Información de la Universidad Pública <b>\"U-Secure\"</b>, "
        "el equipo consultor <b>INSEGUS (Security Team 3)</b> ha ejecutado una auditoría técnica integral y un proceso exhaustivo de "
        "bastionado de la seguridad en cuatro frentes estratégicos de su infraestructura digital:",
        body_style
    ))

    story.append(Paragraph("• <b>Auditoría y Bastionado de Endpoints Linux:</b> Análisis diagnóstico con <b>Lynis 3.1.7</b> bajo estándares CIS Benchmarks y ENS sobre la estación de referencia Kali Linux Rolling (Kernel 7.1.5). El sistema incrementó su índice de robustez de <b>65/100</b> (No Conforme) a <b>72/100</b> (Aprobado), erradicando el 100% de los avisos críticos (0 Warnings) mediante endurecimiento sysctl, restricción de umask, control de periféricos y perfil institucional de exenciones justificadas.", bullet_style))
    story.append(Paragraph("• <b>Fortificación de Navegadores Web:</b> Despliegue de directivas empresariales centralizadas en Mozilla Firefox ESR mediante <code>policies.json</code>, forzando HTTPS-Only, DNS sobre HTTPS (DoH), inhabilitando el gestor local de contraseñas contra InfoStealers (RedLine, Lumma, Vidar) y bloqueando fugas de direcciones IP privadas internas vía WebRTC.", bullet_style))
    story.append(Paragraph("• <b>Seguridad en Dispositivos Móviles (BYOD):</b> Verificación de cumplimiento de una matriz de 8 controles corporativos sobre dispositivos Android (Pixel 8 Pro y Galaxy S23), complementada con una auditoría física en vivo vía <b>ADB</b> sobre un terminal real <b>Samsung Galaxy A55 5G</b> con procesador seguro <b>Knox Vault (eSE EAL5+)</b> y contenedor segregado User 150, demostrando la resistencia física frente a extracciones por cable USB.", bullet_style))
    story.append(Paragraph("• <b>Seguridad de Aplicaciones Web (DAST):</b> Auditoría dinámica asistida por el proxy interceptor <b>OWASP ZAP 2.17.0</b> sobre el portal académico simulado (OWASP Mutillidae II). Se completó la importación del <b>Certificado CA Raíz dinámico X.509</b>, la intercepción y edición de peticiones en tránsito mediante <b>Breakpoints (MitM)</b> y la ejecución de <b>Fuzzing automatizado con diccionarios jbrofuzz/SecLists</b>. Se explotaron con éxito 3 vulnerabilidades críticas OWASP Top 10 (SQLi, XSS reflejado y Path Traversal/LFI), aportando las directrices de programación segura en PHP (PDO prepared statements, htmlspecialchars y listas blancas de rutas).", bullet_style))

    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Resumen Ejecutivo de Indicadores Clave de Rendimiento (KPIs):</b>", h3_style))

    kpi_data = [
        [Paragraph("<b>Área Auditada</b>", table_header_style), Paragraph("<b>Métrica Inicial</b>", table_header_style), Paragraph("<b>Métrica Final</b>", table_header_style), Paragraph("<b>Estado de Conformidad</b>", table_header_style)],
        [Paragraph("Endpoints Linux (Lynis)", table_cell_bold), Paragraph("65 / 100 (1 Warning)", table_cell_style), Paragraph("<b>72 / 100 (0 Warnings)</b>", table_cell_style), Paragraph("<font color='#16A34A'><b>✅ SUPERADO (Meta ≥ 70)</b></font>", table_cell_style)],
        [Paragraph("Navegador Web (Firefox)", table_cell_bold), Paragraph("Configuración estándar abierta", table_cell_style), Paragraph("7 directivas policies.json", table_cell_style), Paragraph("<font color='#16A34A'><b>✅ BASTIONADO ACTIVO</b></font>", table_cell_style)],
        [Paragraph("Dispositivos Móviles (BYOD)", table_cell_bold), Paragraph("Riesgo mixto no controlado", table_cell_style), Paragraph("8/8 controles + Knox eSE", table_cell_style), Paragraph("<font color='#16A34A'><b>✅ 100% CUMPLIMIENTO</b></font>", table_cell_style)],
        [Paragraph("Seguridad Web (DAST ZAP)", table_cell_bold), Paragraph("3 fallas críticas OWASP Top 10", table_cell_style), Paragraph("Explotadas y código PHP seguro", table_cell_style), Paragraph("<font color='#16A34A'><b>✅ PLAN DE REMEDIACIÓN</b></font>", table_cell_style)],
    ]
    t_kpi = Table(kpi_data, colWidths=[45 * mm, 38 * mm, 45 * mm, 46 * mm])
    t_kpi.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
    ]))
    story.append(t_kpi)
    story.append(PageBreak())

    # ==================== 2. ENDPOINTS LINUX ====================
    story.append(Paragraph("2. AUDITORÍA Y BASTIONADO DE SISTEMAS INFORMÁTICOS (ENDPOINTS LINUX)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=8))

    story.append(Paragraph("2.1. Descripción de los Sistemas y Herramientas de Análisis", h2_style))
    story.append(Paragraph(
        "Se auditó el parque institucional de la Universidad U-Secure compuesto por <b>3 sistemas Linux heterogéneos</b>: "
        "<b>Sistema 1</b> (Estación de Referencia y Auditoría sobre <b>Kali Linux Rolling</b>, Kernel 7.1.5 x86_64), "
        "<b>Sistema 2</b> (Servidor Web Académico sobre <b>Ubuntu Server 22.04 LTS</b>) y "
        "<b>Sistema 3</b> (Servidor de Datos y Expedientes sobre <b>Debian 12 Bookworm</b>). "
        "Se empleó <b>Lynis 3.1.7</b> como motor de análisis automatizado conforme a CIS Benchmarks y el ENS.",
        body_style
    ))

    story.append(Paragraph("2.2. Diagnóstico Inicial y Justificación de Hallazgos Críticos (Índice < 70)", h2_style))
    story.append(Paragraph(
        "El análisis diagnóstico inicial arrojó puntuaciones por debajo del umbral corporativo de 70 (Sistema 1: 65, Sistema 2: 61, Sistema 3: 58). "
        "Las instalaciones estándar presentan una superficie de exposición inaceptable para la infraestructura universitaria:",
        body_style
    ))
    story.append(Paragraph("• <b>Warning Crítico NETW-2705 (Único Servidor DNS):</b> La máquina dependía exclusivamente de la dirección local <code>192.168.1.1</code>. Ante una caída transitoria del router, la estación quedaba incomunicada, representando un punto único de fallo que comprometía la disponibilidad operativa de servicios académicos.", bullet_style))
    story.append(Paragraph("• <b>Máscara Permisiva AUTH-9328 (Umask 022):</b> Por defecto, los archivos creados tenían permisos <code>644</code> (lectura para cualquier usuario local). En entornos multiusuario universitarios, esto posibilitaba que cualquier usuario sin privilegios examinase scripts, claves privadas o volcados de datos generados por otros analistas.", bullet_style))
    story.append(Paragraph("• <b>Riesgo Físico USB-1000 y STRG-1846 (Drivers USB/DMA):</b> La activación sin restricciones de módulos de almacenamiento USB y FireWire exponía los equipos a inyecciones automatizadas de teclado mediante microcontroladores maliciosos (<i>BadUSB / Rubber Ducky</i>) y ataques de Acceso Directo a Memoria (DMA) capaces de extraer claves criptográficas directamente desde la memoria RAM.", bullet_style))
    story.append(Paragraph("• <b>Exposición de Memoria y Kernel KRNL-6000:</b> Parámetros como <code>dmesg_restrict</code> y <code>kptr_restrict</code> abiertos permitían que atacantes locales leyesen direcciones absolutas de memoria, anulando de facto la protección KASLR (Kernel Address Space Layout Randomization) y facilitando exploits de elevación de privilegios.", bullet_style))

    story.append(Paragraph("2.3. Acciones Correctoras y Fundamentación de Parámetros del Kernel", h2_style))
    story.append(Paragraph(
        "A través del script automatizado modular <code>hardening_sistema1.sh</code> se aplicaron remediaciones de bajo nivel en el parque:",
        body_style
    ))
    story.append(Paragraph("1. <b>Redundancia DNS:</b> Se incorporó <code>1.1.1.1</code> (Cloudflare) como resolver secundario en <code>/etc/resolv.conf</code>, erradicando el punto único de fallo.", bullet_style))
    story.append(Paragraph("2. <b>Banners Legales (BANN-7126 / BANN-7130):</b> Se configuraron advertencias formales pre-login en <code>/etc/issue</code> e <code>/etc/issue.net</code> advirtiendo de acceso restringido y monitorizado conforme a las exigencias jurídicas del ENS y la norma ISO 27001.", bullet_style))
    story.append(Paragraph("3. <b>Control de Accesos y Cuentas (AUTH-9328 / AUTH-9286):</b> Se fijó <code>umask 027</code> (permisos <code>640</code> por defecto) y rotación de contraseñas cada 90 días (<code>PASS_MAX_DAYS 90</code>, mínimo 7 días y 5000 rondas SHA-512) en <code>/etc/login.defs</code>.", bullet_style))
    story.append(Paragraph("4. <b>Inhabilitación de Controladores Físicos:</b> Se enrutaron los módulos <code>usb-storage</code> y <code>firewire-core</code> hacia <code>/bin/true</code> en <code>/etc/modprobe.d/hardening.conf</code>, bloqueando la carga de drivers de periféricos no autorizados.", bullet_style))
    story.append(Paragraph("5. <b>Bastionado Sysctl del Kernel:</b> En <code>/etc/sysctl.d/99-hardening.conf</code> se activó <code>rp_filter=1</code> (Reverse Path Filtering contra IP Spoofing), <code>accept_redirects=0</code> (mitigación de ataques MitM ICMP), <code>dmesg_restrict=1</code> y <code>kptr_restrict=2</code> (ocultamiento de punteros de memoria para blindar KASLR), y <code>yama.ptrace_scope=1</code> (bloqueo de inyección de código entre procesos de usuario).", bullet_style))
    story.append(Paragraph("6. <b>Perfil Corporativo Justificado (custom.prf):</b> Se documentaron formalmente exenciones técnicas en <code>/etc/lynis/custom.prf</code> (como la separación estricta de particiones <code>/tmp</code> con <code>noexec</code>), ya que en máquinas virtuales de laboratorio impedirían la compilación de software y el despliegue de contenedores Docker, justificando técnicamente la decisión sin falsear la postura de riesgo.", bullet_style))

    story.append(Paragraph("2.4. Resultados Post-Bastionado de los 3 Sistemas Linux", h2_style))
    t_sys_data = [
        [Paragraph("<b>Sistema (Rol Institucional)</b>", table_header_style), Paragraph("<b>Distribución / Kernel</b>", table_header_style), Paragraph("<b>Pre-Hardening</b>", table_header_style), Paragraph("<b>Post-Hardening</b>", table_header_style), Paragraph("<b>Dictamen Lynis</b>", table_header_style)],
        [Paragraph("<b>Sistema 1:</b> Estación PDI/PTGAS", table_cell_bold), Paragraph("Kali Rolling (7.1 x86_64)", table_cell_style), Paragraph("65 (1 Warning)", table_cell_style), Paragraph("<b>72 (0 Warnings)</b>", table_cell_style), Paragraph("<font color='#16A34A'><b>✅ APROBADO (≥ 70)</b></font>", table_cell_style)],
        [Paragraph("<b>Sistema 2:</b> Servidor Web Académico", table_cell_bold), Paragraph("Ubuntu Server 22.04", table_cell_style), Paragraph("61 (2 Warnings)", table_cell_style), Paragraph("<b>74 (0 Warnings)</b>", table_cell_style), Paragraph("<font color='#16A34A'><b>✅ APROBADO (≥ 70)</b></font>", table_cell_style)],
        [Paragraph("<b>Sistema 3:</b> Servidor BD Expedientes", table_cell_bold), Paragraph("Debian 12 Bookworm", table_cell_style), Paragraph("58 (1 Warning)", table_cell_style), Paragraph("<b>71 (0 Warnings)</b>", table_cell_style), Paragraph("<font color='#16A34A'><b>✅ APROBADO (≥ 70)</b></font>", table_cell_style)],
    ]
    t_sys = Table(t_sys_data, colWidths=[45 * mm, 38 * mm, 28 * mm, 31 * mm, 32 * mm])
    t_sys.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(t_sys)
    story.append(PageBreak())

    # ==================== 2.5 CUADRO COMPARATIVO, 2.6 MATRIZ Y 2.7 CONCLUSIONES ====================
    story.append(Paragraph("2.5. Cuadro Comparativo Detallado de Controles Lynis", h2_style))
    ctrl_data = [
        [Paragraph("<b>Control Lynis</b>", table_header_style), Paragraph("<b>Estado Inicial (Nota 65)</b>", table_header_style), Paragraph("<b>Acción de Bastionado (Nota 72)</b>", table_header_style), Paragraph("<b>Impacto Técnico de Seguridad</b>", table_header_style)],
        [Paragraph("<code>NETW-2705</code>", code_style), Paragraph("❌ [WARNING] 1 DNS (192.168.1.1)", table_cell_style), Paragraph("✅ DNS secundario 1.1.1.1 en resolv.conf", table_cell_style), Paragraph("Alta Disponibilidad en resolución de nombres corporativos.", table_cell_style)],
        [Paragraph("<code>BANN-7126/30</code>", code_style), Paragraph("⚠️ [WEAK] Banners genéricos", table_cell_style), Paragraph("✅ Banners formales pre-login aplicados", table_cell_style), Paragraph("Respaldo jurídico institucional conforme al ENS / ISO 27001.", table_cell_style)],
        [Paragraph("<code>AUTH-9328</code>", code_style), Paragraph("⚠️ [SUGGESTION] Umask 022", table_cell_style), Paragraph("✅ umask 027 en login.defs y profile", table_cell_style), Paragraph("Ficheros nuevos creados con permisos restrictivos 640.", table_cell_style)],
        [Paragraph("<code>AUTH-9286/30</code>", code_style), Paragraph("⚠️ [DISABLED] Sin caducidad", table_cell_style), Paragraph("✅ PASS_MAX_DAYS 90, rondas 5000", table_cell_style), Paragraph("Fuerza rotación trimestral y frena crackeo offline de shadow.", table_cell_style)],
        [Paragraph("<code>USB-1000 / STRG</code>", code_style), Paragraph("⚠️ [ACTIVE] Módulos activos", table_cell_style), Paragraph("✅ Blacklist /bin/true en hardening.conf", table_cell_style), Paragraph("Bloquea inyecciones BadUSB y ataques DMA a memoria RAM.", table_cell_style)],
        [Paragraph("<code>KRNL-6000 (Net)</code>", code_style), Paragraph("⚠️ rp_filter=0, redirects=1", table_cell_style), Paragraph("✅ rp_filter=1, accept_redirects=0", table_cell_style), Paragraph("Previene suplantación de IP (anti-spoofing) y MitM ICMP.", table_cell_style)],
        [Paragraph("<code>KRNL-6000 (Mem)</code>", code_style), Paragraph("⚠️ dmesg y punteros abiertos", table_cell_style), Paragraph("✅ dmesg_restrict=1, kptr_restrict=2", table_cell_style), Paragraph("Oculta memoria del kernel mitigando evasión de KASLR.", table_cell_style)],
        [Paragraph("<code>FILE-7524</code>", code_style), Paragraph("⚠️ Permisos cron abiertos", table_cell_style), Paragraph("✅ chmod 700 /etc/cron.*", table_cell_style), Paragraph("Impide a usuarios leer o manipular tareas administrativas.", table_cell_style)],
        [Paragraph("<code>Perfil custom.prf</code>", code_style), Paragraph("⚠️ Exigencias de partición en VM", table_cell_style), Paragraph("✅ Exenciones justificadas formalizadas", table_cell_style), Paragraph("Realismo técnico sin falsear riesgos en entornos virtuales.", table_cell_style)],
    ]
    t_ctrl = Table(ctrl_data, colWidths=[26 * mm, 46 * mm, 50 * mm, 52 * mm])
    t_ctrl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 1.8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.8),
    ]))
    story.append(t_ctrl)

    story.append(Spacer(1, 3))
    story.append(Paragraph("2.6. Matriz de Trazabilidad de Hallazgos y Rutas de Evidencias (Endpoints Linux)", h2_style))
    ev_lin_data = [
        [Paragraph("<b>ID Hallazgo</b>", table_header_style), Paragraph("<b>Control / Vulnerabilidad</b>", table_header_style), Paragraph("<b>Severidad</b>", table_header_style), Paragraph("<b>Ubicación Exacta de la Evidencia (Ruta / Archivo)</b>", table_header_style), Paragraph("<b>Estado</b>", table_header_style)],
        [Paragraph("HAL-EP-01", code_style), Paragraph("Aviso Crítico DNS único (NETW-2705)", table_cell_style), Paragraph("<font color='#B91C1C'><b>ALTA</b></font>", table_cell_style), Paragraph("<code>evidencias/endpoints/sistema1_kali_pre_report.dat</code> (L. 412)", table_cell_style), Paragraph("<font color='#16A34A'><b>✅ Resuelto</b></font>", table_cell_style)],
        [Paragraph("HAL-EP-02", code_style), Paragraph("Ausencia de banners legales (BANN-7126)", table_cell_style), Paragraph("<font color='#D97706'>MEDIA</font>", table_cell_style), Paragraph("<code>evidencias/endpoints/configs_aplicadas/issue</code> y <code>issue.net</code>", table_cell_style), Paragraph("<font color='#16A34A'><b>✅ Conforme</b></font>", table_cell_style)],
        [Paragraph("HAL-EP-03", code_style), Paragraph("Máscara de archivos permisiva (AUTH-9328)", table_cell_style), Paragraph("<font color='#D97706'>MEDIA</font>", table_cell_style), Paragraph("<code>evidencias/endpoints/sistema1_kali_post_report.dat</code> (L. 889)", table_cell_style), Paragraph("<font color='#16A34A'><b>✅ Conforme</b></font>", table_cell_style)],
        [Paragraph("HAL-EP-04", code_style), Paragraph("Sin caducidad ni rondas hash (AUTH-9286)", table_cell_style), Paragraph("<font color='#D97706'>MEDIA</font>", table_cell_style), Paragraph("<code>evidencias/endpoints/sistema1_kali_post_report.dat</code>", table_cell_style), Paragraph("<font color='#16A34A'><b>✅ Conforme</b></font>", table_cell_style)],
        [Paragraph("HAL-EP-05", code_style), Paragraph("Controladores USB/FireWire activos", table_cell_style), Paragraph("<font color='#B91C1C'><b>ALTA</b></font>", table_cell_style), Paragraph("<code>evidencias/endpoints/configs_aplicadas/hardening.conf</code>", table_cell_style), Paragraph("<font color='#16A34A'><b>✅ Bloqueado</b></font>", table_cell_style)],
        [Paragraph("HAL-EP-06", code_style), Paragraph("Parámetros sysctl permisivos (KRNL-6000)", table_cell_style), Paragraph("<font color='#B91C1C'><b>ALTA</b></font>", table_cell_style), Paragraph("<code>evidencias/endpoints/configs_aplicadas/99-hardening.conf</code>", table_cell_style), Paragraph("<font color='#16A34A'><b>✅ Blindado</b></font>", table_cell_style)],
        [Paragraph("HAL-EP-07", code_style), Paragraph("Excepciones arquitectónicas justificadas", table_cell_style), Paragraph("INFO", table_cell_style), Paragraph("<code>evidencias/endpoints/configs_aplicadas/custom.prf</code>", table_cell_style), Paragraph("<font color='#16A34A'><b>✅ Justificado</b></font>", table_cell_style)],
        [Paragraph("HAL-EP-08", code_style), Paragraph("Script maestro automatizado y reproducible", table_cell_style), Paragraph("INFO", table_cell_style), Paragraph("<code>scripts/hardening_sistema1.sh</code>", table_cell_style), Paragraph("<font color='#16A34A'><b>✅ Operativo</b></font>", table_cell_style)],
        [Paragraph("HAL-EP-09", code_style), Paragraph("Trazas forenses completas Sistema 1 (Lynis)", table_cell_style), Paragraph("INFO", table_cell_style), Paragraph("<code>evidencias/endpoints/sistema1_kali_post_lynis.log</code> (1.15 MB)", table_cell_style), Paragraph("<font color='#16A34A'><b>✅ Preservado</b></font>", table_cell_style)],
        [Paragraph("HAL-EP-10", code_style), Paragraph("Auditoría y reportes Sistemas 2 y 3 (≥ 70)", table_cell_style), Paragraph("INFO", table_cell_style), Paragraph("<code>evidencias/endpoints/sistema2_ubuntu*</code> y <code>sistema3*</code>", table_cell_style), Paragraph("<font color='#16A34A'><b>✅ Conforme</b></font>", table_cell_style)],
    ]
    t_ev_lin = Table(ev_lin_data, colWidths=[18 * mm, 46 * mm, 18 * mm, 68 * mm, 24 * mm])
    t_ev_lin.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 1.6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.6),
    ]))
    story.append(t_ev_lin)

    story.append(Spacer(1, 2))
    story.append(Paragraph("2.7. Conclusiones del Bastionado de Endpoints Linux", h2_style))
    story.append(Paragraph(
        "El bastionado sobre los Sistemas 1, 2 y 3 demuestra que es viable elevar sustancialmente la postura de seguridad de todo el parque Linux institucional "
        "(alcanzando índices de 72, 74 y 71 puntos, erradicando el 100% de los avisos críticos) sin degradar la capacidad operativa. La automatización mediante un script modular "
        "garantiza el despliegue desatendido y homogéneo sobre los servidores web y de bases de datos de la "
        "Universidad U-Secure, garantizando el pleno cumplimiento del Esquema Nacional de Seguridad (ENS).",
        body_style
    ))
    story.append(PageBreak())

    # ==================== 3. NAVEGADOR WEB ====================
    story.append(Paragraph("3. ANÁLISIS Y BASTIONADO DE NAVEGADOR WEB", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=8))

    story.append(Paragraph("3.1. Descripción del Sistema y Vectores de Amenaza (InfoStealers, WebRTC)", h2_style))
    story.append(Paragraph(
        "El navegador <b>Mozilla Firefox ESR</b> constituye el punto de entrada primario a la Sede Electrónica, correo institucional y "
        "sistemas de gestión académica. Sin embargo, las configuraciones predeterminadas introducen vectores de ataque críticos en el entorno corporativo:",
        body_style
    ))
    story.append(Paragraph("• <b>Troyanos de Tipo InfoStealer (RedLine, Vidar, Lumma):</b> Este malware opera en el espacio del usuario sin requerir privilegios de superusuario. Su objetivo primario es sustraer las bases de datos SQLite locales de contraseñas de Firefox (<code>logins.json</code> y <code>key4.db</code>). Permitir el gestor nativo de contraseñas expone las credenciales institucionales de la universidad a un robo masivo e instantáneo.", bullet_style))
    story.append(Paragraph("• <b>Fuga de Direcciones IP Privadas vía WebRTC (IP Leak):</b> El protocolo WebRTC utiliza peticiones STUN/TURN directas entre extremos para establecer conexiones de voz y vídeo. A través de código JavaScript no autorizado, un sitio malicioso puede forzar al navegador a divulgar la IP local interna del equipo (ej. subredes <code>10.x.x.x</code> o <code>172.16.x.x</code>), permitiendo a atacantes externos mapear la topología de la red interna universitaria, incluso cuando el usuario navega a través de una VPN corporativa.", bullet_style))
    story.append(Paragraph("• <b>Espionaje en Redes Wi-Fi Abiertas o Eduroam (Falta de DoH):</b> Las consultas DNS estándar en texto claro (puerto 53 UDP) son vulnerables a escuchas pasivas y ataques de suplantación de nombres (DNS Spoofing) en redes inalámbricas del campus universitario.", bullet_style))

    story.append(Paragraph("3.2. Directivas Corporativas Aplicadas (policies.json)", h2_style))
    story.append(Paragraph(
        "Mediante el script automatizado <code>hardening_browser.sh</code> se desplegó la directiva centralizada <b>policies.json</b> en "
        "<code>/etc/firefox/policies/policies.json</code> y en la distribución global del aplicativo:",
        body_style
    ))

    t_browser_data = [
        [Paragraph("<b>Parámetro Corporativo</b>", table_header_style), Paragraph("<b>Valor Aplicado</b>", table_header_style), Paragraph("<b>Propósito y Mitigación de Seguridad</b>", table_header_style)],
        [Paragraph("<code>DisableTelemetry</code>", code_style), Paragraph("<code>true</code>", code_style), Paragraph("Anula la recolección y exfiltración de telemetría hacia servidores de Mozilla.", table_cell_style)],
        [Paragraph("<code>PasswordManagerEnabled</code>", code_style), Paragraph("<code>false</code>", code_style), Paragraph("Inhabilita el guardado local de credenciales, mitigando malware InfoStealer (RedLine, Lumma).", table_cell_style)],
        [Paragraph("<code>HttpsOnlyMode</code>", code_style), Paragraph("<code>&quot;force_enabled&quot;</code>", code_style), Paragraph("Fuerza TLS en todas las conexiones, impidiendo ataques de degradación HTTP (MitM).", table_cell_style)],
        [Paragraph("<code>ExtensionSettings</code>", code_style), Paragraph("<code>blocked / signed</code>", code_style), Paragraph("Bloqueo estricto de extensiones no autorizadas y no firmadas (evita complementos espía).", table_cell_style)],
        [Paragraph("<code>Cookies</code>", code_style), Paragraph("<code>reject-foreign</code>", code_style), Paragraph("Restricción estricta de cookies de terceros, mitigando rastreo entre sitios.", table_cell_style)],
        [Paragraph("<code>DNSOverHTTPS</code>", code_style), Paragraph("<code>Enabled (Cloudflare)</code>", code_style), Paragraph("Cifra peticiones DNS institucionales, evitando espionaje y envenenamiento de caché.", table_cell_style)],
        [Paragraph("<code>EnableTrackingProtection</code>", code_style), Paragraph("<code>true (Cryptomining, Fingerprinting)</code>", code_style), Paragraph("Bloquea scripts de rastreo invasivos y huellas digitales de lienzo.", table_cell_style)],
        [Paragraph("<code>media.peerconnection.enabled</code>", code_style), Paragraph("<code>false</code>", code_style), Paragraph("Deshabilita WebRTC, evitando la fuga inadvertida de direcciones IP privadas de la red interna.", table_cell_style)],
        [Paragraph("<code>privacy.firstparty.isolate</code>", code_style), Paragraph("<code>true</code>", code_style), Paragraph("Aísla el almacenamiento de cookies y caché por dominio de primer nivel.", table_cell_style)],
    ]
    t_br = Table(t_browser_data, colWidths=[48 * mm, 42 * mm, 84 * mm])
    t_br.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 2.0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.0),
    ]))
    story.append(t_br)

    story.append(Paragraph("3.3. Plan de Pruebas y Evidencias Visuales (about:policies)", h2_style))
    story.append(Paragraph(
        "La efectividad del bastionado se comprobó accediendo a la consola interna <code>about:policies</code> del navegador. "
        "El motor confirmó el estado activo e inmutable del perfil mediante la notificación: "
        "<i>\"The Enterprise Policies service is active.\"</i> La captura probatoria se indexa en <code>evidencias/browser/firefox_policies_active.png</code>.",
        body_style
    ))
    story.append(PageBreak())

    # ==================== 3.4 MATRIZ NAVEGADOR Y 3.5 CONCLUSIONES ====================
    story.append(Paragraph("3.4. Matriz de Trazabilidad de Hallazgos y Rutas de Evidencias (Navegador Web)", h2_style))
    ev_brw_data = [
        [Paragraph("<b>ID Hallazgo</b>", table_header_style), Paragraph("<b>Vulnerabilidad / Directiva</b>", table_header_style), Paragraph("<b>Severidad</b>", table_header_style), Paragraph("<b>Ubicación Exacta de la Evidencia (Ruta / Archivo)</b>", table_header_style), Paragraph("<b>Estado</b>", table_header_style)],
        [Paragraph("HAL-BRW-01", code_style), Paragraph("Telemetría Mozilla activa por defecto", table_cell_style), Paragraph("<font color='#D97706'>MEDIA</font>", table_cell_style), Paragraph("<code>evidencias/browser/firefox_policies.json</code>", table_cell_style), Paragraph("<font color='#16A34A'><b>✅ Inhabilitada</b></font>", table_cell_style)],
        [Paragraph("HAL-BRW-02", code_style), Paragraph("Gestor de contraseñas vulnerable a InfoStealers", table_cell_style), Paragraph("<font color='#B91C1C'><b>ALTA</b></font>", table_cell_style), Paragraph("<code>evidencias/browser/firefox_policies.json</code>", table_cell_style), Paragraph("<font color='#16A34A'><b>✅ Bloqueado</b></font>", table_cell_style)],
        [Paragraph("HAL-BRW-03", code_style), Paragraph("Conexiones sin forzar TLS (Degradación HTTP)", table_cell_style), Paragraph("<font color='#B91C1C'><b>ALTA</b></font>", table_cell_style), Paragraph("<code>evidencias/browser/firefox_policies.json</code>", table_cell_style), Paragraph("<font color='#16A34A'><b>✅ Forzado TLS</b></font>", table_cell_style)],
        [Paragraph("HAL-BRW-04", code_style), Paragraph("Fuga de IP privada interna por WebRTC", table_cell_style), Paragraph("<font color='#B91C1C'><b>ALTA</b></font>", table_cell_style), Paragraph("<code>evidencias/browser/firefox_policies.json</code>", table_cell_style), Paragraph("<font color='#16A34A'><b>✅ Bloqueado</b></font>", table_cell_style)],
        [Paragraph("HAL-BRW-05", code_style), Paragraph("Verificación visual en interfaz de políticas", table_cell_style), Paragraph("INFO", table_cell_style), Paragraph("<code>evidencias/browser/firefox_policies_active.png</code>", table_cell_style), Paragraph("<font color='#16A34A'><b>✅ Verificado</b></font>", table_cell_style)],
        [Paragraph("HAL-BRW-06", code_style), Paragraph("Script de despliegue corporativo", table_cell_style), Paragraph("INFO", table_cell_style), Paragraph("<code>scripts/hardening_browser.sh</code>", table_cell_style), Paragraph("<font color='#16A34A'><b>✅ Automatizado</b></font>", table_cell_style)],
    ]
    t_ev_brw = Table(ev_brw_data, colWidths=[18 * mm, 46 * mm, 18 * mm, 68 * mm, 24 * mm])
    t_ev_brw.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(t_ev_brw)

    story.append(Spacer(1, 4))
    story.append(Paragraph("3.5. Conclusiones del Bastionado de Navegadores Web", h2_style))
    story.append(Paragraph(
        "El bastionado mediante el motor corporativo <code>policies.json</code> convierte al navegador en un enclave seguro e inmutable, "
        "impidiendo que los usuarios deshabiliten involuntariamente las protecciones de red o almacenen credenciales en claro en el disco local. "
        "Esta medida mitiga con éxito el principal vector de entrada de troyanos modernos (InfoStealers) y previene la fuga pasiva de información "
        "topológica de la red universitaria vía WebRTC, cumpliendo plenamente con las recomendaciones del CCN-CERT para puestos de trabajo.",
        body_style
    ))
    story.append(PageBreak())

    # ==================== 4. DISPOSITIVOS MÓVILES (BYOD) ====================
    story.append(Paragraph("4. AUDITORÍA DE SEGURIDAD EN DISPOSITIVOS MÓVILES (BYOD)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=8))

    story.append(Paragraph("4.1. Entorno de Uso Mixto y Modelo Zero Trust en Terminales Personales", h2_style))
    story.append(Paragraph(
        "El acceso a servicios universitarios desde terminales móviles de uso mixto (Bring Your Own Device - BYOD) por parte de PDI y PTGAS "
        "obliga a adoptar un modelo <b>Zero Trust</b>: la institución no controla el hardware ni la totalidad de las aplicaciones instaladas por el usuario, "
        "por lo que debe exigir garantías criptográficas y arquitectónicas inquebrantables. Se auditaron dos perfiles corporativos de referencia:",
        body_style
    ))
    story.append(Paragraph("1. <b>DEV-BYOD-01 (PDI - Docencia):</b> Google Pixel 8 Pro, SoC Tensor G3, chip Titan M2, Android 14.", bullet_style))
    story.append(Paragraph("2. <b>DEV-BYOD-02 (PTGAS - Gestión):</b> Samsung Galaxy S23, SoC Snapdragon 8 Gen 2, Knox Vault 3.10, Android 14 / One UI 6.1.", bullet_style))

    story.append(Paragraph("4.2. Matriz de Conformidad de las 8 Medidas de Seguridad Corporativas", h2_style))
    byod_data = [
        [Paragraph("<b>ID Medida</b>", table_header_style), Paragraph("<b>Medida de Seguridad</b>", table_header_style), Paragraph("<b>Requisito Normativo (CIS/ENS)</b>", table_header_style), Paragraph("<b>Pixel 8 Pro (DEV-01)</b>", table_header_style), Paragraph("<b>Galaxy S23 (DEV-02)</b>", table_header_style), Paragraph("<b>Dictamen</b>", table_header_style)],
        [Paragraph("<b>MED-01</b>", code_style), Paragraph("Bloqueo y Autenticación", table_cell_style), Paragraph("PIN ≥ 6 dígitos / Biometría; ≤ 5m", table_cell_style), Paragraph("✅ PIN 6d + Biometría", table_cell_style), Paragraph("✅ PIN 8d + Knox Bio", table_cell_style), Paragraph("<b>APROBADO</b>", table_cell_style)],
        [Paragraph("<b>MED-02</b>", code_style), Paragraph("Cifrado Completo FBE", table_cell_style), Paragraph("Cifrado por Hardware dedicado", table_cell_style), Paragraph("✅ Titan M2 HSM AES-256", table_cell_style), Paragraph("✅ Knox Vault eSE AES", table_cell_style), Paragraph("<b>APROBADO</b>", table_cell_style)],
        [Paragraph("<b>MED-03</b>", code_style), Paragraph("Anti-Root y Tampering", table_cell_style), Paragraph("Integridad de bootloader y kernel", table_cell_style), Paragraph("✅ Play Integrity STRONG", table_cell_style), Paragraph("✅ Warranty Bit 0x0", table_cell_style), Paragraph("<b>APROBADO</b>", table_cell_style)],
        [Paragraph("<b>MED-04</b>", code_style), Paragraph("Parches de Seguridad", table_cell_style), Paragraph("Antigüedad de parche ≤ 60 días", table_cell_style), Paragraph("✅ Parche Oct 2026 (Al día)", table_cell_style), Paragraph("✅ Parche Oct 2026 (Al día)", table_cell_style), Paragraph("<b>APROBADO</b>", table_cell_style)],
        [Paragraph("<b>MED-05</b>", code_style), Paragraph("Conexiones Inseguras", table_cell_style), Paragraph("Prohibición redes abiertas / WEP", table_cell_style), Paragraph("✅ Perfiles purgados", table_cell_style), Paragraph("✅ WEP purgado; eduroam", table_cell_style), Paragraph("<b>APROBADO</b>", table_cell_style)],
        [Paragraph("<b>MED-06</b>", code_style), Paragraph("Bloqueo de Sideloading", table_cell_style), Paragraph("Prohibir orígenes desconocidos", table_cell_style), Paragraph("✅ Revocado en Chrome", table_cell_style), Paragraph("✅ Bloqueado por Knox", table_cell_style), Paragraph("<b>APROBADO</b>", table_cell_style)],
        [Paragraph("<b>MED-07</b>", code_style), Paragraph("Protección Antimalware", table_cell_style), Paragraph("Escaneo Koodous / Malwarebytes", table_cell_style), Paragraph("✅ PUP utilidades removido", table_cell_style), Paragraph("✅ Plugin no firmado purgado", table_cell_style), Paragraph("<b>APROBADO</b>", table_cell_style)],
        [Paragraph("<b>MED-08</b>", code_style), Paragraph("Contenedor Corporativo", table_cell_style), Paragraph("Perfil de trabajo y borrado remoto", table_cell_style), Paragraph("✅ Android Work Profile", table_cell_style), Paragraph("✅ Knox Secure Folder", table_cell_style), Paragraph("<b>APROBADO</b>", table_cell_style)],
    ]
    t_by = Table(byod_data, colWidths=[15 * mm, 32 * mm, 41 * mm, 32 * mm, 32 * mm, 22 * mm])
    t_by.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(t_by)
    story.append(PageBreak())

    # ==================== 4.3 AUDITORÍA FÍSICA SAMSUNG A55 ====================
    story.append(Paragraph("4.3. Validación Empírica en Dispositivo Físico Real (Samsung Galaxy A55 5G con Knox Vault)", h2_style))
    story.append(Paragraph(
        "Para corroborar empíricamente la aplicabilidad de los controles sobre hardware físico de producción, el equipo conectó un terminal real "
        "<b>Samsung Galaxy A55 5G (SM-A556E)</b> vía <b>ADB (Android Debug Bridge 1.0.41)</b> al entorno Kali Linux, extrayendo telemetría viva:",
        body_style
    ))
    story.append(Paragraph("• <b>Arquitectura de Procesador y Kernel Seguro:</b> Modelo SM-A556E (serie <code>RQCXB03YBEJ</code>), arquitectura ARM64 (aarch64), Linux Kernel 6.1.157 LTS compilado con directivas <code>SMP PREEMPT</code>. La planificación determinista y de baja latencia mitiga ataques de elevación local de privilegios basados en condiciones de carrera (Race Conditions).", bullet_style))
    story.append(Paragraph("• <b>Cifrado FBE y Procesador Físico Independiente Knox Vault:</b> Parámetro <code>ro.crypto.state: encrypted</code>. A diferencia de soluciones de software, Knox Vault cuenta con su propio procesador de seguridad, memoria SRAM aislada y bus cifrado, blindado contra ataques físicos de inyección de fallos por láser o variación de voltaje (Glitching) y frío (Cold Boot).", bullet_style))
    story.append(Paragraph("• <b>Integridad Criptográfica del Hardware (ro.boot.warranty_bit: 0):</b> El valor 0 certifica que los fusibles electrónicos (e-fuses) de seguridad están intactos de fábrica, confirmando que el gestor de arranque (bootloader) nunca ha sido desbloqueado ni se ha instalado firmware no firmado.", bullet_style))
    story.append(Paragraph("• <b>Aislamiento Pericial Comprobado de Contenedor Knox (User 150):</b> Al intentar listar los paquetes del perfil corporativo desde la interfaz externa ADB, el sistema operativo denegó el acceso con la excepción: <code>SecurityException: Shell does not have permission to access user 150</code>. <b>Hallazgo Pericial:</b> Incluso contando con acceso físico por cable USB y depuración autorizada (UID shell 2000), el subsistema Knox bloquea la extracción o lectura de datos institucionales, certificando la segregación física y lógica exigida por el ENS.", bullet_style))
    story.append(Paragraph("• <b>Telemetría Térmica (27,5 °C) y Batería (96%):</b> La temperatura medida de <b>27,5 °C</b> descarta taxativamente la presencia de procesos en segundo plano de minería de criptomonedas (Cryptojacking) o balizas de spyware de exfiltración continua. El usuario mantiene activo el modo de protección de batería al 80% (<code>mProtectBatteryMode: 3</code>), prolongando la vida física de las celdas de litio.", bullet_style))
    story.append(Paragraph("• <b>Defensa Activa USB (Auto Blocker):</b> Bloqueo automático de comandos por cable USB hasta autorización explícita mediante firma criptográfica RSA en la pantalla del dispositivo, neutralizando ataques de infección por cargadores públicos manipulados (<i>Juice Jacking</i>).", bullet_style))
    story.append(Paragraph("• <b>Auditoría de 79 Aplicaciones Instaladas:</b> Se auditaron 79 paquetes en User 0: <b>14 aplicaciones críticas</b> (incluyendo la app oficial de la Universidad de Sevilla <code>net.universia.us</code>, banca comercial e identidad digital Gov.br/DNIe), <b>58 seguras de productividad</b> y <b>7 bajo monitorización</b> (Expo Go, AppLovin, Samsung Max, Foxit PDF Lite).", bullet_style))
    story.append(Paragraph("• <b>Recomendaciones Periciales:</b> Confinamiento de <code>net.universia.us</code> y banca dentro de la Carpeta Segura (Knox User 150), reactivación de Auto Blocker y cierre definitivo de la depuración ADB.", bullet_style))
    story.append(PageBreak())

    # ==================== 4.4 MATRIZ MÓVIL Y 4.5 CONCLUSIONES ====================
    story.append(Paragraph("4.4. Matriz de Trazabilidad de Hallazgos y Rutas de Evidencias (BYOD Móvil)", h2_style))
    ev_mob_data = [
        [Paragraph("<b>ID Hallazgo</b>", table_header_style), Paragraph("<b>Componente / Control Auditado</b>", table_header_style), Paragraph("<b>Severidad</b>", table_header_style), Paragraph("<b>Ubicación Exacta de la Evidencia (Ruta / Archivo)</b>", table_header_style), Paragraph("<b>Estado</b>", table_header_style)],
        [Paragraph("HAL-MOB-01", code_style), Paragraph("Matriz 8 Controles Normativos (Pixel / Galaxy)", table_cell_style), Paragraph("<font color='#B91C1C'><b>ALTA</b></font>", table_cell_style), Paragraph("<code>evidencias/mobile/matriz_conformidad_byod.csv</code>", table_cell_style), Paragraph("<font color='#16A34A'><b>✅ 8/8 Conformes</b></font>", table_cell_style)],
        [Paragraph("HAL-MOB-02", code_style), Paragraph("Informes de auditoría por dispositivo móvil", table_cell_style), Paragraph("INFO", table_cell_style), Paragraph("<code>evidencias/mobile/dev-byod-01_audit_report.log</code> y <code>02</code>", table_cell_style), Paragraph("<font color='#16A34A'><b>✅ Certificados</b></font>", table_cell_style)],
        [Paragraph("HAL-MOB-03", code_style), Paragraph("Diagnóstico antimalware y PUPs analizados", table_cell_style), Paragraph("<font color='#D97706'>MEDIA</font>", table_cell_style), Paragraph("<code>evidencias/mobile/koodous_malwarebytes_evidence.json</code>", table_cell_style), Paragraph("<font color='#16A34A'><b>✅ Limpio</b></font>", table_cell_style)],
        [Paragraph("HAL-MOB-04", code_style), Paragraph("Telemetría ADB en vivo terminal real Samsung A55", table_cell_style), Paragraph("<font color='#B91C1C'><b>ALTA</b></font>", table_cell_style), Paragraph("<code>evidencias/mobile/auditoria_real_samsung_a55.log</code> (L. 1-320)", table_cell_style), Paragraph("<font color='#16A34A'><b>✅ Verificado</b></font>", table_cell_style)],
        [Paragraph("HAL-MOB-05", code_style), Paragraph("Aislamiento perimetral Knox User 150 demostrado", table_cell_style), Paragraph("<font color='#B91C1C'><b>CRÍTICA</b></font>", table_cell_style), Paragraph("<code>auditoria_real_samsung_a55.log</code> (L. 190, SecurityException)", table_cell_style), Paragraph("<font color='#16A34A'><b>✅ Aislado</b></font>", table_cell_style)],
        [Paragraph("HAL-MOB-06", code_style), Paragraph("Telemetría térmica (27,5 °C) sin Cryptojacking", table_cell_style), Paragraph("<font color='#D97706'>MEDIA</font>", table_cell_style), Paragraph("<code>auditoria_real_samsung_a55.log</code> (L. 145, salud 96%)", table_cell_style), Paragraph("<font color='#16A34A'><b>✅ Conforme</b></font>", table_cell_style)],
        [Paragraph("HAL-MOB-07", code_style), Paragraph("Auditoría 79 apps (app US net.universia.us y banca)", table_cell_style), Paragraph("<font color='#B91C1C'><b>ALTA</b></font>", table_cell_style), Paragraph("<code>auditoria_real_samsung_a55.log</code> (L. 220-305)", table_cell_style), Paragraph("<font color='#16A34A'><b>✅ Clasificado</b></font>", table_cell_style)],
    ]
    t_ev_mob = Table(ev_mob_data, colWidths=[18 * mm, 46 * mm, 18 * mm, 68 * mm, 24 * mm])
    t_ev_mob.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(t_ev_mob)

    story.append(Spacer(1, 4))
    story.append(Paragraph("4.5. Conclusiones de la Auditoría Móvil y Entorno BYOD", h2_style))
    story.append(Paragraph(
        "El análisis pericial evidencia que el modelo BYOD es plenamente viable en una universidad pública si se sustenta en tecnologías "
        "de contenedor criptográfico respaldadas por hardware dedicado (Samsung Knox Vault / Google Titan M2). La demostración empírica mediante ADB "
        "confirma que los datos institucionales permanecen inaccesibles frente a extracciones físicas por cable USB, cumpliendo con los niveles más "
        "exigentes del Esquema Nacional de Seguridad (ENS) y el estándar OWASP MASVS v2.0.",
        body_style
    ))
    story.append(PageBreak())

    # ==================== 5. SEGURIDAD WEB DAST ====================
    story.append(Paragraph("5. AUDITORÍA DE SEGURIDAD WEB DAST Y PLAN DE MITIGACIÓN", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=8))

    story.append(Paragraph("5.1. Despliegue del Laboratorio en Docker (Mutillidae II)", h2_style))
    story.append(Paragraph(
        "Se desplegó la aplicación web académica <b>OWASP Mutillidae II</b> (v2.6.62) mediante un contenedor Docker aislado "
        "en el puerto 8080 (<code>docker run -d -p 8080:80 citizenstig/nowasp</code>). El entorno reproduce un portal universitario "
        "con módulos de autenticación de estudiantes, herramientas de diagnóstico de red y visores documentales.",
        body_style
    ))

    story.append(Paragraph("5.2. Despliegue de Proxy y Cadena Criptográfica CA Raíz Dinámica X.509", h2_style))
    story.append(Paragraph(
        "El análisis dinámico de caja negra (DAST) requiere inspeccionar el tráfico en tránsito entre cliente y servidor. Para evitar que las directivas "
        "HSTS y las alertas TLS del navegador abortasen las sesiones sobre endpoints HTTPS, se configuró <b>OWASP ZAP 2.17.0</b> en el puerto <code>8081</code>:",
        body_style
    ))
    story.append(Paragraph("• <b>Generación e Inyección del Certificado X.509:</b> En ZAP se generó un Certificado CA Raíz dinámico (<code>owasp_zap_root_ca.cer</code>) y se importó en el almacén de autoridades de certificación de Mozilla Firefox ESR marcando <i>Trust this CA to identify websites</i>.", bullet_style))
    story.append(Paragraph("• <b>Mecanismo de Descifrado Transparente:</b> La confianza en la CA raíz permitió a ZAP emitir certificados TLS al vuelo para cada dominio interceptado, desencapsulando peticiones cifradas para su análisis y volviéndolas a cifrar hacia el navegador sin provocar alertas de seguridad.", bullet_style))

    story.append(Paragraph("5.3. Intercepción y Edición en Vivo mediante Breakpoints (Técnica MitM)", h2_style))
    story.append(Paragraph(
        "A diferencia de modificar parámetros en el navegador (donde validaciones de JavaScript del lado cliente pueden interferir), la técnica "
        "de <b>Breakpoint Man-in-the-Middle</b> captura la petición en el búfer TCP de ZAP antes de su salida a la red:",
        body_style
    ))
    story.append(Paragraph("1. Se activó el Breakpoint global en la barra de ZAP (icono rojo activo).", bullet_style))
    story.append(Paragraph("2. Se cursó una petición de login legítima; ZAP retuvo la trama HTTP POST en memoria.", bullet_style))
    story.append(Paragraph("3. En el Request Editor de ZAP, se reemplazó el campo <code>username</code> por el payload <code>' or 1=1 #</code>.", bullet_style))
    story.append(Paragraph("4. Al pulsar <i>Step / Continue</i>, el servidor procesó el payload adulterado concediendo la sesión administrativa (302 Found). Traza documentada en <code>breakpoint_mitm_trace.log</code>.", bullet_style))

    story.append(Paragraph("5.4. Fuzzing Automatizado con Diccionarios de Inyección (jbrofuzz / SecLists)", h2_style))
    story.append(Paragraph(
        "Para contrastar la resistencia ante ataques de fuerza bruta e inyección masiva, se configuró el <b>Fuzzer de OWASP ZAP</b> sobre la petición interceptada. "
        "Se definió el punto de inyección en el parámetro <code>username</code> y se cargaron los diccionarios especializados de <b>jbrofuzz</b> "
        "(sección <i>SQL Injection - Auth Bypass</i>) y <i>SecLists</i>. El motor correlacionó las respuestas analizando códigos de estado (302 Found), "
        "tamaño del cuerpo y tiempos de respuesta (RTT), identificando automáticamente anomalías etiquetadas como <code>Reflected</code>. Reporte en <code>fuzzer_sqli_jbrofuzz.log</code>.",
        body_style
    ))
    story.append(PageBreak())

    # ==================== 5.5. EXPLOTACIÓN OWASP TOP 10 ====================
    story.append(Paragraph("5.5. Explotación Demostrada y Análisis de 3 Vulnerabilidades OWASP Top 10", h2_style))

    story.append(Paragraph("<b>1. Inyección SQL (A03:2021 – Injection / CWE-89):</b>", h3_style))
    story.append(Paragraph(
        "• <b>Mecánica del Ataque en el Parser SQL:</b> En el formulario de login (<code>login.php</code>), el parámetro <code>username</code> se concatenaba directamente en la sentencia SQL. Al inyectar <code>' or 1=1 #</code>, la comilla simple cierra prematuramente el delimitador léxico de cadena; el operador lógico <code>OR 1=1</code> altera el árbol sintáctico del motor relacional introduciendo una tautología universal (siempre verdadera); y el carácter almohadilla <code>#</code> descarta como comentario el resto de la consulta, anulando la verificación criptográfica del hash de contraseña.<br/>"
        "• <b>Impacto Técnico:</b> El cursor de MySQL retorna el primer registro de la tabla <code>accounts</code>, autenticando al atacante como Superadministrador (<i>Logged In Admin: admin</i>, UID 1).<br/>"
        "• <b>Evidencias Preservadas:</b> Formulario con payload (<code>sqli_login_form.png</code>), Admin activo (<code>sqli_admin_authenticated.jpg</code>) y ZAP Req. ID 168 (<code>sqli_zap_history.png</code>).",
        body_style
    ))

    story.append(Paragraph("<b>2. Cross-Site Scripting Reflejado (A03:2021 – Injection / CWE-79):</b>", h3_style))
    story.append(Paragraph(
        "• <b>Mecánica del Ataque en el DOM:</b> En la herramienta de diagnóstico DNS (<code>dns-lookup.php</code>), el parámetro POST <code>target_host</code> se reflejaba directamente en el cuerpo HTML de respuesta sin saneamiento ni codificación de entidades. Al enviar <code>&lt;script&gt;alert('Vulnerabilidade XSS - Grupo 3');&lt;/script&gt;</code>, el motor de renderizado del navegador interpreta las etiquetas como código JavaScript ejecutable.<br/>"
        "• <b>Impacto Técnico:</b> Al ejecutarse en el contexto del origen (Same-Origin Policy), un atacante puede exfiltrar cookies de sesión (<code>document.cookie</code>), capturar pulsaciones de teclado o secuestrar sesiones académicas.<br/>"
        "• <b>Evidencias Preservadas:</b> Alerta modal en pantalla (<code>xss_alert_browser.jpg</code>) y ZAP Req. ID 177 con alerta Medium (<code>xss_zap_history.jpg</code>).",
        body_style
    ))

    story.append(Paragraph("<b>3. Path Traversal / Inclusión Local de Archivos (A01:2021 – Broken Access Control / CWE-22):</b>", h3_style))
    story.append(Paragraph(
        "• <b>Mecánica del Ataque en el Sistema de Ficheros:</b> El backend PHP concatenaba el valor del parámetro <code>$_GET['page']</code> directamente a una instrucción <code>include()</code>. Al enviar secuencias <code>../../../../../../../../etc/passwd</code>, la llamada al sistema de ficheros de Linux resuelve las rutas relativas ascendentes, desbordando el directorio raíz web (<code>DocumentRoot</code> /var/www/html) y alcanzando la raíz absoluta del sistema operativo.<br/>"
        "• <b>Impacto Técnico:</b> Exfiltración y volcado completo de las cuentas de usuario locales, shells asignadas y grupos de servicio.",
        body_style
    ))
    passwd_dump = """root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
... [14 cuentas intermedias del sistema omitidas] ...
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
syslog:x:101:104::/home/syslog:/bin/false
mysql:x:102:105:MySQL Server,,,:/nonexistent:/bin/false"""
    t_dump = Table([[Paragraph(f"<pre>{passwd_dump}</pre>", code_style)]], colWidths=[174 * mm])
    t_dump.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_bg_code),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(Paragraph("• <b>Cuentas de Sistema Exfiltradas (/etc/passwd extraído con 22 registros):</b>", body_style))
    story.append(t_dump)
    story.append(Paragraph("Evidencia gráfica preservada en <code>evidencias/web_dast/path_traversal_browser.jpg</code>.", body_style))
    story.append(PageBreak())

    # ==================== 5.6 MATRIZ DAST Y 5.7 CÓDIGO SEGURO ====================
    story.append(Paragraph("5.6. Matriz de Trazabilidad de Hallazgos y Rutas de Evidencias (Web DAST)", h2_style))
    ev_dast_data = [
        [Paragraph("<b>ID Hallazgo</b>", table_header_style), Paragraph("<b>Vulnerabilidad / Prueba DAST</b>", table_header_style), Paragraph("<b>Severidad</b>", table_header_style), Paragraph("<b>Ubicación Exacta de la Evidencia (Ruta / Archivo)</b>", table_header_style), Paragraph("<b>Estado</b>", table_header_style)],
        [Paragraph("HAL-DAST-01", code_style), Paragraph("Inyección SQL (CWE-89) Bypass Login", table_cell_style), Paragraph("<font color='#B91C1C'><b>CRÍTICA</b></font>", table_cell_style), Paragraph("<code>evidencias/web_dast/sqli_login_form.png</code> y <code>sqli_admin_authenticated.jpg</code>", table_cell_style), Paragraph("<font color='#16A34A'><b>✅ Explotado / Mitigado</b></font>", table_cell_style)],
        [Paragraph("HAL-DAST-02", code_style), Paragraph("Trazabilidad ZAP de Inyección SQL", table_cell_style), Paragraph("<font color='#B91C1C'><b>ALTA</b></font>", table_cell_style), Paragraph("<code>evidencias/web_dast/sqli_zap_history.png</code> (Req. ID 168)", table_cell_style), Paragraph("<font color='#16A34A'><b>✅ Registrado</b></font>", table_cell_style)],
        [Paragraph("HAL-DAST-03", code_style), Paragraph("XSS Reflejado (CWE-79) en dns-lookup", table_cell_style), Paragraph("<font color='#B91C1C'><b>ALTA</b></font>", table_cell_style), Paragraph("<code>evidencias/web_dast/xss_alert_browser.jpg</code>", table_cell_style), Paragraph("<font color='#16A34A'><b>✅ Explotado / Mitigado</b></font>", table_cell_style)],
        [Paragraph("HAL-DAST-04", code_style), Paragraph("Trazabilidad ZAP de XSS Reflejado", table_cell_style), Paragraph("<font color='#D97706'>MEDIA</font>", table_cell_style), Paragraph("<code>evidencias/web_dast/xss_zap_history.jpg</code> (Req. ID 177)", table_cell_style), Paragraph("<font color='#16A34A'><b>✅ Registrado</b></font>", table_cell_style)],
        [Paragraph("HAL-DAST-05", code_style), Paragraph("Path Traversal / LFI (CWE-22) en page", table_cell_style), Paragraph("<font color='#B91C1C'><b>CRÍTICA</b></font>", table_cell_style), Paragraph("<code>evidencias/web_dast/path_traversal_browser.jpg</code>", table_cell_style), Paragraph("<font color='#16A34A'><b>✅ Exfiltrado / Mitigado</b></font>", table_cell_style)],
        [Paragraph("HAL-DAST-06", code_style), Paragraph("Certificado CA Raíz Dinámico X.509", table_cell_style), Paragraph("<font color='#B91C1C'><b>ALTA</b></font>", table_cell_style), Paragraph("<code>evidencias/web_dast/owasp_zap_root_ca.cer</code>", table_cell_style), Paragraph("<font color='#16A34A'><b>✅ Importado Firefox</b></font>", table_cell_style)],
        [Paragraph("HAL-DAST-07", code_style), Paragraph("Intercepción y manipulación MitM Breakpoints", table_cell_style), Paragraph("<font color='#B91C1C'><b>ALTA</b></font>", table_cell_style), Paragraph("<code>evidencias/web_dast/breakpoint_mitm_trace.log</code>", table_cell_style), Paragraph("<font color='#16A34A'><b>✅ Demostrado</b></font>", table_cell_style)],
        [Paragraph("HAL-DAST-08", code_style), Paragraph("Fuzzing Automatizado jbrofuzz / SecLists", table_cell_style), Paragraph("<font color='#B91C1C'><b>ALTA</b></font>", table_cell_style), Paragraph("<code>evidencias/web_dast/fuzzer_sqli_jbrofuzz.log</code>", table_cell_style), Paragraph("<font color='#16A34A'><b>✅ Completado</b></font>", table_cell_style)],
    ]
    t_ev_dast = Table(ev_dast_data, colWidths=[18 * mm, 46 * mm, 18 * mm, 68 * mm, 24 * mm])
    t_ev_dast.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(t_ev_dast)

    story.append(Paragraph("5.7. Plan de Mitigación en Código Seguro PHP", h2_style))
    story.append(Paragraph(
        "Se diseñaron soluciones defensivas que erradican de raíz cada vulnerabilidad:",
        body_style
    ))

    code_sqli = """// Código Seguro: PDO Prepared Statements con enlace estricto de parámetros
$pdo = new PDO("mysql:host=localhost;dbname=nowasp;charset=utf8mb4", $db_user, $db_pass, [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
    PDO::ATTR_EMULATE_PREPARES => false // Forzar preparación nativa en MySQL
]);
$stmt = $pdo->prepare('SELECT id, password_hash, role FROM accounts WHERE username = :user LIMIT 1');
$stmt->execute([':user' => $_POST['username']]);
$account = $stmt->fetch();
if ($account && password_verify($_POST['password'], $account['password_hash'])) {
    session_regenerate_id(true); // Mitigación de fijación de sesión
    $_SESSION['auth'] = true;
}"""
    t_code1 = Table([[Paragraph(f"<pre>{code_sqli}</pre>", code_style)]], colWidths=[174 * mm])
    t_code1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_bg_code),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(Paragraph("<b>A. Remediación SQLi mediante PDO Prepared Statements:</b>", h3_style))
    story.append(t_code1)

    code_xss = """// Código Seguro: Validación de formato y codificación contextual HTML5
$host = trim($_POST['target_host'] ?? '');
if (!filter_var($host, FILTER_VALIDATE_IP) && !preg_match('/^[a-z0-9.-]+$/i', $host)) {
    die("Formato de host no permitido.");
}
$safe_output = htmlspecialchars($host, ENT_QUOTES | ENT_HTML5, 'UTF-8');
echo "<p>Host consultado: <strong>" . $safe_output . "</strong></p>";"""
    t_code2 = Table([[Paragraph(f"<pre>{code_xss}</pre>", code_style)]], colWidths=[174 * mm])
    t_code2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_bg_code),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(Paragraph("<b>B. Remediación XSS mediante htmlspecialchars y CSP:</b>", h3_style))
    story.append(t_code2)

    code_path = """// Código Seguro: Extracción de nombre base y validación por Whitelist estricta
$whitelist = ['home' => 'pages/home.php', 'login' => 'pages/login.php', 'dns' => 'pages/dns.php'];
$page = basename($_GET['page'] ?? 'home');
$key  = str_replace('.php', '', $page);
if (array_key_exists($key, $whitelist) && file_exists($whitelist[$key])) {
    require_once $whitelist[$key];
} else {
    http_response_code(403);
    die("Acceso denegado a recurso no autorizado.");
}"""
    t_code3 = Table([[Paragraph(f"<pre>{code_path}</pre>", code_style)]], colWidths=[174 * mm])
    t_code3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_bg_code),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(Paragraph("<b>C. Remediación Path Traversal mediante Whitelist y basename():</b>", h3_style))
    story.append(t_code3)
    story.append(PageBreak())

    # ==================== 5.8 CONCLUSIONES DAST, 6, 7 Y 8 MATRIZ MAESTRA ====================
    story.append(Paragraph("5.8. Conclusiones de la Auditoría Web DAST", h2_style))
    story.append(Paragraph(
        "El análisis dinámico demostró que los fallos del OWASP Top 10 persisten cuando los datos del usuario se concatenan directamente "
        "en lógica de servidor. La adopción de Sentencias Preparadas (PDO) a nivel de arquitectura, el escapado contextual HTML5 y la validación "
        "estricta mediante listas blancas resuelven de raíz el 100% de las vulnerabilidades descubiertas sin requerir complejas reglas WAF.",
        body_style
    ))

    story.append(Paragraph("6. CONCLUSIONES GLOBALES Y DICTAMEN INSTITUCIONAL", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=8))
    story.append(Paragraph(
        "El proyecto <b>PAI-3 VULNAWEB</b> ha cumplido con rigor técnico y metodológico la totalidad de los objetivos fijados para la evaluación "
        "defensiva de la Universidad Pública \"U-Secure\":",
        body_style
    ))
    story.append(Paragraph("1. <b>Endpoints Linux:</b> Se superó el umbral corporativo alcanzando <b>72/100</b> en Lynis y eliminando el 100% de los avisos críticos (0 warnings).", bullet_style))
    story.append(Paragraph("2. <b>Navegador Corporativo:</b> Se impusieron directivas inmutables en Firefox ESR mediante <code>policies.json</code>, mitigando InfoStealers, fugas WebRTC y asegurando DNS cifrado.", bullet_style))
    story.append(Paragraph("3. <b>Dispositivos Móviles:</b> Se validó la matriz de 8 medidas en terminales BYOD y se corroboró empíricamente sobre hardware real Samsung con procesador seguro Knox Vault y contenedor User 150.", bullet_style))
    story.append(Paragraph("4. <b>Aplicaciones Web DAST:</b> Se demostró la trazabilidad HTTP/HTTPS mediante proxy ZAP con certificado raíz CA X.509, intercepción con Breakpoints (MitM), Fuzzing con diccionarios jbrofuzz/SecLists y explotación de 3 vulnerabilidades Top 10, aportando las soluciones definitivas en código PHP seguro.", bullet_style))

    story.append(Paragraph("7. REFERENCIAS NORMATIVAS Y ESTÁNDARES TÉCNICOS", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=6))
    story.append(Paragraph("1. <b>Centro Criptológico Nacional (CCN-CERT):</b> Guías CCN-STIC 800 - Esquema Nacional de Seguridad (ENS).", bullet_style))
    story.append(Paragraph("2. <b>Center for Internet Security (CIS):</b> CIS Distribution-Independent Linux Benchmark v2.4.0 y CIS Google Android Benchmark v2.4.0.", bullet_style))
    story.append(Paragraph("3. <b>CISOfy:</b> Lynis Security Auditing & System Hardening Technical Manual (v3.1.7).", bullet_style))
    story.append(Paragraph("4. <b>OWASP Foundation:</b> OWASP Top 10 Web Application Security Risks (2021) y Mobile App Security Verification Standard (MASVS v2.0).", bullet_style))
    story.append(Paragraph("5. <b>Mozilla Corporation:</b> Firefox Enterprise Policy Engine (policies.json) Implementation Guide.", bullet_style))

    story.append(Paragraph("8. MATRIZ MAESTRA DE INVENTARIO Y TRAZABILIDAD DE EVIDENCIAS (PAI3-ST3.zip)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=6))
    story.append(Paragraph(
        "Catálogo completo de los 22 artefactos técnicos probatorios preservados en el paquete oficial de entrega <code>PAI3-ST3.zip</code>:",
        body_style
    ))

    master_ev_data = [
        [Paragraph("<b>Categoría</b>", table_header_style), Paragraph("<b>Ruta Relativa en PAI3-ST3.zip</b>", table_header_style), Paragraph("<b>Tipo / Formato</b>", table_header_style), Paragraph("<b>Finalidad Forense / Valor Probatorio</b>", table_header_style)],
        [Paragraph("Endpoints", table_cell_bold), Paragraph("<code>evidencias/endpoints/sistema1_kali_pre_report.dat</code>", table_cell_style), Paragraph("Reporte Lynis", table_cell_style), Paragraph("Diagnóstico inicial no conforme (Hardening Index: 65, 1 Warning)", table_cell_style)],
        [Paragraph("Endpoints", table_cell_bold), Paragraph("<code>evidencias/endpoints/sistema1_kali_post_report.dat</code>", table_cell_style), Paragraph("Reporte Lynis", table_cell_style), Paragraph("Verificación de bastionado superado (Hardening Index: 72, 0 Warnings)", table_cell_style)],
        [Paragraph("Endpoints", table_cell_bold), Paragraph("<code>evidencias/endpoints/sistema1_kali_post_lynis.log</code>", table_cell_style), Paragraph("Log Texto (1.15MB)", table_cell_style), Paragraph("Registro íntegro de ejecución paso a paso de 271 pruebas Lynis", table_cell_style)],
        [Paragraph("Endpoints", table_cell_bold), Paragraph("<code>evidencias/endpoints/sistema2_ubuntu*</code>", table_cell_style), Paragraph("Reportes / Log", table_cell_style), Paragraph("Auditoría Lynis Sistema 2 Servidor Web (Pre: 61 → Post: 74)", table_cell_style)],
        [Paragraph("Endpoints", table_cell_bold), Paragraph("<code>evidencias/endpoints/sistema3_debian*</code>", table_cell_style), Paragraph("Reportes / Log", table_cell_style), Paragraph("Auditoría Lynis Sistema 3 Servidor BD (Pre: 58 → Post: 71)", table_cell_style)],
        [Paragraph("Endpoints", table_cell_bold), Paragraph("<code>evidencias/endpoints/configs_aplicadas/</code>", table_cell_style), Paragraph("5 Ficheros Conf", table_cell_style), Paragraph("Configuraciones aplicadas: issue, issue.net, hardening.conf, 99-sysctl, custom.prf", table_cell_style)],
        [Paragraph("Navegadores", table_cell_bold), Paragraph("<code>evidencias/browser/firefox_policies.json</code>", table_cell_style), Paragraph("JSON Directivas", table_cell_style), Paragraph("Plantilla empresarial inmutable de políticas Firefox ESR", table_cell_style)],
        [Paragraph("Navegadores", table_cell_bold), Paragraph("<code>evidencias/browser/firefox_policies_active.png</code>", table_cell_style), Paragraph("Imagen PNG", table_cell_style), Paragraph("Captura probatoria de directivas activas en about:policies", table_cell_style)],
        [Paragraph("BYOD Móvil", table_cell_bold), Paragraph("<code>evidencias/mobile/matriz_conformidad_byod.csv</code>", table_cell_style), Paragraph("Matriz CSV", table_cell_style), Paragraph("Evaluación comparativa de las 8 medidas en Pixel 8 Pro y Galaxy S23", table_cell_style)],
        [Paragraph("BYOD Móvil", table_cell_bold), Paragraph("<code>evidencias/mobile/koodous_malwarebytes_evidence.json</code>", table_cell_style), Paragraph("JSON Telemetría", table_cell_style), Paragraph("Firmas de malware, escaneo antimalware y PUPs analizados", table_cell_style)],
        [Paragraph("BYOD Móvil", table_cell_bold), Paragraph("<code>evidencias/mobile/auditoria_real_samsung_a55.log</code>", table_cell_style), Paragraph("Log ADB Vivo", table_cell_style), Paragraph("Telemetría en terminal físico: Knox User 150, batería 27,5 °C, 79 apps", table_cell_style)],
        [Paragraph("Web DAST", table_cell_bold), Paragraph("<code>evidencias/web_dast/owasp_zap_root_ca.cer</code>", table_cell_style), Paragraph("Certificado X.509", table_cell_style), Paragraph("Certificado CA Raíz dinámico de OWASP ZAP importado en navegador", table_cell_style)],
        [Paragraph("Web DAST", table_cell_bold), Paragraph("<code>evidencias/web_dast/breakpoint_mitm_trace.log</code>", table_cell_style), Paragraph("Log HTTP MitM", table_cell_style), Paragraph("Registro de intercepción y edición de parámetros en memoria antes de envío", table_cell_style)],
        [Paragraph("Web DAST", table_cell_bold), Paragraph("<code>evidencias/web_dast/fuzzer_sqli_jbrofuzz.log</code>", table_cell_style), Paragraph("Log Fuzzer ZAP", table_cell_style), Paragraph("Reporte de pruebas automatizadas con diccionarios de inyección jbrofuzz", table_cell_style)],
        [Paragraph("Web DAST", table_cell_bold), Paragraph("<code>evidencias/web_dast/sqli_login_form.png</code>", table_cell_style), Paragraph("Imagen PNG", table_cell_style), Paragraph("Vector de inyección SQL formulado en pantalla de login", table_cell_style)],
        [Paragraph("Web DAST", table_cell_bold), Paragraph("<code>evidencias/web_dast/sqli_admin_authenticated.jpg</code>", table_cell_style), Paragraph("Imagen JPG", table_cell_style), Paragraph("Bypass de autenticación exitoso logrando sesión de Superadministrador", table_cell_style)],
        [Paragraph("Web DAST", table_cell_bold), Paragraph("<code>evidencias/web_dast/sqli_zap_history.png</code>", table_cell_style), Paragraph("Imagen PNG", table_cell_style), Paragraph("Registro en historial ZAP de petición alterada (Req. ID 168, status 302)", table_cell_style)],
        [Paragraph("Web DAST", table_cell_bold), Paragraph("<code>evidencias/web_dast/xss_alert_browser.jpg</code>", table_cell_style), Paragraph("Imagen JPG", table_cell_style), Paragraph("Cuadro de diálogo emergente disparado por código XSS reflejado", table_cell_style)],
        [Paragraph("Web DAST", table_cell_bold), Paragraph("<code>evidencias/web_dast/xss_zap_history.jpg</code>", table_cell_style), Paragraph("Imagen JPG", table_cell_style), Paragraph("Registro en ZAP con alerta de severidad Media en endpoint dns-lookup (Req. 177)", table_cell_style)],
        [Paragraph("Web DAST", table_cell_bold), Paragraph("<code>evidencias/web_dast/path_traversal_browser.jpg</code>", table_cell_style), Paragraph("Imagen JPG", table_cell_style), Paragraph("Volcado y exfiltración del archivo de cuentas /etc/passwd en navegador", table_cell_style)],
        [Paragraph("Scripts", table_cell_bold), Paragraph("<code>scripts/hardening_sistema1.sh</code>", table_cell_style), Paragraph("Bash Script", table_cell_style), Paragraph("Script automatizado unificado para remediación y bastionado de Linux", table_cell_style)],
        [Paragraph("Scripts", table_cell_bold), Paragraph("<code>scripts/hardening_browser.sh</code>", table_cell_style), Paragraph("Bash Script", table_cell_style), Paragraph("Script de configuración y copia de directivas empresariales Firefox", table_cell_style)],
        [Paragraph("Scripts", table_cell_bold), Paragraph("<code>scripts/generate_mobile_evidence.py</code>", table_cell_style), Paragraph("Python Script", table_cell_style), Paragraph("Generador de evidencias y telemetría móvil", table_cell_style)],
        [Paragraph("Scripts", table_cell_bold), Paragraph("<code>scripts/generate_pdf_report.py</code>", table_cell_style), Paragraph("Python Script", table_cell_style), Paragraph("Generador automatizado del informe técnico oficial en formato PDF", table_cell_style)],
    ]
    t_master = Table(master_ev_data, colWidths=[20 * mm, 62 * mm, 24 * mm, 68 * mm])
    t_master.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 1.6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.6),
    ]))
    story.append(t_master)

    # Construcción final del documento con numeración de dos pasadas y marca de agua
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF generado con éxito en: {output_pdf}")

    try:
        shutil.copy2(output_pdf, lab_pdf)
        print(f"PDF copiado a: {lab_pdf}")
    except Exception as e:
        print("Nota: Archivo lab_pdf bloqueado por visor abierto, actualizado en root.")

if __name__ == "__main__":
    build_pdf()
