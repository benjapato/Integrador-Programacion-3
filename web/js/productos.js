import { crearProducto, listarCategorias, listarProductos } from "./api.js?v=filtros-stock";
import { datosPagina, mostrarPaginacion } from "./paginacion.js";
import { datosProducto, erroresDeApi, validarProducto } from "./validaciones.js";
import { cargarOpciones, fotoProducto, mensajeError, precioFormateado, texto } from "./vista.js";

const LIMITE = 10;
const filas = document.querySelector("#filas");
const resultados = document.querySelector("#resultados-inventario");
const resumen = document.querySelector("#resumen-inventario");
const botonesFiltro = resumen.querySelectorAll("[data-filtro]");
const estado = document.querySelector("#estado-inventario");
const reintentar = document.querySelector("#reintentar-inventario");
const controles = {
    anterior: document.querySelector("#pagina-anterior"),
    siguiente: document.querySelector("#pagina-siguiente"),
    actual: document.querySelector("#pagina-actual"),
};

let pagina = 1;
let totalActivos = 0;
let filtro = "activos";
let peticionInventario;
let recargar = () => cargarPagina(1);

function crearFila(producto) {
    const fila = document.createElement("tr");
    const imagen = document.createElement("td");
    imagen.append(fotoProducto(producto));
    const nombre = texto("th", producto.nombre, "tabla__nombre");
    nombre.scope = "row";
    const stock = document.createElement("td");
    stock.className = "tabla__numero";
    stock.append(texto("span", producto.stock, producto.stock === 0 ? "stock stock--vacio" : "stock"));

    fila.append(
        texto("td", producto.id, "tabla__id"),
        imagen,
        nombre,
        texto("td", producto.categoria.nombre),
        texto("td", precioFormateado(producto.precio), "tabla__numero tabla__precio"),
        stock,
    );
    return fila;
}

function mostrarResumen(activos, conStock) {
    const cantidades = {
        activos,
        "con-stock": conStock,
        "sin-stock": activos - conStock,
    };
    for (const boton of botonesFiltro) {
        boton.querySelector("strong").textContent = cantidades[boton.dataset.filtro];
    }
    resumen.hidden = false;
}

function marcarFiltro() {
    for (const boton of botonesFiltro) {
        boton.setAttribute("aria-pressed", String(boton.dataset.filtro === filtro));
    }
}

async function consultarSinStock(destino, signal) {
    // La API ofrece solo_con_stock para los productos disponibles.
    // Recorremos sus páginas para reunir los productos con stock cero.
    const sinStock = [];
    let skip = 0;
    let activos;
    do {
        const datos = await listarProductos({ skip, limit: 50, signal });
        activos = datos.total;
        sinStock.push(...datos.items.filter((producto) => producto.stock === 0));
        if (datos.items.length === 0) break;
        skip += datos.items.length;
    } while (skip < activos);

    const { paginas } = datosPagina(destino, LIMITE, sinStock.length);
    const numero = Math.min(destino, paginas);
    const desde = datosPagina(numero, LIMITE, sinStock.length).skip;
    return {
        items: sinStock.slice(desde, desde + LIMITE),
        numero,
        paginas,
        activos,
        conStock: Math.max(0, activos - sinStock.length),
    };
}

async function consultarInventario(destino, irAlFinal, signal) {
    if (filtro === "sin-stock") return consultarSinStock(destino, signal);

    const soloConStock = filtro === "con-stock";
    const pedirPagina = (numero) => listarProductos({
        skip: datosPagina(numero, LIMITE, totalActivos).skip,
        limit: LIMITE,
        soloConStock,
        signal,
    });

    let [datos, otroGrupo] = await Promise.all([
        pedirPagina(destino),
        listarProductos({ limit: 1, soloConStock: !soloConStock, signal }),
    ]);
    let { paginas } = datosPagina(destino, LIMITE, datos.total);
    const numero = irAlFinal ? paginas : Math.min(destino, paginas);
    if (numero !== destino) {
        datos = await pedirPagina(numero);
        ({ paginas } = datosPagina(numero, LIMITE, datos.total));
    }

    const activos = soloConStock ? otroGrupo.total : datos.total;
    const conStock = soloConStock ? datos.total : otroGrupo.total;
    return { items: datos.items, numero, paginas, activos, conStock: Math.min(activos, conStock) };
}

async function cargarPagina(destino, irAlFinal = false) {
    peticionInventario?.abort();
    peticionInventario = new AbortController();
    const { signal } = peticionInventario;
    recargar = () => cargarPagina(destino, irAlFinal);
    estado.textContent = "Cargando el inventario…";
    estado.classList.remove("estado__error");
    reintentar.hidden = true;
    resultados.setAttribute("aria-busy", "true");
    controles.anterior.disabled = true;
    controles.siguiente.disabled = true;

    try {
        const datos = await consultarInventario(destino, irAlFinal, signal);
        if (signal.aborted) return;
        pagina = datos.numero;
        totalActivos = datos.activos;
        mostrarResumen(datos.activos, datos.conStock);
        filas.replaceChildren(...datos.items.map(crearFila));
        resultados.hidden = datos.items.length === 0;
        const mensajesVacios = {
            activos: "Todavía no hay productos en el inventario.",
            "con-stock": "No hay productos con stock.",
            "sin-stock": "No hay productos sin stock.",
        };
        estado.textContent = datos.items.length === 0 ? mensajesVacios[filtro] : "";
        mostrarPaginacion(controles, pagina, datos.paginas);
    } catch (error) {
        if (signal.aborted) return;
        resultados.hidden = true;
        resumen.hidden = true;
        estado.textContent = mensajeError(error);
        estado.classList.add("estado__error");
        reintentar.hidden = false;
    } finally {
        if (!signal.aborted) resultados.setAttribute("aria-busy", "false");
    }
}

controles.anterior.addEventListener("click", () => cargarPagina(pagina - 1));
controles.siguiente.addEventListener("click", () => cargarPagina(pagina + 1));
reintentar.addEventListener("click", () => recargar());

function seleccionarFiltro(valor) {
    filtro = valor;
    marcarFiltro();
    resultados.hidden = true;
}

for (const boton of botonesFiltro) {
    boton.addEventListener("click", () => {
        if (filtro === boton.dataset.filtro) return;
        seleccionarFiltro(boton.dataset.filtro);
        cargarPagina(1);
    });
}

const modal = document.querySelector("#alta");
const formulario = document.querySelector("#formulario-alta");
const categoria = formulario.elements.categoria_id;
const abrir = document.querySelector("#abrir-alta");
const cerrar = document.querySelector("#cerrar-alta");
const cancelar = document.querySelector("#cancelar-alta");
const guardar = document.querySelector("#guardar-producto");
const reintentarCategorias = document.querySelector("#reintentar-categorias");
const errorAlta = document.querySelector("#error-alta");
const exito = document.querySelector("#exito-alta");

const campos = ["nombre", "descripcion", "precio", "stock", "categoria_id", "imagen_url"];
const mensajes = new Map(campos.map((campo) => [campo, document.getElementById(`error-${campo}`)]));

let peticionCategorias;
let guardando = false;

function mostrarError(campo, mensaje = "") {
    const aviso = mensajes.get(campo);
    aviso.textContent = mensaje;
    aviso.hidden = !mensaje;
    if (mensaje) formulario.elements[campo].setAttribute("aria-invalid", "true");
    else formulario.elements[campo].removeAttribute("aria-invalid");
}

function mostrarErrores(errores) {
    const afectados = campos.filter((campo) => errores[campo]);
    for (const campo of afectados) mostrarError(campo, errores[campo]);
    if (afectados.length > 0) formulario.elements[afectados[0]].focus();
    return afectados.length > 0;
}

async function pedirCategorias() {
    peticionCategorias?.abort();
    peticionCategorias = new AbortController();
    const { signal } = peticionCategorias;
    categoria.disabled = true;
    guardar.disabled = true;
    reintentarCategorias.hidden = true;
    mostrarError("categoria_id");
    categoria.options[0].textContent = "Cargando categorías…";

    try {
        const opciones = (await listarCategorias(signal)).filter((item) => item.activo);
        if (signal.aborted) return;
        cargarOpciones(categoria, opciones);
        categoria.value = "";
        categoria.options[0].textContent = "Elegí una categoría";
        if (opciones.length === 0) {
            mostrarError("categoria_id", "Todavía no hay categorías activas.");
            reintentarCategorias.hidden = false;
            return;
        }
        categoria.disabled = false;
        guardar.disabled = false;
    } catch (error) {
        if (signal.aborted) return;
        categoria.options[0].textContent = "Elegí una categoría";
        mostrarError("categoria_id", mensajeError(error));
        reintentarCategorias.hidden = false;
    }
}

abrir.addEventListener("click", () => {
    exito.hidden = true;
    errorAlta.hidden = true;
    for (const campo of campos) mostrarError(campo);
    modal.showModal();
    pedirCategorias();
});
cerrar.addEventListener("click", () => modal.close());
cancelar.addEventListener("click", () => modal.close());
reintentarCategorias.addEventListener("click", pedirCategorias);
modal.addEventListener("cancel", (evento) => {
    if (guardando) evento.preventDefault();
});
modal.addEventListener("close", () => {
    if (!modal.open) peticionCategorias?.abort();
});

formulario.addEventListener("input", (evento) => {
    if (mensajes.has(evento.target.name)) mostrarError(evento.target.name);
});

formulario.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    if (guardando || guardar.disabled) return;
    errorAlta.hidden = true;
    for (const campo of campos) mostrarError(campo);

    const datos = datosProducto(formulario);
    if (mostrarErrores(validarProducto(datos))) return;

    guardando = true;
    guardar.disabled = true;
    cerrar.disabled = true;
    cancelar.disabled = true;
    guardar.textContent = "Creando…";

    let producto;
    try {
        producto = await crearProducto(datos);
    } catch (error) {
        if (!mostrarErrores(erroresDeApi(error))) {
            errorAlta.textContent = mensajeError(error);
            errorAlta.hidden = false;
        }
    } finally {
        guardando = false;
        guardar.disabled = false;
        cerrar.disabled = false;
        cancelar.disabled = false;
        guardar.textContent = "Crear producto";
    }

    if (producto) {
        formulario.reset();
        modal.close();
        exito.textContent = `Producto #${producto.id} creado. ${producto.nombre} ya está en el catálogo.`;
        exito.hidden = false;
        exito.focus();
        seleccionarFiltro("activos");
        await cargarPagina(Math.ceil((totalActivos + 1) / LIMITE), true);
    }
});

cargarPagina(1);

