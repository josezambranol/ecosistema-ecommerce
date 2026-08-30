# Taller Práctico: Implementación de un Ecosistema Mínimo de Microservicios con Spring Boot

**Asignatura:** Electiva I – Arquitectura de Microservicios con Spring Boot  
**Institución:** Fundación Universitaria Tecnológico Comfenalco — V Semestre (2026-I)  

---

## 👥 Integrantes del Equipo
- **José Daniel Zambrano**
- **Carlos Mario Bechara**
- **Rafael Sarmiento Peña**

---

## 📌 1. Objetivo de Aprendizaje
Construir, configurar, ejecutar y conectar dos microservicios independientes desarrollados con **Spring Boot 3** y **Java 21**, aplicando principios de **responsabilidad única (Single Responsibility Principle)** y **bajo acoplamiento**, estableciendo comunicación síncrona HTTP mediante `RestTemplate` y verificando el ecosistema mediante pruebas de API.

---

## 🏢 2. Escenario de Negocio y Bounded Contexts

El ecosistema se basa en un dominio de comercio electrónico (e-commerce) dividido en dos bounded contexts claramente diferenciados:

```
                  ┌────────────────────────────────────────┐
                  │              Cliente API               │
                  └──────────────┬──────────────────┬──────┘
                                 │                  │
               1. Crear/Listar   │                  │ 3. Crear Pedido
                  Productos      │                  │    (POST /api/pedidos)
                                 ▼                  ▼
                    ┌─────────────────┐       ┌─────────────────┐
                    │producto-service │       │ pedido-service  │
                    │  (Puerto 8081)  │       │  (Puerto 8082)  │
                    └────────┬────────┘       └────────┬────────┘
                             ▲                         │
                             │  2. Consulta Síncrona   │
                             │     HTTP (RestTemplate) │
                             └─────────────────────────┘
                                   GET /api/productos/{id}
```

| Microservicio | Puerto | Responsabilidad (Bounded Context) | Base de Datos |
| :--- | :---: | :--- | :--- |
| **`producto-service`** | `8081` | Gestiona el catálogo de productos: creación, consulta individual por ID, listado general y verificación de existencias. | H2 en memoria (`productodb`) |
| **`pedido-service`** | `8082` | Gestiona los pedidos de los clientes. Al recibir una orden, consulta a `producto-service` para validar la existencia y precio del producto, calcula el total y registra el pedido. | H2 en memoria (`pedidodb`) |

---

## 📁 3. Estructura del Ecosistema

El proyecto está estructurado con dos microservicios autónomos e independientes dentro del repositorio:

```
ecosistema-ecommerce/
├── .gitignore
├── README.md
├── DOCUMENTO_ENTREGABLE.md
│
├── producto-service/                              # Microservicio de Catálogo (Puerto 8081)
│   ├── pom.xml
│   └── src/
│       ├── main/
│       │   ├── java/com/ecosistema/producto_service/
│       │   │   ├── ProductoServiceApplication.java
│       │   │   ├── model/
│       │   │   │   └── Producto.java              # Entidad JPA: id, nombre, precio, stock
│       │   │   ├── repository/
│       │   │   │   └── ProductoRepository.java    # Interfaz JpaRepository<Producto, Long>
│       │   │   └── controller/
│       │   │       └── ProductoController.java    # REST: GET /api/productos, POST, etc.
│       │   └── resources/
│       │       └── application.yml                # Config: Puerto 8081, H2, Consola H2
│       └── test/
│
└── pedido-service/                                # Microservicio de Pedidos (Puerto 8082)
    ├── pom.xml
    └── src/
        ├── main/
        │   ├── java/com/ecosistema/pedido_service/
        │   │   ├── PedidoServiceApplication.java
        │   │   ├── config/
        │   │   │   └── RestTemplateConfig.java    # Bean de comunicación HTTP RestTemplate
        │   │   ├── model/
        │   │   │   └── Pedido.java                # Entidad JPA: id, productoId, cantidad, total, estado
        │   │   ├── dto/
        │   │   │   └── Producto.java              # DTO para deserializar respuesta de producto-service
        │   │   ├── repository/
        │   │   │   └── PedidoRepository.java      # Interfaz JpaRepository<Pedido, Long>
        │   │   ├── service/
        │   │   │   └── PedidoService.java         # Lógica: llamada a producto-service y cálculo de total
        │   │   ├── controller/
        │   │   │   └── PedidoController.java      # REST: POST /api/pedidos?productoId=X&cantidad=Y
        │   │   └── exception/
        │   │       └── GlobalExceptionHandler.java# Control de errores (404 Not Found, 503 Service Unavailable)
        │   └── resources/
        │       └── application.yml                # Config: Puerto 8082, H2, URL producto-service
        └── test/
```

---

## 🛠️ 4. Paso a Paso de la Construcción

### Parte 2 — Construcción de `producto-service`

1. **Configuración (`producto-service/src/main/resources/application.yml`):**
   - Puerto de escucha asignado: `8081`.
   - Conexión a base de datos en memoria H2 (`jdbc:h2:mem:productodb`).
   - Habilitación de la consola Web de H2 en `/h2-console`.

2. **Entidad JPA (`Producto.java`):**
   - Atributos: `id` (Generación `IDENTITY`), `nombre` (`String`), `precio` (`BigDecimal`), `stock` (`Integer`).
   - Anotaciones Lombok: `@Data`, `@NoArgsConstructor`, `@AllArgsConstructor`.

3. **Capa de Persistencia (`ProductoRepository.java`):**
   - Extiende `JpaRepository<Producto, Long>` heredando operaciones CRUD automáticas.

4. **Capa de Exposición REST (`ProductoController.java`):**
   - Endpoint `GET /api/productos`: Retorna el listado completo de productos.
   - Endpoint `GET /api/productos/{id}`: Retorna un producto específico o `404 Not Found` si no existe.
   - Endpoint `POST /api/productos`: Recibe un JSON en el body y persiste el nuevo producto.

---

### Parte 3 — Construcción de `pedido-service`

1. **Configuración (`pedido-service/src/main/resources/application.yml`):**
   - Puerto de escucha asignado: `8082`.
   - Conexión a su propia base de datos H2 (`jdbc:h2:mem:pedidodb`).
   - Declaración de la propiedad `producto-service.url: http://localhost:8081` para la comunicación entre servicios.

2. **Entidad JPA y DTOs:**
   - **`Pedido.java`:** Atributos `id`, `productoId`, `cantidad`, `total` (`BigDecimal`), `estado` (`String`).
   - **`Producto.java` (DTO):** Representación desacoplada del producto que se recibe al consultar `producto-service`.

3. **Configuración del Cliente HTTP (`RestTemplateConfig.java`):**
   - Registro del Bean `@Bean public RestTemplate restTemplate()` en el contenedor de Spring.

4. **Lógica de Negocio y Comunicación Síncrona (`PedidoService.java`):**
   - Inyecta `RestTemplate` y la URL configurada mediante `@Value("${producto-service.url}")`.
   - Realiza la llamada HTTP GET `restTemplate.getForObject(productoServiceUrl + "/api/productos/" + productoId, Producto.class)`.
   - Si el producto no existe (retorna 404), captura la excepción y lanza `IllegalArgumentException("Producto no encontrado: " + productoId)`.
   - Si `producto-service` no se encuentra disponible (servicio caído), captura `RestClientException` y lanza `IllegalStateException`.
   - Calcula el total del pedido multiplicando el precio unitario por la cantidad: `producto.getPrecio().multiply(BigDecimal.valueOf(cantidad))`.
   - Asigna el estado `"CREADO"` y guarda la orden en `PedidoRepository`.

5. **Capa Controladora y Manejo de Excepciones:**
   - **`PedidoController.java`:** Expone `POST /api/pedidos?productoId={id}&cantidad={cantidad}`.
   - **`GlobalExceptionHandler.java`:** Captura las excepciones de negocio y genera respuestas JSON limpias y estructuradas con códigos HTTP adecuados (404 para productos inexistentes y 503 para caídas del servicio de productos), previniendo respuestas de error 500 no controladas.

---

## 🚀 5. Cómo Ejecutar el Proyecto Localmente

### Prerrequisitos
- **Java 21 LTS** (`java -version`)
- **Maven 3.9+** (`mvn -version`)

### Paso 1: Levantar `producto-service` (Terminal 1)
```powershell
cd producto-service
mvn spring-boot:run
```
*El servicio estará activo en `http://localhost:8081`.*

### Paso 2: Levantar `pedido-service` (Terminal 2)
```powershell
cd pedido-service
mvn spring-boot:run
```
*El servicio estará activo en `http://localhost:8082`.*

---

## 🧪 6. Guía de Pruebas con Postman (5 Pruebas Paso a Paso)

Con ambos microservicios en ejecución, ejecutar en Postman (o mediante cURL / PowerShell) la siguiente secuencia:

### Prueba 1: Crear Producto en `producto-service`
- **Método:** `POST`
- **URL:** `http://localhost:8081/api/productos`
- **Headers:** `Content-Type: application/json`
- **Body (raw JSON):**
  ```json
  {
    "nombre": "Laptop Gamer",
    "precio": 3500000.00,
    "stock": 10
  }
  ```
- **Respuesta (200 OK):**
  ```json
  {
    "id": 1,
    "nombre": "Laptop Gamer",
    "precio": 3500000.00,
    "stock": 10
  }
  ```

---

### Prueba 2: Confirmar Registro de Productos (GET)
- **Método:** `GET`
- **URL:** `http://localhost:8081/api/productos`
- **Respuesta (200 OK):**
  ```json
  [
    {
      "id": 1,
      "nombre": "Laptop Gamer",
      "precio": 3500000.00,
      "stock": 10
    }
  ]
  ```

---

### Prueba 3 & 4: Crear Pedido y Verificar Total Calculado
- **Método:** `POST`
- **URL:** `http://localhost:8082/api/pedidos?productoId=1&cantidad=2`
- **Respuesta (200 OK):**
  ```json
  {
    "id": 1,
    "productoId": 1,
    "cantidad": 2,
    "total": 7000000.00,
    "estado": "CREADO"
  }
  ```
  *(Se comprueba que `3500000.00 * 2 = 7000000.00` se calculó en base al precio real del producto).*

---

### Prueba 5: Caso de Error Controlado — Producto Inexistente
- **Método:** `POST`
- **URL:** `http://localhost:8082/api/pedidos?productoId=999&cantidad=2`
- **Respuesta (404 Not Found):**
  ```json
  {
    "status": 404,
    "error": "Not Found",
    "message": "Producto no encontrado: 999",
    "timestamp": "2026-08-30T..."
  }
  ```

---

### Punto de Verificación Clave (Resiliencia): `producto-service` Caído
- **Procedimiento:** Detener `producto-service` (Ctrl+C en la Terminal 1) y realizar un POST de creación de pedido a `pedido-service`.
- **URL:** `POST http://localhost:8082/api/pedidos?productoId=1&cantidad=2`
- **Respuesta (503 Service Unavailable):**
  ```json
  {
    "status": 503,
    "error": "Service Unavailable",
    "message": "Error de comunicación: producto-service no disponible",
    "timestamp": "2026-08-30T..."
  }
  ```
  *El servicio no colapsa ni cae, responde de manera elegante y controlada.*

---

## 📝 7. Preguntas de Reflexión Arquitectural (Entregable Sección 8)

### 1. ¿Qué responsabilidad tiene cada microservicio?
- **`producto-service`:** Administra de manera exclusiva el catálogo de productos (creación, lectura, inventario) y garantiza el aislamiento de sus datos a través de su propia base de datos (`productodb`).
- **`pedido-service`:** Gestiona el ciclo de vida de las compras de los clientes (órdenes de pedido). Depende síncronamente de `producto-service` para la validación y cotización de los artículos, manteniendo sus registros aislados en su base de datos (`pedidodb`).

### 2. ¿Qué pasaría si necesitáramos escalar solo `producto-service`?
Al tratarse de microservicios independientes, podemos realizar **escalado horizontal selectivo** levantando múltiples instancias de `producto-service` (por ejemplo, en puertos 8081, 8083, 8084 o múltiples pods en Kubernetes) optimizando recursos, ya que en el e-commerce las consultas de productos superan en gran proporción a las compras efectivas.  
Sin embargo, con la arquitectura actual donde `pedido-service` tiene la URL quemada (`http://localhost:8081`), no se podría aprovechar este escalamiento sin un balanceador de carga o un registro de servicios dinámico.

### 3. ¿Qué limitación notaron al tener la URL del otro servicio escrita directamente en `application.yml`?
- **Acoplamiento rígido de red:** Obliga a conocer de antemano la IP y puerto exactos. Cualquier cambio de infraestructura requiere modificar archivos y reiniciar el servicio.
- **Sin balanceo de carga integrado:** No es posible distribuir peticiones entre réplicas de forma transparente.
- **Sin tolerancia a fallos dinámica:** No hay detección automática de instancias caídas ni enrutamiento hacia instancias sanas.
- **Fundamento para Service Discovery:** Esto justifica directamente el uso de **Spring Cloud Config Server** (Semana 6) y **Eureka / Service Discovery** (Semana 7).
