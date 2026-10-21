# Cartaviva

Plataforma web para descubrir, inscribirse y hacer check-in seguro en eventos comunitarios de **Cartagena de Indias**.
Proyecto articulado entre **Diseño Web** y **Aplicaciones Web II**, Institución Universitaria Rafael Núñez.

**Equipo:** Katiusca Quiroz · Miguel Ortega · Gabriel Ruiz Rivera · Isaac David Triviño Ruiz · Jhon Perez

**Esqueleto publicado:** https://cartaviva-ten.vercel.app (QR en `entregables/QR_esqueleto_cartaviva.png`)
**Repositorio:** https://github.com/isaactrivi14/cartaviva

Stack: Python · Django 5.2 · MySQL (o SQLite para probar) · HTML5 · CSS3 · JavaScript · pytest

---

## Qué hay en esta carpeta

| Carpeta / archivo | Para qué sirve |
| --- | --- |
| `entregables/` | La ficha del proyecto en Word y la presentación en PowerPoint |
| `esqueleto/` | El esqueleto de 6 pantallas como sitio web estático, listo para publicar en Vercel |
| `config/`, `usuarios/`, `eventos/`, `inscripciones/` | El MVP en Django (backend) |
| `templates/`, `static/` | Las pantallas del MVP (HTML, CSS y JavaScript) |
| `tests/` | 11 pruebas automatizadas con pytest |
| `iniciar.bat` | Instala y arranca todo con doble clic (Windows) |
| `iniciar.sh` | Lo mismo para macOS o Linux |
| `publicar.bat` | Sube el proyecto a tu GitHub y publica el esqueleto en tu Vercel (Windows) |

---

## 1. Qué instalar (una sola vez)

| Programa | Obligatorio | Dónde se descarga | Ojo |
| --- | --- | --- | --- |
| **Python 3.12 o superior** | Sí | https://www.python.org/downloads/ | En el instalador marca **"Add python.exe to PATH"** |
| **Visual Studio Code** | Ya lo tienes | https://code.visualstudio.com/ | Al abrir la carpeta te sugerirá la extensión **Python**: acéptala |
| **Git** | Solo para subir a GitHub y Vercel | https://git-scm.com/downloads | Deja todas las opciones por defecto |
| **MySQL 8** | Solo si van a usar MySQL | https://dev.mysql.com/downloads/installer/ o XAMPP (https://www.apachefriends.org/) | Para la demo no hace falta: arranca con SQLite |

Para comprobar que Python quedó bien, abre una terminal (en VS Code: menú **Terminal → New Terminal**) y escribe:

```
python --version
```

Debe responder `Python 3.12.x` o superior. Si dice que no se reconoce el comando, reinstala Python marcando "Add python.exe to PATH".

---

## 2. Correr el MVP

### Opción fácil (Windows)

1. Descomprime la carpeta `cartaviva` en el Escritorio.
2. Haz **doble clic en `iniciar.bat`**.
3. La primera vez tarda unos minutos porque instala las librerías. Al final se abre el navegador en **http://127.0.0.1:8000**.
4. Para detener el servidor, cierra la ventana negra o presiona `CTRL + C`.

Las siguientes veces basta con volver a hacer doble clic en `iniciar.bat`.

### Opción desde la terminal de VS Code

Abre la carpeta en VS Code (**File → Open Folder…**), abre una terminal y ejecuta:

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py cargar_demo
python manage.py runserver
```

En macOS o Linux cambia `.venv\Scripts\activate` por `source .venv/bin/activate` y `copy` por `cp`.

### Usuarios de prueba

Contraseña para todos: **`Cartaviva2026!`**

| Rol | Correo | Para probar |
| --- | --- | --- |
| Administrador | `admin@cartaviva.co` | Todo, más el panel `/admin/` |
| Anfitrión | `anfitrion@cartaviva.co` | Crear, editar y eliminar eventos; escanear pases; ver métricas |
| Asistente | `asistente@cartaviva.co` | Inscribirse, ver su pase QR y su Pasaporte Cartagenero |
| Asistente menor de edad | `menor@cartaviva.co` | Que el sistema lo rechace en eventos +18 |

---

## 3. Guion para mostrar el MVP (5 minutos)

1. **Mapa:** en la página de inicio se ven los eventos de Cartagena con colores por estado: abierto (azul), últimos cupos (naranja), lleno (gris) y en vivo (rojo, con pulso). Prueba los filtros *Hoy*, *Relámpago* y *Categoría*.
2. **Inscripción:** entra como `asistente@cartaviva.co`, abre «Feria de sabores…» y toca **Inscribirme**. Aparece el **pase QR**.
3. **Reglas de negocio:** intenta inscribirte a «Noche de jazz (+18)»: está lleno. Entra como `menor@cartaviva.co`: un evento +18 no lo deja inscribirse.
4. **Check-in:** en otra ventana del navegador (modo incógnito) entra como `anfitrion@cartaviva.co` → **Panel** → **Escanear** en la Feria. Apunta la cámara del portátil al QR del celular o de la otra ventana. Si no hay cámara, copia el código que aparece en «¿No funciona la cámara del anfitrión?» del pase y pégalo en el escáner.
5. **Validación ciega:** el escáner solo muestra alias, foto, «Pase autorizado» y «+18 verificado». Toca **Registrar ingreso**. Si escaneas el mismo QR otra vez, lo rechaza.
6. **Métricas:** vuelve al **Panel**: la tasa de asistencia efectiva subió. En **Perfil** del asistente se ve el Pasaporte Cartagenero.
7. **CRUD:** como anfitrión crea un evento, márcalo como *Plan relámpago* con 9 horas de duración. El servidor lo rechaza: debe durar entre 1 y 6 horas.

> La cámara del navegador solo funciona en `localhost` o con HTTPS. En el portátil funciona; desde un celular conectado por la red local no, hasta que se despliegue con HTTPS (Clase 5).

---

## 4. Usar MySQL (requisito de la guía)

1. Instala MySQL 8 (o XAMPP y enciende **MySQL** en su panel).
2. Crea la base de datos. En MySQL Workbench, o en la consola de MySQL:
   ```sql
   CREATE DATABASE cartaviva CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
3. Abre el archivo `.env` y cambia:
   ```
   DB_ENGINE=mysql
   DB_USER=root
   DB_PASSWORD=tu_contraseña_de_mysql
   ```
   (En XAMPP el usuario es `root` y la contraseña va vacía.)
4. Ejecuta `python manage.py migrate` y `python manage.py cargar_demo`, o vuelve a abrir `iniciar.bat`.

El conector es **PyMySQL**, que se instala con pip sin compilar nada.

---

## 5. Pruebas automatizadas

Con el entorno activado (`.venv\Scripts\activate`):

```
pytest -v
```

Son 11 pruebas (la guía pide mínimo 6). Cubren el estado del evento, la tasa de asistencia, los planes relámpago, la ubicación dentro de Cartagena, la autorización de datos en el registro, el rechazo a menores en eventos +18, el cupo y la doble inscripción, los permisos por rol y la validación ciega del QR.

---

## 6. Publicar el esqueleto en Vercel (link para el celular)

Lo que se publica es solo la carpeta `esqueleto/` (HTML estático). El MVP de Django no se sube a Vercel.

### Opción automática: doble clic en `publicar.bat` (Windows)

1. Ten a mano tus cuentas de **GitHub** y **Vercel** (crea la de Vercel en https://vercel.com entrando con GitHub).
2. Haz **doble clic en `publicar.bat`**.
3. Si te falta Git, GitHub CLI o Node.js, el script los instala con winget. Acepta si Windows pide permiso. Cuando termine, **cierra la ventana y vuelve a abrir `publicar.bat`**.
4. Escribe tu nombre y tu correo de GitHub cuando te los pida (solo la primera vez).
5. Se abrirá el navegador **dos veces**: una para GitHub (copia el código que muestra la ventana y pégalo en la página) y otra para Vercel (elige *Continue with GitHub*). Inicia sesión y vuelve a la ventana negra.
6. Al final aparece una línea **Production** con el link `https://….vercel.app`. Ese es el link para el celular.

Para publicar cambios después, vuelve a abrir `publicar.bat`: guarda, sube y vuelve a publicar.

### Opción manual

#### Paso A: subir el proyecto a tu GitHub desde VS Code

1. Instala Git (ver tabla de arriba) y reinicia VS Code.
2. Abre la carpeta `cartaviva` en VS Code.
3. Ve al ícono de **Source Control** (la ramita, a la izquierda) → **Initialize Repository**.
4. Escribe un mensaje, por ejemplo `Entregable 1: ficha, esqueleto y MVP`, y toca **Commit**. Si VS Code pregunta por nombre y correo, configúralos en la terminal:
   ```
   git config --global user.name "Tu Nombre"
   git config --global user.email "tu-correo@ejemplo.com"
   ```
5. Toca **Publish Branch** → **Publish to GitHub** → inicia sesión con tu cuenta → elige **public** o **private**.

El archivo `.gitignore` ya evita que se suban el `.env`, la base de datos y el entorno virtual.

#### Paso B: conectarlo con Vercel

1. Entra a https://vercel.com e inicia sesión **con tu cuenta de GitHub**.
2. **Add New… → Project** → elige el repositorio `cartaviva` → **Import**.
3. En la configuración:
   - **Root Directory:** toca *Edit* y elige **`esqueleto`** (esto es lo más importante).
   - **Framework Preset:** `Other`.
   - Build Command y Output Directory: déjalos vacíos.
4. Toca **Deploy**. En menos de un minuto Vercel da un link como `https://cartaviva-xxxx.vercel.app`.
5. Abre ese link en el celular. Desde la portada se navega por las 6 pantallas.

Cada vez que hagan *Commit* y *Sync* en VS Code, Vercel vuelve a publicar solo.

---

## 7. Cómo está construido (para la sustentación)

- **Tres apps de Django:** `usuarios` (cuenta, roles, Pasaporte), `eventos` (entidad central, CRUD, mapa, API JSON) e `inscripciones` (pase QR, escáner, check-in).
- **Usuario personalizado** (`usuarios.Usuario`) con `rol` = ADMIN, ANFITRION o ASISTENTE. Se creó antes de la primera migración porque Django no permite cambiarlo después.
- **Permisos por rol:** decorador `rol_requerido` en `usuarios/permisos.py`. Además, cada anfitrión solo puede editar, eliminar o escanear sus propios eventos.
- **Validaciones en el servidor:** `Evento.clean()` (fechas, duración del plan relámpago entre 1 y 6 horas, cupo, ubicación dentro de Cartagena) y `RegistroForm` (correo único, fecha de nacimiento válida, autorización de datos obligatoria).
- **Estado del evento calculado**, no guardado: abierto, últimos cupos, lleno, en vivo o finalizado salen de las fechas y los cupos.
- **Mapa:** Leaflet + OpenStreetMap (gratis, sin API key). Los marcadores salen del endpoint `/api/eventos/`, que consulta la base de datos. El filtro de distancia usa la fórmula de Haversine.
- **Pase QR con privacidad primero (Ley 1581 de 2012):** el QR contiene un UUID aleatorio **firmado** con la `SECRET_KEY` (`django.core.signing`). No lleva datos personales y no se puede falsificar. El escáner usa `html5-qrcode` con la cámara del navegador.
- **Validación ciega:** `inscripciones/views.py → validar` solo devuelve alias, foto, si el pase está autorizado y si es mayor de 18. No se guarda cédula ni teléfono.
- **Cupo sin carreras:** la inscripción usa `transaction.atomic()` + `select_for_update()`, y una restricción única en la BD impide inscribirse dos veces.
- **Seguridad:** secretos en `.env`, `DEBUG` desde el entorno, protección CSRF activa (también en las peticiones `fetch` del escáner) y contraseñas cifradas por Django.

## 8. Checklist de despliegue en producción (Clase 5)

- [ ] `DEBUG=False` y una `SECRET_KEY` nueva y larga en el `.env` del servidor
- [ ] `ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS` con el dominio real
- [ ] `DB_ENGINE=mysql` con la base de datos del hosting
- [ ] `python manage.py migrate` y `python manage.py collectstatic`
- [ ] HTTPS activo (necesario para que el escáner use la cámara del celular)
- [ ] Crear el superusuario con `python manage.py createsuperuser`
