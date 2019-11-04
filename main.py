#!/usr/bin/env python
"""
AySA Command Line Interface

usage:
    aysax [options] [development|quality]

Argumentos Opcionales:
    -h, --help                              Muestra la `ayuda` del programa.
    -v, --version                           Muestra la `versión` del programa.
    -D, --debug                             Activa el modo `debug`.
    -V, --verbose                           Activa el modo `verbose`.
    -O filename, --debug-output=filename    Archivo de salida para el modo `debug`.
    -E filename, --env=filename             Archivo de configuración del entorno (`.ini`),
                                            el mismo será buscado en la siguiente ruta
                                            de no ser definido: `~/.aysa/config.ini`.
"""

import sys
import logging
from fabric import Connection
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter, Completer, Completion
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.shortcuts import yes_no_dialog
from prompt_toolkit.styles import Style
from shlex import split
from docopt import docopt, DocoptExit
from inspect import getdoc
from pathlib import Path

bindings = KeyBindings()
log = logging.getLogger(__name__)

HOME = Path('~/.aysa').expanduser()

_ssh_user = '0608156'
_ssh_ppky = HOME.joinpath('I0000001_rsa')
_his_file = HOME.joinpath('history')

QUALITY = 'quality'
DEVELOPMENT = 'development'

ENDPOINTS = {
    DEVELOPMENT: {
        'host': 'scosta01.aysa.ad',
        'user': _ssh_user,
        'connect_kwargs': {
            'key_filename': _ssh_ppky
        }
    },
    QUALITY: {
        'host': 'scosta02.aysa.ad',
        'user': _ssh_user,
        'connect_kwargs': {
            'key_filename': _ssh_ppky
        }
    },
}


def docstring(obj):
    if not isinstance(obj, str):
        obj = getdoc(obj)
    return ' \n{}\n\n '.format(obj)


class BaseCommand:
    def __init__(self, endpoints, default=DEVELOPMENT, **kwargs):
        self.__cnx = {}
        self.__endpoint = None
        self.__endpoints = endpoints
        self.__options = kwargs
        self.set_enpoint(default)

    @property
    def env(self):
        return self.get_cnx(self.endpoint)

    @property
    def cd(self):
        return self.env.cd

    @property
    def run(self):
        return self.env.run

    @property
    def endpoint(self):
        return self.__endpoint

    def set_enpoint(self, value):
        value = str(value).lower()
        if value not in self.__endpoints:
            raise KeyError('El endpoint "{}" no es válido.'.format(value))
        self.__endpoint = value
        log.debug('endpoint (set): "%s"', value)

    def get_cnx(self, endpoint):
        try:
            cnx = self.__cnx[endpoint]
            log.debug('endpoint (cache): "%s"', endpoint)
        except KeyError:
            cnx = Connection(**self.__endpoints[endpoint])
            self.__cnx[endpoint] = cnx
            log.debug('endpoint (create): "%s"', endpoint)
        log.debug('endpoint (cnx): "%s"', cnx)
        return cnx

    def get_yes(self, title=None, text=None, **kwargs):
        log.debug('yes (dialog): "%s", kwargs: %s', text, kwargs)
        return kwargs.get('--yes', False) \
            or yes_no_dialog(title=title or 'ATENCIÓN!',
                             text=text or 'Desea continuar?')

    def docstring(self, obj=None):
        return docstring(obj or self)

    def help(self, *args, **kwargs):
        log.error(self.docstring())

    def exit(self, code=0):
        sys.exit(code)

    def parse(self, argv, *args, **kwargs):
        argv = split(argv)

        if not argv:
            log.debug('parse (argv): no arguments')
            return

        cmd = argv[0].lower()
        log.debug('parse (cmd): %s', cmd)

        if not hasattr(self, cmd) or cmd == 'help':
            log.debug('parse (%s): command not found or get help', cmd)
            return self.help()

        elif cmd == 'exit':
            log.debug('parse (exit)')
            self.exit()

        hdr = getattr(self, cmd)
        log.debug('parse (handler): %s', hdr)

        doc = self.docstring(hdr)

        try:
            if 'help' in argv:
                raise DocoptExit()

            hdr(docopt(doc, argv[1:]))

        except DocoptExit as e:
            log.debug('parse (DocoptExit): %s', e)
            log.error(doc)

        except SystemExit as e:
            log.debug('parse (SystemExit)')

        except Exception as e:
            log.debug('parse (Exception): %s', e)
            log.error(e)


class Commands(BaseCommand):
    """
    AySA Command Line Interface.

    Usage:
        COMMAND [ARGS...]

    Comandos:
        deploy      Inicia el proceso de despliegue.
        down        Detiene y elimina todos servicios.
        prune       Detiene y elimina todos servicios, omo así también
                    las imágenes y volúmenes aosicados.
        restart     Reinicia uno o más servicios.
        select      Selecciona el entorno de ejecución.
        services    Lista los servicios disponibles.
        start       Inicia uno o más servicios.
        stop        Detiene uno o más servicios.
        up          Crea e inicia uno o más servicios.

    Generales:
        help        Muestra la ayuda del programa.
        exit        Sale del programa. (Ctrl + D)
    """

    def select(self, options, **kwargs):
        """
        Selecciona el entorno de ejecución.

        usage: select ENDPOINT
        """
        self.set_enpoint(options['ENDPOINT'])

    def deploy(self, options, **kwargs):
        """
        Inicia el proceso de despliegue.

        usage: deploy [options] [ARGS...]

        Argumentos Opcionales:
            -y, --yes    Responde "SI" a todas las preguntas.
        """
        if self.get_yes(**options):
            log.error(options)


class CommandCompleter(Completer):
    def __init__(self):
        self.commands = {
            'help': None,
            'exit': None,
            'deploy': ['--yes', '--update'],
            'down': ['--yes'],
            'prune': None,
            'restart': ['--yes'],
            'select': ['development', 'quality'],
            'services': ['development', 'quality'],
            'start': ['--yes'],
            'stop': ['--yes'],
            'up': ['--yes', '--update'],
            'config': None,
            'registry': {
                'ls': ['--manifest', '--data', '--tags-filter'],
                'make': ['quality', 'production']
            }
        }

    def get_completions(self, document, complete_event):
        def matcher(xx, yy):
            return str(xx).lower().startswith(yy)

        word = document.get_word_before_cursor()
        line = document.text_before_cursor
        complete_list = self.commands

        try:
            log.debug('1: %s', document.text_before_cursor)
            log.debug('2: %s', document.get_word_before_cursor())
        except:
            pass

        # if not line or line.count(' ') == 0:
        #     complete_list = self.commands
        # else:
        #     key = split(line)[0]
        #     value = self.commands.get(key, None)
        #     if value is not None:
        #         complete_list = value
        #     else:
        #         complete_list = []

        for x in complete_list:
            if matcher(x, word):
                yield Completion(x, -len(word))


def setup_logger(options):
    if options.get('--debug', False):
        level = logging.DEBUG
    elif options.get('--verbose', False):
        level = logging.INFO
    else:
        level = logging.ERROR

    debug_output = options.get('--debug-output', None)

    if debug_output is not None:
        file_formatter = logging.Formatter('%(asctime)s %(levelname)s '
                                           '%(filename)s %(lineno)d '
                                           '%(message)s')
        file_handler = logging.FileHandler(debug_output, 'w')
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.DEBUG)
        log.addHandler(file_handler)
        level = logging.ERROR

    console_formatter = logging.Formatter('%(message)s')
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(level)
    log.addHandler(console_handler)
    log.setLevel(logging.DEBUG)


def main():
    # arguments
    doc = docstring(__doc__)

    try:
        opt = docopt(doc, version='v1.0.0.dev.0')
    except DocoptExit:
        raise SystemExit(doc)

    setup_logger(opt)
    log.debug('main (opt): %s', opt)
    log.debug('main (logger): %s', log)

    # session
    session = PromptSession(
        completer=CommandCompleter(),  # CommandCompleter(['help', 'exit']),
        history=FileHistory(_his_file),
        auto_suggest=AutoSuggestFromHistory(),
        key_bindings=bindings)
    log.debug('main (session): %s', session)

    # styles
    style = Style.from_dict({'': '#FFFFFF', 'environ': '#006600'})
    log.debug('main (style): %s', style)

    # dispatcher
    default = QUALITY if opt.get(QUALITY, False) else DEVELOPMENT
    commands = Commands(ENDPOINTS, default)
    log.debug('main (commands): %s', commands)

    # loop
    while 1:
        try:
            text = session.prompt([
                ('class:environ', '({}) '.format(commands.endpoint)),
                ('class:', '> ')
            ], style=style)
            commands.parse(text)

        except KeyboardInterrupt:
            log.debug('main (KeyboardInterrupt)')
            continue

        except EOFError:
            log.debug('main (EOFError): ctrl + D')
            break


if __name__ == '__main__':
    main()
