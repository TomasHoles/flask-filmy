# Standard Library imports

# Core Flask imports
from flask import Blueprint, render_template

# Third-party imports

# App imports
from app import db_manager
from app import login_manager
from .views import (
    error_views,
    account_management_views,
    static_views,
)
from .models import User,Uzivatele, Film

bp = Blueprint('routes', __name__)

# alias
db = db_manager.session
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, BooleanField, SubmitField,DateField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length,InputRequired

class FormFormular(FlaskForm):
    name = StringField('Name', validators=[ InputRequired(message="You can't leave this empty")])
    surename = StringField('Surename', validators=[ InputRequired(message="You can't leave this empty")])

@bp.route("/formular", methods=["GET", "POST"])
def formular():
    form=FormFormular()
    if form.validate_on_submit():
        print(form.name.data)
        new_user = Uzivatele(name=form.name.data, surename=form.surename.data)
        db.add(new_user)
        db.commit()
        return "Formular submitted"
    return render_template("formular.html",form=form)
# Request management
class KnihaForm(FlaskForm):
    nazev = StringField('nazev', validators=[InputRequired(message="Title is required"), Length(max=255)])
    iban = StringField('iban', validators=[InputRequired(message="Author is required"), Length(max=255)])
    popisek = StringField('popisek', validators=[InputRequired(message="Published date is required")])


class EditaceFilmForm(FlaskForm):
     nazev = StringField('Nazev', validators=[InputRequired(message="Nazev is required"), Length(max=100)])
     rok = IntegerField('Rok', validators=[InputRequired(message="Rok is required")])
     reziser = StringField('Režisér', validators=[InputRequired(message="Režisér is required"), Length(max=100)])
     hodnoceni = IntegerField('Hodnocení')


@bp.route("/editace_film/<int:id>", methods=["GET", "POST"])
def editace_film(id):
    film_record = Film.query.get(id)
    if not film_record:
        return f"Film with id {id} not found", 404

    form = EditaceFilmForm(obj=film_record)
    if form.validate_on_submit():
        film_record.nazev = form.nazev.data
        film_record.rok = form.rok.data
        film_record.reziser = form.reziser.data
        film_record.hodnoceni = form.hodnoceni.data
        db.commit()
        return f"Film with id {id} has been updated"
    
    return render_template("film.html", form=form, film_record=film_record)


class AddFilmForm(FlaskForm):
    nazev = StringField('Nazev', validators=[InputRequired(message="Nazev is required"), Length(max=100)])
    rok = IntegerField('Rok', validators=[InputRequired(message="Rok is required")])
    reziser = StringField('Režisér', validators=[InputRequired(message="Režisér is required"), Length(max=100)])
    hodnoceni = IntegerField('Hodnocení')

@bp.route("/add_film", methods=["GET", "POST"])
def add_film():
    form = AddFilmForm()
    if form.validate_on_submit():
        new_film = Film(nazev=form.nazev.data, rok=form.rok.data, reziser=form.reziser.data, hodnoceni=form.hodnoceni.data)
        db.add(new_film)
        db.commit()
        return "Film submitted"
    return render_template("film.html", form=form)


@bp.before_app_request
def before_request():
    db()

@bp.teardown_app_request
def shutdown_session(response_or_exc):
    db.remove()

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    if user_id and user_id != "None":
        return User.query.filter_by(user_id=user_id).first()

# Error views
bp.register_error_handler(404, error_views.not_found_error)

bp.register_error_handler(500, error_views.internal_error)

# Public views
bp.add_url_rule("/", view_func=static_views.index)

bp.add_url_rule("/register", view_func=static_views.register)

bp.add_url_rule("/login", view_func=static_views.login)

# Login required views
bp.add_url_rule("/settings", view_func=static_views.settings)

# Public API
bp.add_url_rule(
   "/api/login", view_func=account_management_views.login_account, methods=["POST"]
)

bp.add_url_rule("/logout", view_func=account_management_views.logout_account)

bp.add_url_rule(
   "/api/register",
   view_func=account_management_views.register_account,
   methods=["POST"],
)

# Login Required API
bp.add_url_rule("/api/user", view_func=account_management_views.user)

bp.add_url_rule(
   "/api/email", view_func=account_management_views.email, methods=["POST"]
)

# Admin required
bp.add_url_rule("/admin", view_func=static_views.admin)