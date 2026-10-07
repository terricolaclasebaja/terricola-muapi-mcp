# Terrícola MuAPI MCP / Chain Bridge

Puente experimental para automatizar generaciones encadenadas de MuAPI sin copiar URLs entre pasos.

## Problema que resuelve

El cliente puede conservar únicamente el `request_id` de una generación anterior. El servidor:

1. consulta el resultado anterior directamente en MuAPI;
2. obtiene internamente su primera URL de salida;
3. la usa como `image_url` de la siguiente edición;
4. devuelve el nuevo `request_id` y, opcionalmente, espera el resultado.

Así la URL intermedia no tiene que ser copiada manualmente ni reenviada por el usuario.

## Endpoint inicial

`POST /chain/image-edit`

Ejemplo conceptual:

```json
{
  "source_request_id": "REQUEST_ID_ANTERIOR",
  "model": "nano-banana-2-edit",
  "prompt": "Create a full-body image preserving exact identity...",
  "aspect_ratio": "9:16",
  "num_images": 1,
  "wait_for_result": true
}
```

## Seguridad

La clave de MuAPI **no se guarda en el repositorio**. Configúrala en el servicio de despliegue como variable de entorno:

`MUAPIAPP_API_KEY`

También puede suministrarse como header `x-api-key`.

## Estado

Versión 0.1: puente REST funcional para probar el encadenamiento server-side. El siguiente paso es desplegarlo en HTTPS y exponer esta operación como herramienta MCP para ChatGPT.
