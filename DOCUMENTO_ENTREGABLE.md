# Documento de Entrega — Taller Básico de Microservicios con Spring Boot

**Asignatura:** Electiva I – Arquitectura de Microservicios con Spring Boot  
**Institución:** Fundación Universitaria Tecnológico Comfenalco  
**Periodo Académico:** 2026-I — V Semestre  

---

## 👥 Integrantes del Equipo
- **José Daniel Zambrano**
- **Carlos Mario Bechara**
- **Rafael Sarmiento Peña**

---

## 1. Responsabilidad de cada Microservicio

| Microservicio | Puerto | Bounded Context y Responsabilidad Principal |
| :--- | :---: | :--- |
| **`producto-service`** | `8081` | **Gestión de Catálogo e Inventario:** Administra de manera exclusiva el ciclo de vida de los productos (creación, consulta por ID, listado general y verificación de existencias). Posee su propia base de datos independiente (`productodb` en H2). |
| **`pedido-service`** | `8082` | **Gestión de Órdenes y Compras:** Gestiona la recepción y registro de los pedidos de los clientes. Al crear un pedido, establece una comunicación HTTP síncrona con `producto-service` para verificar la existencia del producto y consultar su precio unitario, calculando el total (`precio × cantidad`) y almacenando el pedido en su base de datos propia (`pedidodb` en H2). |

---

## 2. Preguntas de Reflexión Arquitectural

### ¿Qué pasaría si necesitáramos escalar solo `producto-service`?
Gracias al desacoplamiento entre servicios, es posible aplicar **escalabilidad horizontal selectiva** a `producto-service` (iniciar 3, 5 o más instancias en diferentes puertos o contenedores) sin tener que duplicar recursos en `pedido-service`. Esto es crucial en comercio electrónico, donde el tráfico de navegación/búsqueda de productos es significativamente mayor que el de órdenes efectivas.

No obstante, bajo la configuración actual donde la dirección está configurada de manera estática (`http://localhost:8081`), `pedido-service` no tiene la capacidad de distribuir el tráfico entre las nuevas instancias de `producto-service`, desaprovechando el escalamiento a menos que se interponga un balanceador o un mecanismo de Service Discovery.

### ¿Qué limitación notaron al tener la URL del otro servicio escrita directamente en `application.yml`?
1. **Acoplamiento de Infraestructura y Red:** Si `producto-service` cambia de IP, nombre de host o puerto, se debe reconfigurar y reiniciar/redesplegar `pedido-service`.
2. **Falta de Balanceo de Carga en Cliente:** Todas las peticiones van a una única dirección fija, impidiendo distribuir peticiones entre réplicas.
3. **Falta de Detección de Caídas y Enrutamiento Dinámico:** Si la instancia cae y se levanta en otra dirección, `pedido-service` no se entera.
4. **Fundamento para Service Discovery:** Esta limitación demuestra la necesidad indispensable de **Eureka / Service Discovery** (para registrar y ubicar servicios por su nombre lógico `producto-service` sin conocer IPs/puertos) y **Spring Cloud Config Server** (para centralizar y actualizar configuraciones en tiempo de ejecución).

---

## 3. Evidencias de Ejecución de Pruebas (Postman)

### Prerrequisitos
Tener ambos microservicios en ejecución:
- `producto-service` corriendo en puerto `8081`
- `pedido-service` corriendo en puerto `8082`

---

### Prueba 1: Crear Producto (POST `producto-service`)
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
- **Respuesta Obtenida (HTTP 200 OK):**
  ```json
  {
    "id": 1,
    "nombre": "Laptop Gamer",
    "precio": 3500000.00,
    "stock": 10
  }
  ```
- **Captura Postman:**
  ![Captura Prueba 1 - Crear Producto](docs/screenshots/prueba1_crear_producto.png)

---

### Prueba 2: Listar Productos (GET `producto-service`)
- **Método:** `GET`
- **URL:** `http://localhost:8081/api/productos`
- **Respuesta Obtenida (HTTP 200 OK):**
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
- **Captura Postman:**
  ![Captura Prueba 2 - Listar Productos](docs/screenshots/prueba2_listar_productos.png)

---

### Prueba 3 & 4: Crear Pedido con Cálculo de Total (POST `pedido-service`)
- **Método:** `POST`
- **URL:** `http://localhost:8082/api/pedidos?productoId=1&cantidad=2`
- **Respuesta Obtenida (HTTP 200 OK):**
  ```json
  {
    "id": 1,
    "productoId": 1,
    "cantidad": 2,
    "total": 7000000.00,
    "estado": "CREADO"
  }
  ```
  *(Se comprueba que el total calculado es `$3,500,000.00 × 2 = $7,000,000.00` obtenido directamente desde `producto-service`).*
- **Captura Postman:**
  ![Captura Prueba 3 y 4 - Crear Pedido y Total](docs/screenshots/prueba3_crear_pedido.png)

---

### Prueba 5: Caso de Error Controlado — Producto Inexistente (POST `pedido-service`)
- **Método:** `POST`
- **URL:** `http://localhost:8082/api/pedidos?productoId=999&cantidad=2`
- **Respuesta Obtenida (HTTP 404 Not Found):**
  ```json
  {
    "status": 404,
    "error": "Not Found",
    "message": "Producto no encontrado: 999",
    "timestamp": "2026-08-30T..."
  }
  ```
  *(El servicio responde con un JSON controlado sin sufrir caídas ni generar errores 500 no controlados).*
- **Captura Postman:**
  ![Captura Prueba 5 - Error 404 Producto Inexistente](docs/screenshots/prueba5_error_404.png)

---

### Punto de Verificación de Resiliencia: `producto-service` Caído
- **Condición:** Detener `producto-service` y enviar una solicitud de creación de pedido a `pedido-service`.
- **URL:** `POST http://localhost:8082/api/pedidos?productoId=1&cantidad=2`
- **Respuesta Obtenida (HTTP 503 Service Unavailable):**
  ```json
  {
    "status": 503,
    "error": "Service Unavailable",
    "message": "Error de comunicación: producto-service no disponible",
    "timestamp": "2026-08-30T..."
  }
  ```
- **Captura Postman:**
  ![Captura Prueba Resiliencia - Error 503](docs/screenshots/prueba_resiliencia_503.png)
