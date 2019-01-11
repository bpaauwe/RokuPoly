#!/usr/bin/env python3
"""
Polyglot v2 node server experimental Roku Media Player control.
Copyright (C) 2019 Robert Paauwe
"""
import polyinterface
import sys
import time
import datetime
import urllib3
import socket
import math
import json
import requests
import write_profile
from xml.etree import ElementTree

LOGGER = polyinterface.LOGGER

class Controller(polyinterface.Controller):
    id = 'Roku'
    hint = [0,0,0,0]
    def __init__(self, polyglot):
        super(Controller, self).__init__(polyglot)
        self.name = 'Roku'
        self.address = 'r_0'
        self.primary = self.address
        self.configured = False
        self.myConfig = {}
        self.base_url = "http://"
        self.port  = 8060
        self.ip_address = ""
        self.active = '0'
        self.nls_map = {}
        self.nls_map_new = {}

        self.poly.onConfig(self.process_config)

    # Process changes to customParameters
    def process_config(self, config):
        if 'customParams' in config:
            # Check if anything we care about was changed...
            if config['customParams'] != self.myConfig:
                changed = False
                LOGGER.info('checking for IP Address in saved config')
                if 'IP Address' in self.myConfig:
                    LOGGER.info('Found IP Address = ' + self.MyConfig['IP Address'])
                    if self.myConfig['IP Address'] != config['customParams']['IP Address']:
                        changed = True
                elif 'IP Address' in config['customParams']:
                    if config['customParams']['IP Address'] != "":
                        LOGGER.info('Changing IP Address to ' + config['customParams']['IP Address'])
                        changed = True
                    else:
                        LOGGER.info('Should we look at ' + self.polyConfig['customParams']['IP Address'])

                self.myConfig = config['customParams']
                if changed:
                    LOGGER.info('IP Address changed, call discover')
                    self.ip_address = config['customParams']['IP Address']
                    self.removeNoticesAll()
                    self.configured = True;
                    discover()

    def start(self):
        LOGGER.info('Starting node server')

        self.check_params()
        self.base_url = 'http://' + self.ip_address + ':' + str(self.port)

        self.discover()

        LOGGER.info('Node server started')

    # Find the current active application, return it's address or ''
    def active_app(self):
        r = requests.get(self.base_url + "/query/active-app")
        tree = ElementTree.fromstring(r.content)
        for child in tree.iter('*'):
            if child.tag == 'app':
                if child.text == 'Roku':
                    return '0'
                elif 'id' in child.attrib:
                    return child.attrib['id']
                else:
                    return '0'
        return '0'

    def longPoll(self):
        return
        self.active = self.active_app()
        if self.active == '':
            for node in self.nodes:
                LOGGER.info(' - Clearing node ' + node)
                if node != 'r_0' and node != 'controller':
                    self.nodes[node].setDriver('ST', 0, report=True, force=False)
        else:
            self.setDriver('GV0', self.active, report=True, force=True)

    def shortPoll(self):
        pass

    def query(self):
        for node in self.nodes:
            self.nodes[node].reportDrivers()

    def build_and_push_nls(map):
        LOGGER.info('Create and write NLS file')

    # Query the Roku and get the list of installed applications.  Create
    # nodes based on the list.
    def discover(self, *args, **kwargs):
        LOGGER.info("In Discovery...")
        if not self.configured:
            LOGGER.info('Skipping discovery because we aren\'t configured yet.')
            return

        r = requests.get(self.base_url + "/query/apps")
        tree = ElementTree.fromstring(r.content)
        #LOGGER.info(r.content)
        cnt = 1
        for child in tree.iter('*'):
            if (child.tag == 'app'):
                # Create a node
                LOGGER.debug(child.text + ', ' + child.attrib['id'])
                node = AppNode(self, self.address, child.attrib['id'], child.text);
                node.base_url = self.base_url
                node.status = self.update_status
                self.addNode(node)
                time.sleep(.35)

                self.nls_map[child.attrib['id']] = (child.text, cnt)
                cnt = cnt + 1

        self.nls_map['0'] = ("Screensaver", 0)

        # self.build_and_push_nls(self.nls_map)
        write_profile.write_profile(LOGGER, self.nls_map)

        # Query for active app and set appropriate status
        self.active = self.active_app()
        for node in self.nodes:
            if node == 'r_0':  # controller node
                self.setDriver('GV0', self.active, report=True, force=True)
                self.setDriver('GV1', self.nls_map[self.active][1], report=True, force=True)
            elif node == 'controller':
                LOGGER.info('skip controller node')
            else:
                if node == self.active:
                    self.nodes[node].setDriver('ST', 1, report=True, force=False)
                else:
                    self.nodes[node].setDriver('ST', 0, report=True, force=False)


    # Delete the node server from Polyglot
    def delete(self):
        LOGGER.info('Removing node server')

    def stop(self):
        LOGGER.info('Stopping node server')

    def update_profile(self, command):
        st = self.poly.installprofile()
        return st

    def check_params(self):
        if 'IP Address' in self.polyConfig['customParams']:
            self.ip_address = self.polyConfig['customParams']['IP Address']

        self.addCustomParam( {
            'IP Address': self.ip_address,
            })

        if (self.ip_address != ''):
            self.configured = True;

        self.removeNoticesAll()

    def remove_notices_all(self, command):
        self.removeNoticesAll()

    def update_status(self, address):
        LOGGER.info('Application was launched, ' + address + ' do something')
        if self.active != '0':
            node = self.nodes[self.active]
            node.setDriver('ST', 0, report=True, force=False)
        self.active = address
        self.setDriver('GV0', address, report=True, force=True)
        self.setDriver('GV1', self.nls_map[address][1], report=True, force=True)

    def keypress(self, command):
        # command['cmd'] holds button name
        # command['address'] holds the node address that generated it
        r = requests.post(self.base_url + "/keypress/" + command['cmd']);
        LOGGER.debug ('requsts: ' + r.reason);

        if command['cmd'] == 'HOME':
            self.update_status('0')

    commands = {
            'HOME': keypress,
            'REV': keypress,
            'FWD': keypress,
            'PLAY': keypress,
            'SELECT': keypress,
            'LEFT': keypress,
            'RIGHT': keypress,
            'DOWN': keypress,
            'UP': keypress,
            'BACK': keypress,
            'REPLAY': keypress,
            'INFO': keypress,
            'BACKSPACE': keypress,
            'SEARCH': keypress,
            'ENTER': keypress,
            }

    drivers = [
            {'driver': 'ST', 'value': 1, 'uom': 2},   # node server status
            {'driver': 'GV0', 'value': 0, 'uom': 25},   # node server status
            {'driver': 'GV1', 'value': 0, 'uom': 25},   # node server status
            ]

class AppNode(polyinterface.Node):
    id = 'Application'
    hint = [0,0,0,0]
    app_name = ''
    base_url = ''
    status = None

    def launch(self, command):
        LOGGER.info('Launch app ' + self.name + "/" + command['address'])
        self.setDriver('ST', 1, report=True, force=True)
        r = requests.post(self.base_url + "/launch/" + command['address']);
        if self.status != None:
            self.status(command['address'])

    commands = {
            'LAUNCH': launch
            }
    drivers = [
            {'driver': 'ST', 'value': 0, 'uom': 2},   # node server status
            ]

    
if __name__ == "__main__":
    try:
        polyglot = polyinterface.Interface('Roku')
        polyglot.start()
        control = Controller(polyglot)
        control.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
        

