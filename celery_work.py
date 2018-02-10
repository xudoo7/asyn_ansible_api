from app import create_app
from app.tasks.FlaskAnsibleCall import Add, AnsibleRunCmd, TaskStatus, AnsibleRunPlaybook

# from gevent import monkey
# from gevent.pywsgi import WSGIServer
# monkey.patch_all()

if __name__ == '__main__':
#    logger = logging.getLogger('myapp')
    app, api = create_app('default')
    api.add_resource(Add, '/add')
    api.add_resource(AnsibleRunCmd, '/ansiblerun', endpoint='AnsibleRunCmd')
    api.add_resource(AnsibleRunPlaybook, '/playbook', endpoint='playbook')
    api.add_resource(TaskStatus,'/taskstatus/<string:task_type>/<string:task_id>', methods=['GET'])
#    logger.info('flask start')
    app.run(debug=True)
    # http_server = WSGIServer(('', 5000), app)
    # http_server.serve_forever()
