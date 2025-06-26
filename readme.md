# Dashboard de Monitoreo de Sensores - Andes Technologies

## Descripción del Proyecto

Este proyecto es un sistema de monitoreo de sensores desarrollado para **Andes Technologies**. Se compone de una arquitectura basada en Django para el backend, Celery + Redis para tareas periódicas, y un dashboard interactivo construido con TailwindCSS, Flowbite y ApexCharts.

El sistema consume datos de sensores remotos que miden parámetros como:
- Temperatura
- Presión
- Batería
- Señal
- Capacidad del cilindro
- Hora del registro

Los datos son almacenados en una base de datos PostgreSQL, con un esquema personalizado `public`, y tres tablas principales: `andes_users`, `andes_sensors`, `andes_variables`.

## Tecnologías Utilizadas

- **Django**: Framework web en Python
- **PostgreSQL**: Base de datos relacional
- **Celery**: Sistema de tareas asíncronas
- **Redis**: Broker para Celery
- **Docker y Docker Compose**: Contenedores y orquestación
- **TailwindCSS + Flowbite**: UI moderna y responsiva
- **ApexCharts**: Visualización de datos en tiempo real

## Funcionalidades Clave

- Consumo automático de datos cada minuto usando Celery y Beat.
- Renderizado dinámico del dashboard con los últimos registros.
- Visualización de estadísticas clave y alertas.
- Interfaz responsive accesible desde dispositivos móviles.
- Exportación de reportes en PDF.

## Estructura de la Base de Datos

### `andes_users`
- `id`: ID del usuario
- `us_name`: Nombre
- `us_contact`: Teléfono
- `us_mail`: Correo electrónico
- `us_hash_pass`: Contraseña hasheada
- `us_status`: Estado (bytea)

### `andes_sensors`
- `sen_id`: ID del sensor
- `sen_name`: Nombre del sensor
- `sen_direction`: Dirección física
- `max_output_force`: Fuerza máxima
- `max_masa`: Masa máxima
- `sen_serialno`: Serial del sensor
- `sen_imei`: IMEI del sensor
- `user_us_id_id`: FK al usuario

### `andes_variables`
- `id`: ID del registro
- `var_temperature`: Temperatura registrada
- `var_radiofrecuency`: Frecuencia de señal
- `var_presure`: Presión
- `var_time`: Fecha y hora del registro
- `var_output_capacity`: Capacidad salida
- `var_current_capacity`: Capacidad actual
- `var_litres`: Volumen en litros
- `var_battery`: Nivel de batería
- `localizacion`: Coordenadas GPS
- `sensors_sen_id_id`: FK al sensor

## Documentación  
Pronto

## Última Actualización

2025-06-26 23:53:51

