-- ════════════════════════════════════════════════════════════════
-- TPI: Análisis de Rendimiento Académico en Medicina
-- Grupo 51: García, Fragapane
-- Esquema de base de datos para MySQL (XAMPP)
--
-- INSTRUCCIONES:
--   1. Abrir phpMyAdmin → pestaña "SQL"
--   2. Pegar y ejecutar este archivo completo
--   3. Luego ejecutar: python importar_datos.py
--      (cargará los 5000 registros del CSV a la tabla)
-- ════════════════════════════════════════════════════════════════
 
 
-- ── 1. BASE DE DATOS ─────────────────────────────────────────────
DROP DATABASE IF EXISTS medicina_db;
CREATE DATABASE medicina_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
 
USE medicina_db;
 
 
-- ── 2. TABLA PRINCIPAL ───────────────────────────────────────────
-- Contiene los datos limpios del Hito 2 + las columnas de
-- Feature Engineering (Nivel_Asistencia, Regular,
-- Indice_Compromiso, Categoria_Riesgo).
-- La carga completa (5000 registros) se realiza desde Python
-- con importar_datos.py usando df.to_sql().
 
DROP TABLE IF EXISTS estudiantes;
CREATE TABLE estudiantes (
    -- Identificación
    Id                          INT             NOT NULL AUTO_INCREMENT,
    Nombre                      VARCHAR(100)    NOT NULL,
    Género                      VARCHAR(20)     NOT NULL,
    Edad                        TINYINT         NOT NULL,
 
    -- Métricas académicas (Hito 1 — variables originales del dataset)
    Promedio_Notas              DECIMAL(4, 2)   NOT NULL COMMENT 'Escala 0 a 10',
    Asistencia_Clases_pct       DECIMAL(5, 2)   NOT NULL COMMENT 'Porcentaje 0-100',
    TP_Entregados_pct           DECIMAL(5, 2)   NOT NULL COMMENT 'Porcentaje 0-100',
    Materias_Aprobadas_Promedio TINYINT         NOT NULL,
    Demora_Traslado_min         SMALLINT        NOT NULL COMMENT 'Minutos de traslado al instituto',
 
    -- Variables categóricas originales
    Trabaja                     ENUM('Sí', 'No') NOT NULL,
    Tipo_Educacion              ENUM('Pública', 'Privada') NOT NULL,
    Año_Cursado                 TINYINT         NOT NULL COMMENT 'Año de carrera: 1 a 6',
 
    -- Feature Engineering (Hito 2 — columnas creadas por el grupo)
    Nivel_Asistencia            ENUM('Alta', 'Baja') NOT NULL
                                COMMENT 'Alta: asistencia >= 75%. Baja: < 75%',
    Regular                     ENUM('Sí', 'No') NOT NULL
                                COMMENT 'Sí: aprobó condición de regularidad',
    Indice_Compromiso           DECIMAL(4, 2)   NOT NULL
                                COMMENT 'Índice sintético: promedio de notas y TPs normalizados',
    Categoria_Riesgo            ENUM('Sin riesgo', 'Riesgo moderado', 'Alto riesgo') NOT NULL
                                COMMENT 'Clasificación de riesgo académico del Hito 2',
 
    PRIMARY KEY (Id)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Dataset de medicina limpio — TPI Grupo 51';
 
 
-- ── 3. ÍNDICES ───────────────────────────────────────────────────
-- Optimizan las consultas filtradas del dashboard (WHERE ... IN ...)
CREATE INDEX idx_año        ON estudiantes (Año_Cursado);
CREATE INDEX idx_trabaja    ON estudiantes (Trabaja);
CREATE INDEX idx_tipo       ON estudiantes (Tipo_Educacion);
CREATE INDEX idx_riesgo     ON estudiantes (Categoria_Riesgo);
CREATE INDEX idx_regular    ON estudiantes (Regular);
 
 
-- ── 4. DATOS DE MUESTRA (10 registros de verificación) ──────────
-- Sirven para confirmar que la tabla funciona correctamente
-- antes de ejecutar la carga masiva con importar_datos.py.
-- La carga completa de los 5000 registros la hace Python.
 
INSERT INTO estudiantes (
    Id, Nombre, Género, Edad,
    Promedio_Notas, Asistencia_Clases_pct, TP_Entregados_pct,
    Trabaja, Tipo_Educacion, Año_Cursado,
    Materias_Aprobadas_Promedio, Demora_Traslado_min,
    Nivel_Asistencia, Regular, Indice_Compromiso, Categoria_Riesgo
) VALUES
(1,  'Alejandro Cabrera',   'Masculino', 24, 5.14,  87.2,  94.7, 'No', 'Privada', 1, 5, 110, 'Alta', 'Sí', 9.10, 'Sin riesgo'),
(2,  'Elena Ramírez',       'Femenino',  21, 7.49,  90.3,  50.5, 'Sí', 'Pública', 6, 3,  26, 'Alta', 'No', 7.04, 'Sin riesgo'),
(3,  'Valentín Rodríguez',  'Masculino', 30, 5.23,  63.6,  90.1, 'Sí', 'Pública', 1, 1, 116, 'Baja', 'No', 7.68, 'Alto riesgo'),
(4,  'Rafael Morales',      'Masculino', 28, 7.12,  73.6,  49.0, 'No', 'Pública', 6, 1, 103, 'Baja', 'No', 6.13, 'Sin riesgo'),
(5,  'Alejandro López',     'Masculino', 25, 4.44,  85.1,  79.5, 'No', 'Pública', 5, 6, 107, 'Alta', 'Sí', 8.23, 'Sin riesgo'),
(6,  'Hernán Romero',       'Masculino', 30, 7.63,  72.0,  49.0, 'No', 'Pública', 5, 3,  87, 'Baja', 'No', 6.05, 'Sin riesgo'),
(7,  'Pablo Sánchez',       'Masculino', 22, 7.10,  55.6,  95.4, 'No', 'Privada', 1, 0, 115, 'Baja', 'No', 7.55, 'Sin riesgo'),
(8,  'Elena Muñoz',         'Femenino',  24, 8.44,  85.3,  73.9, 'No', 'Privada', 3, 6,  16, 'Alta', 'Sí', 7.96, 'Sin riesgo'),
(9,  'Aldana Ramos',        'Femenino',  27, 7.78,  95.6,  59.8, 'Sí', 'Privada', 2, 3, 102, 'Alta', 'No', 7.77, 'Sin riesgo'),
(10, 'Víctor Jiménez',      'Masculino', 20, 7.30,  82.6,  48.4, 'No', 'Privada', 5, 5,  66, 'Alta', 'No', 6.55, 'Sin riesgo');
 
 
-- ── 5. VISTAS ANALÍTICAS ─────────────────────────────────────────
-- Consultas predefinidas que el dashboard puede usar directamente.
 
-- Vista 1: Resumen por año y situación laboral (Pregunta 1)
CREATE OR REPLACE VIEW v_promedio_por_año_trabajo AS
    SELECT
        Año_Cursado,
        Trabaja,
        ROUND(AVG(Promedio_Notas), 2)        AS Promedio_Notas,
        ROUND(AVG(Asistencia_Clases_pct), 2) AS Asistencia_Media,
        COUNT(Id)                             AS Cantidad_Estudiantes
    FROM estudiantes
    GROUP BY Año_Cursado, Trabaja
    ORDER BY Año_Cursado, Trabaja;
 
-- Vista 2: Distribución de riesgo por tipo de educación (Pregunta 2)
CREATE OR REPLACE VIEW v_riesgo_por_educacion AS
    SELECT
        Tipo_Educacion,
        Categoria_Riesgo,
        COUNT(Id)                             AS Cantidad,
        ROUND(COUNT(Id) * 100.0 /
            SUM(COUNT(Id)) OVER (PARTITION BY Tipo_Educacion), 1)
                                              AS Porcentaje
    FROM estudiantes
    GROUP BY Tipo_Educacion, Categoria_Riesgo
    ORDER BY Tipo_Educacion, Categoria_Riesgo;
 
-- Vista 3: Perfil del estudiante en alto riesgo (Pregunta 3)
CREATE OR REPLACE VIEW v_perfil_riesgo AS
    SELECT
        Categoria_Riesgo,
        COUNT(Id)                                    AS Cantidad,
        ROUND(AVG(Promedio_Notas), 2)               AS Promedio_Notas,
        ROUND(AVG(Asistencia_Clases_pct), 2)        AS Asistencia_Media,
        ROUND(AVG(TP_Entregados_pct), 2)            AS TPs_Promedio,
        ROUND(AVG(Demora_Traslado_min), 1)          AS Demora_Traslado_Media,
        ROUND(AVG(Indice_Compromiso), 2)            AS Indice_Compromiso_Medio
    FROM estudiantes
    GROUP BY Categoria_Riesgo
    ORDER BY FIELD(Categoria_Riesgo, 'Sin riesgo', 'Riesgo moderado', 'Alto riesgo');
 
 
-- ── 6. VERIFICACIÓN RÁPIDA ───────────────────────────────────────
-- Ejecutar estas líneas para confirmar que todo quedó bien.
 
SELECT 'Registros en tabla estudiantes:'   AS Info, COUNT(*) AS Valor FROM estudiantes
UNION ALL
SELECT 'Registros en Alto riesgo:',         COUNT(*) FROM estudiantes WHERE Categoria_Riesgo = 'Alto riesgo'
UNION ALL
SELECT 'Registros en Riesgo moderado:',     COUNT(*) FROM estudiantes WHERE Categoria_Riesgo = 'Riesgo moderado'
UNION ALL
SELECT 'Registros Sin riesgo:',             COUNT(*) FROM estudiantes WHERE Categoria_Riesgo = 'Sin riesgo';
 