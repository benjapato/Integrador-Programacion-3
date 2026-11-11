# Food Store · Trabajo Práctico Integrador

La web usa HTML, CSS y módulos de JavaScript. La API del Parcial 2 usa FastAPI y SQLite. Al iniciar con una base nueva se cargan 26 productos activos en cinco categorías.

## Ejecutar

Abrí dos terminales en la carpeta del proyecto. En Windows, usá el lanzador py de Python 3 y dejá las dos terminales abiertas. En macOS o Linux, usá python3 en lugar de py.

1. **API** en la primera terminal.

   ```powershell
   cd api
   py -m pip install -r requirements.txt
   py probar_api.py
   py -m uvicorn main:app --reload
   ```

   La suite debe indicar **128/128**. La documentación interactiva está en [Swagger](http://127.0.0.1:8000/docs).

2. **Web** en la segunda terminal.

   ```powershell
   cd web
   py -m http.server 5500
   ```

   Abrí [Food Store](http://localhost:5500). También se admite el origen `http://127.0.0.1:5500`. Abrí la web desde el servidor HTTP para que se carguen los módulos y funcione CORS.

## Cómo se conectan las pantallas

- **Catálogo** (`web/index.html`). `catalogo.js` solicita categorías y productos. Al cambiar de categoría manda `categoria_id` a la API. El buscador usa el parámetro `q`. Los productos se dibujan con el DOM a partir de la respuesta.
- **Ficha de producto** (`web/producto.html`). Cada tarjeta lleva a una ficha con foto, precio y stock. Desde ahí se puede volver al catálogo con los mismos filtros o abrir otro producto de la categoría.
- **Inventario** (`web/productos.html`). `productos.js` pide 10 productos por página. `paginacion.js` calcula `skip = (página - 1) × límite` y la cantidad de páginas a partir de `total`.
- **Alta**. El modal usa las restricciones HTML y las reglas de `validaciones.js`. El envío manda `nombre`, `descripcion`, `precio`, `stock`, `imagen_url` y `categoria_id`. El precio admite centavos, el stock es entero y la imagen vacía viaja como `null`. Con un alta exitosa se vuelve a consultar el inventario y se muestra la página del producto recién agregado. La API identifica el producto con un ID.
- **API**. `web/js/api.js` centraliza la URL y los pedidos. Los errores de HTTP y de red llegan a las pantallas como `ApiError`. `api/main.py` autoriza los dos orígenes locales de la web mediante CORS.

## Comprobar un alta

Con la pestaña **Red** abierta, entrá al inventario y elegí **Nuevo producto**. Probá el formulario vacío, un nombre con espacios y un nombre repetido como **Pizza Muzzarella**. Después creá un producto válido y revisá el `201`, el identificador y la nueva consulta a la lista. Buscá el mismo nombre en el catálogo.

Desde otra terminal en `api/`, consultá la base que usa el servidor antes y después de cada intento.

```powershell
py probar_api.py --ver-base
```

Para revisar la recuperación de conexión, detené la API, recargá la web, volvé a iniciar la API y pulsá **Reintentar**.

## Practicar la defensa

Grabá entre 5 y 10 minutos con la cámara encendida y la pantalla compartida. Explicá con tus palabras y señalá el código mientras mostrás cada flujo.

1. **Alta válida.** Mostrá la base antes del alta. En **Red**, compará el JSON enviado y el devuelto con `ProductoCreate` y `ProductoPublic`. Mostrá el ID nuevo en la base, la tabla y el catálogo. El formulario manda `categoria_id` porque identifica la relación con una categoría.
2. **Validaciones.** Probá el formulario vacío, un nombre con espacios y un nombre repetido. Mostrá en **Red** cuándo sale el POST y seguí el `409` desde `api.js` hasta Nombre. Volvé a consultar la base. Probá también el nombre `<b>Prueba</b>` para mostrar cómo `textContent` lo presenta como texto.
3. **Carga de datos.** Aplicá un filtro y cambiá de página en el inventario. Mostrá cómo se calculan `skip` y la cantidad de páginas, y cómo se arma una tarjeta. Explicá que el navegador aplica CORS porque la API y la web se sirven desde puertos distintos. Mostrá por qué el modal te permite volver al inventario después del alta.

## Imágenes

Los 26 productos de ejemplo tienen fotografías diferentes de Pexels y Wikimedia Commons. Se sirven desde `web/img/catalogo/` en JPEG de 1200 × 900 px (4:3). Cada foto pesa menos de 200 KB.

Las fotos son ilustrativas. Los autores, las fuentes, las licencias y los ajustes están en [Créditos de fotos](web/img/catalogo/creditos.txt) y [fuentes.json](web/img/catalogo/fuentes.json).

La API carga las rutas de las fotos al iniciar con una base nueva. Si la imagen de un producto falta o no carga, la web muestra **Sin imagen**.
