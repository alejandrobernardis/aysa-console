# Author: Alejandro M. BERNARDIS
# Email alejandro.bernardis at gmail.com
# Created: 2019/11/05 07:22

import shlex
from functools import partialmethod
from prompt_toolkit.completion import Completer, Completion

DEVELOPMENT = 'development'
QUALITY = 'quality'
ENVIRONS = (DEVELOPMENT, QUALITY)

OPT_HELP = '--help'
OPT_YES = '--yes'
OPT_UPDATE = '--update'
OPT_FORCE = '--force'
ARG_SERVICE = '<SERVICE>'
ARG_IMAGE = '<IMAGE>'


class CommandCompleter(Completer):
    def __init__(self):
        self._images = None
        self._services = None
        self._variables = None

        self.commands = {
            # general
            'help': None,
            'exit': None,
            # despliegue
            'deploy': [OPT_YES, OPT_UPDATE, ARG_SERVICE],
            'make': [OPT_YES, OPT_FORCE, ARG_IMAGE],
            'prune': [OPT_YES],
            'select': [DEVELOPMENT, QUALITY],
            # Contenedores
            'config': None,
            'down': [OPT_YES],
            'images': None,
            'ps': None,
            'restart': [OPT_YES, ARG_SERVICE],
            'rm': [OPT_YES, ARG_SERVICE],
            'services': None,
            'start': [OPT_YES, ARG_SERVICE],
            'stop': [OPT_YES, ARG_SERVICE],
            'up': [OPT_YES, ARG_SERVICE],
            # hidden
            '.set': [OPT_YES]
        }

    def __check_value(self, variable, values):
        value = values if values and isinstance(values, (set, list, tuple)) \
            else None
        if not isinstance(value, set):
            value = set(value)
        setattr(self, variable, value)

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
            except:
                cmd = None
                value = None
            if value is not None:
                if cmd == '.set' and self._variables:
                    if line_count == 1:
                        complete_list = self._variables
                else:
                    self._find_values(self._services, ARG_SERVICE, value)
                    self._find_values(self._images, ARG_IMAGE, value)
                    complete_list = value
        word = document.get_word_before_cursor()
        complete_list = sorted(complete_list)
        for x in complete_list:
            if x.lower().startswith(word) and x not in line:
                yield Completion(x, -len(word))

    def _find_values(self, variable, argument, value):
        if variable and argument in value:
            value.pop(-1)
            value += variable
        return value
