from flask import Blueprint, render_template, url_for, redirect, request, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from markupsafe import escape
from io import BytesIO
import os
from ..run import app

site = Blueprint('site', __name__, static_folder='static', template_folder='templates')

@site.route('/')
def index():
    return render_template('index.html')

@site.route('/flash/')
def flash():
    return render_template('site.flash.html')

@site.route('/testbed/')
def testbed():
    return render_template('testbed.html')

@site.route('/profile/')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name, lastname=current_user.lastname, email=current_user.email)

@site.route('/firmware/')
@login_required
def firmware():
    return render_template('firmware.html')

@site.route('/experiments/')
@login_required
def experiments():
    return render_template('experiments.html')

@site.route('/my_experiments/')
@login_required
def my_experiments():
    return render_template('my_experiments.html')

@site.route('/view_nodes/')
def view_nodes():
    from ..db.models import NodesData
    return render_template('view_nodes.html', values=NodesData.query.all())

@site.route('/view_experiments/')
def view_experiments():
    from ..db.models import ExperimentsData
    return render_template('view_experiments.html', values=ExperimentsData.query.all())

@site.route('/view_users/')
def view_users():
    from ..db.models import UsersData
    return render_template('view_users.html', values=UsersData.query.all())

@site.route('/view_firmwares/')
def view_firmwares():
    from ..db.models import FirmwaresData
    return render_template('view_firmwares.html', values=FirmwaresData.query.all())

@site.route('/download/<firmware>')
def download(firmware):
    from ..db.models import FirmwaresData
    print('::::::', firmware)
    firmware = FirmwaresData.query.filter_by(_name=firmware).first()

    if firmware:
        return send_file(BytesIO(firmware.bin_file), attachment_filename=firmware.filename, as_attachment=True), 200
    return {}, 404

from ..run import csrf
@site.route('/upload/<filename>', methods=['POST', 'PUT'])
@csrf.exempt
def upload(filename):
    
    filename = secure_filename(filename)
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    with open(path, 'ab') as f:
        chunk_size = 10
        chunk = request.stream.read(chunk_size)
        f.write(chunk)

    return {'filename': filename}




@site.route('/erase/', methods=['POST', 'GET'])
def erase():
    if(request.method == 'GET'):
        return render_template('erase.html')
        
    if(request.method == 'POST'):
        is_erase_sink = request.form.get('erase_sink_cb') == 'on'
        is_erase_nodes = request.form.get('erase_nodes_cb') == 'on'
        
        if(not is_erase_sink and not is_erase_nodes):
            return render_template('erase.html')

        return redirect(url_for('api.erase', is_erase_sink=is_erase_sink, is_erase_nodes=is_erase_nodes))


@site.route('/error/<string:err>')
def error(err):
    return render_template('error.html', error=err), 404

@site.errorhandler(404)
def not_found(error):
    return render_template('page_not_found.html'), 404

