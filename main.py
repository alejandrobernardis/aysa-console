# #!/usr/bin/env python
# """
# AySA Command Line Interface
#
# usage:
#     aysax [options] [development|quality]
#
# Argumentos Opcionales:
#     -h, --help                              Muestra la `ayuda` del programa.
#     -v, --version                           Muestra la `versión` del programa.
#     -D, --debug                             Activa el modo `debug`.
#     -V, --verbose                           Activa el modo `verbose`.
#     -O filename, --debug-output=filename    Archivo de salida para el modo `debug`.
#     -E filename, --env=filename             Archivo de configuración del entorno (`.ini`),
#                                             el mismo será buscado en la siguiente ruta
#                                             de no ser definido: `~/.aysa/config.ini`.
# """
#
# import re
# import sys
# import json
# import logging
# from copy import deepcopy
# from fabric import Connection
# from prompt_toolkit import PromptSession
# from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
# from prompt_toolkit.completion import WordCompleter, Completer, Completion
# from prompt_toolkit.history import FileHistory
# from prompt_toolkit.key_binding import KeyBindings
# from prompt_toolkit.shortcuts import yes_no_dialog, input_dialog
# from prompt_toolkit.styles import Style
# from shlex import split
# from docopt import docopt, DocoptExit
# from inspect import getdoc
# from pathlib import Path
# from registry import Image, Api
#
# bindings = KeyBindings()
# log = logging.getLogger()
#
# rx_login = re.compile(r'Login\sSucceeded$', re.I)
# rx_service = re.compile(r'^[a-z](?:[\w_])+$', re.I)
# rx_image = re.compile(r'^[a-z](?:[\w_])+_\d{1,3}\s{2,}[a-z0-9](?:[\w.-]+)'
#                        r'(?::\d{1,5})?/[a-z0-9](?:[\w.-/])*\s{2,}'
#                        r'(?:[a-z][\w.-]*)\s', re.I)
#
# HOME = Path('~/.aysa').expanduser()
#
# _ssh_user = '0608156'
# _ssh_ppky = str(HOME.joinpath('I0000001_rsa'))
# _his_file = str(HOME.joinpath('history'))
#
# QUALITY = 'quality'
# DEVELOPMENT = 'development'
#
# ENDPOINTS = {
#     DEVELOPMENT: {
#         'host': 'scosta01.aysa.ad',
#         'user': _ssh_user,
#         'connect_kwargs': {
#             'key_filename': _ssh_ppky
#         }
#     },
#     QUALITY: {
#         'host': 'scosta02.aysa.ad',
#         'user': _ssh_user,
#         'connect_kwargs': {
#             'key_filename': _ssh_ppky
#         }
#     },
# }
#
# ENDPOINTS_REMOTE_PATH = '/data/deploy/dashboard'
#
# REGISTRY = {
#     'host': '10.17.65.128:5000',
#     'insecure': True,
#     'verify': False,
#     'user': 'dashboard',
#     'pasw': 'qwe123',
#     'namespace': 'dash',
# }
#
# def docstring(obj):
#     if not isinstance(obj, str):
#         obj = getdoc(obj)
#     return ' \n{}\n\n '.format(obj)
#
#
# class BaseCommand:
#     def __init__(self, endpoints, remote_path, registry, default=DEVELOPMENT,
#                  **kwargs):
#         self.__cnx = {}
#         self.__endpoint = None
#         self.__endpoints = endpoints
#         self.__endpoints_remote_path = remote_path
#         self.__registry = registry
#         self.__api = None
#         self.__options = kwargs
#         self.set_enpoint(default)
#
#     @property
#     def env(self):
#         return self.get_cnx(self.endpoint)
#
#     @property
#     def cwd(self):
#         return self.env.cd(self.__endpoints_remote_path)
#
#     @property
#     def run(self):
#         return self.env.run
#
#     @property
#     def endpoint(self):
#         return self.__endpoint
#
#     @property
#     def registry(self):
#         if self.__registry is None:
#             raise ValueError('La configuración de la "registry" '
#                              'no fue definida.')
#         if self.__api is None:
#             cfg = deepcopy(self.__registry)
#             cfg.pop('namespace', None)
#             credentials = '{}:{}'.format(cfg.pop('user', ''),
#                                          cfg.pop('pasw', ''))
#             self.__api = Api(credentials=credentials, **cfg)
#         return self.__api
#
#     def set_enpoint(self, value):
#         value = str(value).lower()
#         if value not in self.__endpoints:
#             raise KeyError('El endpoint "{}" no es válido.'.format(value))
#         self.__endpoint = value
#         log.debug('endpoint (set): "%s"', value)
#
#     def get_cnx(self, endpoint):
#         try:
#             cnx = self.__cnx[endpoint]
#             log.debug('endpoint (cache): "%s"', endpoint)
#         except KeyError:
#             cnx = Connection(**self.__endpoints[endpoint])
#             self.__cnx[endpoint] = cnx
#             log.debug('endpoint (create): "%s"', endpoint)
#         log.debug('endpoint (cnx): "%s"', cnx)
#         return cnx
#
#     def get_yes(self, title=None, text=None, **kwargs):
#         log.debug('yes (dialog): "%s", kwargs: %s', text, kwargs)
#         return kwargs.get('--yes', False) \
#             or yes_no_dialog(title=title or 'ATENCIÓN!',
#                              text=text or 'Desea continuar?')
#
#     def docstring(self, obj=None):
#         return docstring(obj or self)
#
#     # comandos generales
#
#     def config(self, *args, **kwargs):
#         print('\n[ENDPOINTS]\n--')
#         print(json.dumps(self.__endpoints, indent=4, default=str))
#         print('\n[REGISTRY]\n--')
#         print(json.dumps(REGISTRY, indent=4, default=str))
#         print('')
#
#     def help(self, *args, **kwargs):
#         log.error(self.docstring())
#
#     def exit(self, code=0):
#         sys.exit(code)
#
#     # ...
#
#     def parse(self, argv, *args, **kwargs):
#         argv = split(argv)
#         if not argv:
#             log.debug('parse (argv): no arguments')
#             return
#         cmd = argv[0].lower()
#         log.debug('parse (cmd): %s', cmd)
#         if not hasattr(self, cmd) or cmd == 'help':
#             log.debug('parse (%s): command not found or get help', cmd)
#             return self.help()
#         elif cmd == 'config':
#             log.debug('parse (config)')
#             return self.config()
#         elif cmd == 'exit':
#             log.debug('parse (exit)')
#             self.exit()
#         hdr = getattr(self, cmd)
#         log.debug('parse (handler): %s', hdr)
#         doc = self.docstring(hdr)
#         try:
#             if 'help' in argv:
#                 raise DocoptExit()
#             return hdr(docopt(doc, argv[1:]))
#         except DocoptExit as e:
#             log.debug('parse (DocoptExit): %s', e)
#             log.error(doc)
#         except SystemExit as e:
#             log.debug('parse (SystemExit)')
#         except Exception as e:
#             log.debug('parse (Exception): %s', e)
#             log.error(e)
#
#     def _list(self, cmd, filter_line=None, obj=None):
#         response = self.run(cmd, hide=True)
#         for line in response.stdout.splitlines():
#             if filter_line and not filter_line.match(line):
#                 continue
#             yield obj(line) if obj is not None else line
#
#
# class Commands(BaseCommand):
#     """
#     AySA Command Line Interface.
#
#     Usage:
#         COMMAND [ARGS...]
#
#     Coamndos de Entorno:
#         select      Selecciona el entorno de ejecución
#                     [default: development]
#
#     Comandos de Despliegue:
#         deploy      Inicia el proceso de despliegue.
#         down        Detiene y elimina todos servicios.
#         images      Lista las imágenes disponibles.
#         make        Crea las imágenes en la registry.
#         prune       Detiene y elimina todos los servicios,
#                     como así también las imágenes y volúmenes
#                     aosicados.
#         restart     Reinicia uno o más servicios.
#         services    Lista los servicios disponibles.
#         start       Inicia uno o más servicios.
#         stop        Detiene uno o más servicios.
#         up          Crea e inicia uno o más servicios.
#
#     Comandos Generales:
#         config      Muestra la configuración actual.
#         help        Muestra la ayuda del programa.
#         exit        Sale del programa. (Ctrl + D)
#     """
#
#     def _norm_service(self, value, sep='_'):
#         return sep.join(value.split(sep)[1:-1])
#
#     def _list_of_services(self, values=None, **kwargs):
#         for x in self._list("docker-compose ps --services", rx_service):
#             if values and x not in values:
#                 continue
#             yield x
#
#     def _list_of_images(self, values=None, **kwargs):
#         for x in self._list("docker-compose images", rx_image):
#             container, image, tag = x.split()[:3]
#             if values and self._norm_service(container) not in values:
#                 continue
#             yield '{}:{}'.format(image, tag)
#
#     def _services(self, values):
#         if isinstance(values, dict):
#             values = values['SERVICE']
#         return set([x for x in self._list_of_services(values)])
#
#     def _images(self, values):
#         if isinstance(values, dict):
#             values = values['IMAGE']
#         return set([x for x in self._list_of_images(values)])
#
#     def _login(self):
#         try:
#             cmd = 'docker login -u {user} -p {pasw} {host}'.format(**REGISTRY)
#             log.debug('login (host): %s, user: %s',
#                       REGISTRY['host'], REGISTRY['user'])
#             res = rx_login.match(self.run(cmd, hide=True).stdout) is not None
#             log.info('login (registry): %s', REGISTRY['host'])
#             return res
#
#         except Exception as e:
#             log.error('login (registry): %s', e)
#             return False
#
#     def _raise_for_login(self):
#         if not self._login():
#             raise ValueError('No se pudo establecer la sesión '
#                              'con la `registry`.')
#
#     def _change_state(self, state, options, **kwargs):
#         if self.get_yes(**options):
#             with self.cwd:
#                 self._raise_for_login()
#                 log.debug('%s (options): %s', state, options)
#                 services = self._services(options)
#                 self.run('docker-compose {} {}'
#                          .format(state, ' '.join(services)))
#                 log.info('%s (state): %s', state, services or 'all')
#
#     def select(self, options, **kwargs):
#         """
#         Selecciona el entorno de ejecución.
#
#         usage:
#             select ENDPOINT
#         """
#         self.set_enpoint(options['ENDPOINT'])
#
#     def services(self, options, **kwargs):
#         """
#         Lista los servicios disponibles.
#
#         usage:
#             services
#         """
#         with self.cwd:
#             for x in self._list_of_services():
#                 print(x)
#
#     def images(self, options, **kwargs):
#         """
#         Lista las imágenes disponibles.
#
#         usage:
#             images
#         """
#         with self.cwd:
#             for x in self._list_of_images():
#                 print(x)
#
#     def up(self, options, **kwargs):
#         """
#         Crea e inicia uno o más servicios.
#
#         usage:
#             up [options] [SERVICE...]
#
#         Argumentos Opcionales:
#             -y, --yes       Responde "SI" a todas las preguntas.
#         """
#         if self.get_yes(**options):
#             with self.cwd:
#                 self._raise_for_login()
#                 services = self._services(options)
#                 self.run('docker-compose up -d --remove-orphans {}'
#                          .format(' '.join(services)))
#                 log.info('up (services): %s', services or 'all')
#
#     def down(self, options, **kwargs):
#         """
#         Detiene y elimina todos servicios.
#
#         usage:
#             down [options]
#
#         Argumentos Opcionales:
#             -y, --yes       Responde "SI" a todas las preguntas.
#         """
#         if self.get_yes(**options):
#             with self.cwd:
#                 self._raise_for_login()
#                 self.run('docker-compose down -v --remove-orphans')
#                 log.info('down (services)')
#
#     def start(self, options, **kwargs):
#         """
#         Inicia uno o más servicios.
#
#         usage:
#             start [options] [SERVICE...]
#
#         Argumentos Opcionales:
#             -y, --yes       Responde "SI" a todas las preguntas.
#         """
#         self._change_state('start', options, **kwargs)
#
#     def stop(self, options, **kwargs):
#         """
#         Detiene uno o más servicios.
#
#         usage:
#             stop [options] [SERVICE...]
#
#         Argumentos Opcionales:
#             -y, --yes       Responde "SI" a todas las preguntas.
#         """
#         self._change_state('stop', options, **kwargs)
#
#     def restart(self, options, **kwargs):
#         """
#         Reinicia uno o más servicios.
#
#         usage:
#             restart [options] [SERVICE...]
#
#         Argumentos Opcionales:
#             -y, --yes       Responde "SI" a todas las preguntas.
#         """
#         self._change_state('restart', options, **kwargs)
#
#     def deploy(self, options, **kwargs):
#         """
#         Inicia el proceso de despliegue.
#
#         usage:
#             deploy [options] [SERVICE...]
#
#         Argumentos Opcionales:
#             -u, --update    Actualiza el repositorio con la
#             -y, --yes       Responde "SI" a todas las preguntas.
#         """
#         if self.get_yes(**options):
#             with self.cwd:
#                 self._raise_for_login()
#                 services = self._services(options)
#                 log.debug('deploy (services): %s', services)
#                 images = self._images(services)
#                 log.debug('deploy (images): %s', images)
#                 if services:
#                     x = ' '.join(services)
#                     self.run('docker-compose rm -fsv {}'.format(x))
#                     log.debug('deploy (remove): %s', services)
#                 if images:
#                     x = ' '.join(images)
#                     self.run('docker rmi -f {}'.format(x))
#                     log.debug('deploy (remove): %s', services)
#                 self.run('docker volume prune -f')
#                 log.debug('deploy (prune): volume')
#                 if kwargs.pop('--update', False) is True:
#                     self.run('git reset --hard')
#                     self.run('git pull --rebase --stat')
#                     log.debug('deploy (update): repo')
#                 self.run('docker-compose up -d --remove-orphans')
#                 log.info('deploy (up): %s', services)
#
#     def prune(self, options, **kwargs):
#         """
#         Inicia el proceso de despliegue.
#
#         usage:
#             prune [options]
#
#         Argumentos Opcionales:
#             -y, --yes       Responde "SI" a todas las preguntas.
#         """
#         message = 'Se procederá a "PURGAR" el entorno de "{0}", el ' \
#                   'siguiente proceso es "IRRÉVERSIBLE". Desdea continuar?\n' \
#                   'Por favor, escriba el nombre del entorno <{0}> para ' \
#                   'continuar:'.format(self.endpoint)
#         log.debug('prune (question): %s', message)
#         if options.get('--yes', False) is False:
#             answer = input_dialog('[PRECAUCIÓN]', message)
#             log.debug('prune (answer): %s', answer)
#             if answer.strip().lower() != self.endpoint:
#                 message = 'El nombre de entorno "{}" no concuerda con "{}"' \
#                           .format(answer, self.endpoint)
#                 log.debug('prune (error): %s', message)
#                 raise ValueError()
#         with self.cwd:
#             self.run('docker-compose down -v --rmi all --remove-orphans')
#             log.debug('prune (down)')
#             self.run('docker volume prune -f')
#             log.debug('prune (volume): prune')
#         log.info('prune (done)')
#
# class CommandCompleter(Completer):
#     def __init__(self):
#         # TODO (0608156): Mejorar la forma en la que se plantea el
#         #                 autocomplete.
#         self.commands = {
#             # general
#             'config': None,
#             'help': None,
#             'exit': None,
#
#             # deployment
#             'deploy': ['--help', '--update', '--yes'],
#             'down': ['--help', '--yes'],
#             'images': ['--help'],
#             'make': ['--help', '--yes'],
#             'prune': ['--help', '--yes'],
#             'restart': ['--help', '--yes'],
#             'select': ['--help', 'development', 'quality'],
#             'services': ['--help'],
#             'start': ['--help', '--yes'],
#             'stop': ['--help', '--yes'],
#             'up': ['--help', '--yes']
#         }
#
#     def get_completions(self, document, complete_event):
#         line = document.text_before_cursor
#         if not line or line.count(' ') == 0:
#             complete_list = self.commands
#         else:
#             value = self.commands.get(split(line)[0], None)
#             if value is not None:
#                 complete_list = value
#             else:
#                 complete_list = []
#         word = document.get_word_before_cursor()
#         for x in complete_list:
#             if x.lower().startswith(word) and not x in line:
#                 yield Completion(x, -len(word))
#
#
# def setup_logger(options):
#     if options.get('--debug', False):
#         level = logging.DEBUG
#     elif options.get('--verbose', False):
#         level = logging.INFO
#     else:
#         level = logging.ERROR
#
#     debug_output = options.get('--debug-output', None)
#
#     if debug_output is not None:
#         file_formatter = logging.Formatter('%(asctime)s %(levelname)s '
#                                            '%(filename)s %(lineno)d '
#                                            '%(message)s')
#         file_handler = logging.FileHandler(debug_output, 'w')
#         file_handler.setFormatter(file_formatter)
#         file_handler.setLevel(logging.DEBUG)
#         log.addHandler(file_handler)
#         level = logging.ERROR
#
#     console_formatter = logging.Formatter('%(message)s')
#     console_handler = logging.StreamHandler(sys.stderr)
#     console_handler.setFormatter(console_formatter)
#     console_handler.setLevel(level)
#     log.addHandler(console_handler)
#     log.setLevel(logging.DEBUG)
#
#
# def main():
#     # arguments
#     doc = docstring(__doc__)
#
#     try:
#         opt = docopt(doc, version='v1.0.0.dev.0')
#     except DocoptExit:
#         raise SystemExit(doc)
#
#     setup_logger(opt)
#     log.debug('main (opt): %s', opt)
#     log.debug('main (logger): %s', log)
#
#     # session
#     session = PromptSession(
#         completer=CommandCompleter(),  # CommandCompleter(['help', 'exit']),
#         history=FileHistory(_his_file),
#         auto_suggest=AutoSuggestFromHistory(),
#         key_bindings=bindings)
#     log.debug('main (session): %s', session)
#
#     # styles
#     style = Style.from_dict({'': '#FFFFFF', 'environ': '#006600'})
#     log.debug('main (style): %s', style)
#
#     # dispatcher
#     default = QUALITY if opt.get(QUALITY, False) else DEVELOPMENT
#     commands = Commands(ENDPOINTS, ENDPOINTS_REMOTE_PATH, REGISTRY, default)
#     log.debug('main (commands): %s', commands)
#
#     # loop
#     while 1:
#         try:
#             text = session.prompt([
#                 ('class:environ', '({}) '.format(commands.endpoint)),
#                 ('class:', '> ')
#             ], style=style)
#             commands.parse(text)
#
#         except KeyboardInterrupt:
#             log.debug('main (KeyboardInterrupt)')
#             continue
#
#         except EOFError:
#             log.debug('main (EOFError): ctrl + D')
#             break
#
#
# if __name__ == '__main__':
#     main()

from prompt_toolkit import prompt

if __name__ == '__main__':
    # System prompt.
    print('(1/3) If you press meta-! or esc-! at the following prompt, you can enter system commands.')
    answer = prompt('Give me some input: ', enable_system_prompt=True)
    print('You said: %s' % answer)

    # Enable suspend.
    print('(2/3) If you press Control-Z, the application will suspend.')
    answer = prompt('Give me some input: ', enable_suspend=True)
    print('You said: %s' % answer)

    # Enable open_in_editor
    print('(3/3) If you press Control-X Control-E, the prompt will open in $EDITOR.')
    answer = prompt('Give me some input: ', enable_open_in_editor=True)
    print('You said: %s' % answer)