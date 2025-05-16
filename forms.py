from flask_wtf import FlaskForm
from wtforms import validators
from wtforms import StringField, FloatField, SelectField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Optional
from models import ComparisonType, AggregationMethod, Periodicity, Perspective, OrganizationalStructure

class KPIForm(FlaskForm):
    nombre = StringField('Nombre del KPI', validators=[DataRequired()])
    
    perspective = SelectField('Perspectiva', coerce=lambda x: int(x) if x and x != '' else None,
                                             validators=[validators.InputRequired()],  
                                             
                            )
    periodicity = SelectField('Periodicidad', coerce=lambda x: int(x) if x and x != '' else None,
                                             validators=[validators.InputRequired()],  
                                             
                            )
    comparison_type = SelectField('Tipo de Comparación', coerce=lambda x: int(x) if x and x != '' else None,
                                             validators=[validators.InputRequired()],  
                                             
                            )
    aggregation_method = SelectField('Método de Agregación', coerce=lambda x: int(x) if x and x != '' else None,
                                             validators=[validators.InputRequired()],
                                             
                            )
    unidad_medida = StringField('Unidad de Medida', validators=[DataRequired()])
    valor_real = FloatField('Valor Actual', validators=[Optional()])
    organizational_structure_id = SelectField('Organizaciones', coerce=lambda x: int(x) if x and x != '' else None,
                                             validators=[validators.InputRequired()],  
                                             
                            )

    # Referencias (simplificado para el ejemplo)
    referencia1 = FloatField('Referencia 1', validators=[validators.Optional()])
    referencia2 = FloatField('Referencia 2', validators=[validators.Optional()])
    referencia3 = FloatField('Referencia 3', validators=[validators.Optional()])
    referencia4 = FloatField('Referencia 4', validators=[validators.Optional()])
    
    # Campos de dimensiones
    estructura_jerarquica_id = SelectField('Estructura Jerárquica', coerce=lambda x: int(x) if x and x != 'None' else None,
        validators=[validators.Optional()])
    centro_costo = StringField('Centro de Costo', validators=[Optional()])
    parent_id = SelectField('Indicador Padre', coerce=lambda x: int(x) if x and x != 'None' else None,
        validators=[validators.Optional()])
    
    # Para campos JSON (simplificado)
    tiempo_dimension = TextAreaField('Dimensión Tiempo (JSON)', validators=[Optional()])
    ubicacion_geografica = TextAreaField('Ubicación Geográfica (JSON)', validators=[Optional()])

    def __init__(self, *args, **kwargs):
        super(KPIForm, self).__init__(*args, **kwargs)
        # Cargar opciones desde la base de datos
        self.perspective.choices = [(p.id, p.nombre) for p in Perspective.query.order_by(Perspective.nombre).all()]
        self.comparison_type.choices = [(c.id, c.nombre) for c in ComparisonType.query.order_by(ComparisonType.nombre).all()]
        self.periodicity.choices = [(p.id, p.nombre) for p in Periodicity.query.order_by(Periodicity.nombre).all()]
        self.aggregation_method.choices = [(a.id, a.nombre) for a in AggregationMethod.query.order_by(AggregationMethod.nombre).all()]
        self.organizational_structure_id.choices = [(org.id, org.nombre) for org in OrganizationalStructure.query.order_by(OrganizationalStructure.nombre).all()]