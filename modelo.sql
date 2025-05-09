-- Tabla para tipos de comparación
CREATE TABLE comparison_types (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL, 
    nombre VARCHAR(50) NOT NULL,
    descripcion TEXT NOT NULL,
    formula_evaluacion TEXT NOT NULL
);

-- Tabla para métodos de agregación
CREATE TABLE aggregation_methods (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    descripcion TEXT
);

-- Tabla para periodicidades
CREATE TABLE periodicities (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    dias INTEGER NOT NULL -- Número de días que representa esta periodicidad
);

-- Tabla para niveles organizacionales
CREATE TABLE hierarchy_levels (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL, 
    nombre VARCHAR(50) NOT NULL,
    descripcion TEXT,
    nivel INTEGER NOT NULL -- Orden jerárquico (1 = más alto)
);

-- Tabla de estructuras organizacionales (modificada)
CREATE TABLE organizational_structures (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    parent_id INTEGER REFERENCES organizational_structures(id),
    level_id INTEGER NOT NULL REFERENCES hierarchy_levels(id),
    activo BOOLEAN DEFAULT TRUE
);

-- Tabla de perspectivas (mejorada)
CREATE TABLE perspectives (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    descripcion VARCHAR(200),
    color_hex VARCHAR(7) DEFAULT '#3498db',
    orden INTEGER NOT NULL DEFAULT 0,
    icono VARCHAR(30)
);

-- Tabla de equipos físicos (mejorada)
CREATE TABLE equipos_fisicos (
    id SERIAL PRIMARY KEY,
    codigo_activo VARCHAR(30) UNIQUE NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    coordenadas GEOGRAPHY(POINT, 4326),
    estructura_id INTEGER NOT NULL REFERENCES organizational_structures(id),
    fecha_adquisicion DATE,
    estado VARCHAR(20) CHECK (estado IN ('OPERATIVO', 'MANTENIMIENTO', 'BAJA')),
    ultimo_mantenimiento DATE
);

-- Tabla principal de indicadores (modificada)
CREATE TABLE indicators (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(30) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    perspective_id INTEGER NOT NULL REFERENCES perspectives(id),
    unidad_medida VARCHAR(20) NOT NULL,
    periodicity_id INTEGER NOT NULL REFERENCES periodicities(id),
    valor_real FLOAT,
    valor_planificado FLOAT,
    referencias JSONB NOT NULL CHECK (jsonb_typeof(referencias) = 'object'),
    comparison_type_id INTEGER NOT NULL REFERENCES comparison_types(id),
    aggregation_method_id INTEGER NOT NULL REFERENCES aggregation_methods(id),
    tiempo_dimension JSONB,
    ubicacion_geografica JSONB,
    estructura_jerarquica_id INTEGER REFERENCES organizational_structures(id),
    centro_costo VARCHAR(50),
    parent_id INTEGER REFERENCES indicators(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    creado_por VARCHAR(50),
    actualizado_por VARCHAR(50),
    
    CONSTRAINT valid_references CHECK (
        (SELECT codigo FROM comparison_types WHERE id = comparison_type_id) IN ('TYPE1','TYPE2') AND referencias ?& array['ref1','ref2']
        OR 
        (SELECT codigo FROM comparison_types WHERE id = comparison_type_id) IN ('TYPE3','TYPE4') AND referencias ?& array['ref1','ref2','ref3','ref4']
    )
);

-- Tabla de relación entre indicadores y equipos físicos
CREATE TABLE indicator_equipment (
    indicator_id INTEGER NOT NULL REFERENCES indicators(id),
    equipo_id INTEGER NOT NULL REFERENCES equipos_fisicos(id),
    fecha_asociacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (indicator_id, equipo_id)
);

-- Tabla para historial de cambios en indicadores
CREATE TABLE indicator_history (
    id SERIAL PRIMARY KEY,
    indicator_id INTEGER NOT NULL REFERENCES indicators(id),
    campo_modificado VARCHAR(50) NOT NULL,
    valor_anterior TEXT,
    valor_nuevo TEXT,
    fecha_cambio TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    usuario VARCHAR(50) NOT NULL
);

-- Insertar datos iniciales para tipos de comparación
INSERT INTO comparison_types (codigo, nombre, descripcion, formula_evaluacion) VALUES
('TYPE1', 'Tipo 1: Mayor o igual Ref1', 'Bien si ≥ Ref1, Regular si > Ref2, Mal si ≤ Ref2', 'IF valor >= ref1 THEN "BIEN" ELSIF valor > ref2 THEN "REGULAR" ELSE "MAL" END'),
('TYPE2', 'Tipo 2: Menor o igual Ref1', 'Bien si ≤ Ref1, Regular si < Ref2, Mal si ≥ Ref2', 'IF valor <= ref1 THEN "BIEN" ELSIF valor < ref2 THEN "REGULAR" ELSE "MAL" END'),
('TYPE3', 'Tipo 3: Entre Ref2 y Ref1', 'Bien si entre Ref2-Ref1, Regular si entre Ref1-Ref3 o Ref2-Ref4, Mal si entre Ref3-Ref4', 'Complex evaluation'),
('TYPE4', 'Tipo 4: Entre Ref3 y Ref4', 'Bien si entre Ref3-Ref4, Regular si entre Ref1-Ref3 o Ref2-Ref4, Mal si entre Ref2-Ref1', 'Complex evaluation');

-- Insertar métodos de agregación
INSERT INTO aggregation_methods (codigo, nombre, descripcion) VALUES
('SUM', 'Suma', 'Agregación por suma de valores'),
('AVG', 'Promedio', 'Agregación por promedio aritmético'),
('WAVG', 'Ponderación', 'Agregación por promedio ponderado');

-- Insertar periodicidades
INSERT INTO periodicities (codigo, nombre, dias) VALUES
('DAILY', 'Diario', 1),
('WEEKLY', 'Semanal', 7),
('MONTHLY', 'Mensual', 30),
('QUARTERLY', 'Trimestral', 90),
('YEARLY', 'Anual', 365);

-- Insertar niveles jerárquicos
INSERT INTO hierarchy_levels (codigo, nombre, descripcion, nivel) VALUES
('OACE', 'OACE', 'Organismo de la Administración Central del Estado', 1),
('OSDE', 'OSDE', 'Organización Superior de Dirección Empresarial', 2),
('EMPRESA', 'Empresa', 'Unidad empresarial base', 3),
('UEB', 'UEB', 'Unidad Empresarial de Base', 4),
('DEPTO', 'Departamento', 'Unidad departamental', 5);

-- Insertar perspectivas básicas
INSERT INTO perspectives (codigo, nombre, descripcion, color_hex, orden, icono) VALUES
('FIN', 'Financiera', 'Indicadores financieros y económicos', '#2ecc71', 1, 'dollar-sign'),
('CLI', 'Cliente', 'Indicadores relacionados con clientes', '#3498db', 2, 'users'),
('PROC', 'Procesos', 'Indicadores de procesos internos', '#9b59b6', 3, 'cogs'),
('APR', 'Aprendizaje', 'Indicadores de aprendizaje y crecimiento', '#e74c3c', 4, 'graduation-cap');

-- Función para evaluar indicadores (actualizada)
CREATE OR REPLACE FUNCTION evaluar_indicador_completo(indicator_id INT) 
RETURNS VARCHAR AS $$
DECLARE
    ind RECORD;
    ref1 FLOAT;
    ref2 FLOAT;
    ref3 FLOAT;
    ref4 FLOAT;
    valor FLOAT;
    tipo_eval VARCHAR(10);
    resultado VARCHAR(20);
BEGIN
    -- Obtener el indicador y sus referencias
    SELECT 
        i.valor_real,
        (i.referencias->>'ref1')::FLOAT as ref1,
        (i.referencias->>'ref2')::FLOAT as ref2,
        (i.referencias->>'ref3')::FLOAT as ref3,
        (i.referencias->>'ref4')::FLOAT as ref4,
        ct.codigo as tipo_codigo
    INTO ind
    FROM indicators i
    JOIN comparison_types ct ON i.comparison_type_id = ct.id
    WHERE i.id = indicator_id;
    
    -- Asignar a variables para mejor legibilidad
    valor := ind.valor_real;
    ref1 := ind.ref1;
    ref2 := ind.ref2;
    ref3 := CASE WHEN ind.ref3 IS NOT NULL THEN ind.ref3 ELSE NULL END;
    ref4 := CASE WHEN ind.ref4 IS NOT NULL THEN ind.ref4 ELSE NULL END;
    tipo_eval := ind.tipo_codigo;
    
    -- Evaluar según el tipo de comparación
    CASE tipo_eval
        WHEN 'TYPE1' THEN
            -- Tipo 1: Mayor o igual Ref1 = Bien; >Ref2 = Regular; <=Ref2 = Mal
            IF valor >= ref1 THEN 
                resultado := 'BIEN';
            ELSIF valor > ref2 THEN 
                resultado := 'REGULAR';
            ELSE 
                resultado := 'MAL';
            END IF;
        
        WHEN 'TYPE2' THEN
            -- Tipo 2: Menor o igual Ref1 = Bien; <Ref2 = Regular; >=Ref2 = Mal
            IF valor <= ref1 THEN 
                resultado := 'BIEN';
            ELSIF valor < ref2 THEN 
                resultado := 'REGULAR';
            ELSE 
                resultado := 'MAL';
            END IF;
        
        WHEN 'TYPE3' THEN
            -- Tipo 3: 
            -- Bien si: entre Ref2 y Ref1 (Ref2 <= valor <= Ref1)
            -- Regular si: >Ref1 y <Ref3 O >Ref2 y <Ref4
            -- Mal si: >=Ref3 y <=Ref4
            IF ref3 IS NULL OR ref4 IS NULL THEN
                resultado := 'REFERENCIAS_INCOMPLETAS';
            ELSIF valor BETWEEN ref2 AND ref1 THEN
                resultado := 'BIEN';
            ELSIF (valor > ref1 AND valor < ref3) OR (valor > ref2 AND valor < ref4) THEN
                resultado := 'REGULAR';
            ELSIF valor BETWEEN ref3 AND ref4 THEN
                resultado := 'MAL';
            ELSE
                resultado := 'FUERA_DE_RANGO';
            END IF;
        
        WHEN 'TYPE4' THEN
            -- Tipo 4:
            -- Bien si: entre Ref3 y Ref4 (Ref3 <= valor <= Ref4)
            -- Regular si: >Ref1 y <Ref3 O >Ref2 y <Ref4
            -- Mal si: entre Ref2 y Ref1 (Ref2 <= valor <= Ref1)
            IF ref3 IS NULL OR ref4 IS NULL THEN
                resultado := 'REFERENCIAS_INCOMPLETAS';
            ELSIF valor BETWEEN ref3 AND ref4 THEN
                resultado := 'BIEN';
            ELSIF (valor > ref1 AND valor < ref3) OR (valor > ref2 AND valor < ref4) THEN
                resultado := 'REGULAR';
            ELSIF valor BETWEEN ref2 AND ref1 THEN
                resultado := 'MAL';
            ELSE
                resultado := 'FUERA_DE_RANGO';
            END IF;
        
        ELSE
            resultado := 'TIPO_NO_VALIDO';
    END CASE;
    
    -- Registrar la evaluación
    UPDATE indicators 
    SET ultima_evaluacion = resultado,
        fecha_ultima_evaluacion = CURRENT_TIMESTAMP
    WHERE id = indicator_id;
    
    RETURN resultado;
END;
$$ LANGUAGE plpgsql;