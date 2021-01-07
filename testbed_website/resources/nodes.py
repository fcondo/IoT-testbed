
from ..utility.errors import error
from ..run import app
from ..db.models import NodesData

from flask import jsonify, make_response
from flask_restful import Resource, reqparse, url_for, request, abort
from werkzeug.utils import secure_filename
import json

class Nodes(Resource):
   
    def __init__(self):
      self.location = app.config['NODES'] 

    def get(self):
        """
            Gets a list of nodes and their status.
            If no nodes set in the DB returns a warning.
        """

        nodes = NodesData.query.all()

        if nodes:
            obj = {}
            for node in nodes:
                obj[node.hostname] = {
                    'state': node.state,
                    'network_address': node.network_address,
                    'archi': node.archi,
                    'site': node.site,
                    'mobile': node.mobile,
                    'uid': node._id
                }

            if(obj):
                return {'nodes': obj}, 200

        return {'error': error(140)}, 500

class NodesIDs(Resource):
   
    def get(self):
        """
            Returns a list of nodes in format 1-2+4 and their status.
        """

        from itertools import groupby
        from operator import itemgetter
            
        nodes = NodesData.query.all()

        if nodes:
            obj = {
                'Alive': [],
                'Suspected': [],
                'Dead': [],
                'Busy': [],
            }
            obj_str = {
                'Alive': '',
                'Suspected': '',
                'Dead': '',
                'Busy': '',
            }

            for node in nodes:
                obj[node.state].append(node._id)
            
            for key in obj:
                obj[key].sort()
                for k, g in groupby(enumerate(obj[key]), lambda x: x[0]-x[1]):
                    interval = list(map(itemgetter(1), g))
                
                    if len(interval) > 1:
                        obj_str[key] += '+' + str(interval[0]) + '-' + str(interval[-1])
                    else:
                        obj_str[key] += '+' + str(interval[0])
                
                # remove starting '+
                obj_str[key] = obj_str[key][1:]
                
                
            # print(obj_str)
            return {'nodes': obj_str}, 200

        return {'error': error(140)}, 500

class Node(Resource):
   
    def get(self, id):
        """
            Returns info on node with given ID.
        """

        node = NodesData.query.filter_by(_id=id)
       
        if node:
            res = {
                'id': node.id,
                'hostname': node.hostname,
                'archi': node.archi,
                'network_address': node.network_address,
                'site': node.site,
                'state': node.state,
                'mobile': node.mobile,
                'fail_count': node.fail_count
            }

            return {'node': res}, 200
        
        return {'error': error(40, id=id)}, 500
    