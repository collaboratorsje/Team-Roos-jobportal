from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap5
from GTAApplication import gta, db, login_manager  #, models, forms
from GTAApplication.forms import forms
from GTAApplication.models import models
from flask_login import login_required, login_user, logout_user
from werkzeug.security import generate_password_hash


@login_manager.user_loader
def load_user(user_id):
    return models.Users.get(user_id)

@gta.route('/')
@login_required
def Home():
    return render_template("index.html")

@gta.route('/login')
def LoginPage():
    form = forms.LoginForm()
    return render_template("login.html", form=form)

@gta.route('/register')
def RegisterPage():
    result = db.session.execute(db.select(models.Roles.role_id, models.Roles.role_name).where(models.Roles.role_id > 1).where(models.Roles.role_id < 5)).all()
    roles = [("", "---")]
    [roles.append((r[0], r[1])) for r in result]
    #roles = [(r[0], r[1]) for r in result]
    result = db.session.execute(db.select(models.Majors.major_id, models.Majors.major_name)).all()
    majors = [("", "---")]
    [majors.append((r[0], r[1])) for r in result]
    #majors = [(r[0], r[1]) for r in result]
    result = db.session.execute(db.select(models.Degrees.degree_id, models.Degrees.degree_name)).all()
    degrees = [("", "---")]
    [degrees.append((r[0], r[1])) for r in result]
    #degrees = [(r[0], r[1]) for r in result]
    form = forms.RegisterForm()
    form.user_role.choices = roles
    form.user_major.choices = majors
    form.user_degree.choices = degrees
    return render_template("register.html", form=form)

@gta.route('/jobs')
@login_required
def JobsPage():
    return render_template('jobs.html')

@gta.route('/applications')
@login_required
def ApplicationsPage():
    return render_template('applications.html')

@gta.route('/admin')
@login_required
def AdminPage():
    return render_template('admin.html')

@gta.route('/account')
def AccountPage():
    return render_template('account.html')

@gta.route('/auth', methods=["POST", "GET"])
def auth():
    form = forms.RegisterForm()
    if form.validate_on_submit():  # make sure to call the method with ()
        new_user = models.Users(
            user_fname=form.first_name.data,
            user_lname=form.last_name.data,
            user_email=form.email.data,
            role=form.user_role.data,
            major=form.user_major.data,
            degree=form.user_degree.data,
            user_pwd=generate_password_hash(form.password.data, method='sha256')
            # Add other fields as necessary
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Thanks for registering!')
        return redirect(url_for('login'))  # or wherever you want to redirect
    return render_template('register.html', form=form)
