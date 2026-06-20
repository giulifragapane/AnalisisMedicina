"""
╔══════════════════════════════════════════════════════════════════╗
║  PASO PREVIO — Importar el CSV limpio a MySQL                    ║
║  Ejecutar UNA SOLA VEZ antes de lanzar el dashboard.             ║
║                                                                  ║
║  EJECUCIÓN:                                                      ║
║    python importar_datos.py                                      ║
╚══════════════════════════════════════════════════════════════════╝
"""
 
import os
import pandas as pd
from sqlalchemy import create_engine, text  # type: ignore[import]
from dotenv import load_dotenv
 
# Las credenciales vienen del .env, nunca del código
load_dotenv()
 
DB_USER     = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST     = os.environ.get("DB_HOST")
DB_PORT     = os.environ.get("DB_PORT")
DB_NAME     = os.environ.get("DB_NAME")
 
# ── 1. Crear la base de datos si no existe
print("Conectando a MySQL...")
engine_root = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}")
 
with engine_root.connect() as conn:
    conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"))
    print(f"✅ Base de datos '{DB_NAME}' lista.")
 
# ── 2. Conectar a la base creada
engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
 
# ── 3. Leer y cargar el CSV
print("📂 Leyendo dataset_medicina_limpio.csv ...")
df = pd.read_csv("dataset_medicina_limpio.csv")
 
df.to_sql(name="estudiantes", con=engine, if_exists="replace", index=False)
 
print(f"✅ {len(df):,} registros cargados en la tabla 'estudiantes'.")
print("   Siguiente paso: streamlit run app_dashboard.py")