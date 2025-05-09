from enum import Enum
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from extensions import db
from datetime import datetime

class Perspective(db.Model):
    __tablename__ = 'perspectives'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.String(200))
    color_hex = db.Column(db.String(7), default='#3498db')
    orden = db.Column(db.Integer, default=0)
    icono = db.Column(db.String(30))
    
    indicators = db.relationship('Indicator', back_populates='perspective')

class ComparisonType(db.Model):
    __tablename__ = 'comparison_types'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    formula_evaluacion = db.Column(db.Text, nullable=False)

class Periodicity(db.Model):
    __tablename__ = 'periodicities'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(50), nullable=False)
    dias = db.Column(db.Integer, nullable=False)

class AggregationMethod(db.Model):
    __tablename__ = 'aggregation_methods'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.Text)

class OrganizationalStructure(db.Model):
    __tablename__ = 'organizational_structures'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(50), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('organizational_structures.id'))
    level_id = db.Column(db.Integer, db.ForeignKey('hierarchy_levels.id'), nullable=False)
    activo = db.Column(db.Boolean, default=True)
    
    level = db.relationship('HierarchyLevel')
    children = db.relationship('OrganizationalStructure')
    indicators = db.relationship('Indicator', back_populates='organizational_structure')

class HierarchyLevel(db.Model):
    __tablename__ = 'hierarchy_levels'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.Text)
    nivel = db.Column(db.Integer, nullable=False)

# Tabla de relación muchos-a-muchos
indicator_equipment = db.Table('indicator_equipment',
    db.Column('indicator_id', db.Integer, db.ForeignKey('indicators.id'), primary_key=True),
    db.Column('equipo_id', db.Integer, db.ForeignKey('equipos_fisicos.id'), primary_key=True),
    db.Column('fecha_asociacion', db.DateTime, default=datetime.utcnow)
)

class EquipoFisico(db.Model):
    __tablename__ = 'equipos_fisicos'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo_activo = db.Column(db.String(30), unique=True, nullable=False)
    nombre = db.Column(db.String(50), nullable=False)
    coordenadas = db.Column(db.String(50))  # Podrías usar PostGIS en producción
    estructura_id = db.Column(db.Integer, db.ForeignKey('organizational_structures.id'), nullable=False)
    fecha_adquisicion = db.Column(db.Date)
    estado = db.Column(db.String(20))
    ultimo_mantenimiento = db.Column(db.Date)
    
    indicadores = db.relationship('Indicator', 
                                secondary=indicator_equipment,
                                back_populates='equipos_fisicos')

class Indicator(db.Model):
    __tablename__ = 'indicators'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(30), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    
    # Relaciones con tablas de configuración
    perspective_id = db.Column(db.Integer, db.ForeignKey('perspectives.id'), nullable=False)
    perspective = db.relationship('Perspective', back_populates='indicators')
    
    comparison_type_id = db.Column(db.Integer, db.ForeignKey('comparison_types.id'), nullable=False)
    comparison_type = db.relationship('ComparisonType')
    
    periodicity_id = db.Column(db.Integer, db.ForeignKey('periodicities.id'), nullable=False)
    periodicity = db.relationship('Periodicity')
    
    aggregation_method_id = db.Column(db.Integer, db.ForeignKey('aggregation_methods.id'), nullable=False)
    aggregation_method = db.relationship('AggregationMethod')
    
    estructura_jerarquica_id = db.Column(db.Integer, db.ForeignKey('organizational_structures.id'))
    organizational_structure = db.relationship('OrganizationalStructure')
    
    # Campos de valores y mediciones
    unidad_medida = db.Column(db.String(20), nullable=False)
    valor_real = db.Column(db.Float)
    valor_planificado = db.Column(db.Float)
    referencias = db.Column(db.JSON)  # Almacena {ref1: x, ref2: y, ...}
    
    # Campos de evaluación
    ultima_evaluacion = db.Column(db.String(20))
    fecha_ultima_evaluacion = db.Column(db.DateTime)
    evaluacion_automatica = db.Column(db.Boolean, default=True)
    
    # Campos dimensionales
    tiempo_dimension = db.Column(db.JSON)  # Ej: {"año": 2023, "trimestre": "Q1"}
    ubicacion_geografica = db.Column(db.JSON)
    centro_costo = db.Column(db.String(50))
    
    # Relación jerárquica entre indicadores
    parent_id = db.Column(db.Integer, db.ForeignKey('indicators.id'))
    children = db.relationship('Indicator', back_populates='parent', remote_side=[id])
    parent = db.relationship('Indicator', back_populates='children', remote_side=[parent_id])
    
    # Relación muchos-a-muchos con equipos físicos
    equipos_fisicos = db.relationship('EquipoFisico', 
                                    secondary='indicator_equipment',
                                    back_populates='indicadores')
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    creado_por = db.Column(db.String(50))
    actualizado_por = db.Column(db.String(50))
    
    def __repr__(self):
        return f'<Indicator {self.codigo}: {self.nombre}>'
    
    def evaluar(self):
        """Evalúa el indicador según su tipo de comparación"""
        if not self.valor_real:
            return "SIN_VALOR"
            
        refs = self.referencias or {}
        
        try:
            if self.comparison_type.codigo == 'TYPE1':
                # Tipo 1: Mayor o igual Ref1 = Bien; >Ref2 = Regular; <=Ref2 = Mal
                if self.valor_real >= refs.get('ref1', 0):
                    return "BIEN"
                elif self.valor_real > refs.get('ref2', 0):
                    return "REGULAR"
                else:
                    return "MAL"
                    
            elif self.comparison_type.codigo == 'TYPE2':
                # Tipo 2: Menor o igual Ref1 = Bien; <Ref2 = Regular; >=Ref2 = Mal
                if self.valor_real <= refs.get('ref1', 0):
                    return "BIEN"
                elif self.valor_real < refs.get('ref2', 0):
                    return "REGULAR"
                else:
                    return "MAL"
                    
            elif self.comparison_type.codigo == 'TYPE3':
                # Tipo 3: Entre Ref2 y Ref1 = Bien; otros rangos específicos = Regular/Mal
                if not all(k in refs for k in ['ref1', 'ref2', 'ref3', 'ref4']):
                    return "REFERENCIAS_INCOMPLETAS"
                
                if refs['ref2'] <= self.valor_real <= refs['ref1']:
                    return "BIEN"
                elif (refs['ref1'] < self.valor_real < refs['ref3']) or (refs['ref2'] < self.valor_real < refs['ref4']):
                    return "REGULAR"
                elif refs['ref3'] <= self.valor_real <= refs['ref4']:
                    return "MAL"
                else:
                    return "FUERA_DE_RANGO"
                    
            elif self.comparison_type.codigo == 'TYPE4':
                # Tipo 4: Entre Ref3 y Ref4 = Bien; otros rangos específicos = Regular/Mal
                if not all(k in refs for k in ['ref1', 'ref2', 'ref3', 'ref4']):
                    return "REFERENCIAS_INCOMPLETAS"
                
                if refs['ref3'] <= self.valor_real <= refs['ref4']:
                    return "BIEN"
                elif (refs['ref1'] < self.valor_real < refs['ref3']) or (refs['ref2'] < self.valor_real < refs['ref4']):
                    return "REGULAR"
                elif refs['ref2'] <= self.valor_real <= refs['ref1']:
                    return "MAL"
                else:
                    return "FUERA_DE_RANGO"
                    
            else:
                return "TIPO_NO_VALIDO"
                
        except Exception as e:
            return f"ERROR_EVALUACION: {str(e)}"
    
    def actualizar_evaluacion(self):
        """Actualiza la evaluación y guarda en la base de datos"""
        if self.evaluacion_automatica:
            self.ultima_evaluacion = self.evaluar()
            self.fecha_ultima_evaluacion = datetime.utcnow()
            db.session.commit()
    
    @classmethod
    def crear_con_referencias(cls, **kwargs):
        """Crea un indicador con validación de referencias"""
        refs = kwargs.get('referencias', {})
        tipo = kwargs.get('comparison_type_id')
        
        if not tipo:
            raise ValueError("Se requiere un tipo de comparación")
        
        # Validar referencias según el tipo
        comparison_type = ComparisonType.query.get(tipo)
        if not comparison_type:
            raise ValueError("Tipo de comparación no válido")
        
        if comparison_type.codigo in ['TYPE1', 'TYPE2'] and not all(k in refs for k in ['ref1', 'ref2']):
            raise ValueError("Faltan referencias requeridas (ref1 y ref2)")
        
        if comparison_type.codigo in ['TYPE3', 'TYPE4'] and not all(k in refs for k in ['ref1', 'ref2', 'ref3', 'ref4']):
            raise ValueError("Faltan referencias requeridas (ref1, ref2, ref3 y ref4)")
        
        indicador = cls(**kwargs)
        db.session.add(indicador)
        db.session.commit()
        indicador.actualizar_evaluacion()
        
        return indicador