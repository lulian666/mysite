#encoding:utf-8
#name:mod_config.py

import ConfigParser
import os

def getConfig(section, key):
    config = ConfigParser.ConfigParser()
    path = os.path.split(os.path.realpath(__file__))[0] + '/settings.conf'
    config.read(path)
    return config.get(section,key)
