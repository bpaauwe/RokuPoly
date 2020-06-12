#!/usr/bin/env python3
"""
Polyglot v2 node server experimental Roku Media Player control.
Copyright (C) 2019,2020 Robert Paauwe
"""
import polyinterface
import sys
import time
#import datetime
#import socket
#import math
import json
import requests
import node_funcs
import write_profile as profile
from xml.etree import ElementTree
from nodes import roku_node

LOGGER = polyinterface.LOGGER

@node_funcs.add_functions_as_methods(node_funcs.functions)
class Controller(polyinterface.Controller):
    id = 'Roku'
    hint = [0,0,0,0]
    def __init__(self, polyglot):
        super(Controller, self).__init__(polyglot)
        self.name = 'Roku'
        self.address = 'roku'
        self.primary = self.address
        self.roku_list = {}
        self.in_config = False
        self.in_discover = False

        self.poly.onConfig(self.process_config)

    # Process changes to customParameters
    def process_config(self, config):
        rediscover = False
        if self.in_config:
            return

        self.in_config = True
        if 'customParams' in self.polyConfig:
            for roku_name in self.polyConfig['customParams']:
                LOGGER.info('found ' + roku_name + ' with ip ' + self.polyConfig['customParams'][roku_name])
                if roku_name not in self.roku_list:
                    address = self.polyConfig['customParams'][roku_name]
                    node_id = 'roku_' + address.split('.')[3]

                    self.roku_list[roku_name] = {'ip':address, 'configured':False, 'node_id':node_id, 'apps':None }
                    rediscover = True

        if rediscover:
            self.discover()

        self.in_config = False

    def start(self):
        LOGGER.info('Starting node server')

        self.set_logging_level()
        self.check_params()
        self.discover()

        LOGGER.info('Node server started')

    def longPoll(self):
        for node in self.nodes:
            if self.nodes[node].address != self.address:
                LOGGER.debug('Polling ' + node)
                self.nodes[node].longPoll()

    def shortPoll(self):
        pass

    def query(self):
        for node in self.nodes:
            self.nodes[node].reportDrivers()

    # Create the nodes for each device configured and query
    # to get the list of installed applications.  
    def discover(self, *args, **kwargs):
        if self.in_discover:
            return

        self.in_discover = True
        LOGGER.info("In Discovery...")
        for rk in self.roku_list:
            LOGGER.debug(self.roku_list[rk])
            if self.roku_list[rk]['configured']:
                LOGGER.info('Roku ' + rk + ' already configured, skipping.')
                self.in_discover = False
                return

            # query app list from roku
            LOGGER.info('query ' + self.roku_list[rk]['ip'])
            nls_map = {}
            r = requests.get('http://' + self.roku_list[rk]['ip'] + ":8060/query/apps")
            tree = ElementTree.fromstring(r.content)
            #LOGGER.info(r.content)
            cnt = 1
            for child in tree.iter('*'):
                if (child.tag == 'app'):
                    # Create a map of applications on this roku
                    name = child.text.replace('&', 'and')
                    LOGGER.debug(name + ', ' + child.attrib['id'])

                    nls_map[child.attrib['id']] = (name, cnt)
                    cnt = cnt + 1

            nls_map['0'] = ("Screensaver", 0)

            self.roku_list[rk]['configured'] = True
            self.roku_list[rk]['apps'] = nls_map

        profile.write_nls(LOGGER, self.roku_list)
        profile.write_nodedef(LOGGER, self.roku_list)
        self.update_profile(None)

        # Create the nodes
        for rk in self.roku_list:
            rd = self.roku_list[rk]
            node = roku_node.RokuNode(self, self.address, rd['node_id'], rk, rd['ip'], rd['apps'])
            self.addNode(node)

        self.in_discover = False

    # Delete the node server from Polyglot
    def delete(self):
        LOGGER.info('Removing node server')

    def stop(self):
        LOGGER.info('Stopping node server')

    def update_profile(self, command):
        st = self.poly.installprofile()
        return st

    # Look at what's configured and create the list of
    # Roku devices.
    def check_params(self):
        if 'customParams' in self.polyConfig:
            for roku_name in self.polyConfig['customParams']:
                LOGGER.info('found ' + roku_name + ' with ip ' + self.polyConfig['customParams'][roku_name])
                if roku_name not in self.roku_list:
                    address = self.polyConfig['customParams'][roku_name]
                    node_id = 'roku_' + address.split('.')[3]

                    self.roku_list[roku_name] = {'ip':address, 'configured':False, 'node_id':node_id, 'apps':None }
        else:
            LOGGER.error('config not found')

        self.removeNoticesAll()

    def remove_notices_all(self, command):
        self.removeNoticesAll()

    def set_logging_level(self, level=None):
        if level is None:
            try:
                level = self.get_saved_log_level()
            except:
                LOGGER.error('unable to get saved log level.')
        if level is None:
            level = 30
        else:
            level = int(level['value'])

        LOGGER.info('Setting log level to %d' % level)
        LOGGER.setLevel(level)
        self.setDriver('GV0', level)


    commands = {
            'DISCOVER': discover,
            'REMOVE_NOTICES_ALL': remove_notices_all,
            'UPDATE_PROFILE': update_profile,
            'DEBUG': set_logging_level,
            }

    drivers = [
            {'driver': 'ST', 'value': 1, 'uom': 2},   # node server status
            {'driver': 'GV0', 'value': 0, 'uom': 25}, # Log Level
            ]

    
