# Sumérgete+ — MVP

App educativa marina con:
- Asistente IA para docentes (chat)
- Fichas de especies marinas

## 1. Probarla en tu computador (antes de subirla a internet)

1. Instala Python si no lo tienes (python.org, versión 3.10 o superior).
2. Abre una terminal en esta carpeta y crea un entorno virtual:
   ```
   python -m venv venv
   source venv/bin/activate      # en Mac/Linux
   venv\Scripts\activate         # en Windows
   ```
3. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```
4. Consigue tu clave de la API de Anthropic en https://console.anthropic.com
5. Copia `.streamlit/secrets.toml.example` a `.streamlit/secrets.toml` y pega tu clave ahí.
   Este archivo NO se sube a GitHub (está en `.gitignore`), así tu clave queda segura.
6. Corre la app:
   ```
   streamlit run app.py
   ```
   Se abrirá sola en tu navegador en `http://localhost:8501`.

## 2. Subir el código a GitHub

1. Crea un repositorio nuevo en GitHub (botón verde "New").
2. Desde esta carpeta, en la terminal:
   ```
   git init
   git add .
   git commit -m "Primera versión del MVP"
   git branch -M main
   git remote add origin https://github.com/TU-USUARIO/NOMBRE-REPO.git
   git push -u origin main
   ```

## 3. Publicarla en internet (Streamlit Community Cloud, gratis)

1. Ve a https://streamlit.io/cloud y entra con tu cuenta de GitHub.
2. Clic en "New app", elige el repositorio que acabas de subir.
3. En "Main file path" escribe `app.py`.
4. Antes de darle "Deploy", entra a "Advanced settings" → "Secrets" y pega:
   ```
   ANTHROPIC_API_KEY = "tu-clave-real-aqui"
   ```
5. Dale "Deploy". En unos minutos tendrás una URL pública (algo como
   `sumergete.streamlit.app`) que puedes enviar a cualquier colegio.

## Próximos pasos sugeridos

- Agregar más especies al archivo `data/especies.json` (no necesitas tocar el
  código, solo copiar el formato de las que ya existen).
- Agregar un módulo simple de evaluación (preguntas + corrección automática).
- Guardar el uso real (qué preguntas hacen los docentes) para tener datos de
  tracción que mostrar en tu próxima postulación a Corfo.
