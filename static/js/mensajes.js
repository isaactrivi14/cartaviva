// Mensajes de estado: se cierran con la X y los de éxito se ocultan solos a los 6 segundos.
document.querySelectorAll(".mensaje").forEach(function (mensaje) {
  function cerrar() {
    mensaje.classList.add("mensaje--saliendo");
    setTimeout(function () { mensaje.remove(); }, 200);
  }
  var boton = mensaje.querySelector(".mensaje__cerrar");
  if (boton) boton.addEventListener("click", cerrar);
  if (mensaje.hasAttribute("data-ocultar")) setTimeout(cerrar, 6000);
});

// Si el formulario volvió con errores, el foco va al resumen para leerlo primero.
var resumen = document.getElementById("resumen-errores");
if (resumen) resumen.focus();
