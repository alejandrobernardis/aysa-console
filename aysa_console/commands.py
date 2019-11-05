# Author: Alejandro M. BERNARDIS
# Email alejandro.bernardis at gmail.com
# Created: 2019/11/05 07:22

import sys
from aysa_console._common import docstring
from aysa_console._docker import Api
from aysa_console.completer import DEVELOPMENT
from fabric import Connection


class BaseCommand:
    def __init__(self, environment, default=DEVELOPMENT):
        self.__cnx = {}
        self.__api = None
        self.__endpoint = None
        self.__environment = environment
        self.set_endpoint(default)

    @property
    def environment(self):
        return self.__environment

    @property
    def endpoint(self):
        return self.__endpoint

    @property
    def endpoints(self):
        return self.environment.endpoints

    @property
    def env(self):
        return self.endpoints[self.endpoint]

    @property
    def cwd(self):
        return self.cnx.cd(self.env.remote_path)

    @property
    def run(self):
        return self.cnx.run

    def get_docstring(self, value=None):
        return docstring(value or self)

    def set_endpoint(self, value):
        value = str(value).lower()
        if value not in self.endpoints:
            raise KeyError('El endpoint "{}" no es válido.'.format(value))
        self.__endpoint = value

    def get_cnx(self, endpoint):
        try:
            cnx = self.__cnx[endpoint]
        except KeyError:
            cnx = Connection(**self.endpoints[endpoint])
            self.__cnx[endpoint] = cnx
        return cnx

    @property
    def cnx(self):
        return self.get_cnx(self.endpoint)

    @property
    def api(self) -> Api:
        if self.__api is None:
            self.__api = Api(**self.environment.registry)
        return self.__api

    def parse(self, argv=None, *args, **kwargs):
        pass


class Commands(BaseCommand):
    """
    AySA Command Line Interface.

    Usage:
        COMMAND [ARGS...]

    Comandos de Entorno:
        config      Muestra la configuración actual.
        select      Selecciona el entorno de ejecución
                    [default: development]

    Comandos de Despliegue:
        deploy      Inicia el proceso de despliegue.
        down        Detiene y elimina todos servicios.
        images      Lista las imágenes disponibles.
        make        Crea las imágenes en la registry.
        prune       Detiene y elimina todos los servicios,
                    como así también las imágenes y volúmenes
                    aosicados.
        restart     Reinicia uno o más servicios.
        services    Lista los servicios disponibles.
        start       Inicia uno o más servicios.
        stop        Detiene uno o más servicios.
        up          Crea e inicia uno o más servicios.

    Comandos Generales:
        help        Muestra la ayuda del programa.
        exit        Sale del programa. (Ctrl + D)
    """

    # Generales

    def help(self, **kwargs):
        print(self.get_docstring())

    def exit(self, code=0, **kwargs):
        sys.exit(code)

    # Entorno

    def config(self, options, **kwargs):
        pass

    def select(self, options, **kwargs):
        pass

    # Despliegue

    def deploy(self, options, **kwargs):
        pass

    def down(self, options, **kwargs):
        pass

    def images(self, options, **kwargs):
        pass

    def make(self, options, **kwargs):
        pass

    def prune(self, options, **kwargs):
        pass

    def restart(self, options, **kwargs):
        pass

    def services(self, options, **kwargs):
        pass

    def start(self, options, **kwargs):
        pass

    def stop(self, options, **kwargs):
        pass

    def up(self, options, **kwargs):
        pass
