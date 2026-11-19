# Reporte de incidencias corregidas

Entregable de la Clase 4 (Pruebas y correcciones). Cada fila es un fallo que apareció
mientras construíamos o probábamos Cartaviva, qué lo causaba y qué prueba evita que vuelva.

Cómo correr las pruebas: `python -m pytest -v` (19 pruebas).

| # | Fecha | Qué pasaba | Causa | Corrección | Prueba que lo cubre |
|---|---|---|---|---|---|
| INC-01 | 2026-10-21 | Crear un evento de prueba fallaba con "Asegúrese de que no haya más de 6 decimales" aunque la coordenada era correcta | Las coordenadas se pasaban como `float` (10.4206 se guarda como 10.42059999…) y el campo es `DecimalField` con 6 decimales | Usar `Decimal("10.420600")` en los datos de prueba | `test_evento_debe_estar_dentro_de_cartagena` y el fixture `hacer_evento` |
| INC-02 | 2026-10-21 | El mapa abría corrido, lejos del centro de Cartagena | Longitud del centro mal escrita en `settings.py` | `CARTAGENA_LNG = -75.5300` | Revisión manual en `/` (el mapa centra en el Centro Histórico) |
| INC-03 | 2026-10-21 | Al probar las páginas con el cliente de Django fuera de pytest salía `DisallowedHost` | `testserver` no está en `ALLOWED_HOSTS` | Usar `Client(HTTP_HOST="localhost")`; pytest-django ya lo maneja solo | Todas las pruebas de vistas |
| INC-04 | 2026-10-29 | `python manage.py check --deploy` daba 2 advertencias de seguridad (W004 y W008) | Faltaban HSTS y la redirección a HTTPS para producción | Configuración HTTPS/HSTS cuando `DEBUG=False` (TAREA-01) | `test_configuracion_de_produccion_pasa_check_deploy` |
| INC-05 | 2026-10-29 | Con `DEBUG=False` en el `.env`, las pruebas de vistas recibían 301 en vez de la página | La redirección a HTTPS también actuaba dentro de las pruebas | Fixture `sin_redireccion_https` en `tests/conftest.py` | Toda la suite corre igual con `DEBUG=True` o `False` |
| INC-06 | 2026-10-29 | `git status` mostraba archivos `~$...docx` | Word crea un archivo temporal mientras el documento está abierto | `~$*` en `.gitignore` | Revisión manual con `git status` |
| INC-07 | 2026-10-29 | En los formularios con errores el aviso salía dos veces y el enlace al campo "Rol" no llevaba a ningún lado | Mensaje general repetido en la vista y las opciones de radio usan el id `id_rol_0` | Resumen de errores único con enlaces correctos (TAREA-03) | `test_formulario_invalido_no_guarda_y_muestra_resumen_de_errores` |

## Qué cubren las pruebas nuevas de esta tarea (`tests/test_crud.py`)

| Prueba | Qué comprueba |
|---|---|
| `test_anfitrion_crea_evento_y_queda_guardado` | Crear: el evento se guarda en la base de datos, a nombre del anfitrión, con mensaje de éxito |
| `test_anfitrion_edita_su_evento` | Actualizar: los cambios quedan guardados |
| `test_eliminar_evento_borra_tambien_sus_inscripciones` | Eliminar: se borra el evento y sus inscripciones (no quedan datos huérfanos) |
| `test_eliminar_no_acepta_get` | Eliminar solo funciona por POST con CSRF; un enlace no puede borrar |
| `test_formulario_invalido_no_guarda_y_muestra_resumen_de_errores` | La validación del servidor frena datos malos y le dice al usuario qué corregir |
| `test_login_y_logout_muestran_mensaje` | Iniciar y cerrar sesión, con sus mensajes de estado |
