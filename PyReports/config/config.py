#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  1 12:45:30 2022

@author: Sina Tureli
"""
import configparser as _cp
import os as _os

_CONFIG_PATH = _os.path.dirname(_os.path.realpath(__file__))
_USE_DEFAULT = False

def format_config_item(config_item):
    split_item = config_item.split('\n')
    counter = 1
    indent =  '    '
    for ind,item in enumerate(split_item):
        counter += item.count('{')-item.count('}')
        split_item[ind] = indent + split_item[ind]

        indent = counter*'    '


    return '\n'.join(split_item)

def default_config():

    global _USE_DEFAULT
    _USE_DEFAULT = True

def user_config():

    global _USE_DEFAULT
    _USE_DEFAULT = False

def load_config(update_config_name='user'):

    config = _cp.ConfigParser(interpolation=None)

    config.read(f'{_CONFIG_PATH}/default.ini')

    if not _USE_DEFAULT:
        if not _os.path.exists(f'{_CONFIG_PATH}/{update_config_name}.ini'):
            raise ValueError('config file with path '
                             f'{_CONFIG_PATH}/{update_config_name}.ini '
                             'does not exist.')

        config.read(f'{_CONFIG_PATH}/{update_config_name}.ini')

    config_dict = {}

    for section in ['SCRIPTS','STYLES']:

        config_dict[section] = {}

        for key in config[section]:
            item = format_config_item(config[section].get(key,''))
            if item == '    ':
                item = ''

            config_dict[section][key.upper()] = item

    return config_dict

def save_config(config_dict, path):

    if path[-4:] != '.ini':
        path += '.ini'

    config = _cp.ConfigParser(interpolation=None)

    for key1 in config_dict:
        config[key1] = {}

        for key2 in config_dict[key1]:
            config[key1][key2] = config_dict[key1][key2]


    with open(path, 'w') as configfile:
       config.write(configfile)


config = load_config()
