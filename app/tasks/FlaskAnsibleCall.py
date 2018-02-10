# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, absolute_import

from flask import Flask
from flask_restful import reqparse, abort, Resource, Api

from app.tasks.CeleryAnsibleCall import callansibleRun, callansiblePlookbook, add_together

app = Flask(__name__)
api = Api(app)

TODOS = {
    'Add': {'Add': 'build an API'},
    'AnsibleRun': {'AnsibleRun': 'build an API'},
}


def abort_if_todo_doesnt_exist(todo_id):
    if todo_id not in TODOS:
        abort(404, message="Todo {} doesn't exist".format(todo_id))


class Add(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('a', int)
        self.reqparse.add_argument('b', int)

    def post(self):
        args = self.reqparse.parse_args()
        res = add_together.delay(int(args["a"]), int(args["b"]))
        return res.get()


class AnsibleRunCmd(Resource):
    def __init__(self):
        super(AnsibleRunCmd, self).__init__()
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('data', type=dict, required=True,
                                   help='No data provided', location='json')

    def post(self):
        args = self.reqparse.parse_args()
        data = args['data']
        task = callansibleRun.delay(data)
        return {'task_id': task.id, 'task_url': api.url_for(TaskStatus, task_type='ad_hoc', task_id=task.id)}


class AnsibleRunPlaybook(Resource):
    def __init__(self):
        super(AnsibleRunPlaybook, self).__init__()
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('data', type=dict, required=True,
                                   help='No data provided', location='json')

    def post(self):
        args = self.reqparse.parse_args()
        data = args['data']
        task = callansiblePlookbook.delay(data)
        return {'task_id': task.id, 'task_url': api.url_for(TaskStatus, task_type='playbook', task_id=task.id)}


class TaskStatus(Resource):
    def __init__(self):
        super(TaskStatus, self).__init__()

    @staticmethod
    def get(task_type, task_id):
        # check client ip
        # ip = request.remote_addr
        # if not is_safe_ip(ip):
        #    abort(401)
        if task_type == "ad_hoc":
            task = callansibleRun.AsyncResult(task_id)
        elif task_type == "playbook":
            task = callansiblePlookbook.AsyncResult(task_id)
        else:
            abort(400, {'message': 'Unknown Task Type!'})

        if task.state == 'PENDING':
            response = {
                'state': task.state,
                'status': 'Pending...'
            }
        elif task.state != 'FAILURE':
            response = {
                'state': task.state,
                'status': task.info
            }
            if 'result' in task.info:
                response['result'] = task.info['result']
        else:
            # something went wrong in the background job
            response = {
                'state': task.state,
                'status': task.info,  # this is the exception raised
            }
        return response

# Post json data with curl for examples:
# curl -H "Content-Type: application/json" -X POST -d '{"data":{"host_list": "127.0.0.1", "module_args": "whoami", "resource": #{"hosts": {"127.0.0.1": {"username": "xusd", "password": "xuderoo7", "port": "22"}}, "groups": {"group1": {"hosts":
# ["127.0.0.1"], "vars": {"var1": "xxxx", "var2": "yyy"}}}}, "module_name": "shell"}}' http://127.0.0.1:5444/testing
