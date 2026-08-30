# Ecosistema Mínimo de Microservicios con Spring Boot

Proyecto desarrollado para el taller práctico de **Arquitectura de Microservicios con Spring Boot** (V Semestre — 2026-I).

## Estructura del Ecosistema

```
ecosistema-ecommerce/
├── .gitignore
├── DOCUMENTO_ENTREGABLE.md
├── README.md
├── producto-service/           # Microservicio independiente (Puerto 8081)
│   ├── src/main/java/...
│   ├── src/main/resources/application.yml
│   └── pom.xml
└── pedido-service/             # Microservicio independiente (Puerto 8082)
    ├── src/main/java/...
    ├── src/main/resources/application.yml
    └── pom.xml
```

---

## Cómo Ejecutar el Ecosistema

### 1. Iniciar `producto-service` (Terminal 1)
```powershell
cd producto-service
mvn spring-boot:run
```
Disponible en: `http://localhost:8081`  
Consola H2: `http://localhost:8081/h2-console` (JDBC URL: `jdbc:h2:mem:productodb`)

### 2. Iniciar `pedido-service` (Terminal 2)
```powershell
cd pedido-service
mvn spring-boot:run
```
Disponible en: `http://localhost:8082`  
Consola H2: `http://localhost:8082/h2-console` (JDBC URL: `jdbc:h2:mem:pedidodb`)

---

## Pruebas de Funcionamiento

Ver detalle paso a paso en [DOCUMENTO_ENTREGABLE.md](DOCUMENTO_ENTREGABLE.md).
