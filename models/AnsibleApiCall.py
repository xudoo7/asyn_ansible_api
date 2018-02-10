# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, absolute_import

import logging
import os
from collections import namedtuple

import ansible.executor.task_queue_manager
from ansible.errors import AnsibleParserError, AnsibleFileNotFound
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.playbook.play import Play

from app.utilites import handle_exception
from config import BaseConfig
from models.ResourceBase import ResourceBase
from models.ResultsCallBack import ResultsCallBack

logger = logging.basicConfig()


# ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# PLAYBOOK_DIR = os.path.join(ROOT_DIR, 'ansible_playbooks')

class AnsibleApiCall(ResourceBase):
    """
    This is a General object for parallel execute modules.
    """

    def __init__(self, resource, *args, **kwargs):
        super(AnsibleApiCall, self).__init__(resource)
        self.options = None
        self.passwords = None
        self.callback = None
        self.__initializeData()
        self.results_raw = {}

    def __initializeData(self):
        """
        initialize ansible
        """
        Options = namedtuple('Options', ['connection', 'module_path', 'forks', 'timeout', 'remote_user',
                                         'ask_pass', 'private_key_file', 'ssh_common_args', 'ssh_extra_args',
                                         'sftp_extra_args',
                                         'scp_extra_args', 'become', 'become_method', 'become_user', 'ask_value_pass',
                                         'verbosity',
                                         'check', 'listhosts', 'listtasks', 'listtags', 'syntax'])

        # initialize needed objects
        self.options = Options(connection='ssh',
                               module_path='/root/proj0731/lib/python3.5/site-packages/ansible/modules', forks=100,
                               timeout=10,
                               remote_user='root', ask_pass=False, private_key_file=None, ssh_common_args=None,
                               ssh_extra_args=None,
                               sftp_extra_args=None, scp_extra_args=None, become=None, become_method=None,
                               become_user='root', ask_value_pass=False, verbosity=None, check=False, listhosts=False,
                               listtasks=False, listtags=False, syntax=False)

        self.passwords = dict(sshpass=None, becomepass=None)
        assert isinstance(self.inventory, object), "Inventory Error"
        self.variable_manager.set_inventory(self.inventory)

    def runcmd(self, host_list=None, module_name=None, module_args=None, *args, **kwargs):
        """
        run module from andible ad-hoc.
        module_name: ansible module_name
        module_args: ansible module args
        """
        # create play with tasks
        play_source = dict(
            name="Ansible Play",
            hosts=host_list,
            gather_facts='no',
            tasks=[dict(action=dict(module=module_name, args=module_args))]
        )
        play = Play().load(play_source, variable_manager=self.variable_manager, loader=self.loader)

        # actually run it
        tqm = None
        self.callback = ResultsCallBack()
        try:
            tqm = ansible.executor.task_queue_manager.TaskQueueManager(
                inventory=self.inventory,
                variable_manager=self.variable_manager,
                loader=self.loader,
                options=self.options,
                passwords=self.passwords,
            )
            tqm._stdout_callback = self.callback
            result = tqm.run(play)
        except AnsibleParserError:
            pass
        finally:
            if tqm is not None:
                tqm.cleanup()

    def runplaybook(self, pb_name=None, pb_type=None, *args, **kwargs):
        self.callback = ResultsCallBack()
        try:
            playbook_type = os.path.join(BaseConfig.PLAYBOOK_DIR, pb_type)
            playbook_path = os.path.join(playbook_type, pb_name)
            pbex = PlaybookExecutor(playbooks=[playbook_path],
                                    inventory=self.inventory,
                                    variable_manager=self.variable_manager,
                                    loader=self.loader,
                                    options=self.options,
                                    passwords=self.passwords)
            pbex._tqm._stdout_callback = self.callback
            result = pbex.run()
        except AnsibleFileNotFound:
            self.results_raw = {'playbook': playbook_path, 'exception': ' playbook is not exist', 'flag': False}
        except AnsibleParserError:
            self.results_raw = {'playbook': playbook_path, 'exception': ' playbook have syntax error',
                       'flag': False}


    def get_result(self, task_id):
        if handle_exception(self.results_raw):
            return self.results_raw
        self.results_raw = {'jid:': task_id, 'success': {}, 'failed': {}, 'unreachable': {}}
        for host, result in self.callback.host_unreachable.items():
            self.results_raw['unreachable'][host] = result._result['msg']

        for host, result in self.callback.host_failed.items():
            try:

                self.results_raw['failed'][host] = result._result['msg']
            except KeyError:
                self.results_raw['failed'][host] = 'Command executed Error!'

        for host, result in self.callback.host_ok.items():
            self.results_raw['success'][host] = result._result

        for host, result in self.callback.playbook_notify.items():
            self.results_raw['notify'][host] = result._result

        # logger.debug("Ansible exec result:%s" % self.results_raw)
        return self.results_raw


if __name__ == "__main__":
    res = {
        "hosts": {
            "10.0.2.15": {"port": "22", "username": "xusd", "password": "xuderoo7"},
        },
        "groups": {
            "group1": {"hosts": ["10.0.2.15"], vars: {'var1': 'xxxx', 'var2': 'yyy'}},
        },
    }
    inv = AnsibleApiCall(res)
    inv.get_lists()
    #inv.runcmd('10.0.2.15', 'shell', 'whoami')
    #print(inv.get_result('001'))
    inv.runplaybook("cmd.yaml","host")
    print(inv.get_result('002'))
