import polyinterface
import requests
import node_funcs
from xml.etree import ElementTree

LOGGER = polyinterface.LOGGER

@node_funcs.add_functions_as_methods(node_funcs.functions)
class RokuNode(polyinterface.Node):
    # class variables
    #id = 'Application'
    hint = [0,0,0,0]
    status= None

    def __init__(self, controller, primary, address, name, ip, apps):
        self.id = address
        self.ip = ip
        self.apps = apps

        # call the default init
        super(RokuNode, self).__init__(controller, primary, address, name)

        # set the current active app
        self.active = self.active_app()
        self.update_status(self.active)

    def longPoll(self):
        self.active = self.active_app()
        self.update_status(self.active)

    def update_status(self, address):
        self.active = address
        self.setDriver('GV2', address, report=True, force=True)
        self.setDriver('GV1', self.apps[address][1], report=True, force=True)

    # Find the current active application, return it's address or ''
    def active_app(self):
        url = 'http://' + self.ip + ':8060/query/active-app'
        try:
            r = requests.get(url)
        except Exception as e:
            LOGGER.error(str(e))
            LOGGER.error(e)
            return 0

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

    def launch(self, command):
        LOGGER.debug('Launch app ' + self.name + "/" + command['value'])
        LOGGER.debug(command)
        # need to convert value (count) into app ID.  self.apps[appid] = (name, count)
        for appid in self.apps:
            if self.apps[appid][1] == int(command['value']):
                LOGGER.info('Launching ' + self.apps[appid][0])
                url = 'http://' + self.ip + ':8060/launch/' + str(appid)
                r = requests.post(url);
                self.update_status(appid)
                return

    def remote(self, command):
        LOGGER.info('Send Remote button ' + command['address'])
        url = 'http://' + self.ip + ':8060/keypress/' + command['cmd']
        r = requests.post(url);
        LOGGER.debug ('requests: ' + r.reason);

        if command['cmd'] == 'HOME':
            self.update_status('0')


    commands = {
            'HOME': remote,
            'REV': remote,
            'FWD': remote,
            'PLAY': remote,
            'SELECT': remote,
            'LEFT': remote,
            'RIGHT': remote,
            'DOWN': remote,
            'UP': remote,
            'BACK': remote,
            'REPLAY': remote,
            'INFO': remote,
            'BACKSPACE': remote,
            'SEARCH': remote,
            'ENTER': remote,
            'LAUNCH': launch
            }
    drivers = [
            {'driver': 'GV1', 'value': 0, 'uom': 25},  # Current running application
            {'driver': 'GV2', 'value': 1, 'uom': 56},  # Current running application id
            ]

    
