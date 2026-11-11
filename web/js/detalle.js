import { listarProductos, obtenerProducto } from "./api.js";
import { crearTarjeta, parametrosCatalogo } from "./tarjetas.js?v=stock-catalogo";
import { fotoProducto, mensajeError, precioFormateado, texto } from "./vista.js";

const detalle = document.querySelector("#detalle");
const estado = document.querySelector("#estado-detalle");
const reintentar = document.querySelector("#reintentar-detalle");
const relacionados = document.querySelector("#relacionados");
const volver = document.querySelector("#volver-catalogo");
const parametros = new URLSearchParams(location.search);
const id = Number(parametros.get("id"));
const filtros = { categoriaId: parametros.get("categoria_id"), q: parametros.get("q") };
const consulta = parametrosCatalogo(filtros).toString();
volver.href = consulta ? `index.html?${consulta}#menu` : "index.html#menu";

function dibujarDetalle(producto) {
    document.title = `${producto.nombre} | Food Store`;
    document.querySelector("#ubicacion-producto").textContent = producto.nombre;

    const info = document.createElement("div");
    info.className = "detalle__info";
    const insignias = document.createElement("div");
    insignias.className = "detalle__insignias";
    insignias.append(
        texto("span", producto.categoria.nombre, "detalle__categoria"),
        producto.stock > 0
            ? texto("span", `${producto.stock} en stock`, "stock")
            : texto("span", "Sin stock", "stock stock--vacio"),
    );
    info.append(insignias, texto("h1", producto.nombre, "titulo detalle__titulo"));
    if (producto.descripcion) {
        info.append(texto("p", producto.descripcion, "detalle__descripcion"));
    }
    info.append(texto("strong", precioFormateado(producto.precio), "detalle__precio"));

    if (producto.etiquetas?.length) {
        const etiquetas = document.createElement("ul");
        etiquetas.className = "detalle__etiquetas";
        for (const etiqueta of producto.etiquetas) {
            etiquetas.append(texto("li", etiqueta.nombre));
        }
        info.append(etiquetas);
    }

    const regreso = texto("a", "← Volver al catálogo", "btn btn--secundario");
    regreso.href = volver.href;
    info.append(regreso);
    detalle.replaceChildren(fotoProducto(producto), info);
    detalle.hidden = false;
}

async function cargarRelacionados(producto) {
    try {
        const { items } = await listarProductos({ categoriaId: producto.categoria_id, limit: 4 });
        const otros = items.filter((item) => item.id !== producto.id).slice(0, 3);
        if (otros.length === 0) return;
        document.querySelector("#titulo-relacionados").textContent = "Más de esta categoría";
        document.querySelector("#tarjetas-relacionadas").replaceChildren(
            ...otros.map((item) => crearTarjeta(item, filtros)),
        );
        relacionados.hidden = false;
    } catch {
        // La ficha principal sigue disponible si falla la consulta de relacionados.
    }
}

async function cargarDetalle() {
    if (!Number.isSafeInteger(id) || id < 1) {
        estado.textContent = "Elegí un producto desde el catálogo.";
        return;
    }
    estado.textContent = "Cargando el producto…";
    estado.classList.remove("estado__error");
    reintentar.hidden = true;
    try {
        const producto = await obtenerProducto(id);
        if (!producto.activo) {
            estado.textContent = "Este producto ya no está disponible.";
            return;
        }
        dibujarDetalle(producto);
        estado.textContent = "";
        cargarRelacionados(producto);
    } catch (error) {
        if (error.status === 404) {
            estado.textContent = "Este producto ya no está disponible.";
            return;
        }
        estado.textContent = mensajeError(error);
        estado.classList.add("estado__error");
        reintentar.hidden = false;
    }
}

reintentar.addEventListener("click", cargarDetalle);
cargarDetalle();

