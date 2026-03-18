# 🤖 AgenteAI — Asistente de Ingeniería Informática Pro

> **AgenteAI v2.5** es una plataforma de inteligencia artificial avanzada diseñada específicamente para potenciar la productividad de ingenieros de software, arquitectos de sistemas y líderes técnicos. Impulsado por el modelo **Google Gemini 2.5 Flash**, este asistente no solo conversa, sino que opera directamente sobre tu entorno de desarrollo.

---

## 📌 ¿Para qué sirve?

AgenteAI actúa como un **Principal Tech Lead Engineer** virtual. Está diseñado para asistir en todas las etapas del ciclo de vida del desarrollo de software (SDLC):

1.  **Levantamiento y Análisis**: Transforma ideas vagas en requerimientos técnicos sólidos, historias de usuario detalladas y criterios de aceptación (Gherkin).
2.  **Arquitectura de Sistemas**: Propone diseños de infraestructura, comparativas de tecnología (Trade-offs) y arquitecturas resilientes (Cloud-Native, Monolitos, Microservicios).
3.  **Implementación de Código**: Genera, analiza y refactoriza código siguiendo principios de **Clean Code**, **SOLID** y patrones de diseño modernos.
4.  **Operaciones y DevOps**: Ayuda con la configuración de pipelines CI/CD, scripts de automatización en Bash/Python y despliegue sobre Docker/Kubernetes.
5.  **Ciberseguridad**: Realiza revisiones de seguridad proactivas y sugiere mejores prácticas basadas en OWASP.

---

## 🏗️ Arquitectura del Sistema

El proyecto sigue una arquitectura modular y reactiva para garantizar rapidez y extensibilidad:

### Flujo de Datos
1.  **Frontend (UI)**: Interfaz basada en terminal que envía mensajes via JSON a Flask.
2.  **Backend (Flask)**: Gestiona las rutas y levanta el motor de IA (`AIAgent`).
3.  **Motor de IA (`AIAgent`)**: 
    *   Inyecta el **Contexto Dinámico** (archivos de `project-context/`).
    *   Gestiona la sesión con **Gemini 2.5 Flash**.
    *   Implementa un **Bucle de Ejecución de Herramientas** manual para permitir streaming real de texto mientras procesa llamadas a funciones.
4.  **Capa de Herramientas (`Tools`)**: Funciones nativas de Python que el agente "llama" para interactuar con el sistema de archivos, la web o el terminal.

### Stack Tecnológico
*   **Lenguaje**: Python 3.10+
*   **Web Framework**: Flask (con soporte SSE para streaming).
*   **Modelo de Lenguaje**: Google Gemini 2.5 Flash API.
*   **Frontend**: HTML5, CSS3 (Custom Terminal Style), Bootstrap 5.
*   **Librerías Clave**:
    *   `google-generativeai`: SDK para interacción con Gemini.
    *   `Mermaid.js`: Motor de renderizado de diagramas técnicos.
    *   `Ace Editor`: IDE lateral integrado para edición de código en vivo.
    *   `Marked.js` & `Highlight.js`: Formateo de texto y sintaxis.

---

## 🧩 Capacidades y Herramientas (Function Calling)

A diferencia de un chat convencional, AgenteAI tiene "manos" en el sistema a través de herramientas programadas:

| Herramienta | Descripción Técnica | Caso de Uso |
| :--- | :--- | :--- |
| `run_command` | Ejecuta comandos Bash/Shell en el sistema host. | `ls -R`, `git status`, `pip install`. |
| `run_python_code` | Ejecuta fragmentos de código Python en tiempo real. | Cálculo complejo, manipulación de datos, pruebas rápidas. |
| `create_file` | Escribe contenido en archivos, creando directorios si es necesario. | Generar scripts, archivos de configuración, documentación. |
| `read_file` | Lee el contenido íntegro de cualquier archivo local. | Analizar código existente, leer logs. |
| `list_directory` | Explora la estructura de carpetas (excluyendo basura como `node_modules`).| Entender la jerarquía de un proyecto nuevo. |
| `fetch_url` | Navega por la web y extrae el texto limpio de una URL. | Leer documentación oficial o noticias técnicas. |
| `search_context` | Busca palabras clave en el directorio `project-context/`. | Localizar guías de estilo o recordatorios específicos. |

---

## 🧠 Inteligencia con Contexto Dinámico

AgenteAI no viene "vacío". Utiliza una técnica de inyección de contexto desde la carpeta `/project-context`:

*   **`guia_estilo_codigo.md`**: El agente siempre escribirá código respetando tus reglas (ej: tabulación, nombres de variables).
*   **`perfil_usuario.md`**: Conoce quién eres, qué tecnologías prefieres y cómo te gusta trabajar.
*   **`stack_tecnologico.md`**: Define las tecnologías por defecto de tus proyectos para que el agente no sugiera cosas fuera de tu stack actual.

> [!TIP]
> Puedes añadir cualquier archivo `.md` a esta carpeta para añadir "conocimiento permanente" al agente.

---

## 🖥️ Experiencia de Usuario (UI/UX)

La interfaz web ha sido diseñada para ser una herramienta de trabajo de alta gama:

*   **Terminal Aesthetic**: Tipografía `Press Start 2P`, colores contrastados y look retro-futurista.
*   **Streaming de Alta Velocidad**: Verás la respuesta de la IA mientras se genera (vía Server-Sent Events).
*   **Diagraming-as-Code**: Integración nativa con **Mermaid.js**. Solo pídele un diagrama de flujo o secuencia y lo verás renderizado al instante.
*   **IDE Lateral (Editor Ace)**: Cada bloque de código tiene un botón **"EDITAR ✎"**. Al hacer clic, se abre un editor lateral tipo VS Code donde puedes modificar el código y guardarlo directamente al sistema de archivos del servidor.
*   **Memoria Persistente**: Todo el historial se guarda en `chat_history.json`. Si reinicias el servidor, el agente recordará lo que estaban haciendo.

---

## 🚀 Instalación y Despliegue

### Requisitos Previos
- Python 3.10 o superior.
- Una API Key de Google Gemini (puedes obtenerla gratis en [Google AI Studio](https://aistudio.google.com/)).

### Pasos
1.  **Clonar:** `git clone https://github.com/TheNewAarons/AgenteAI.git`
2.  **Entorno Virtual:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  **Dependencias:** `pip install -r requirements.txt`
4.  **Configuración:** Crea un archivo `.env` con lo siguiente:
    ```env
    GEMINI_API_KEY=tu_api_key_aqui
    ```
5.  **Ejecutar:** `python3 app.py`

Accede en: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 📂 Organización del Proyecto

*   `app.py`: Punto de entrada Flask y configuración del servidor.
*   `agent.py`: Interfaz de línea de comandos (CLI) minimalista.
*   `core/`: El "corazón" del sistema.
    *   `agent_engine.py`: Lógica de orquestación de Gemini y manejo de hilos.
    *   `tools.py`: Definición de funciones y herramientas del sistema.
    *   `routes.py`: Endpoints de la API REST.
*   `project-context/`: Base de datos de conocimiento en Markdown.
*   `static/` & `templates/`: El motor visual (CSS, JS, Jinja2).

---

## 🤝 Créditos y Contribución

Desarrollado como una herramienta de ingeniería de precisión. 
Si deseas contribuir, asegúrate de mantener la modularidad en `core/tools.py` y el estilo arquitectónico decoupled.

**Autor**: [TheNewAarons](https://github.com/TheNewAarons)
**Licencia**: Uso Educativo / Personal.
