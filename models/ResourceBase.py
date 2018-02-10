# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, absolute_import

import ansible.constants as ANS_CONS
from ansible.inventory import Inventory
from ansible.inventory.group import Group
from ansible.inventory.host import Host
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager


class ResourceBase(object):
    """
    generate inventory

    :param resource: inventory resource, format:
        {
            "hosts" : {
                "host1": {"port": "22", "username": "test", "password": "xxxx"},
                "host2": {"port": "22", "username": "test", "password": "xxxx"},
            },
            "groups": {
                "group1": {"hosts": ["host1", "host2",...], "vars": {'var1':'xxxx', 'var2':'yyy',...} },
                "group2": {"hosts": ["host1", "host2",...], "child": ["group1"], "vars": {'var1':'xxxx', 'var2':'yyy',...} },
            }
        }
    """

    def __init__(self, resource=None):
        host_list = not resource and ANS_CONS.DEFAULT_HOST_LIST or []
        self.loader = DataLoader()
        self.variable_manager = VariableManager()
        self.resource = resource
        self.inventory = Inventory(loader=self.loader, variable_manager=self.variable_manager, host_list=host_list)
        #resource and self.gen_inventory()
        self.gen_inventory()

    @staticmethod
    def gen_host(host_name=None, host_vars=None):
        """
        Generate ansible Host object
        :param host_name: <string> ansible inventory hostname
        :param host_vars: <dict> host variables
        :return: Host object
        """
        if host_vars is None:
            host_vars = {}
        ssh_host = host_vars.get('ip', host_name)
        ssh_port = host_vars.get('port', ANS_CONS.DEFAULT_REMOTE_PORT)
        ssh_user = host_vars.get('username')
        ssh_pass = host_vars.get('password')
        ssh_fkey = host_vars.get('ssh_key')
        # init Host
        host = Host(name=host_name, port=ssh_port)
        host.set_variable('ansible_ssh_host', ssh_host)
        # shortcut variables
        ssh_user and host.set_variable('ansible_ssh_user', ssh_user)
        ssh_pass and host.set_variable('ansible_ssh_pass', ssh_pass)
        ssh_fkey and host.set_variable('ansible_private_key_file', ssh_fkey)
        # extra variables
        for key, value in host_vars.items():
            if key not in ['ip', 'port', 'username', 'password', 'ssh_key']:
                host.set_variable(key, value)
        # return Host object
        return host

    @staticmethod
    def gen_group(group_name=None, group_vars=None):
        """
        Generate ansible Group object
        :param group_name: <string> Group Name
        :param group_vars: <dict> Group Variables
        :return: ansible Group object
        """
        if group_vars is None:
            group_vars = {}
        group = Group(name=group_name)
        for key, value in group_vars.items():
            group.set_variable(key, value)
        return group

    def gen_inventory(self):
        """
        :return: None
        """
        # set hosts
        if 'hosts' in self.resource.keys():
            for host, info in self.resource['hosts'].items():
                obj_host = self.gen_host(host, info)
                self.inventory.get_group('all').add_host(obj_host)
        # add group
        if 'groups' in self.resource.keys():
            for group, detail in self.resource['groups'].items():
                obj_group = self.gen_group(group, detail.get('vars', {}))
                for host in detail.get('hosts', []):
                    obj_group.add_host(self.inventory.get_host(host))
                if 'child' in detail.get('child', []):
                    for child in detail.get('child', []):
                        obj_group.add_child_group(self.inventory.get_group(child))
                self.inventory.add_group(obj_group)

    def get_lists(self):
        print("Host: ")
        print("=================")
        for host in self.inventory.list_hosts():
            print(host)
        print("Group: ")
        print("=================")
        for group in self.inventory.list_groups():
            print(group)


if __name__ == "__main__":
    res = {
        "hosts": {
            "127.0.0.1": {"port": "22", "username": "root", "password": "xxxx"},
            "192.168.1.2": {"port": "22", "username": "root", "password": "yyyy"},
            "192.168.1.3": {"port": "22", "username": "root", "password": "zzz"},
            "192.168.1.4": {"port": "22", "username": "root", "password": "zzz"},
            "192.168.1.6": {"port": "22", "username": "root", "password": "zzz"},
            "192.168.1.7": {"port": "22", "username": "root", "password": "zzz"},
        },
        "groups": {
            "group1": {"hosts": ["127.0.0.1", "192.168.1.2"], vars: {'var1': 'xxxx', 'var2': 'yyy'}},
            "group2": {"hosts": ["192.168.1.1", "192.168.1.2"], vars: {'var1': 'xxxx', 'var2': 'yyy'}},
            "group7": {"hosts": ["192.168.1.3"], "child": ["group1"], vars: {'var3': 'z', 'var4': 'o'}},
        }
    }
    inv = ResourceBase(res)
    inv.get_lists()
