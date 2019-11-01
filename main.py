#!/usr/bin/env python
import sys
import logging
from fabric import Connection
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.shortcuts import yes_no_dialog
from prompt_toolkit.styles import Style
from docopt import docopt, DocoptExit
from inspect import getdoc

# settings
_ssh_user = '0608156'
_ssh_ppky = 'c:/users/i0608156/.aysa/I0000001_rsa'

ENDPOINTS = {
    'development': {
        'host': 'scosta01.aysa.ad',
        'user': _ssh_user,
        'connect_kwargs': {
            'key_filename': _ssh_ppky
        }
    },
    'quality': {
        'host': 'scosta02.aysa.ad',
        'user': _ssh_user,
        'connect_kwargs': {
            'key_filename': _ssh_ppky
        }
    },
}

# objects
bindings = KeyBindings()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class BaseCommands:
    def __init__(self, endpoints, cnx_create=False, default='development',
                 **kwargs):
        self.__cnx = {}
        self.__endpoint = None
        self.__endpoints = endpoints
        self.__env = kwargs.pop('env', None)
        self.__options = kwargs

        if cnx_create is True:
            for endpoint in self.__endpoints.keys():
                self.get_cnx(endpoint)

        self.set_env(default)

    @property
    def env(self):
        return self.__env

    @property
    def endpoint(self):
        return self.__endpoint

    def set_env(self, value):
        value = str(value).lower()
        if value not in self.__endpoints:
            raise KeyError('El endpoint "{}" no es válido.'.format(value))
        self.__env = self.get_cnx(value)
        self.__endpoint = value
        log.info('endpoint (set): "%s"', value)

    def get_cnx(self, endpoint):
        try:
            cnx = self.__cnx[endpoint]
            log.info('endpoint (cache): "%s"', endpoint)
        except KeyError:
            log.debug('endpoint (create): "%s"', endpoint)
            cnx = Connection(**self.__endpoints[endpoint])
            self.__cnx[endpoint] = cnx
        return cnx

    def get_yes(self, title=None, text=None, **kwargs):
        return kwargs.get('--yes', False) or \
               yes_no_dialog(title=title or 'ATENCIÓN!',
                             text=text or 'Desea continuar?')

    def get_doc(self, obj=None):
        return ' \n{}\n\n '.format(getdoc(obj or self))

    def parse(self, line, *args, **kwargs):

        if not line:
            return

        values = line.lower().split()

        if 'help' in values:
            return self.help()

        if 'exit' in values:
            self.exit()

        cmd = values[0]
        arg = values[1:]

        log.debug('cmd (%s): %s', cmd, arg)

        if not hasattr(self, cmd):
            return self.help()

        hdr = getattr(self, cmd)
        doc = self.get_doc(hdr)

        try:
            opt = docopt(doc, arg, **kwargs)
            hdr(opt, *args, **kwargs)
        except DocoptExit:
            log.error(doc)

    def help(self, *args, **kwargs):
        print(self.get_doc())

    def exit(self, code=0):
        sys.exit(code)


class Commands(BaseCommands):
    """
    AySA Command Line Interface.

    Usage: COMMAND [ARGS...]

    Comandos Disponibles:
        deploy     Inicia el proceso de despliegue.
        down       Detiene y elimina todos servicios.
        prune      Detiene y elimina todos servicios, omo así también
                   las imágenes y volúmenes aosicados.
        restart    Reinicia uno o más servicios.
        services   Lista los servicios disponibles.
        set        Estable el entorno a utilizar [default: development].
        start      Inicia uno o más servicios.
        stop       Detiene uno o más servicios.
        up         Crea e inicia uno o más servicios.

    Comando Generales:
        help       Muestra la ayuda del programa.
        exit       Sale del programa.
    """
    def deploy(self, options, **kwargs):
        """
        usage: deploy [options] [ARGS...]

        Argumentos Opcionales:
            -y, --yes    Responde "SI" a todas las preguntas.
        """
        if self.get_yes(**options):
            log.info(options)

    def set(self, options, **kwargs):
        """
        usage: set ENVIRONMENT
        """
        self.set_env(options['ENVIRONMENT'])


def main():
    # argmuents
    argv = sys.argv[1:]

    # logger
    fmt = logging.Formatter('[%(levelname)s] %(message)s')
    hdr = logging.StreamHandler()
    hdr.setFormatter(fmt)
    hdr.setLevel(logging.ERROR if '-D' not in argv else logging.DEBUG)
    log.addHandler(hdr)

    # session
    session = PromptSession(
        completer=WordCompleter([
            'help',
            'exit',
            'deploy',
            'set',
            'development',
            'quality'
        ]),
        history=FileHistory('c:/users/i0608156/.aysa/history'),
        auto_suggest=AutoSuggestFromHistory(),
        mouse_support=True,
        key_bindings=bindings
    )

    # dispatcher
    commands = Commands(ENDPOINTS)

    # styles
    style = Style.from_dict({
        '': '#FFFFFF',
        'environ': '#006600'
    })

    while 1:
        try:
            ps1 = [
                ('class:environ', '({}) '.format(commands.endpoint)),
                ('class:', '> ')
            ]
            commands.parse(session.prompt(ps1, style=style))
        except KeyboardInterrupt:
            continue
        except EOFError:
            break


if __name__ == '__main__':
    main()
