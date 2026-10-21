# GUÍA DEL PROYECTO INTEGRADOR: APLICACIONES WEB II

## 1. Información General del Proyecto
- **Tecnologías Principales:** Python, Django, MySQL, HTML5, CSS3, JavaScript, Git/GitHub, `pytest`, `pytest-django`.
- **Objetivo:** Convertir el diseño de software aprobado en una aplicación web funcional, dinámica, probada y desplegada en producción.
- **Metodología:** Desarrollo incremental basado en un MVP (Producto Mínimo Viable) en equipos de 3 a 4 estudiantes. Cada integrante debe entender y defender todo el código.

---

## 2. Tecnologías y Estructura Técnica
- **Frontend:** `base.html` y plantillas hijas, HTML semántico, CSS3, Bootstrap (opcional), JavaScript vanilla/Web APIs.
- **Backend:** Django (Proyecto, Apps, Modelos, Vistas, Formularios/ModelForms, URLs, Middlewares).
- **Base de Datos:** MySQL conectada mediante Django ORM (Migraciones, Consultas ORM, Relaciones/FK).
- **Pruebas:** `pytest` y `pytest-django` (Mínimo 6 pruebas automatizadas).
- **Seguridad:** Variables de entorno (`.env`), `DEBUG = False` en producción, protección CSRF, contraseñas encriptadas, validaciones del lado del servidor.

---

## 3. Cronograma por Clases y Entregables

### Clase 1: Entorno y Frontend
- **Objetivo:** Configuración inicial del entorno y maquetación navegable.
- **Actividades:**
  - Crear entorno virtual (`venv`), instalar dependencias e inicializar proyecto Django y App.
  - Configurar rutas, vistas iniciales y archivos estáticos.
  - Crear plantilla `base.html` y vistas secundarias con navegación.
- **Entregables:** Repositorio GitHub con primer commit ejecutable y páginas iniciales navegables.

### Clase 2: Backend y MySQL
- **Objetivo:** Persistencia de datos y operaciones CRUD principales.
- **Actividades:**
  - Configurar conexión a base de datos MySQL en `settings.py`.
  - Definir entidades en `models.py` y ejecutar migraciones (`makemigrations`, `migrate`).
  - Crear formularios de Django y vistas para operaciones CRUD sobre la entidad principal.
- **Entregables:** Operaciones de Crear, Leer, Actualizar y Eliminar (CRUD) completamente funcionales y persistidas en MySQL.

### Clase 3: Integración Completa
- **Objetivo:** Conexión total de vistas, usuarios, roles y reglas de negocio.
- **Actividades:**
  - Implementar autenticación nativa (Login/Logout).
  - Configurar al menos 2 roles de usuario con permisos diferenciados.
  - Integrar mensajes de estado/error y validaciones de servidor en formularios.
- **Entregables:** Demostración de un caso de uso completo de principio a fin con usuarios autenticados.

### Clase 4: Pruebas y Correcciones
- **Objetivo:** Asegurar calidad del software mediante pruebas automatizadas.
- **Actividades:**
  - Configurar `pytest` y `pytest-django`.
  - Escribir pruebas para modelos, validaciones, formularios y restricciones de permisos.
  - Documentar y corregir fallos detectados.
- **Entregables:** Mínimo 6 pruebas automatizadas ejecutadas exitosamente y reporte de incidencias corregidas.

### Clase 5: Despliegue en Producción
- **Objetivo:** Publicar la aplicación web en un servidor accesible en línea.
- **Actividades:**
  - Configurar hosting compatible con Django.
  - Ocultar secretos en variables de entorno (`SECRET_KEY`, datos DB).
  - Configurar `ALLOWED_HOSTS`, desactivar `DEBUG` y ejecutar `collectstatic`.
- **Entregables:** URL pública accesible, archivo `README.md` con instrucciones de instalación y checklist de despliegue.

---

## 4. Requisitos Técnicos Mínimos de Entrega
1. **Módulos y CRUD:** Dos módulos funcionales principales y un CRUD completo sobre la entidad central.
2. **Autenticación y Permisos:** Sistema de login/logout con al menos 2 roles diferenciados.
3. **Validación:** Validaciones estrictas en el servidor (nunca confiar solo en JavaScript).
4. **Calidad de Código:** Mínimo 6 casos de prueba automatizados con `pytest-django`.
5. **Historial de Commits:** Commits progresivos y verificables de todos los integrantes del equipo.
6. **Documentación:** Archivo `README.md` detallado con pasos para clonar y ejecutar el proyecto.

---

## 5. Criterios de Evaluación
| Criterio | Porcentaje |
| :--- | :--- |
| **Backend y Lógica de Negocio** | 25% |
| **Frontend y Experiencia de Usuario (UX)** | 15% |
| **Base de Datos e Integración (MySQL)** | 15% |
| **Funcionalidades Completas del MVP** | 15% |
| **Pruebas y Calidad (pytest)** | 15% |
| **Despliegue y Documentación (README)** | 10% |
| **Sustentación Individual** | 5% |

---

## 6. Lo que NO se Aceptará
- Presentar prototipos estáticos (Figma) como aplicación terminada.
- Pantallas sin lógica de negocio o sin persistencia en base de datos MySQL.
- Aplicaciones que usen datos fijos (*hardcoded*) codificados en HTML/JS.
- Proyectos sin participación o commits verificables de los integrantes.
- Proyectos sin suite de pruebas o sin enlace de despliegue en línea.