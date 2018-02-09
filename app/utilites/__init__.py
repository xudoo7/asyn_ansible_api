# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, absolute_import

import os
# urllib by python3.5
from urllib.request import urlretrieve
from ansible.errors import AnsibleParserError
import yaml
from config import BaseConfig


def temp_iter(tg_dict=None, tg_key=None, src_list=list()):
    """

    :type src_list: object
    """
    if isinstance(tg_dict, list):
        for value in tg_dict:
            temp_iter(value, tg_key)
    elif isinstance(tg_dict, dict):
        if tg_key in tg_dict:
            src_list.append(tg_dict[tg_key])
        else:
            for _, keys in tg_dict.items():
                temp_iter(keys, tg_key)
    else:
        pass
    return src_list


def load_pb(file_name=None, file_type=None, *args, **kwargs):
    base_dir = os.path.join(BaseConfig.PLAYBOOK_DIR, file_type)
    work_path = os.path.join(base_dir, file_name)
    with open(work_path) as f_yaml:
        to_json = yaml.load(f_yaml)
    return to_json


def pb_prepare(pb_name=None, pb_type=None, pb_key=None):
    try:
        check_file(pb_name, pb_type) or get_playbook(pb_name, pb_type)
        pb_json = load_pb(pb_name, pb_type)
        pb_temp = temp_iter(pb_json, pb_key)
        if pb_temp:
            for value in pb_temp:
                src_path = value[:value.index("des=")-1].strip()
                src = src_path[src_path.index("=")+1:].strip()
                get_template(src)
        else:
            print('No found {0} in {1}!'.format(pb_key, pb_name))
        print("Playbook prepare ok")
    except:
        print("Prepare playbook {0} error!".format(pb_name))


def get_playbook(pb_name=None, pb_type=None):
    try:
        url_path = os.path.join(BaseConfig.PLAYBOOK_SERVER, pb_type)
        url_file = os.path.join(url_path, pb_name)
        work_path = os.path.join(BaseConfig.PLAYBOOK_DIR, pb_name)
        urlretrieve(url_file, work_path)
    except:
        print("{0} downloads playbook error!".format(pb_name))


def get_template(temp_path=None, *args, **kwargs):
    try:
        url_path = os.path.join(BaseConfig.TEMPLATE_SERVER, temp_path)
        work_path = os.path.join(BaseConfig.TEMPLATE_DIR, temp_path)
        urlretrieve(url_path, work_path)
    except:
        print("{0} downloads templates error!".format(temp_path))


def check_file(file_name=None, file_type=None):
    type_path = os.path.join(BaseConfig.PLAYBOOK_DIR, file_type)
    playbook_path = os.path.join(type_path, file_name)
    return os.path.exists(playbook_path) or False


def handle_exception(result, *args, **kwargs):
    if 'exception' in result:
        return result


if __name__ == '__main__':
    name = "test.yaml"
    type = "host"
    key = "template"
    pb_prepare(name, type, key)
