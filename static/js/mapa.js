/* Mapa de Cartaviva con Leaflet + OpenStreetMap (gratis, sin API key).
   Los eventos se piden al endpoint /api/eventos/, que los lee de la base de datos. */
window.Cartaviva = window.Cartaviva || {};

(function () {
  const COLORES = { ABIERTO: "#0077B6", ULTIMOS: "#F77F00", LLENO: "#8A96A3", EN_VIVO: "#D62839" };

  function crearMapa(id, centro, zoom) {
    const mapa = L.map(id, { zoomControl: true }).setView([centro.lat, centro.lng], zoom || 13);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: "&copy; OpenStreetMap",
    }).addTo(mapa);
    return mapa;
  }

  function icono(evento) {
    const clases = ["marcador", "marcador--" + evento.estado];
    if (evento.relampago) clases.push("marcador--relampago");
    return L.divIcon({
      className: "",
      html: '<div class="' + clases.join(" ") + '" style="background:' + (COLORES[evento.estado] || "#0077B6") + '"></div>',
      iconSize: [22, 22],
      iconAnchor: [11, 11],
    });
  }

  function escapar(texto) {
    const div = document.createElement("div");
    div.textContent = texto;
    return div.innerHTML;
  }

  function tarjeta(e) {
    return '<a class="evento-item" href="' + e.url + '">' +
      '<span class="evento-item__color" style="background:' + e.color + '"></span><div>' +
      '<div class="fila" style="gap:6px"><span class="etiqueta etiqueta--' + e.estado + '">' + escapar(e.estado_label) + "</span>" +
      (e.relampago ? '<span class="etiqueta etiqueta--relampago">Relámpago</span>' : "") + "</div>" +
      '<div class="evento-item__titulo">' + escapar(e.titulo) + "</div>" +
      '<div class="evento-item__meta">' + escapar(e.categoria) + " · " + escapar(e.inicio) + " · " + escapar(e.barrio) +
      (e.distancia !== null ? " · " + e.distancia + " km" : "") + "</div></div></a>";
  }

  Cartaviva.iniciarExplorar = function (opciones) {
    const mapa = crearMapa("mapa", opciones.centro, 13);
    const capa = L.layerGroup().addTo(mapa);
    const lista = document.getElementById("lista");
    const titulo = document.getElementById("titulo-lista");

    function cargar(extra) {
      const params = new URLSearchParams(window.location.search);
      Object.entries(extra || {}).forEach(([k, v]) => params.set(k, v));
      // Skeletons mientras llega la respuesta de la BD
      lista.innerHTML = '<div class="skeleton skeleton--item"></div>'.repeat(3);
      fetch(opciones.api + "?" + params.toString())
        .then((r) => r.json())
        .then((datos) => {
          capa.clearLayers();
          datos.eventos.forEach((e) => {
            L.marker([e.lat, e.lng], { icon: icono(e), title: e.titulo })
              .bindPopup("<strong>" + escapar(e.titulo) + "</strong><br>" + escapar(e.estado_label) + " · " + escapar(e.inicio) +
                '<br><a href="' + e.url + '">Ver detalle</a>')
              .addTo(capa);
          });
          lista.innerHTML = datos.eventos.length
            ? datos.eventos.map(tarjeta).join("")
            : '<div class="tarjeta vacio">No hay eventos con esos filtros.</div>';
          titulo.textContent = datos.eventos.length + (datos.eventos.length === 1 ? " evento" : " eventos");
        })
        .catch(() => { lista.innerHTML = '<div class="tarjeta vacio">No se pudieron cargar los eventos.</div>'; });
    }

    cargar();

    const botonCerca = document.getElementById("cerca");
    if (botonCerca) {
      botonCerca.addEventListener("click", () => {
        if (!navigator.geolocation) return alert("Tu navegador no permite ubicación.");
        botonCerca.textContent = "Ubicando…";
        navigator.geolocation.getCurrentPosition(
          (pos) => {
            const { latitude, longitude } = pos.coords;
            botonCerca.textContent = "A 5 km de mí";
            botonCerca.classList.add("activo");
            L.circle([latitude, longitude], { radius: 5000, color: "#0077B6", weight: 1, fillOpacity: 0.06 }).addTo(capa);
            mapa.setView([latitude, longitude], 13);
            cargar({ lat: latitude, lng: longitude, km: 5 });
          },
          () => { botonCerca.textContent = "Cerca de mí"; alert("No pudimos obtener tu ubicación."); }
        );
      });
    }
  };

  // Mapa para elegir el punto del evento en el formulario del anfitrión
  Cartaviva.iniciarSelector = function (opciones) {
    const lat = document.getElementById("id_latitud");
    const lng = document.getElementById("id_longitud");
    const inicial = lat.value && lng.value ? { lat: parseFloat(lat.value), lng: parseFloat(lng.value) } : opciones.centro;
    const mapa = crearMapa("mapa", inicial, 14);
    let marcador = lat.value ? L.marker([inicial.lat, inicial.lng]).addTo(mapa) : null;
    mapa.on("click", (ev) => {
      lat.value = ev.latlng.lat.toFixed(6);
      lng.value = ev.latlng.lng.toFixed(6);
      if (marcador) marcador.setLatLng(ev.latlng); else marcador = L.marker(ev.latlng).addTo(mapa);
    });
  };

  // Mapa de solo lectura en el detalle
  Cartaviva.iniciarPunto = function (opciones) {
    const mapa = crearMapa("mapa", opciones.punto, 15);
    L.marker([opciones.punto.lat, opciones.punto.lng]).addTo(mapa);
  };
})();
