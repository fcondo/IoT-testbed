from flask_restful import Resource, reqparse, url_for, request
from datetime import datetime, timedelta
from sqlalchemy import func, exc
from ..db.models import db, ExperimentsData, FirmwaresData
from ..utility.errors import error, set_error_from_code
from ..scheduler.apscheduler import flash_nodes
import json


class ExperimentsTotal(Resource):

    def get(self):
        '''
            Returns total number of experiments.
        '''

        experiments = ExperimentsData.query.all()
        if experiments:
            return {'num': len(experiments)}, 200

        return {'error': error(130)}, 500


class ExperimentsID(Resource):

    def delete(self, id):
        '''
            Deletes an experiment.
        '''

        experiment = ExperimentsData.query.filter_by(_id=id).first()
        if experiment:
            experiment['stopped_date'] = datetime.now()
            try:
                db.session.commit()

                from ..scheduler.apscheduler import stop_experiment
                stop_experiment()

                return {'success': {'type': 'success', 'message': ('Experiment with ID <b>{0}</b> correctly stopped.').format(id)}}, 200
            except:
                db.session.rollback()
                return {'error': error(30, id=id)}, 500

        return {'error': error(30, id=id)}, 500

    def get(self, id):
        '''
            Returns an experiment.
        '''

        experiment = ExperimentsData.query.filter_by(_id=id).first()
        if experiment:
            ret = {
                'id': experiment._id,
                'name': experiment.name,
                'user': experiment.user,
                'num_nodes': experiment.num_nodes,
                'state': experiment.state,
                'submitted_duration': experiment.submitted_duration,
                'scheduled_date': experiment.scheduled_date.strftime("%m/%d/%Y, %H:%M:%S") if experiment.scheduled_date else '',
                'started_date': experiment.started_date.strftime("%m/%d/%Y, %H:%M:%S") if experiment.start_date else '',
                'finish_date': experiment.finish_date.strftime("%m/%d/%Y, %H:%M:%S") if experiment.finish_date else '',
                'expected_finish_date': experiment.expected_finish_date.strftime("%m/%d/%Y, %H:%M:%S") if experiment.expected_finish_date else '',
                'stopped_date': experiment.stopped_date.strftime("%m/%d/%Y, %H:%M:%S") if experiment.stopped_date else '',
                'nodes_list': experiment.nodes_list,
                'associations': experiment.associations
            }

            return {'experiment': ret}, 200

        return {'error': error(31, id=id)}, 500


class ExperimentsRunning(Resource):

    def get(self):
        '''
            Returns running testbed experiments list.
        '''

        experiments = ExperimentsData.query.filter_by(state='Running').all()
        if experiments:
            exps_list = []

            for experiment in experiments:
                exps_list.append(experiment._id)

            return {'experiments': exps_list}, 200

        return {'error': error(131)}, 500


class Experiments(Resource):

    def get(self):
        '''
            Returns experiments list.
        '''

        experiments = ExperimentsData.query.all()
        if experiments:
            exps_list = {}
            for experiment in experiments:

                # if(experiment.state == 'Running'):
                exps_list[experiment._id] = {
                    'id': experiment._id,
                    'name': experiment.name,
                    'user': experiment.user,
                    'state': experiment.state,
                    'submitted_duration': experiment.submitted_duration,
                    'scheduled_date': experiment.scheduled_date.strftime("%m/%d/%Y, %H:%M:%S") if experiment.scheduled_date else '',
                    'started_date': experiment.started_date.strftime("%m/%d/%Y, %H:%M:%S") if experiment.started_date else '',
                    'finish_date': experiment.finish_date.strftime("%m/%d/%Y, %H:%M:%S") if experiment.finish_date else '',
                    'expected_finish_date': experiment.expected_finish_date.strftime("%m/%d/%Y, %H:%M:%S") if experiment.expected_finish_date else '',
                    'stopped_date': experiment.stopped_date.strftime("%m/%d/%Y, %H:%M:%S") if experiment.stopped_date else '',
                    'nodes_list': experiment.nodes_list
                }

                return {'experiments': exps_list}, 200

        return {'error': error(130)}, 500

    def post(self):
        '''
           Submit an experiment.
        '''

        name = request.form['name']
        state = 'Waiting'
        submitted_duration = int(request.form['submitted_duration'])
        scheduled_hour_min = request.form['scheduled_date']
        mapping = request.form['mapping']

        from flask_login import current_user
        user = current_user.name

        nodes_list = []
        associations = {}
        data = json.loads(mapping)

        for key in data:
            nodes_list.extend(data[key]['nodes_list'])
            associations[key] = {
                'firmware': data[key]['firmware'],
                'nodes_list': data[key]['nodes_list']
            }

        if scheduled_hour_min == 'as_soon_as_possible':
            scheduled_date = datetime(1970, 1, 1)
        else:
            h, m = scheduled_hour_min.split(':')
            scheduled_date = datetime.today().replace(
                hour=int(h), minute=int(m), second=0, microsecond=0)

        experiment_data = ExperimentsData(
            name, state, submitted_duration, scheduled_date, user, nodes_list, associations)
        
        try:
            db.session.add(experiment_data)
            db.session.commit()

            # if scheduled_hour_min != 'as_soon_as_possible':

            #     # get the just posted experiment to obtain its ID
            #     exp_id = db.session.query(func.max(ExperimentsData._id)).scalar()
            #     from ..scheduler.apscheduler import scheduler, launch_experiment
                
            #     synch_reset_time = scheduled_date + timedelta(minutes=1)
            #     scheduler.add_job(func=launch_experiment, trigger='date', run_date=scheduled_date, args=[
            #         experiment_data._id], id='launch_experiment_' + str(exp_id))

            return {'success': {'type': 'success', 'message': ('Experiment <b>' + name + '</b> correctly submitted.').format(name)}}, 200
        
        except exc.IntegrityError:
            db.session.rollback()
            return {'error': error(34, name=name)}, 500
        except:
            db.session.rollback()
            return {'error': error(32, name=name)}, 500
            

class ExperimentsIDNodes(Resource):

    def get(self, id):
        '''
            Returns experiment nodes list.
        '''

        experiment = ExperimentsData.query.filter_by(_id=id).first()
        if experiment:
            return {'nodes_list': experiment.nodes_list}, 200

        return {'error': error(31, id=id)}, 500


class ExperimentsIDNodesIDs(Resource):

    def get(self, id):
        '''
            Returns experiment nodes id list (e.g. 1-6+9).
        '''

        from itertools import groupby
        from operator import itemgetter

        experiment = ExperimentsData.query.filter_by(_id=id).first()

        if experiment:
            ret_val = ''
            nodes = experiment.nodes_list
            for k, g in groupby(enumerate(nodes), lambda x: x[0]-x[1]):
                interval = list(map(itemgetter(1), g))

                if len(interval) > 1:
                    ret_val += '+' + str(interval[0]) + '-' + str(interval[-1])
                else:
                    ret_val += '+' + str(interval[0])

            # remove starting '+
            return {'nodes': ret_val[1:]}, 200
        
        return {'error': error(31, id=id)}, 500


class ExperimentsIDReload(Resource):

    def post(self, id):
        '''
            Reload experiment.
        '''
        experiment = ExperimentsData.query.filter_by(_id=id).first()

        if experiment:
            return {}, 200

        return {'error': error(33, id=id)}, 500


class ExperimentsIDNodesFlash(Resource):

    def post(self, id, name):
        '''
            Sends experiment nodes flash firmware command with name.
        '''
        experiment = ExperimentsData.query.filter_by(_id=id).first()

        if experiment:
            firmware = FirmwaresData.query.filter_by(_name=name).first()
            if firmware:
                # flash_nodes()
                return {}, 200

            return {}, 500

        return {}, 500
