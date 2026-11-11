const ES_LOCAL = ["localhost", "127.0.0.1"].includes(location.hostname);
const ORIGEN_API_PUBLICA = location.hostname === "benjapato.github.io"
    ? "https://food-store-benjapato.onrender.com"
    : location.origin;
const URL_BASE = ES_LOCAL ? "http://127.0.0.1:8000" : ORIGEN_API_PUBLICA;

export class ApiError extends Error {
    constructor(status, detail, mensaje) {
        super(mensaje);
        this.name = "ApiError";
        this.status = status;
        this.detail = detail;
    }
}

async function pedir(ruta, opciones) {
    let respuesta;
    try {
        respuesta = await fetch(URL_BASE + ruta, opciones);
    } catch {
        const mensaje = ES_LOCAL
            ? "No se pudo conectar con la API. Revisá que esté encendida en el puerto 8000."
            : "No se pudo conectar con la API. Volvé a intentar en unos instantes.";
        throw new ApiError(0, null, mensaje);
    }

    const datos = await respuesta.json().catch(() => null);
    if (!respuesta.ok) {
        throw new ApiError(respuesta.status, datos?.detail ?? null, `La API respondió con el código ${respuesta.status}.`);
    }
    if (datos === null) {
        throw new ApiError(respuesta.status, null, "La API devolvió una respuesta inesperada.");
    }
    return datos;
}

export function listarCategorias(signal) {
    return pedir("/categorias/", { signal });
}

export function listarProductos({ skip = 0, limit = 10, categoriaId, q, soloConStock, signal } = {}) {
    const parametros = new URLSearchParams({ skip, limit });
    if (categoriaId) parametros.set("categoria_id", categoriaId);
    if (q) parametros.set("q", q);
    if (soloConStock) parametros.set("solo_con_stock", "true");
    return pedir(`/productos/?${parametros}`, { signal });
}

export function obtenerProducto(id) {
    return pedir("/productos/" + encodeURIComponent(id));
}

export function crearProducto(datos) {
    return pedir("/productos/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(datos),
    });
}

