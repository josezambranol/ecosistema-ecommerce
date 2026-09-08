import base64
import os
import subprocess
from pathlib import Path
import io
import fitz  # PyMuPDF
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter

BASE_DIR = Path(r"C:\Users\josed\ecosistema-ecommerce")
DOCS_DIR = BASE_DIR / "docs" / "screenshots"
HTML_OUTPUT = BASE_DIR / "documento_entregable.html"
RAW_PDF = BASE_DIR / "raw_documento.pdf"
FINAL_PDF = BASE_DIR / "DOCUMENTO_ENTREGABLE.pdf"
PREVIEW_DIR = BASE_DIR / "pdf_previews"

PREVIEW_DIR.mkdir(exist_ok=True)

def get_base64_img(filename):
    path = DOCS_DIR / filename
    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"

img_p1 = get_base64_img("prueba1_crear_producto.png")
img_p2 = get_base64_img("prueba2_listar_productos.png")
img_p3 = get_base64_img("prueba3_crear_pedido.png")
img_p5 = get_base64_img("prueba5_error_404.png")
img_res = get_base64_img("prueba_resiliencia_503.png")

html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Documento de Entrega — Taller Básico de Microservicios</title>
    <style>
        @page {{
            size: letter;
            margin: 16mm 16mm 16mm 16mm;
        }}

        *, *:before, *:after {{
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', system-ui, -apple-system, Roboto, Helvetica, Arial, sans-serif;
            font-size: 9.7pt;
            line-height: 1.44;
            color: #1e293b;
            background-color: #ffffff;
            margin: 0;
            padding: 0;
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
        }}

        /* Encabezado institucional */
        .doc-header {{
            border-bottom: 2px solid #0284c7;
            padding-bottom: 10px;
            margin-bottom: 12px;
        }}

        .doc-title {{
            font-size: 15.5pt;
            font-weight: 700;
            color: #0f172a;
            margin: 0 0 6px 0;
            letter-spacing: -0.02em;
        }}

        .meta-card {{
            background-color: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 5px;
            padding: 8px 12px;
            margin-bottom: 8px;
            font-size: 8.8pt;
            color: #334155;
        }}

        .meta-row {{
            margin-bottom: 3px;
        }}

        .meta-row:last-child {{
            margin-bottom: 0;
        }}

        .meta-label {{
            font-weight: 600;
            color: #0f172a;
        }}

        .note-box {{
            background-color: #f0f9ff;
            border-left: 3.5px solid #0284c7;
            padding: 6px 10px;
            font-size: 8.6pt;
            color: #0369a1;
            margin-bottom: 12px;
            border-radius: 0 4px 4px 0;
        }}

        /* Secciones */
        h2.section-title {{
            font-size: 12pt;
            font-weight: 700;
            color: #0f172a;
            margin-top: 0;
            margin-bottom: 10px;
            padding-bottom: 4px;
            border-bottom: 1px solid #cbd5e1;
            break-after: avoid;
            page-break-after: avoid;
        }}

        h3.subsection-title {{
            font-size: 10.5pt;
            font-weight: 600;
            color: #0f172a;
            margin-top: 11px;
            margin-bottom: 5px;
            break-after: avoid;
            page-break-after: avoid;
        }}

        p {{
            margin: 0 0 6px 0;
            text-align: justify;
        }}

        strong {{
            color: #0f172a;
        }}

        code {{
            font-family: 'Cascadia Code', Consolas, 'Courier New', monospace;
            font-size: 8.6pt;
            background-color: #f1f5f9;
            color: #0f172a;
            padding: 1px 4px;
            border-radius: 3px;
            border: 1px solid #e2e8f0;
        }}

        ol {{
            margin: 0 0 6px 0;
            padding-left: 20px;
        }}

        li {{
            margin-bottom: 3px;
            text-align: justify;
        }}

        hr.divider {{
            border: none;
            border-top: 1px solid #e2e8f0;
            margin: 10px 0;
        }}

        /* Anexo y Evidencias */
        .page-break {{
            page-break-before: always;
            break-before: always;
        }}

        .evidence-card {{
            page-break-inside: avoid;
            break-inside: avoid;
            margin-top: 10px;
            margin-bottom: 16px;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            background-color: #ffffff;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
        }}

        .evidence-header {{
            background-color: #f8fafc;
            border-bottom: 1px solid #e2e8f0;
            padding: 9px 14px;
            font-size: 9.8pt;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 6px;
        }}

        .evidence-title {{
            font-weight: 700;
            color: #0f172a;
        }}

        .evidence-endpoint {{
            font-family: 'Cascadia Code', Consolas, monospace;
            font-size: 8.6pt;
            background-color: #e0f2fe;
            color: #0369a1;
            padding: 2px 6px;
            border-radius: 4px;
            border: 1px solid #bae6fd;
            word-break: break-all;
        }}

        .evidence-detail {{
            padding: 8px 14px 6px 14px;
            font-size: 9.2pt;
            color: #334155;
            line-height: 1.42;
        }}

        .evidence-image-container {{
            padding: 0 14px 10px 14px;
            text-align: center;
        }}

        .evidence-img {{
            max-width: 100%;
            height: auto;
            border: 1px solid #cbd5e1;
            border-radius: 4px;
            display: block;
            margin: 0 auto;
        }}

        .evidence-caption {{
            font-size: 8.3pt;
            color: #64748b;
            margin-top: 5px;
            font-style: italic;
        }}
    </style>
</head>
<body>

    <!-- PÁGINA 1: PREGUNTAS TEÓRICAS -->
    <header class="doc-header">
        <h1 class="doc-title">Documento de Entrega — Taller Básico de Microservicios</h1>
        
        <div class="meta-card">
            <div class="meta-row">
                <span class="meta-label">Asignatura:</span> Electiva I: Arquitectura de Microservicios con Spring Boot &nbsp;|&nbsp; 
                <span class="meta-label">Semestre:</span> V Semestre · 2026-I
            </div>
            <div class="meta-row">
                <span class="meta-label">Institución:</span> Fundación Universitaria Tecnológico Comfenalco
            </div>
            <div class="meta-row">
                <span class="meta-label">Integrantes:</span> José Daniel Zambrano · Carlos Mario Bechara · Rafael Sarmiento Peña
            </div>
        </div>

        <div class="note-box">
            Código fuente, instrucciones de ejecución y capturas de las pruebas en Postman: ver <code>README.md</code>.
        </div>
    </header>

    <!-- PREGUNTA 1 -->
    <section>
        <h3 class="subsection-title">1. ¿Qué responsabilidad tiene cada microservicio?</h3>
        
        <p>
            <strong><code>producto-service</code> (puerto 8081) — catálogo.</strong> Es el dueño exclusivo de los productos: 
            los crea, los lista, los consulta por ID y expone sus existencias. Ningún otro servicio toca su base de datos 
            (<code>productodb</code>); quien necesite un producto debe pedírselo por HTTP.
        </p>

        <p>
            <strong><code>pedido-service</code> (puerto 8082) — pedidos.</strong> Es el dueño de las órdenes de compra. Al recibir 
            un pedido consulta a <code>producto-service</code> para verificar que el producto exista y obtener su precio, calcula 
            <code>total = precio × cantidad</code>, marca el pedido como <code>CREADO</code> y lo guarda en su propia base (<code>pedidodb</code>).
        </p>

        <p>
            La separación se sostiene en dos decisiones: <strong>cada servicio tiene su propia base de datos</strong> y 
            <strong>la única vía de contacto es HTTP</strong>. Eso es lo que permite desplegarlos, versionarlos y escalarlos por separado.
        </p>
    </section>

    <hr class="divider">

    <!-- PREGUNTA 2 -->
    <section>
        <h3 class="subsection-title">2. ¿Qué pasaría si necesitáramos escalar solo <code>producto-service</code>?</h3>
        
        <p>
            Podríamos hacerlo sin tocar <code>pedido-service</code>, y es justo lo que conviene: en un e-commerce, la gente 
            consulta el catálogo muchísimo más de lo que efectivamente compra. Levantar tres o cinco instancias del 
            catálogo, dejando una sola de pedidos, aprovecha los recursos donde hace falta. Esa es la ventaja 
            concreta frente al monolito, donde para atender más consultas de productos habría que replicar 
            <em>también</em> toda la lógica de pedidos.
        </p>

        <p>
            <strong>Pero con el diseño actual no lo aprovecharíamos.</strong> <code>pedido-service</code> apunta a una dirección fija, 
            <code>http://localhost:8081</code>, así que seguiría enviando el 100 % del tráfico a una sola instancia mientras 
            las demás quedan ociosas. Para que el escalado sirva haría falta un balanceador delante del catálogo, o 
            un registro de servicios que permita descubrir las réplicas y repartir entre ellas.
        </p>
    </section>

    <hr class="divider">

    <!-- PREGUNTA 3 -->
    <section>
        <h3 class="subsection-title">3. ¿Qué limitación notaron al tener la URL del otro servicio escrita en <code>application.yml</code>?</h3>
        
        <p>
            Que <strong>acopla el servicio a una topología de red concreta</strong>. En detalle:
        </p>

        <ol>
            <li>
                <strong>Hay que conocer host y puerto de antemano.</strong> Si el catálogo cambia de dirección —otro servidor, 
                otro puerto, un contenedor nuevo— hay que editar el archivo y reiniciar <code>pedido-service</code>.
            </li>
            <li>
                <strong>No hay balanceo de carga.</strong> Una URL fija apunta a una sola instancia; no existe forma de repartir 
                peticiones entre varias réplicas.
            </li>
            <li>
                <strong>No hay detección de caídas.</strong> Si esa instancia muere, <code>pedido-service</code> sigue insistiendo contra una 
                dirección muerta. Nuestro manejo de errores lo convierte en un <code>503</code> controlado, pero el servicio no 
                puede reintentar contra otra instancia sana porque no sabe que existen.
            </li>
            <li>
                <strong>La configuración vive dentro del artefacto.</strong> Cambiar un valor obliga a recompilar o redesplegar, 
                y cada entorno (local, pruebas, producción) necesita su propia versión del archivo.
            </li>
        </ol>

        <p>
            Estas tres limitaciones son exactamente el problema que resuelven los temas siguientes del curso: 
            <strong>Config Server</strong> (Semana 6) externaliza la configuración para no tener que reconstruir el servicio, y 
            <strong>Eureka / Service Discovery</strong> (Semana 7) elimina la necesidad de conocer host y puerto: <code>pedido-service</code> 
            pedirá el servicio por su nombre lógico, <code>producto-service</code>, y el registro le dirá qué instancias hay 
            disponibles en ese momento.
        </p>
    </section>

    <!-- PÁGINA 2: ANEXO - PRUEBA 1 -->
    <div class="page-break"></div>

    <section>
        <h2 class="section-title">Anexo — Evidencias de las pruebas en Postman</h2>
        
        <p>
            Ejecución de la colección <code>ecosistema_ecommerce.postman_collection.json</code> contra ambos microservicios 
            levantados en <code>localhost:8081</code> y <code>localhost:8082</code>. Cada captura muestra la petición enviada y la 
            respuesta real del servicio, con su código de estado y su cuerpo JSON.
        </p>

        <div class="evidence-card">
            <div class="evidence-header">
                <span class="evidence-title">Prueba 1 — Crear producto</span>
                <span class="evidence-endpoint">POST http://localhost:8081/api/productos</span>
            </div>
            <div class="evidence-detail">
                <strong>Resultado esperado y obtenido:</strong> Código <code>200 OK</code> con el objeto JSON registrado: 
                <code>&#123; "id": 1, "nombre": "Laptop Gamer", "precio": 3500000.00, "stock": 10 &#125;</code>.
            </div>
            <div class="evidence-image-container">
                <img class="evidence-img" src="{img_p1}" alt="Prueba 1 - Crear producto">
                <div class="evidence-caption">Captura 1: Inserción y persistencia exitosa de producto en base de datos H2 de producto-service.</div>
            </div>
        </div>
    </section>

    <!-- PÁGINA 3: PRUEBA 2 -->
    <div class="page-break"></div>

    <section>
        <div class="evidence-card">
            <div class="evidence-header">
                <span class="evidence-title">Prueba 2 — Listar productos</span>
                <span class="evidence-endpoint">GET http://localhost:8081/api/productos</span>
            </div>
            <div class="evidence-detail">
                <strong>Resultado esperado y obtenido:</strong> Código <code>200 OK</code> retornando el array JSON con la totalidad 
                de los productos registrados en el catálogo de <code>producto-service</code>.
            </div>
            <div class="evidence-image-container">
                <img class="evidence-img" src="{img_p2}" alt="Prueba 2 - Listar productos">
                <div class="evidence-caption">Captura 2: Listado completo de existencias en catálogo expuesto a clientes HTTP.</div>
            </div>
        </div>
    </section>

    <!-- PÁGINA 4: PRUEBAS 3 Y 4 -->
    <div class="page-break"></div>

    <section>
        <div class="evidence-card">
            <div class="evidence-header">
                <span class="evidence-title">Pruebas 3 y 4 — Crear pedido y verificar el total</span>
                <span class="evidence-endpoint">POST http://localhost:8082/api/pedidos?productoId=1&amp;cantidad=2</span>
            </div>
            <div class="evidence-detail">
                <strong>Resultado esperado y obtenido:</strong> Código <code>200 OK</code>. <code>pedido-service</code> consulta 
                síncronamente a <code>producto-service</code> vía <code>RestTemplate</code>, valida la existencia del producto y calcula 
                el total: <code>3 500 000,00 × 2 = 7 000 000,00</code>. El pedido queda almacenado con estado <code>CREADO</code>.
            </div>
            <div class="evidence-image-container">
                <img class="evidence-img" src="{img_p3}" alt="Pruebas 3 y 4 - Crear pedido">
                <div class="evidence-caption">Captura 3: Creación de pedido y comunicación interservicios síncrona exitosa.</div>
            </div>
        </div>
    </section>

    <!-- PÁGINA 5: PRUEBA 5 -->
    <div class="page-break"></div>

    <section>
        <div class="evidence-card">
            <div class="evidence-header">
                <span class="evidence-title">Prueba 5 — Producto inexistente</span>
                <span class="evidence-endpoint">POST http://localhost:8082/api/pedidos?productoId=999&amp;cantidad=2</span>
            </div>
            <div class="evidence-detail">
                <strong>Resultado esperado y obtenido:</strong> Código <code>404 Not Found</code> con el mensaje 
                <code>"Producto no encontrado: 999"</code>. El sistema intercepta el error mediante <code>GlobalExceptionHandler</code> 
                respondiendo de manera controlada y estructurada sin comprometer la estabilidad del servicio.
            </div>
            <div class="evidence-image-container">
                <img class="evidence-img" src="{img_p5}" alt="Prueba 5 - Error 404">
                <div class="evidence-caption">Captura 4: Manejo controlado de excepción de dominio cuando el producto solicitado no existe.</div>
            </div>
        </div>
    </section>

    <!-- PÁGINA 6: PUNTO DE RESILIENCIA -->
    <div class="page-break"></div>

    <section>
        <div class="evidence-card">
            <div class="evidence-header">
                <span class="evidence-title">Punto de verificación clave — <code>producto-service</code> caído</span>
                <span class="evidence-endpoint">POST http://localhost:8082/api/pedidos?productoId=1&amp;cantidad=2</span>
            </div>
            <div class="evidence-detail">
                <strong>Resultado esperado y obtenido:</strong> Con el catálogo detenido, la petición devuelve 
                <code>503 Service Unavailable</code> y el mensaje <code>"Error de comunicación: producto-service no disponible"</code>. 
                <code>pedido-service</code> absorbe la indisponibilidad de su dependencia sin caerse ni propagar excepciones no deseadas.
            </div>
            <div class="evidence-image-container">
                <img class="evidence-img" src="{img_res}" alt="Resiliencia - Error 503">
                <div class="evidence-caption">Captura 5: Tolerancia a fallos y resiliencia ante caída del microservicio dependiente.</div>
            </div>
        </div>
    </section>

</body>
</html>
"""

with open(HTML_OUTPUT, "w", encoding="utf-8") as f:
    f.write(html_content)

print("HTML escrito correctamente.")

# Paso 1: Generar RAW PDF sin cabeceras/pies de Chrome
chrome_exe = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
cmd = [
    chrome_exe,
    "--headless=new",
    "--disable-gpu",
    "--no-pdf-header-footer",
    f"--print-to-pdf={RAW_PDF}",
    str(HTML_OUTPUT)
]

subprocess.run(cmd, check=True)
print(f"RAW PDF generado en {RAW_PDF}")

# Paso 2: Crear Overlay con ReportLab (Encabezados elegantes y numeración de página limpia)
reader = PdfReader(RAW_PDF)
total_pages = len(reader.pages)
print(f"Páginas detectadas: {total_pages}")

packet = io.BytesIO()
can = canvas.Canvas(packet, pagesize=letter)
width, height = letter

for p_num in range(1, total_pages + 1):
    can.saveState()
    
    # Línea y texto de pie de página en todas las páginas
    can.setStrokeColorRGB(0.88, 0.91, 0.94)  # #e2e8f0
    can.setLineWidth(0.75)
    can.line(45.35, 36, width - 45.35, 36)
    
    can.setFont("Helvetica", 8)
    can.setFillColorRGB(0.39, 0.45, 0.55)  # #64748b
    can.drawString(45.35, 24, "Fundación Universitaria Tecnológico Comfenalco · V Semestre 2026-I")
    
    page_text = f"Página {p_num} de {total_pages}"
    can.drawRightString(width - 45.35, 24, page_text)
    
    # En páginas 2 a 6, agregar encabezado superior sutil
    if p_num > 1:
        can.line(45.35, height - 32, width - 45.35, height - 32)
        can.drawString(45.35, height - 26, "Taller Básico de Microservicios · Electiva I")
        can.drawRightString(width - 45.35, height - 26, "Anexo: Evidencias de Pruebas en Postman")
        
    can.restoreState()
    can.showPage()

can.save()
packet.seek(0)

# Paso 3: Combinar Overlay con el RAW PDF
overlay_reader = PdfReader(packet)
writer = PdfWriter()

for i, page in enumerate(reader.pages):
    page.merge_page(overlay_reader.pages[i])
    writer.add_page(page)

with open(FINAL_PDF, "wb") as f_out:
    writer.write(f_out)

print(f"PDF Final generado exitosamente en: {FINAL_PDF} (Tamano: {FINAL_PDF.stat().st_size} bytes)")

# Paso 4: Exportar imágenes de cada página para verificación visual
doc = fitz.open(FINAL_PDF)
for i, page in enumerate(doc):
    pix = page.get_pixmap(dpi=150)
    out_img = PREVIEW_DIR / f"pagina_{i+1}.png"
    pix.save(str(out_img))
    print(f"Preview guardada: {out_img}")

# Limpiar raw pdf intermedio
if RAW_PDF.exists():
    RAW_PDF.unlink()
