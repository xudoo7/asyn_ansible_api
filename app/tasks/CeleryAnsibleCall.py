# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, absolute_import

from app import celery
from app.utilites import pb_prepare
from models.AnsibleApiCall import AnsibleApiCall


@celery.task
def add_together(a, b):
    return a + b


@celery.task(bind=True)
def callansibleRun(self,resource):
    try:
        inventory = resource.pop('resource')
    except KeyError:
        inventory = None
    ansibleRun = AnsibleApiCall(inventory)
    ansibleRun.runcmd(**resource)
    runResult = ansibleRun.get_result(self.request.id)
    return runResult


@celery.task(bind=True)
def callansiblePlookbook(self, resource):
    try:
        inventory = resource.pop('resource')
        playbook_info = resource.pop('playbook')
        pb_prepare(**playbook_info)
    except KeyError:
        inventory = None
        playbook_info = None
    ansiblePlaybook = AnsibleApiCall(inventory)
    ansiblePlaybook.runplaybook(**playbook_info)
    runResult = ansiblePlaybook.get_result(self.request.id)
    return runResult

if __name__ == "__main__":
    '''
    cmd interface:
        res = {
       "resource":{
        "hosts": {
            "127.0.0.1": {"port": "22", "username": "xusd", "password": "xuderoo7"},
            },
        "groups": {
            "group1": {"hosts": ["127.0.0.1"], "vars": {'var1': 'xxxx', 'var2': 'yyy'}},
            },
        },
       "host_list": "127.0.0.1",
       "module_name": "shell",
       "module_args": "whoami",
       }

    playbook interface:
        res = {
       "resource":{
        "hosts": {
            "127.0.0.1": {"port": "22", "username": "xusd", "password": "xuderoo7"},
            },
        "groups": {
            "group1": {"hosts": ["127.0.0.1"], "vars": {'var1': 'xxxx', 'var2': 'yyy'}},
            },
        },
       "playbook": {
        "pb_type": "host",
        "pb_name": "cmd.yaml",
        },
       }
    '''
    res = {
        "resource": {
            "hosts": {
                "127.0.0.1": {"port": "22", "username": "xusd", "password": "xuderoo7"},
            },
            "groups": {
                "group1": {"hosts": ["127.0.0.1"], "vars": {'var1': 'xxxx', 'var2': 'yyy'}},
            },
        },
        "playbook": {
            "pb_type": "host",
            "pb_name": "cmd.yaml",
        },
    }
    rundelay=callansiblePlookbook.delay(res)
    rundelay.get()
