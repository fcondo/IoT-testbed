from flask import Blueprint, render_template, url_for, redirect, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from ..db.models import db, UsersData
from ..utility.errors import error
import re

auth = Blueprint('auth', __name__, static_folder='static', template_folder='templates')


@auth.route('/login/')
def login():
    return render_template('login.html')
    
@auth.route('/login/', methods=['POST'])
def login_post():

    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    if password is None or password == '':
        return {'error': error(3)}, 400
    
    if email is None or email == '':
        return {'error': error(4)}, 400
    
    user = UsersData.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return {'error': error(7)}, 400

    # creates cookie, session and tells the app the user is logged in
    login_user(user)

    return {}, 200

@auth.route('/logout/')
@login_required
def logout():
    logout_user()
    return render_template('login.html')

@auth.route('/signup/')
def signup():
    return render_template('login.html')

@auth.route('/signup/', methods=['POST'])
def signup_post():

    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    password2 = request.form.get('password2')
        
    
    if(not bool(re.match('^[a-zA-Z]*$', name))):
        return {'error': error(8)}, 400
    if(not bool(re.match('^[a-zA-Z0-9@.]*$', email))):
        return {'error': error(10)}, 400

    if name is None or name == '':
        return {'error': error(5)}, 400
    else:
        if len(name) < 2:
            return {'error': error(101)}, 400

    if password is None or password2 is None or password == '' or password2 == '':
        return {'error': error(3)}, 400
    if password != password2:
        return {'error': error(2)}, 400
    else:
        if(len(password) < 5):
            return {'error': error(102)}, 400
    if email is None or email == '':
        return {'error': error(4)}, 400
    elif not '@' in email or not '.' in email or len(email) < 5:
        return {'error': error(6)}, 400

    
    user = UsersData.query.filter_by(email=email).first()
    if user:
        return {'error': error(1)}, 400
    
    new_user = UsersData(email=email, password=generate_password_hash(password, method='sha256'), name=name)
    
    db.session.add(new_user)
    db.session.commit()

    # # creates cookie, session and tells the app the user is logged in
    # login_user(user)
    
    return {}, 200

@login_required
@auth.route('/user_update/', methods=['PUT'])
def user_update():

    email = request.form.get('email')
    name = request.form.get('firstname')
    lastname = request.form.get('lastname')

    if(not bool(re.match('^[a-zA-Z]*$', str(name)))):
        return {'error': error(8)}, 400
    if(not bool(re.match('^[a-zA-Z]*$', str(lastname)))):
        return {'error': error(9)}, 400
    if(not bool(re.match('^[a-zA-Z0-9@.]*$', str(email)))):
        return {'error': error(10)}, 400

    user = UsersData.query.filter_by(email=current_user.email).first()
    
    if user:
        
        if(name is not None and name != ''):
            if len(name) < 2:
                return {'error': error(101)}, 400
            user.name = name

        if(email is not None and email != ''):
            if not '@' in email or not '.' in email or len(email) < 5:
                return {'error': error(6)}, 400
            user.email = email
        
        if(lastname is not None and lastname != ''):
            if len(name) < 2:
                return {'error': error(103)}, 400
            user.lastname = lastname

        db.session.commit()
    
        return {'success': {'type': 'success', 'message': 'Profile correctly updated.'}}, 200
    
    return {'error': error(20)}, 400