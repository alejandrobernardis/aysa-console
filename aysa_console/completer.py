# Author: Alejandro M. BERNARDIS
# Email alejandro.bernardis at gmail.com
# Created: 2019/11/05 07:22

import shlex
from functools import partialmethod
from prompt_toolkit.completion import Completer, Completion

DEVELOPMENT = 'development'
QUALITY = 'quality'
PRODUCTION = 'production'
ENVIRONS = (DEVELOPMENT, QUALITY)  # , PRODUCTION)

OPT_HELP = '--help'
OPT_YES = '--yes'
OPT_UPDATE = '--update'
OPT_FORCE = '--force'
ARG_ENVIRONS = '<ENVIRONS>'
ARG_IMAGE = '<IMAGE>'
ARG_SERVICE = '<SERVICE>'


class CommandCompleter(Completer):
    def __init__(self):
        self.commands = {
            # general
            'help': None,
            'version': None,
            'exit': None,
            # despliegue
            'deploy': [OPT_HELP, OPT_YES, OPT_UPDATE, ARG_SERVICE],
            'make': [OPT_HELP, OPT_YES, OPT_FORCE, ARG_IMAGE],
            'prune': [OPT_HELP, OPT_YES],
            'select': [OPT_HELP, ARG_ENVIRONS],
            # Contenedores
            'config': [OPT_HELP],
            'down': [OPT_HELP, OPT_YES],
            'images': [OPT_HELP],
            'ps': [OPT_HELP],
            'restart': [OPT_HELP, OPT_YES, ARG_SERVICE],
            'rm': [OPT_HELP, OPT_YES, ARG_SERVICE],
            'rmi': [OPT_HELP, OPT_YES, ARG_IMAGE],
            'services': [OPT_HELP],
            'start': [OPT_HELP, OPT_YES, ARG_SERVICE],
            'stop': [OPT_HELP, OPT_YES, ARG_SERVICE],
            'up': [OPT_HELP, OPT_YES, ARG_SERVICE],
        }
        self.hidden_commands = {
            '.save': [OPT_HELP, OPT_YES],
            '.set': [OPT_HELP, OPT_YES],
            '.show': [OPT_HELP, OPT_YES],
        }

    def __check_value(self, variable, values):
        print(variable, values)
        value = values if values and isinstance(values, (set, list, tuple)) \
            else None
        if not isinstance(value, set):
            value = set(value)
        setattr(self, variable, value)

    set_environs = partialmethod(__check_value, '_environs')
    set_images = partialmethod(__check_value, '_images')
    set_services = partialmethod(__check_value, '_services')
    set_variables = partialmethod(__check_value, '_variables')

    def get_completions(self, document, complete_event):
        line = document.text_before_cursor
        line_count = line.count(' ')
        if not line or line_count == 0:
            complete_list = self.commands
        else:
            complete_list = []
            try:
                cmd = shlex.split(line)[0]
                value = self.commands.get(cmd, None)
                value = self.hidden_commands.get(cmd, value)
            except Exception:
                cmd = None
                value = None
            if value is not None:
                variables = getattr(self, '_variables', None)
                if cmd in ('.set', '.save', '.show') and variables:
                    if line_count == 1:
                        complete_list = variables
                else:
                    self._find_values('_environs', ARG_ENVIRONS, value)
                    self._find_values('_images', ARG_IMAGE, value)
                    self._find_values('_services', ARG_SERVICE, value)
                    complete_list = value
        word = document.get_word_before_cursor(WORD=True)
        complete_list = sorted(complete_list)
        for x in complete_list:
            if x.lower().startswith(word) and x not in line:
                yield Completion(x, -len(word))

    def _find_values(self, variable, argument, value):
        if argument in value:
            value.pop(-1)
            value += getattr(self, variable, None) or []
        return value
