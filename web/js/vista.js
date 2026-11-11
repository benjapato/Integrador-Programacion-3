const formatoPrecio = new Intl.NumberFormat("es-AR", {
    style: "currency",
    currency: "ARS",
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
});

export function precioFormateado(precio) {
    return formatoPrecio.format(precio);
}

export function texto(etiqueta, contenido, clase) {
    const nodo = document.createElement(etiqueta);
    nodo.textContent = contenido;
    if (clase) nodo.className = clase;
    return nodo;
}

export function fotoProducto(producto) {
    const foto = document.createElement("div");
    foto.className = "foto";

    function mostrarSinImagen() {
        foto.replaceChildren(texto("span", "Sin imagen", "foto__vacia"));
    }

    if (!producto.imagen_url) {
        mostrarSinImagen();
        return foto;
    }

    const imagen = document.createElement("img");
    imagen.alt = `Foto de ${producto.nombre}`;
    imagen.loading = "lazy";
    imagen.addEventListener("error", mostrarSinImagen, { once: true });
    imagen.src = producto.imagen_url;
    foto.append(imagen);
    return foto;
}

export function cargarOpciones(select, categorias) {
    select.replaceChildren(select.options[0]);
    for (const categoria of categorias) {
        const opcion = texto("option", categoria.nombre);
        opcion.value = categoria.id;
        select.append(opcion);
    }
}

export function mensajeError(error) {
    return typeof error.detail === "string" ? error.detail : error.message;
}

