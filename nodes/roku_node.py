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
            {'driver': 'ST', 'value': 1, 'uom': 2},   # node server status
            ]

    
