export function datosPagina(numero, limite, total) {
    return {
        skip: (numero - 1) * limite,
        paginas: Math.max(1, Math.ceil(total / limite)),
    };
}

export function mostrarPaginacion(controles, numero, paginas) {
    controles.actual.textContent = `Página ${numero} de ${paginas}`;
    controles.anterior.disabled = numero <= 1;
    controles.siguiente.disabled = numero >= paginas;
}

