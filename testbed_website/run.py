import atexit
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from markupsafe import escape
from kombu import Exchange, Queue
from kombu.common import Broadcast
from .utility.flask_celery import make_celery
from flask_restful import Api
from flask_login import LoginManager

# from flask_restplus import Api

import os

SECRET_KEY = os.urandom(32)
IP_ADDR = '192.168.1.118'
UPLOAD_FOLDER = 'firmwares'


app = Flask(__name__)

app.config['SECRET_KEY'] = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/database.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from .db.models import db
db.create_all()
db.init_app(app)

# app.config['SESSION_COOKIE_SECURE'] = False

csrf = CSRFProtect(app)

# add broadcast queue
broadcast_exchange = Exchange(
    'broadcast_exchange', type='fanout', routing_key='broadcast_routing')
recv_broadcast_exchange = Exchange('myres', type='fanout')
queue_recv_broadcast = Queue(
    name="response-queue", exchange=recv_broadcast_exchange, routing_key="kombu_routing")

# integration with Celery
app.config.update(
    CELERY_INCLUDE=['RPi_WebClient.tasks'],
    CELERY_TIMEZONE='Europe/Rome',
    CELERY_ENABLE_UTC=True,
    CELERY_BROKER_URL='amqp://ubuntu:raspberry@' + IP_ADDR + '/rpi_vhost',
    # CELERY_RESULT_BACKEND = 'rpc://',
    CELERY_QUEUES=(queue_recv_broadcast,
                   Broadcast(name='broadcast_tasks', exchange=broadcast_exchange),),
    # CELERY_ROUTES = {
    #     'RPi_WebClient.tasks.erase_task': {
    #         'queue': 'broadcast_tasks',
    #         'exchange': 'broadcast_exchange'
    #     },
    #     'tasks.erase_task': {
    #         'queue': 'broadcast_tasks',
    #         'exchange': 'broadcast_exchange'
    #     },
    #     'erase_task': {
    #         'queue': 'broadcast_tasks',
    #         'exchange': 'broadcast_exchange'
    #     }
    # }
    NODES='./config',
    FIRMWARES='./firmwares',
    UPLOAD_FOLDER='./logs',
    PERCENT_ALIVE_NODE_TO_START_EXPERIMENT=30,
    PERCENT_FLASHED_NODE_TO_START_EXPERIMENT=30,
)

celery = make_celery(app)

# purge old tasks left in the queues
celery.control.purge()

# initialize periodic jobs
from .scheduler.apscheduler import scheduler
atexit.register(lambda: scheduler.shutdown())

from .api.routes import api
from .site.routes import site
from .auth.routes import auth

# register routes Blueprint
app.register_blueprint(site)
app.register_blueprint(auth)
app.register_blueprint(api)


# authentication
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

# to connect cookie to DB user's data
@login_manager.user_loader 
def load_user(user_id):
    from .db.models import UsersData
    return UsersData.query.get(int(user_id))

# register API
api = Api(app)

# from .tasks import add, flash_task, erase_task
from .resources.experiments import Experiments, ExperimentsTotal, ExperimentsRunning, ExperimentsIDNodesFlash
from .resources.experiments import ExperimentsID, ExperimentsIDNodes, ExperimentsIDNodesIDs, ExperimentsIDReload
from .resources.nodes import Nodes, NodesIDs, Node
from .resources.firmware import Firmwares, FirmwaresName, FirmwaresChecker

API_PATH = 'api/'
API_VERSION = 'v1.0/'

# firmwares
api.add_resource(FirmwaresChecker,
                 ('/{0}{1}firmwares/checker').format(API_PATH, API_VERSION))
api.add_resource(Firmwares, '/{0}{1}firmwares/'.format(API_PATH, API_VERSION))
api.add_resource(
    FirmwaresName, '/{0}{1}firmwares/<string:name>'.format(API_PATH, API_VERSION))

# nodes
api.add_resource(Node, '/{0}{1}node/<int:id>'.format(API_PATH, API_VERSION))
api.add_resource(Nodes, '/{0}{1}nodes/'.format(API_PATH, API_VERSION))
api.add_resource(NodesIDs, '/{0}{1}nodes/ids'.format(API_PATH, API_VERSION))

# experiment
api.add_resource(
    Experiments, '/{0}{1}experiment/'.format(API_PATH, API_VERSION))
api.add_resource(ExperimentsTotal,
                 '/{0}{1}experiments/total/'.format(API_PATH, API_VERSION))
api.add_resource(ExperimentsRunning,
                 '/{0}{1}experiments/running/'.format(API_PATH, API_VERSION))
api.add_resource(ExperimentsID,
                 '/{0}{1}experiment/<int:id>/'.format(API_PATH, API_VERSION))
api.add_resource(ExperimentsIDNodes,
                 '/{0}{1}experiment/<int:id>/nodes'.format(API_PATH, API_VERSION))
api.add_resource(ExperimentsIDNodesIDs,
                 '/{0}{1}experiment/<int:id>/nodes_ids'.format(API_PATH, API_VERSION))
api.add_resource(ExperimentsIDReload,
                 '/{0}{1}experiment/<int:id>/reload'.format(API_PATH, API_VERSION))
api.add_resource(ExperimentsIDNodesFlash,
                 '/{0}{1}experiment/<int:id>/nodes/flash/<filename>'.format(API_PATH, API_VERSION))

# try:
#     from .db.models import NodesData
    
#     firmware_data = NodesData('nrf52840dk', '192.168.1.132', 'my home', 'Alive', False)
#     db.session.add(firmware_data)
#     db.session.commit()
    
#     firmware_data2 = NodesData('nrf52840dk', '192.168.1.133', 'my home', 'Alive', False)
#     db.session.add(firmware_data2)
#     db.session.commit()
    
#     firmware_data3 = NodesData('nrf52840dk', '192.168.1.134', 'my home', 'Alive', False)
#     db.session.add(firmware_data3)
#     db.session.commit()
# except:
#     db.session.rollback()

from .db.models import ExperimentsData
from datetime import datetime

# try:
#     experiment_data = ExperimentsData('testaa', 'Waiting', 2, datetime.now(), [2], {"0": {"firmware": "Hello world", "nodes_list": [2]}})
#     db.session.add(experiment_data)
#     db.session.commit()
# except:
#     db.session.rollback()

    # experiment = ExperimentsData.query.filter_by(_id=1).first()

#     from .tasks import start_experiment_task
#     task = start_experiment_task.apply_async(args=[experiment.associations], queue='broadcast_tasks')

from .tasks import dummy_task
dummy_task.apply_async(args=[], queue='broadcast_tasks')