from flask_apscheduler import APScheduler
from flask import jsonify, make_response
from ..utility.errors import set_error_from_code
from ..db.models import db, NodesData, ExperimentsData
from ..run import app
from ..tasks import flash_node_task, launch_experiment_task, stop_experiment_task

from datetime import datetime, timedelta
import json

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

NUM_FAIL_NODE_SUSPECTED = 4
NUM_FAIL_NODE_DEAD = 10


def check_node_status():

    nodes = NodesData.query.all()

    if nodes:
        hosts = sorted([node.network_address for node in nodes])

        from netaddr import IPAddress, iter_iprange
        ip_list = iter_iprange(hosts[0], hosts[-1])

        # Alive, Busy, Suspected, Dead

        import subprocess
        import os

        alive = []
        devnull = open(os.devnull, 'w')
        for ip in ip_list:
            retval = subprocess.run(
                ["ping", "-c2", "-n", "-W1", str(ip)], stdout=devnull, stderr=devnull)

            node = NodesData.query.filter_by(network_address=str(ip)).first()

            if retval.returncode == 0:
                alive.append(str(ip))
                node.fail_count = 0

                # if not BUSY
                if node.state != 'Busy':
                    node.state = 'Alive'

            else:
                node.fail_count += 1

                if node.fail_count + 1 >= NUM_FAIL_NODE_DEAD:
                    node.fail_count = NUM_FAIL_NODE_DEAD
                    node.state = 'Dead'

                elif node.fail_count + 1 >= NUM_FAIL_NODE_SUSPECTED:
                    node.state = 'Suspected'

            db.session.commit()
    else:
        print('No nodes defined')


def check_experiments():
    
    experiments = ExperimentsData.query.all()
    if experiments:
        for experiment in experiments:
            if datetime.now() > experiment.scheduled_date and experiment.state == 'Waiting':
                launch_experiment(experiment._id)

                # # minimum percentage [0-100] of nodes Alive to let the experiment run
                # min_percentage = app.config['PERCENT_ALIVE_NODE_TO_START_EXPERIMENT']
                # alive_counter = 0
                
                # for node_id in experiment.nodes_list:
                #     node = NodesData.query.filter_by(_id=id).first()
                #     if node.state == 'Alive':
                #         alive_counter += 1

                # if len(experiment.nodes_list) > 0:
                #     if (alive_counter/len(experiment.nodes_list)) > (min_percentage/100):
                #         flash_nodes(experiment.id)

def experiment_to_stop_after_restart():
    experiments = ExperimentsData.query.all()
    for experiment in experiments:
        if(datetime.now() > experiment.expected_finish_date and experiment.state == 'Running'):
            stop_experiment(experiment._id)
            print(datetime.now(), experiment.expected_finish_date,
              datetime.now() - experiment.expected_finish_date)


def stop_experiment(id):
    print('^^^^^^^^^^^^STOP^^^^^^^^^^^^^^', id)

    experiment = ExperimentsData.query.filter_by(_id=id).first()
    if experiment:
        experiment.state = 'Terminated'
        experiment.finish_date = datetime.now()
        db.session.commit()

        for node_id in experiment.nodes_list:
            node = NodesData.query.filter_by(_uid=node_id).first()
            if node.state == 'Busy':
                node.state = 'Alive'

                db.session.commit()

        task = stop_experiment_task.apply_async(
            args=[], queue='broadcast_tasks')


def launch_experiment(id):
    print('^^^^^^^^^^^^^FLASH^^^^^^^^^^^^^', id)

    experiment = ExperimentsData.query.filter_by(_id=id).first()
    if experiment:
        nodes_to_flash = []
        # experiment.state = 'Running'
        # experiment.started_date = datetime.now()
        experiment.state = 'Launching'
        
        for node_id in experiment.nodes_list:

            node = NodesData.query.filter_by(_id=node_id).first()
            if node.state == 'Alive' or True:                                   # TODO remove or True
                nodes_to_flash.append(node.network_address)
                node.state = 'Busy'
        
        try:
            experiment.started_date = datetime.now()
            experiment.expected_finish_date = experiment.started_date + + timedelta(minutes=experiment.submitted_duration)
            # schedule reset and grabserial collection 1 minute ahead
            reset_time = experiment.started_date + timedelta(minutes=1)

            task = launch_experiment_task.apply_async(
                args=[experiment._id, experiment.associations, reset_time], queue='broadcast_tasks')
            
            db.session.commit()

        except Exception as exc:
            print(exc)
            db.session.rollback()
            return

        # duration = experiment.submitted_duration
        # experiment.started_date = datetime.now()

        # scheduler.add_job(func=stop_experiment, trigger='date', run_date=datetime.now()
        #                   + timedelta(minutes=duration), args=[id], id='stop_experiment_' + str(id))

def flash_nodes(id, launch_experiment=False, launch_time=None):
    print('^^^^^^^^^^^^^FLASH^^^^^^^^^^^^^', id)

    experiment = ExperimentsData.query.filter_by(_id=id).first()
    if experiment:
        nodes_to_flash = []
        # experiment.state = 'Running'
        # experiment.started_date = datetime.now()
        experiment.state = 'Launching'
        try:
            db.session.commit()
        except:
            db.session.rollback()
            return

        for node_id in experiment.nodes_list:

            node = NodesData.query.filter_by(_id=node_id).first()
            if node.state == 'Alive' or True:
                nodes_to_flash.append(node.network_address)
                node.state = 'Busy'
                try:
                    db.session.commit()
                except:
                    db.session.rollback()
                    return


        task = flash_node_task.apply_async(
            args=[experiment._id, experiment.associations, True], queue='broadcast_tasks')

        # duration = experiment.submitted_duration
        # experiment.started_date = datetime.now()

        # scheduler.add_job(func=stop_experiment, trigger='date', run_date=datetime.now()
        #                   + timedelta(minutes=duration), args=[id], id='stop_experiment_' + str(id))



scheduler.add_job(func=check_node_status, trigger='interval',
                  seconds=30, args=[], id='nodes_status')

scheduler.add_job(func=check_experiments, trigger='interval',
                  seconds=10, args=[], id='scheduled_as_soon_as_possible_experiments')

print('$$$$$$$$$$$')

experiment_to_stop_after_restart()
