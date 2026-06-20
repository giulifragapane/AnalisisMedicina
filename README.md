# 🎓 Dashboard de Desempeño Académico — Medicina

**Trabajo Práctico Integrador — Hito 4**  
Grupo 51 · García, Fragapane  
Tecnicatura Universitaria en Programación · 2026

---

## 📋 Sobre el proyecto

Este dashboard analiza el rendimiento académico de **5.000 estudiantes de la carrera de Medicina**, de 1° a 6° año, provenientes de instituciones de educación **pública y privada**. Los datos incluyen variables académicas (promedio de notas, asistencia, entrega de trabajos prácticos), socioeconómicas (situación laboral, demora de traslado) y clasificaciones generadas mediante *feature engineering* (índice de compromiso, categoría de riesgo, condición de regularidad).

El sistema lee los datos en **tiempo real desde una base de datos MySQL**, y permite filtrar por año de carrera, género, tipo de educación y situación laboral. Todos los gráficos y métricas se actualizan automáticamente con cada cambio de filtro.

### ❓ Preguntas de negocio que responde

| # | Pregunta |
|---|---|
| **P1** | ¿Cuál es la diferencia en el promedio de notas entre estudiantes que trabajan y los que no, y esa diferencia se mantiene en todos los años de la carrera? |
| **P2** | ¿Los estudiantes con asistencia mayor al 75% aprueban más materias en promedio que los que tienen menor asistencia, y cómo varía eso según el tipo de educación (pública o privada)? |
| **P3** | ¿Qué porcentaje de estudiantes tiene simultáneamente un promedio de notas menor a 6, una entrega de TPs menor al 60% y una asistencia menor al 70%, y cuál es la demora de traslado promedio de ese grupo? |

---

## 🗂️ Estructura del repositorio

```
hito4/
├── app_dashboard.py          # Dashboard principal (Streamlit)
├── importar_datos.py         # Script de carga del CSV a MySQL (ejecutar una vez)
├── db.sql                    # Esquema de la base de datos y datos de muestra
├── dataset_medicina_limpio.csv  # Dataset limpio (5.000 registros)
├── .env.example              # Plantilla de variables de entorno
├── .env                      # Credenciales reales (NO se sube a GitHub)
└── .gitignore                # Excluye .env y archivos sensibles
```

---

## ⚙️ Requisitos previos

- **Python 3.10 o superior**
- **XAMPP** con el módulo **MySQL activo** (puerto 3306)
- **Git** instalado

---

## 🚀 Pasos para ejecutar localmente

### 1. Clonar el repositorio

Abrí una terminal y ejecutá:

```bash
git clone https://github.com/TU_USUARIO/TU_REPOSITORIO.git
cd hito4
```

> Reemplazá `TU_USUARIO/TU_REPOSITORIO` con la URL real del repositorio.

---

### 2. Instalar las dependencias

Dentro de la carpeta del proyecto, ejecutá:

```bash
pip install streamlit pymysql sqlalchemy pandas matplotlib seaborn python-dotenv
```

---

### 3. Iniciar XAMPP

Abrí el **Panel de Control de XAMPP** y hacé clic en **Start** en la fila de **MySQL**. Debe quedar en verde:

```
MySQL   [Start]  ✅ Running  →  puerto 3306
```

---

### 4. Crear el esquema de la base de datos

1. Abrí el navegador y entrá a: `http://localhost/phpmyadmin`
2. Hacé clic en la pestaña **SQL** (menú superior)
3. Copiá el contenido completo del archivo `db.sql` y pegalo en el editor
4. Hacé clic en **Ejecutar**

Esto crea la base de datos `medicina_db` con la tabla `estudiantes`, los índices necesarios y 10 registros de muestra para verificar que todo funciona.

---

### 5. Configurar las credenciales de conexión

Copiá el archivo de ejemplo y renombralo:

```bash
# En Windows
copy .env.example .env
```

Abrí el archivo `.env` y completalo con tus datos:

```env
DB_USER=root
DB_PASSWORD=          ← dejá vacío si tu XAMPP no tiene contraseña
DB_HOST=localhost
DB_PORT=3306
DB_NAME=medicina_db
```

> **⚠️ Importante:** el archivo `.env` nunca se sube a GitHub. Ya está incluido en el `.gitignore` para que esto no ocurra accidentalmente.

---

### 6. Cargar los datos del CSV a MySQL

Este paso se ejecuta **una sola vez**. Carga los 5.000 registros del dataset limpio a la base de datos:

```bash
python importar_datos.py
```

Si todo está bien, verás:

```
Conectando a MySQL...
✅ Base de datos 'medicina_db' lista.
📂 Leyendo dataset_medicina_limpio.csv ...
✅ 5000 registros cargados en la tabla 'estudiantes'.
   Siguiente paso: streamlit run app_dashboard.py
```

Podés verificar la carga en **phpMyAdmin** → `medicina_db` → `estudiantes` → debería mostrar 5.000 filas.

---

### 7. Lanzar el dashboard

```bash
streamlit run app_dashboard.py
```

El navegador se abre automáticamente en:

```
http://localhost:8501
```

---


## 🛠️ Tecnologías utilizadas

| Herramienta | Rol |
|---|---|
| **Python 3** | Lenguaje principal |
| **Streamlit** | Framework del dashboard interactivo |
| **MySQL (XAMPP)** | Motor de base de datos |
| **SQLAlchemy + PyMySQL** | Conexión Python ↔ MySQL |
| **Pandas** | Manipulación y análisis de datos |
| **Matplotlib + Seaborn** | Visualizaciones |
| **python-dotenv** | Manejo seguro de credenciales |

---

## 🔒 Seguridad

Las credenciales de base de datos **nunca están escritas en el código**. Se leen desde el archivo `.env` usando `os.environ.get()`, siguiendo las buenas prácticas de la industria. El archivo `.env` está excluido del control de versiones mediante `.gitignore`.

Todas las consultas SQL usan **parámetros (`%s`)** en lugar de concatenación de strings, lo que previene ataques de **SQL Injection**.

---

*Tecnicatura Universitaria en Programación · Análisis de Datos · 2026*
