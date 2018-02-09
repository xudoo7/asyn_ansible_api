# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, absolute_import

from ansible.plugins.callback import CallbackBase


# class ResultsCallBack(CallbackBase):
#    def __init__(self, *args, **kwargs):
#        super(ResultsCallBack, self).__init__(*args, **kwargs)
#        self.host_ok = {}
#        self.host_unreachable = {}
#        self.host_failed = {}

#    def v2_runner_on_unreachable(self, result):
#        self.host_unreachable[result._host.get_name()] = result

#    def v2_runner_on_ok(self, result, *args, **kwargs):
#        self.host_ok[result._host.get_name()] = result

#    def v2_runner_on_failed(self, result, *args, **kwargs):
#        self.host_failed[result._host.get_name()] = result

class ResultsCallBack(CallbackBase):
    def __init__(self, *args, **kwargs):
        super(ResultsCallBack, self).__init__(display=None)
        self.status_ok = {}
        self.status_fail = {}
        self.status_unreachable = {}
        self.status_playbook = {}
        self.status_no_hosts = False
        self.host_ok = {}
        self.host_failed = {}
        self.host_unreachable = {}
        self.playbook_notify = {}


    def v2_runner_on_ok(self, result):
        host = result._host.get_name()
        self.host_ok[host] = result

    def v2_runner_on_failed(self, result, ignore_errors=False):
        host = result._host.get_name()
        self.host_failed[host] = result

    def v2_runner_on_unreachable(self, result):
        host = result._host.get_name()
        self.host_unreachable[host] = result

    def v2_playbook_on_no_hosts_matched(self):
        self.playbook_on_no_hosts_matched()
        self.status_no_hosts = True

    def v2_playbook_on_play_start(self, play):
        self.playbook_on_play_start(play.name)
        self.playbook_path = play.name

    def v2_playbook_on_stats(self, stats):
        self.playbook_on_stats(stats)

    def v2_playbook_on_notify(self, result, handler):
        host = result._host.get_name()
        self.playbook_notify[host] = self.playbook_on_notify(host, handler)
