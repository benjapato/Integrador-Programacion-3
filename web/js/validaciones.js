export function datosProducto(formulario) {
    const campos = new FormData(formulario);
    return {
        nombre: campos.get("nombre").trim(),
        descripcion: campos.get("descripcion").trim(),
        precio: formulario.elements.precio.valueAsNumber,
        stock: formulario.elements.stock.valueAsNumber,
        imagen_url: campos.get("imagen_url").trim() || null,
        categoria_id: Number(campos.get("categoria_id")),
    };
}

export function validarProducto(datos) {
    const errores = {};
    if (datos.nombre.length < 3 || datos.nombre.length > 60) {
        errores.nombre = "Ingresá entre 3 y 60 caracteres, sin contar espacios en los extremos.";
    }
    if (datos.descripcion.length > 200) {
        errores.descripcion = "La descripción puede tener hasta 200 caracteres.";
    }
    if (!Number.isFinite(datos.precio) || datos.precio <= 0) {
        errores.precio = "Ingresá un precio mayor a cero.";
    }
    if (!Number.isSafeInteger(datos.stock) || datos.stock < 0) {
        errores.stock = "Ingresá un número entero mayor o igual a cero.";
    }
    if (!Number.isSafeInteger(datos.categoria_id) || datos.categoria_id <= 0) {
        errores.categoria_id = "Elegí una categoría.";
    }
    if (datos.imagen_url?.length > 255) {
        errores.imagen_url = "La ruta de imagen puede tener hasta 255 caracteres.";
    }
    return errores;
}

export function erroresDeApi(error) {
    if (error.status === 409) return { nombre: error.detail };
    if (error.status === 404) return { categoria_id: error.detail };
    if (error.status !== 422 || !Array.isArray(error.detail)) return {};

    const campos = {};
    for (const detalle of error.detail) {
        const campo = detalle.loc?.[1];
        if (detalle.loc?.[0] === "body" && campo) {
            campos[campo] = detalle.msg;
        }
    }
    return campos;
}

