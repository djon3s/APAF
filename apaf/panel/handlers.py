from cyclone import web, escape, auth

import apaf
from apaf import config

class PanelHandler(web.RequestHandler):
    """
    A simple RequestHandler with utils for the panel
    """
    def get_logged_user(self):
        pass

    def initialize(self, action=None):
        self.action = action

    def error(self, msg):
        """
        Performs JSON response:
         * {"error" : error message }

        :param msg: error message
        """
        self.finish(escape.json_encode({'error':msg}))

    def result(self, boolean):
        """
        Performs JSON response:
         * {"result" : true}
         * {"result": false}
        :param boolean: the boolean to be returned
        """
        self.finish(escape.json_encode({'result':boolean}))


    def set_default_headers(self):
        """
        Panel API is performed entirely via json calls.
        """
        self.set_header("Content-Type", "application/json")

class AuthHandler(PanelHandler, auth.OAuthMixin):
    """
    Authentication:
        ** shall check if requests come from localhost?
        ** just oauth login?
        ***
    """
    pass


class ConfigHandler(PanelHandler):
    """
    Controller for editing config.custom.
    """
    def get(self):
        """
        Process GET requests:
            * /config
        Return a dictionary item:value for each item configurable from the
        panel.
        """
        return self.finish(escape.json_encode(dict(config.custom)))

    def put(self):
        """
        Processes PUT requests:
            * /config
        Processes a dictionary key:value, and put it on the configuration file.
        """
        if 'Settings' not in self.request.headers:
            return self.error('invalid query')

        settings = escape.json_decode(self.request.headers['Settings'])
        if not all(x in config.custom for x in settings):
           return self.error('invalid config file')

        try:
           for key, value in settings.iteritems():
               config.custom.key = value
           self.result(config.custom.commit())
        except KeyErorr as err:
           self.error(err)


class ServiceHandler(PanelHandler):
    _actions = ['state', 'start', 'stop']

    @property
    def services(self):
        """
        Return a dictionary service-name:service-class of all instantiated
        services.
        """
        return {service.name:service for service in apaf.hiddenservices}

   # cache decorator here.
    def _get_service(self, name=None):
        if not name in self.services:
            raise web.HTTPError(404)
        else:
            return self.services[name]

    def state(self, service):
        """
        Process GET request:
            * /services/<service>/
        Return a dictionary containig a summary of what the service is and on
        which url is running on.
        """
        keys = ['name', 'desc', 'url']
        return {name:getattr(service, name, None) for name in keys}

    def start(self, service):
        """
        Process GET request:
            * /services/<service>/start
        """

    def stop(self, service):
        """
        Process GET request:
            * /services/<service>/stop
        """

    # @web.authenticated
    def get(self, service=None):
        """
        Processes GET requests:
          * /services/
          * /services/<service>/
          * /services/<service>/start
          * /services/<service>/stop
        """
        if not service:
            resp = self.services.keys()
        elif self.action in self._actions:
            service = self._get_service(service)
            resp = getattr(self, self.action)(service)

        self.finish(escape.json_encode(resp))
