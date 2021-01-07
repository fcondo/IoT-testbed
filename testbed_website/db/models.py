from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import func, exc
import datetime
from ..run import app

db = SQLAlchemy(app)

class UsersData(UserMixin, db.Model):
    
    id = db.Column('id', db.Integer, primary_key=True)
    email = db.Column('email', db.String(30), unique=True)
    password = db.Column('password', db.String(100), nullable=False)
    name = db.Column('name', db.String(30))
    lastname = db.Column('lastname', db.String(30), default='')
    is_admin = db.Column('is_admin', db.Boolean, default=False)

    def __init(self, email, password, name, is_admin=False):
        self.email = email
        self.password = password
        self.name = name
        self.is_admin = is_admin


class FirmwaresData(db.Model):
    
    # _id = db.Column('id', db.Integer, primary_key=True)
    _name = db.Column('name', db.String(30), primary_key=True)
    filename = db.Column('filename', db.String(30), nullable=False)
    firm_type = db.Column('type', db.String(15), nullable=False, default='userdefined')
    archi = db.Column('archi', db.String(30))
    description = db.Column('description', db.String(100))
    lastModified = db.Column('lastModified', db.DateTime, nullable=False)
    bin_file = db.Column('bin_file', db.LargeBinary, nullable=False)

    def __init__(self, identifier, filename, archi, description, lastModified, bin_file, firm_type=None):
        self._name = identifier
        self.filename = filename
        if(firm_type is not None):
            self.firm_type = 'predefined'
        self.archi = archi
        self.description = description
        self.lastModified = lastModified
        self.bin_file = bin_file


class NodesData(db.Model):

    _id = db.Column('id', db.Integer(), autoincrement=True, primary_key=True)
    hostname = db.Column('hostname', db.String(30))
    archi = db.Column('archi', db.String(30))
    network_address	=  db.Column('network_address', db.String(15), nullable=False, unique=True)
    site = db.Column('site', db.String(30), nullable=False)
    state = db.Column('state', db.String(10), nullable=False)
    fail_count = db.Column('fail_count', db.Integer(), nullable=False, default=0)
    mobile = db.Column('mobile', db.Boolean, nullable=False, default=False)
    
    def __init__(self, archi, network_address, site, state, mobile=False):
        # import random, string
        # _id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        # self._id = _id

        max_id = db.session.query(func.max(NodesData._id)).scalar()
        print(max_id, '???????')
        node_id =  (int(max_id) + 1) if max_id else 1
        self.hostname = "".join((archi + '-' + str(node_id) + '.' + site).split()) 
        self.archi = archi
        self.network_address = network_address
        self.site = site
        self.state = state
        self.mobile = mobile
        self.fail_count = 0


class ExperimentsData(db.Model):
    
    _id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column('name', db.String(30), nullable=False, unique=True)
    num_nodes = db.Column('num_nodes', db.Integer, nullable=False, default=0)
    state = db.Column('state', db.String(30), nullable=False)
    submitted_duration = db.Column('submitted_duration', db.Integer, nullable=False, default=0)
    scheduled_date = db.Column('scheduled_date', db.DateTime, nullable=False, default=0)
    started_date = db.Column('started_date', db.DateTime)
    expected_finish_date = db.Column('expected_finish_date', db.DateTime)
    finish_date = db.Column('finish_date', db.DateTime)
    stopped_date = db.Column('stopped_date', db.DateTime)
    user = db.Column('user', db.String(30), nullable=False)
    nodes_list = db.Column('nodes_list', db.PickleType, nullable=False)
    associations = db.Column('association', db.PickleType, nullable=False)

    # nodes = db.relationship("NodesData", backref="experimentsdata", lazy='select')
    
    def __init__(self, name, state, submitted_duration, scheduled_date, user, nodes_list, associations):
        
        self.name = name
        self.num_nodes = len(nodes_list)
        self.state = state
        self.submitted_duration = submitted_duration
        self.scheduled_date = scheduled_date
        self.nodes_list = nodes_list
        self.user = user
        self.associations = associations
        self.expected_finish_date = scheduled_date + datetime.timedelta(minutes=submitted_duration)


'''


id	integer
name	string
type*	string
default: physicalEnum:
Array [ 2 ]
user	string
pattern: ^[a-z][0-9a-z]{3,19}$
minLength: 4
maxLength: 20
nb_nodes	integer
state	stringEnum:
Array [ 7 ]
submitted_duration	integer
effective_duration	integer
scheduled_date	string($dateTime)
start_date	string($dateTime)
stop_date	string($dateTime)
submission_date	string($dateTime)
profiles	{...}
mobilities	{...}
nodes	NodesList[...]
duration	integer
reservation	integer
profileassociations	[...]
firmwareassociations	[...]


id	integer
name	string
user	string
pattern: ^[a-z][0-9a-z]{3,19}$
minLength: 4
maxLength: 20
nb_nodes	integer
state	stringEnum:
Array [ 7 ]
submitted_duration	integer
effective_duration	integer
scheduled_date	string($dateTime)
start_date	string($dateTime)
stop_date	string($dateTime)
submission_date	string($dateTime)


'''