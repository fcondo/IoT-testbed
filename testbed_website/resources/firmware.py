
from ..utility.errors import error
from ..run import app
from ..db.models import db, FirmwaresData

from flask import jsonify, make_response
from flask_restful import Resource, reqparse, url_for, request, abort
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import json

ALLOWED_EXTENSIONS = ['hex']

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class FirmwaresChecker(Resource):

    def post(self):
        '''
           Returns firmware format. 
        '''
        
        # check if the post request has the file part
        if('file-submit' not in request.files):
            print('No file part')
            return {'error': error(50)}, 500

        file = request.files['file-submit']

        # if user does not select file, browser also
        # submit an empty part without filename
        if(file.filename == ''):
            print('No selected file')
            return {'error': error(51)}, 500

        if(file and allowed_file(file.filename)):
            filename = secure_filename(file.filename)
            # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return {'format': filename.rsplit('.', 1)[1]}, 200
        else:
            return {'error': error(52)}, 500
        
class FirmwaresName(Resource):
    
    def __init__(self):
        self.location = app.config['FIRMWARES'] 
        
    def get(self, name):
        '''
            Gets a stored firmware metadata.
        '''
        fileset = {}

        firmware = FirmwaresData.query.filter_by(_name=name).first()
        
        if firmware:
            name = firmware._name
            filename = firmware.filename
            user = firmware.user
            firm_type = firmware.type
            archi = firmware.archi
            description = firmware.description
            lastModified = firmware.lastModified.strftime('%H:%M:%S, %d/%m/%Y') if firmware.lastModified else ''
            
            fileset[name] = {
                'filename': filename,
                'user': user,
                'type': firm_type,
                'lastModified': lastModified,
                'description': description,
                'archi': archi
            }
            return {'firmwares': fileset}, 200

        return {'error': error(53, filename=name)}, 500

    def put(self, name):
        '''
           Replace a firmware in the firmwares directory. 
        '''
        
        # check if the post request has the file part
        if('file-submit' not in request.files):
            print('No file part')
            return {'error': error(50)}, 500

        file = request.files['file-submit']

        # if user does not select file, browser also
        # submit an empty part without filename
        if(file.filename == ''):
            print('No selected file')
            return {'error': error(51)}, 500

        if(file and allowed_file(file.filename)):
            filename = secure_filename(file.filename)
             
            identifier = request.form['identifier']
            description = request.form['description']
            archi = request.form['archi']

            file.stream.seek(0)
            firmware_data = FirmwaresData.query.filter_by(_name=name).first()

            firmware_data.identifier = identifier
            firmware_data.filename = filename
            firmware_data.archi = archi
            firmware_data.description = description
            firmware_data.lastModified = datetime.now()
            firmware_data.bin_file = file.read()

            db.session.commit()

            return {'success': {'type': 'success', 'message': ('File <b>' + filename + '</b> correctly overwritten.').format(filename)}}, 200
        else:
            return {'error': error(52)}, 500

    def delete(self, name):

        firmware = FirmwaresData.query.filter_by(_name=name)
        
        if(firmware):
            firmware.delete()
            db.session.commit()

            return {'success': {'type': 'success', 'message': ('File <b>' + filename + '</b> correctly deleted.').format(filename)}}, 200
        else:
            return {'error': error(54, filename=name)}, 500
  
class Firmwares(Resource):
    
    def __init__(self):
        self.location = app.config['FIRMWARES'] 

    def get(self):
        '''
            Gets a list of stored firmware metadatas (name, size in KB, last modified date).
            If no data available returns a warning.
        '''
        
        fileset = {}

        firmwares = FirmwaresData.query.all()

        for firmware in firmwares:
            name = firmware._name
            filename = firmware.filename
            archi = firmware.archi
            description = firmware.description
            lastModified = firmware.lastModified.strftime('%H:%M:%S, %d/%m/%Y')
            
            fileset[name] = {
                'filename': filename, 
                'lastModified': lastModified,
                'description': description,
                'archi': archi
            }
            
        if(fileset):
            return {'files': fileset}, 200
        else:
            return {'error': set_error_from_code(101)}, 500

        """ 
        fileset = {}
        with open(self.location + '/metadata.json', 'r+') as metadata:
            data = metadata.read()

            # parse file
            obj = json.loads(data)

            with os.scandir(self.location) as dir_entries:
                for entry in dir_entries:
                    info = entry.stat()
                    if 'metadata' in entry.name:
                        continue
                    archi = obj[entry.name]['archi']
                    description = obj[entry.name]['description']
                    lastModified = obj[entry.name]['lastModified']
                    
                    size_kbyte = float(obj[entry.name]['size'])/(10**3)
                
                    if(int(size_kbyte) > 10**3):
                        size = str(size_kbyte/(10**3)) + ' MB'
                    else:
                        size = str(size_kbyte) + ' KB'
                    fileset[entry.name] = {
                        'size': size, 
                        'lastModified': lastModified,
                        'description': description,
                        'archi': archi
                    }
                   
        if(fileset):
            return {'files': fileset}, 200

        return {'error': set_error_from_code(101, 'firmware')}, 500 """

    def post(self):
        '''
           Saves a firmware in the firmwares directory. 
        '''
        
        # check if the post request has the file part
        if('file-submit' not in request.files):
            print('No file part')
            return {'error': error(50)}, 500

        file = request.files['file-submit']

        # if user does not select file, browser also
        # submit an empty part without filename
        if(file.filename == ''):
            print('No selected file')
            return {'error': error(51)}, 500

        if(file and allowed_file(file.filename)):
            filename = secure_filename(file.filename)

            identifier = request.form['identifier']
            description = request.form['description']
            archi = request.form['archi']

            file.stream.seek(0)
            firmware_data = FirmwaresData(identifier, filename, archi, description, datetime.now(), file.read())
            
            db.session.add(firmware_data)
            db.session.commit()

            return {'success': {'type': 'success', 'message': ('File <b>' + filename + '</b> correctly submitted.').format(filename)}}, 200
        else:
            return {'error': error(52)}, 500