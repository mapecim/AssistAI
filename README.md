# AssistAI – All-In-One Basket Analytics App 🏀🤖

**AssistAI** es una aplicación completa de analítica de baloncesto enfocada en la **Euroliga**, que permite a los usuarios interactuar a través de un chat inteligente para resolver dudas sobre estadísticas, generar informes, comparar jugadores/equipos, realizar búsquedas de jugadores similares y predecir el rendimiento de un quinteto basado en sus datos estadísticos.

## 🚀 Funcionalidades principales

| Funcionalidad                      | Descripción                                                                    |
| ---------------------------------- | ------------------------------------------------------------------------------ |
| 💬 Chat asistido                   | Realiza preguntas sobre datos de Euroliga y obtén respuestas contextualizadas. |
| 📊 Informes automáticos            | Genera informes detallados de jugadores o equipos.                             |
| 🔍 Búsqueda de jugadores similares | Encuentra jugadores con perfiles estadísticos parecidos.                       |
| 🔮 Predicción de quintetos         | Predice el rendimiento de un quinteto con cualquier combinación de jugadores.  |

---

## 📽️ Demo

[![AssistAI - DEMO](https://img.youtube.com/vi/CS19B3H0pqM/0.jpg)](https://www.youtube.com/watch?v=CS19B3H0pqM)

---

## 🧱 Tecnologías utilizadas

| Capa                | Tecnología           |
| ------------------- | -------------------- |
| Backend             | **Python + FastAPI** |
| Frontend            | **Streamlit**        |
| Base de datos       | **PostgreSQL**       |
| Versión recomendada | **Python 3.12.5**    |

---

## 📁 Estructura del proyecto

```
.
├── requirements.txt
├── src
│   ├── backend
│   │   └── main.py            ← Endpoints FastAPI
│   ├── frontend
│   │   └── ...                ← Aplicación Streamlit
│   └── ...
└── README.md
```

---

## ⚙️ Instalación

1. **Clonar el repositorio**

```bash
git clone https://github.com/mapecim/AssistAI.git
cd AssistAI
```

2. **Crear entorno virtual (opcional pero recomendado)**

```bash
python -m venv venv
source venv/bin/activate   # en Linux/macOS
venv\Scripts\activate      # en Windows
```

3. **Instalar dependencias**

```bash
pip install -r requirements.txt
```

4. **Configurar variables**

Puedes encontrar una plantilla del archivo `.env` que espera el proyecto en `.env-nokeys`. Cambia el nombre a `.env` y añade tus claves.

5. **Crear la Base de Datos**

Para crear la BD únicamente has de ejecutar el fichero correspondiente, el cual creará y poblará esta BD:

```bash
python etl/advanced/main.py
```

---

## ▶️ Ejecución

**1. Iniciar el backend FastAPI**

```bash
uvicorn src.backend.main:app --reload
```

**2. Iniciar el frontend Streamlit**

```bash
streamlit run src/frontend/app.py
```

> Abrirá automáticamente una ventana en tu navegador con la interfaz de AssistAI.

---

## 🔧 Endpoints principales (FastAPI)

Todos los endpoints del backend están definidos en:

```
src/backend/main.py
```

Puedes ver/usar todos los endpoints navegando a:

```
http://localhost:8000/docs
```

(autogenerado automáticamente por SwaggerUI)

---

## ✅ Requisitos

| Requisito  | Versión |
| ---------- | ------- |
| Python     | 3.12.5  |
| PostgreSQL | ≥ 13    |

---

## 📄 Licencia

Este proyecto se distribuye bajo la licencia **MIT**.

```
MIT License - Copyright (c) 2025 Mateo Peciña

```
