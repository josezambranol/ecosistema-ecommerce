package com.ecosistema.pedido_service.service;

import com.ecosistema.pedido_service.dto.Producto;
import com.ecosistema.pedido_service.model.Pedido;
import com.ecosistema.pedido_service.repository.PedidoRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;

import java.math.BigDecimal;

@Service
@RequiredArgsConstructor
public class PedidoService {

    private final RestTemplate restTemplate;
    private final PedidoRepository repository;

    @Value("${producto-service.url}")
    private String productoServiceUrl;

    public Pedido crearPedido(Long productoId, Integer cantidad) {
        Producto producto;
        try {
            producto = restTemplate.getForObject(
                    productoServiceUrl + "/api/productos/" + productoId,
                    Producto.class
            );
        } catch (HttpClientErrorException.NotFound e) {
            throw new IllegalArgumentException("Producto no encontrado: " + productoId);
        } catch (RestClientException e) {
            throw new IllegalStateException("Error de comunicación: producto-service no disponible");
        }

        if (producto == null) {
            throw new IllegalArgumentException("Producto no encontrado: " + productoId);
        }

        Pedido pedido = new Pedido(
                null,
                productoId,
                cantidad,
                producto.getPrecio().multiply(BigDecimal.valueOf(cantidad)),
                "CREADO"
        );
        return repository.save(pedido);
    }
}
