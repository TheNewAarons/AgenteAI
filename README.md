# 🤖 AgenteAI — Asistente de Ingeniería Informática

> **Asistente de Inteligencia Artificial especializado en Ingeniería Informática**, impulsado por **Google Gemini 2.5 Flash**, con interfaz web tipo terminal, streaming en tiempo real, generación de diagramas y editor de código integrado.

---

## 📌 ¿Para qué sirve?

AgenteAI es un asistente técnico de alto nivel diseñado para apoyar a ingenieros en informática en todas las fases de un proyecto de software. Actúa como un **Principal Tech Lead Engineer** con conocimientos multidisciplinarios, capaz de:

- 📋 **Levantamiento de Requerimientos**: Analiza necesidades, desglosa épicas, formula historias de usuario y criterios de aceptación (funcionales y no funcionales).
- 🗂️ **Planificación de Proyectos**: Propone checklists detallados, estimaciones de tiempo, asignación de roles y hojas de ruta.
- 🧠 **Toma de Decisiones**: Presenta análisis de Pros y Contras estructurados para diferentes alternativas tecnológicas o arquitectónicas.
- 💻 **Generación de Código**: Escribe código en Python, JavaScript, SQL, HTML/CSS, Bash y más, respetando principios de Clean Code, SOLID y Patrones de Diseño.
- 📊 **Diagramas Técnicos**: Genera diagramas en tiempo real dentro del chat usando **Mermaid.js**:
  - Diagramas de Flujo
  - Diagramas de Secuencia (UML)
  - Diagramas Entidad-Relación (ER / Base de Datos)
  - Diagramas de Arquitectura (microservicios, monolito, serverless)
  - Diagramas de Red e Infraestructura
- ✏️ **IDE de Código Integrado**: Al recibir un fragmento de código, puedes abrirlo en un editor lateral con resaltado de sintaxis (**Ace Editor**) para editarlo y copiarlo fácilmente.

---

## 🛠️ Tecnologías Utilizadas

### Backend
| Tecnología | Uso |
|---|---|
| **Python 3** | Lenguaje base |
| **Flask** | Servidor web y API REST |
| **Google Gemini 2.5 Flash** | Modelo de IA generativa |
| **google-generativeai** | SDK oficial de Gemini |
| **python-dotenv** | Gestión de variables de entorno |

### Frontend
| Biblioteca | Uso |
|---|---|
| **HTML + CSS + JavaScript** | Interfaz de usuario |
| **Bootstrap 5** | Layout base responsivo |
| **Marked.js** | Renderizado de Markdown con saltos de línea |
| **Highlight.js** | Coloreado de sintaxis en bloques de código |
| **Mermaid.js** | Renderizado de diagramas técnicos |
| **Ace Editor** | Editor de código lateral en vivo |

---

## 🚀 Instalación y Ejecución

### 1. Clona el repositorio
```bash
git clone https://github.com/TheNewAarons/AgenteAI.git
cd AgenteAI
```

### 2. Crea y activa el entorno virtual
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows
```

### 3. Instala las dependencias
```bash
pip install -r requirements.txt
```

### 4. Configura tu API Key de Gemini
Crea un archivo `.env` en la raíz del proyecto:
```env
GEMINI_API_KEY=tu_clave_aqui
```
> Puedes obtener tu clave gratis en [aistudio.google.com](https://aistudio.google.com/apikey)

### 5. Ejecuta el servidor
```bash
python3 app.py
```

### 6. Abre la interfaz web
Visita en tu navegador: **http://127.0.0.1:5000**

---

## 🖥️ Características de la Interfaz

- **Diseño de Terminal**: Estética estilo hacker/terminal con tipografía `Press Start 2P`.
- **Streaming en Tiempo Real**: Las respuestas del agente aparecen letra por letra.
- **Markdown Renderizado**: Listas, tablas, encabezados y bloques de código formateados.
- **Diagramas Dinámicos**: Mermaid.js convierte texto en diagramas SVG interactivos.
- **Editor Lateral (IDE)**: Botón "EDITAR ✎" en cada bloque de código que abre **Ace Editor** con:
  - Detección automática del lenguaje
  - Números de línea
  - Coloreado de sintaxis
  - Copia directa al portapapeles
- **Memoria Persistente**: El historial del chat se guarda en `chat_history.json` y persiste entre reinicios.

### Comandos rápidos disponibles
| Comando | Función |
|---|---|
| `/help` | Muestra la ayuda y comandos disponibles |
| `/clear` | Limpia el chat y borra el historial de memoria |
| `/status` | Muestra el estado del sistema |
| `/history` | Informacion sobre el historial guardado |

---

## 📂 Estructura del Proyecto

```
AgenteAI/
├── app.py                 # Backend Flask: API, Gemini, streaming, function calling
├── agent.py               # CLI alternativo para usar el agente en terminal
├── requirements.txt       # Dependencias Python
├── .env                   # Variables de entorno (NO se sube a Git)
├── .gitignore             # Archivos excluidos de Git
├── README.md              # Este archivo
└── templates/
    └── index.html         # Interfaz web completa (UI + JS + CSS)
```

---

## 🧩 Áreas de Especialización del Agente

El agente está configurado como un **Ingeniero Principal en Informática** con experiencia en:

- **Desarrollo de Software**: Python, JavaScript, arquitectura de aplicaciones.
- **Bases de Datos**: SQL, NoSQL, diseño de esquemas, optimización de queries.
- **Redes y Sockets**: Topologías, protocolos, configuración de firewall.
- **Ciberseguridad**: Análisis de vulnerabilidades, mejores prácticas, OWASP.
- **DevOps / Cloud**: CI/CD, Docker, Kubernetes, Terraform, AWS, GCP.

---

## 📄 Licencia

Proyecto de uso personal / educativo. Todos los derechos reservados al autor.
