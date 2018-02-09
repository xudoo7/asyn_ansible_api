# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, absolute_import

from app import celery
from models.AnsibleApiCall import AnsibleApiCall
from app.utilites import pb_prepare


"""@celery.taskHost:
#=================
#192.168.1.7
192.168.1.4
192.168.1.2
192.168.1.6
127.0.0.1
192.168.1.3
Group:
=================
all
group1
group2
group7
ungrouped"""

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
        pb_prepare(**resource)
    except KeyError:
        inventory = None
        playbook_info = None
    ansiblePlaybook = AnsibleApiCall(inventory)
    ansiblePlaybook.runplaybook(**resource)
    runResult = ansiblePlaybook.get_result(self.request)
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
    print(rundelay.get())
