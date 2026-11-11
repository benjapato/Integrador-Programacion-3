import { listarCategorias, listarProductos } from "./api.js";
import { crearTarjeta, parametrosCatalogo } from "./tarjetas.js?v=stock-catalogo";
import { mensajeError, texto } from "./vista.js";

const formulario = document.querySelector("#filtros");
const categorias = document.querySelector("#lista-categorias");
const buscar = document.querySelector("#buscar");
const tarjetas = document.querySelector("#tarjetas");
const cantidad = document.querySelector("#cantidad-catalogo");
const estado = document.querySelector("#estado-catalogo");
const reintentar = document.querySelector("#reintentar-catalogo");

const parametros = new URLSearchParams(location.search);
const idInicial = parametros.get("categoria_id") ?? "";
let categoriaId = /^[1-9]\d*$/.test(idInicial) && Number.isSafeInteger(Number(idInicial)) ? idInicial : "";
let consulta = (parametros.get("q") ?? "").slice(0, 50).trim();
buscar.value = consulta;

let categoriasCargadas = false;
let peticion;

function marcarCategoria() {
    for (const boton of categorias.querySelectorAll("[data-categoria]")) {
        boton.setAttribute("aria-pressed", String(boton.dataset.categoria === categoriaId));
    }
}

function mostrarCategorias(items) {
    const todos = categorias.querySelector('[data-categoria=""]');
    todos.disabled = false;
    for (const item of items.filter((categoria) => categoria.activo)) {
        const boton = texto("button", item.nombre, "categorias__boton");
        boton.type = "button";
        boton.dataset.categoria = item.id;
        categorias.append(boton);
    }
    marcarCategoria();
}

async function pedirCatalogo(filtros) {
    const limit = 50;
    const productos = [];
    let total;
    do {
        const datos = await listarProductos({ ...filtros, skip: productos.length, limit });
        total = datos.total;
        productos.push(...datos.items);
        if (datos.items.length === 0) break;
    } while (productos.length < total);
    return productos;
}

async function mostrarCatalogo() {
    peticion?.abort();
    peticion = new AbortController();
    const { signal } = peticion;
    const filtros = { categoriaId, q: consulta };

    estado.textContent = "Cargando el menú…";
    estado.classList.remove("estado__error");
    reintentar.hidden = true;
    tarjetas.hidden = true;
    cantidad.hidden = true;

    try {
        const [productos, opciones] = await Promise.all([
            pedirCatalogo({ ...filtros, signal }),
            categoriasCargadas ? null : listarCategorias(signal),
        ]);
        if (signal.aborted) return;

        if (opciones) {
            mostrarCategorias(opciones);
            categoriasCargadas = true;
        }
        tarjetas.replaceChildren(...productos.map((producto) => crearTarjeta(producto, filtros)));
        tarjetas.hidden = productos.length === 0;
        cantidad.textContent = productos.length === 1 ? "1 producto" : `${productos.length} productos`;
        cantidad.hidden = productos.length === 0;
        estado.textContent = productos.length === 0 ? "No hay productos para esta selección." : "";
    } catch (error) {
        if (signal.aborted) return;
        estado.textContent = mensajeError(error);
        estado.classList.add("estado__error");
        reintentar.hidden = false;
    }
}

function aplicarFiltros() {
    const url = new URL(location.href);
    url.search = parametrosCatalogo({ categoriaId, q: consulta }).toString();
    history.replaceState(null, "", url);
    mostrarCatalogo();
}

formulario.addEventListener("submit", (evento) => {
    evento.preventDefault();
    consulta = buscar.value.trim();
    aplicarFiltros();
});
categorias.addEventListener("click", (evento) => {
    const boton = evento.target.closest("[data-categoria]");
    if (!boton || boton.dataset.categoria === categoriaId) return;
    categoriaId = boton.dataset.categoria;
    marcarCategoria();
    aplicarFiltros();
});
reintentar.addEventListener("click", mostrarCatalogo);

mostrarCatalogo();

