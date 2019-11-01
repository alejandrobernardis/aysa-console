#!/usr/bin/env python
import sys
import logging
from fabric import Connection
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory
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
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Commands:
    """
    AySA Command Line Interface.

    Usage: COMMAND [ARGS...]

    Comandos Disponibles:
        exit      Termina el proceso.
        help      Muestra la ayuda.
        remote    Ejecuta comando de forma remota.
    """

    def __init__(self, endpoints, cnx_create=False, **kwargs):
        self.__cnx = {}
        self.__endpoints = endpoints
        self.__options = kwargs

        if cnx_create is True:
            for endpoint in self.__endpoints.keys():
                self._cnx(endpoint)

    def _cnx(self, endpoint):
        try:
            return self.__cnx[endpoint]
        except KeyError:
            log.debug('endpoint key: "%s"', endpoint)
            cnx = Connection(**self.__endpoints[endpoint])
            self.__cnx[endpoint] = cnx
            return cnx

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

        log.debug('cmd: %s, arg: %s', cmd, arg)

        if not hasattr(self, cmd):
            return self.help()

        hdr = getattr(self, cmd)
        doc = getdoc(hdr)

        try:
            opt = docopt(doc, arg, **kwargs)
            hdr(opt, *args, **kwargs)
        except DocoptExit:
            log.error(doc)

    def remote(self, options, *args, **kwargs):
        """
        Ejecuta comando de forma remota.

        Usage: remote [options] CMD [ARGS...]

        Opciones:
            -y, --yes    Responde "SI" a todas las preguntas.

        """
        print(options)

    def help(self):
        log.error(getdoc(Commands))

    def exit(self, code=0):
        sys.exit(code)


def main():
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
            'remote',
            'exit',
            'development',
            'quality'
        ]),
        history=FileHistory('c:/users/i0608156/.aysa/history'),
        mouse_support=True
    )

    # dispatcher
    commands = Commands(ENDPOINTS)

    while 1:
        try:
            value = session.prompt('> ')
        except KeyboardInterrupt:
            continue
        except EOFError:
            break
        else:
            commands.parse(value)


if __name__ == '__main__':
    main()
