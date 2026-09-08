# Ecosistema Mínimo de Microservicios con Spring Boot

**Taller Básico — Electiva I: Arquitectura de Microservicios con Spring Boot**
Fundación Universitaria Tecnológico Comfenalco · V Semestre · 2026-I

### Integrantes
- José Daniel Zambrano
- Carlos Mario Bechara
- Rafael Sarmiento Peña

---

## 1. Objetivo

Construir, ejecutar y conectar **dos microservicios independientes** en Spring Boot, aplicando
responsabilidad única y bajo acoplamiento, y estableciendo **comunicación síncrona HTTP** entre ellos
mediante `RestTemplate`.

## 2. Arquitectura y bounded contexts

```
                    ┌────────────────────────┐
                    │      Cliente API       │
                    │       (Postman)        │
                    └───────┬────────────┬───┘
       1. Crear / listar    │            │   3. Crear pedido
          productos         │            │      POST /api/pedidos
                            ▼            ▼
              ┌──────────────────┐   ┌──────────────────┐
              │ producto-service │   │  pedido-service  │
              │   puerto 8081    │   │   puerto 8082    │
              │  H2: productodb  │   │  H2: pedidodb    │
              └────────▲─────────┘   └─────────┬────────┘
                       │                       │
                       │  2. Consulta síncrona │
                       │     RestTemplate      │
                       └───────────────────────┘
                     GET /api/productos/{id}
```

| Microservicio | Puerto | Responsabilidad (bounded context) | Base de datos |
| :--- | :---: | :--- | :--- |
| `producto-service` | 8081 | Catálogo de productos: creación, consulta por ID, listado y exposición de existencias. | H2 en memoria (`productodb`) |
| `pedido-service` | 8082 | Pedidos de clientes. Al crear uno, consulta a `producto-service` para validar que el producto exista y obtener su precio, calcula el total y lo persiste. | H2 en memoria (`pedidodb`) |

Cada servicio tiene su **propia base de datos**: no comparten esquema ni acceden a las tablas del otro.
Toda la comunicación entre ellos pasa por HTTP.

## 3. Stack técnico

| Componente | Versión |
| :--- | :--- |
| Java | 21 (LTS) |
| Spring Boot | 3.5.16 |
| Maven | 3.9.x |
| Persistencia | Spring Data JPA + H2 en memoria |
| Comunicación entre servicios | `RestTemplate` (opción 6.3A de la guía) |
| Utilidades | Lombok |

## 4. Estructura del repositorio

```
ecosistema-ecommerce/
├── README.md                                  ← este documento
├── DOCUMENTO_ENTREGABLE.md                    ← documento breve con la reflexión
├── ecosistema_ecommerce.postman_collection.json
├── docs/screenshots/                          ← evidencias de las pruebas en Postman
│
├── producto-service/                          # puerto 8081
│   ├── pom.xml
│   └── src/main/java/com/ecosistema/producto_service/
│       ├── ProductoServiceApplication.java
│       ├── model/Producto.java                # entidad JPA: id, nombre, precio, stock
│       ├── repository/ProductoRepository.java # JpaRepository<Producto, Long>
│       └── controller/ProductoController.java # API REST del catálogo
│
└── pedido-service/                            # puerto 8082
    ├── pom.xml
    └── src/main/java/com/ecosistema/pedido_service/
        ├── PedidoServiceApplication.java
        ├── model/Pedido.java                  # entidad JPA: id, productoId, cantidad, total, estado
        ├── dto/Producto.java                  # DTO de la respuesta de producto-service
        ├── config/RestTemplateConfig.java     # bean RestTemplate
        ├── repository/PedidoRepository.java   # JpaRepository<Pedido, Long>
        ├── service/PedidoService.java         # llamada síncrona + cálculo del total
        ├── controller/PedidoController.java   # API REST de pedidos
        └── exception/GlobalExceptionHandler.java   # traduce excepciones a 404 / 503
```

## 5. Cómo ejecutar

**Requisitos:** JDK 21 (`java -version`) y Maven 3.9+ (`mvn -version`).

Los dos servicios son aplicaciones independientes: se levantan en **dos terminales separadas** y ninguno
depende del arranque del otro.

```bash
# Terminal 1 — catálogo
cd producto-service
mvn spring-boot:run          # escucha en http://localhost:8081

# Terminal 2 — pedidos
cd pedido-service
mvn spring-boot:run          # escucha en http://localhost:8082
```

Consola H2 del catálogo: `http://localhost:8081/h2-console` (JDBC URL `jdbc:h2:mem:productodb`).

> Las bases de datos son **en memoria**: los datos se pierden al detener cada servicio.

## 6. Endpoints

### producto-service — `http://localhost:8081`

| Método | Ruta | Descripción | Respuestas |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/productos` | Lista todos los productos | `200` |
| `GET` | `/api/productos/{id}` | Consulta un producto por ID | `200`, `404` si no existe |
| `POST` | `/api/productos` | Crea un producto (JSON en el body) | `200` |

### pedido-service — `http://localhost:8082`

| Método | Ruta | Descripción | Respuestas |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/pedidos?productoId={id}&cantidad={n}` | Crea un pedido consultando el precio a `producto-service` | `200`, `404`, `503` |

## 7. Comunicación síncrona

Al recibir `POST /api/pedidos`, `pedido-service` ejecuta:

```java
Producto producto = restTemplate.getForObject(
        productoServiceUrl + "/api/productos/" + productoId, Producto.class);
```

La dirección del otro servicio no está escrita en el código: se inyecta desde `application.yml`.

```yaml
producto-service:
  url: http://localhost:8081
```

```java
@Value("${producto-service.url}")
private String productoServiceUrl;
```

Con el precio recibido calcula `total = precio × cantidad`, marca el pedido como `CREADO` y lo persiste
en su propia base de datos.

## 8. Manejo controlado de errores

`pedido-service` distingue **dos fallos distintos** y responde con el código HTTP que corresponde a cada
uno, en lugar de propagar un `500` sin control:

| Situación | Excepción capturada | Respuesta |
| :--- | :--- | :--- |
| El producto no existe (el catálogo responde 404) | `HttpClientErrorException.NotFound` → `IllegalArgumentException` | `404 Not Found` |
| `producto-service` está caído (no hay comunicación) | `RestClientException` → `IllegalStateException` | `503 Service Unavailable` |

`GlobalExceptionHandler`, anotado con `@RestControllerAdvice`, convierte cada excepción en una respuesta
JSON limpia con `timestamp`, `status`, `error` y `message`.

**El punto clave:** si `producto-service` se cae, `pedido-service` **no se cae con él**. Responde `503`,
sigue en pie y vuelve a operar en cuanto el catálogo regresa. Esta es la introducción informal a la
resiliencia que la Semana 9 formaliza con Resilience4j (Circuit Breaker, Retry, Timeout).

## 9. Evidencias de pruebas (Postman)

La colección `ecosistema_ecommerce.postman_collection.json` se importa directamente en Postman y
reproduce toda la secuencia. Las capturas corresponden a su ejecución real contra ambos servicios
levantados en `localhost:8081` y `localhost:8082`.

### Prueba 1 — Crear producto

`POST http://localhost:8081/api/productos` con el body:

```json
{ "nombre": "Laptop Gamer", "precio": 3500000.00, "stock": 10 }
```

Respuesta `200 OK` → `{ "id": 1, "nombre": "Laptop Gamer", "precio": 3500000.00, "stock": 10 }`

![Prueba 1 - Crear producto](docs/screenshots/prueba1_crear_producto.png)

### Prueba 2 — Listar productos

`GET http://localhost:8081/api/productos` → `200 OK` con los dos productos registrados.

![Prueba 2 - Listar productos](docs/screenshots/prueba2_listar_productos.png)

### Pruebas 3 y 4 — Crear pedido y verificar el total

`POST http://localhost:8082/api/pedidos?productoId=1&cantidad=2` → `200 OK`

El total llega calculado a partir del precio **real** obtenido de `producto-service`:
`3 500 000,00 × 2 = 7 000 000,00`.

![Pruebas 3 y 4 - Crear pedido](docs/screenshots/prueba3_crear_pedido.png)

### Prueba 5 — Producto inexistente

`POST http://localhost:8082/api/pedidos?productoId=999&cantidad=2` → `404 Not Found` con el mensaje
`"Producto no encontrado: 999"`. El servicio responde de forma controlada, sin caerse ni devolver `500`.

![Prueba 5 - Error 404](docs/screenshots/prueba5_error_404.png)

### Punto de verificación clave — `producto-service` caído

Con el catálogo **detenido**, la misma petición devuelve `503 Service Unavailable` y el mensaje
`"Error de comunicación: producto-service no disponible"`. `pedido-service` sigue respondiendo.

![Resiliencia - Error 503](docs/screenshots/prueba_resiliencia_503.png)

## 10. Reflexión

Las respuestas completas están en **[`DOCUMENTO_ENTREGABLE.md`](DOCUMENTO_ENTREGABLE.md)** y en formato PDF formal en **[`DOCUMENTO_ENTREGABLE.pdf`](DOCUMENTO_ENTREGABLE.pdf)**. En resumen:

- **Responsabilidades.** `producto-service` es dueño exclusivo del catálogo; `pedido-service` es dueño de
  los pedidos y depende del primero únicamente para validar y cotizar.
- **Escalar solo `producto-service`.** Se pueden levantar más instancias del catálogo sin tocar pedidos,
  que es lo sensato porque en e-commerce se consulta mucho más de lo que se compra. Pero con la URL fija
  actual, `pedido-service` no sabría repartir tráfico entre esas réplicas.
- **Límite de la URL fija en `application.yml`.** Obliga a conocer host y puerto de antemano, impide el
  balanceo entre réplicas y no detecta instancias caídas. De ahí la necesidad de Config Server (Semana 6)
  y Service Discovery con Eureka (Semana 7).

## 11. Entregables

| Requisito del taller (sección 8) | Dónde está |
| :--- | :--- |
| Repositorio Git con el código de ambos microservicios | Este repositorio |
| Capturas de las 5 pruebas de Postman, incluido el caso de error | Sección 9 · archivos en `docs/screenshots/` |
| Documento breve con las 3 preguntas de reflexión | [`DOCUMENTO_ENTREGABLE.md`](DOCUMENTO_ENTREGABLE.md) · [`DOCUMENTO_ENTREGABLE.pdf`](DOCUMENTO_ENTREGABLE.pdf) |

