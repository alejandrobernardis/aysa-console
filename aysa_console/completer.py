# Author: Alejandro M. BERNARDIS
# Email alejandro.bernardis at gmail.com
# Created: 2019/11/05 07:22

from shlex import split
from prompt_toolkit.completion import Completer, Completion

ARGUMENTS = [
    ('-h', '--help'),
    ('-u', '--update'),
    ('-y', '--yes')
]

DEVELOPMENT = 'development'
QUALITY = 'quality'
ENVIRONS = (DEVELOPMENT, QUALITY)


class CommandCompleter(Completer):
    def __init__(self):
        self.commands = {

            # general
            'config': None,
            'help': None,
            'exit': None,

            # deployment
            'deploy': ['--help', '--update', '--yes'],
            'down': ['--help', '--yes'],
            'images': ['--help'],
            'make': ['--help', '--yes'],
            'prune': ['--help', '--yes'],
            'restart': ['--help', '--yes'],
            'select': ['--help', 'development', 'quality'],
            'services': ['--help'],
            'start': ['--help', '--yes'],
            'stop': ['--help', '--yes'],
            'up': ['--help', '--yes']

        }

    def get_completions(self, document, complete_event):
        line = document.text_before_cursor
        if not line or line.count(' ') == 0:
            complete_list = self.commands
        else:
            value = self.commands.get(split(line)[0], None)
            if value is not None:
                complete_list = value
            else:
                complete_list = []
        word = document.get_word_before_cursor()
        for x in complete_list:
            if x.lower().startswith(word) and not x in line:
                yield Completion(x, -len(word))