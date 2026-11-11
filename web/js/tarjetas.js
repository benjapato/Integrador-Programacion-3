import { fotoProducto, precioFormateado, texto } from "./vista.js";

export function parametrosCatalogo({ categoriaId, q } = {}) {
    const parametros = new URLSearchParams();
    if (categoriaId) parametros.set("categoria_id", categoriaId);
    if (q) parametros.set("q", q);
    return parametros;
}

export function crearTarjeta(producto, filtros) {
    const tarjeta = document.createElement("article");
    tarjeta.className = "producto";
    const cuerpo = document.createElement("div");
    cuerpo.className = "producto__cuerpo";

    cuerpo.append(
        texto("p", producto.categoria.nombre, "producto__categoria"),
        texto("h3", producto.nombre, "producto__nombre"),
    );
    if (producto.descripcion) {
        cuerpo.append(texto("p", producto.descripcion, "producto__descripcion"));
    }
    if (producto.stock === 0) {
        cuerpo.append(texto("span", "Sin stock", "stock stock--vacio producto__stock"));
    }

    const parametros = parametrosCatalogo(filtros);
    parametros.set("id", producto.id);
    const enlace = texto("a", "Ver ficha →", "producto__enlace");
    enlace.href = `producto.html?${parametros}`;
    enlace.setAttribute("aria-label", `Ver ficha de ${producto.nombre}`);

    const pie = document.createElement("div");
    pie.className = "producto__pie";
    pie.append(texto("strong", precioFormateado(producto.precio), "producto__precio"), enlace);
    cuerpo.append(pie);
    tarjeta.append(fotoProducto(producto), cuerpo);
    return tarjeta;
}

