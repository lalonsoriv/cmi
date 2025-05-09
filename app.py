from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from forms import KPIForm
from models import db, Indicator, Perspective, AggregationMethod, ComparisonType, Periodicity, OrganizationalStructure
import os
from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres:8673.l@localhost:5432/modelo')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#db = SQLAlchemy(app)
db.init_app(app)

# Funciones auxiliares para obtener opciones de la BD
def get_perspective_choices():
    return [(p.id, p.name) for p in Perspective.query.order_by(Perspective.name).all()]

def get_aggregation_method_choices():
    return [(m.id, m.name) for m in AggregationMethod.query.order_by(AggregationMethod.name).all()]

def get_comparison_type_choices():
    return [(t.id, t.name) for t in ComparisonType.query.order_by(ComparisonType.name).all()]

def get_periodicity_choices():
    return [(p.id, p.name) for p in Periodicity.query.order_by(Periodicity.name).all()]

def get_organizational_structure_choices():
    return [(o.id, o.name) for o in OrganizationalStructure.query.order_by(OrganizationalStructure.name).all()]

def get_parent_kpi_choices():
    return [(k.id, k.name) for k in Indicator.query.order_by(Indicator.name).all()]

@app.route('/')
def index():
    return redirect(url_for('list_kpis'))

@app.route('/kpis')
def list_kpis():
    kpis = Indicator.query.all()
    return render_template('list_kpis.html', kpis=kpis)

@app.route('/kpi/create', methods=['GET', 'POST'])
def create_kpi():
    form = KPIForm()
    
    # Poblar todos los campos select
    form.perspective.choices = [('', '-- Seleccione Perspectiva --')] + get_perspective_choices()
    form.aggregation_method.choices = [('', '-- Seleccione Método --')] + get_aggregation_method_choices()
    form.comparison_type.choices = [('', '-- Seleccione Tipo --')] + get_comparison_type_choices()
    form.periodicity.choices = [('', '-- Seleccione Periodicidad --')] + get_periodicity_choices()
    form.organizational_structure_id.choices = [('', '-- Ninguna --')] + get_organizational_structure_choices()
    form.parent_id.choices = [('', '-- Ninguno --')] + get_parent_kpi_choices()

    if form.validate_on_submit():
        try:
            kpi = Indicator(
                name=form.name.data,
                description=form.description.data,
                perspective_id=form.perspective.data,
                aggregation_method_id=form.aggregation_method.data,
                comparison_type_id=form.comparison_type.data,
                periodicity_id=form.periodicity.data,
                organizational_structure_id=form.organizational_structure_id.data if form.organizational_structure_id.data else None,
                parent_id=form.parent_id.data if form.parent_id.data else None,
                target_value=float(form.target_value.data) if form.target_value.data else None,
                min_value=float(form.min_value.data) if form.min_value.data else None,
                max_value=float(form.max_value.data) if form.max_value.data else None
            )
            
            db.session.add(kpi)
            db.session.commit()
            flash('KPI creado exitosamente!', 'success')
            return redirect(url_for('list_kpis'))
            
        except ValueError as e:
            db.session.rollback()
            flash(f'Error en valores numéricos: {str(e)}', 'danger')
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Error de base de datos: {str(e)}', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Error inesperado: {str(e)}', 'danger')

    return render_template('create_kpi.html', form=form)

@app.route('/kpi/edit/<int:id>', methods=['GET', 'POST'])
def edit_kpi(id):
    kpi = Indicator.query.get_or_404(id)
    form = KPIForm(obj=kpi)
    
    # Poblar los mismos campos que en create
    form.perspective.choices = get_perspective_choices()
    form.aggregation_method.choices = get_aggregation_method_choices()
    form.comparison_type.choices = get_comparison_type_choices()
    form.periodicity.choices = get_periodicity_choices()
    form.organizational_structure_id.choices = [('', '-- Ninguna --')] + get_organizational_structure_choices()
    form.parent_id.choices = [('', '-- Ninguno --')] + get_parent_kpi_choices()

    if form.validate_on_submit():
        try:
            form.populate_obj(kpi)
            db.session.commit()
            flash('KPI actualizado exitosamente!', 'success')
            return redirect(url_for('list_kpis'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar KPI: {str(e)}', 'danger')

    return render_template('edit_kpi.html', form=form, kpi=kpi)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=os.getenv('FLASK_DEBUG', 'False') == 'True')