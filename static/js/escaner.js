/* Escáner web del anfitrión: usa la cámara del navegador (html5-qrcode / WebRTC),
   sin instalar ninguna app. La cámara solo funciona en localhost o con HTTPS. */
window.Cartaviva = window.Cartaviva || {};

Cartaviva.iniciarEscaner = function (opciones) {
  const csrf = document.querySelector("[name=csrfmiddlewaretoken]").value;
  const $ = (id) => document.getElementById(id);
  const resultado = $("resultado");
  let codigoActual = null;
  let lector = null;
  let pausado = false;

  async function validar(codigo, confirmar) {
    const respuesta = await fetch(opciones.url, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRFToken": csrf },
      body: JSON.stringify({ codigo: codigo, confirmar: confirmar }),
    });
    return respuesta.json();
  }

  function mostrar(datos) {
    resultado.classList.add("visible");
    resultado.classList.toggle("resultado--si", !!datos.autorizado);
    resultado.classList.toggle("resultado--no", !datos.autorizado);
    $("r-alias").textContent = datos.alias || "Pase no reconocido";
    $("r-estado").textContent = datos.autorizado ? (datos.registrado ? "Ingreso registrado" : "Pase autorizado") : "Pase rechazado";
    $("r-estado").className = "etiqueta " + (datos.autorizado ? "etiqueta--ok" : "etiqueta--EN_VIVO");
    $("r-edad").hidden = !datos.mayor_18;
    $("r-mensaje").textContent = datos.mensaje || "";
    if (datos.foto) { $("r-foto").src = datos.foto; $("r-foto").hidden = false; $("r-sin-foto").hidden = true; }
    else { $("r-foto").hidden = true; $("r-sin-foto").hidden = false; }
    $("confirmar").hidden = !(datos.autorizado && !datos.registrado);
    if (datos.registrado) $("contador").textContent = datos.ingresados + " de " + datos.inscritos;
  }

  async function procesar(codigo) {
    if (pausado) return;
    pausado = true;
    codigoActual = codigo;
    if (navigator.vibrate) navigator.vibrate(60);
    try { mostrar(await validar(codigo, false)); }
    catch (e) { mostrar({ autorizado: false, mensaje: "No hubo conexión con el servidor." }); }
  }

  $("confirmar").addEventListener("click", async () => {
    if (!codigoActual) return;
    $("confirmar").disabled = true;
    try { mostrar(await validar(codigoActual, true)); }
    finally { $("confirmar").disabled = false; }
  });

  $("otro").addEventListener("click", () => {
    resultado.classList.remove("visible");
    codigoActual = null;
    pausado = false;
    $("codigo").value = "";
  });

  $("manual").addEventListener("submit", (ev) => {
    ev.preventDefault();
    const codigo = $("codigo").value.trim();
    if (codigo) { pausado = false; procesar(codigo); }
  });

  if (window.Html5Qrcode) {
    lector = new Html5Qrcode("lector");
    lector.start({ facingMode: "environment" }, { fps: 10, qrbox: { width: 220, height: 220 } }, procesar, () => {})
      .then(() => { $("estado-camara").textContent = "Apunta la cámara al QR del asistente."; })
      .catch(() => { $("estado-camara").textContent = "No se pudo abrir la cámara (requiere permiso y HTTPS o localhost). Puedes pegar el código abajo."; });
  } else {
    $("estado-camara").textContent = "No cargó el lector de QR. Puedes pegar el código abajo.";
  }
};
