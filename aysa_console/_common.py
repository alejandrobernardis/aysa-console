# Author: Alejandro M. BERNARDIS
# Email alejandro.bernardis at gmail.com
# Created: 2019/11/05 07:22

import sys
import json
from inspect import getdoc
from functools import partialmethod
from docopt import docopt, DocoptExit
from pathlib import Path
from tomlkit import api
from prompt_toolkit.output import get_default_output


class DotDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self

    def __getattribute__(self, item):
        value = super().__getattribute__(item)
        if isinstance(value, dict):
            return DotDict(**value)
        return value


class EnvFile:
    def __init__(self, filename=None):
        self.__filename = None
        self.__old_filename = None
        self.__document = None
        self.set_filename(filename)

    def load(self, filename=None):
        if filename is not None:
            self.set_filename(filename)
        with self.filename.open('r', encoding='uft-8') as f:
            self.__document = api.parse(f.read())
        return self

    def save(self, document=None, filename=None):
        if filename is not None:
            self.set_filename(filename)
        value = api.dumps(document or self.__document)
        with self.filename.open('w') as f:
            f.write(value)
        return self.load()

    @property
    def filename(self):
        return self.__filename

    @property
    def document(self):
        return self.__document

    @property
    def dotted(self):
        return DotDict(**self.__document)

    def set_filename(self, value):
        if value is None:
            value = '~/.aysa/config.toml'
        if not isinstance(value, Path):
            value = Path(str(value))
        if self.__filename is not None:
            self.__old_filename = self.__filename
        self.__filename = value.expanduser()
        return self.__filename


def load_env(filename=None):
    return EnvFile(filename).load()


def raw_input(self, message=None, recursive=False, default=None, values=None,
              cast=None):
    if not isinstance(message, str):
        message = 'Por favor, ingrese un valor'
    else:
        message = message.strip()
    if not message.endswith(':'):
        message += ': '
    if values or default:
        if not values:
            values = default
        message = '{} [{}]: '.format(message[:-2], str(values))
    value = input(message).strip()
    if default is not None and not value:
        return default
    if cast is not None:
        try:
            value = cast(value)
        except Exception:
            if recursive is True:
                return self.input(message, recursive, default, cast)
            raise TypeError('Valor incorrecto: ' + value)
    return value


def is_yes(value):
    return str(value).lower() in ('true', 'yes', 'si', 'y', 's', '1')


def docstring(obj, tmpl=' \n{}\n\n'):
    if not isinstance(obj, str):
        obj = getdoc(obj)
    if tmpl is not None:
        return tmpl.format(obj)
    return obj


def docoptions(obj, *args, **kwargs):
    obj = docstring(obj)
    try:
        return docopt(obj, *args, **kwargs), obj
    except DocoptExit:
        raise CommandError(obj)


class Printer:
    def __init__(self, output=None):
        if output is None:
            try:
                output = get_default_output()
            except:
                output = sys.stdout
        if not all([hasattr(output, 'write'), hasattr(output, 'flush')]):
            raise TypeError('El objeto "%s" no posee los métodos '
                            '"write" y/o "flush".' % output)
        self.__output = output

    def _parse(self, *message, sep=' ', end='\n', endx=None, tab=0, tmpl=None,
               prefix='', subffix='', **kwargs):
        message = tmpl.format(*message) if tmpl is not None \
            else sep.join([str(x) for x in message])
        message = prefix + message + subffix
        if endx is not None:
            end = (end or '\n') * max(1, endx or 1)
        if end and not message.endswith(end):
            message += end
        for x in ('lower', 'upper', 'title', 'capitalize', 'swapcase'):
            if kwargs.get(x, False) is True:
                message = getattr(message, x)()
                break
        return (' ' * tab) + message

    def write(self, *message, **kwargs):
        value = self._parse(*message, **kwargs)
        value and self.__output.write(value)

    def flush(self, *message, **kwargs):
        if message:
            self.write(*message, **kwargs)
        self.__output.flush()

    def done(self):
        self.flush('Done')

    def blank(self):
        self.flush('')

    def rule(self, size=1, char='-'):
        self.flush(char * max(1, size or 1))

    def header(self, *message, **kwargs):
        self.blank()
        self.write(*message, **kwargs)
        self.rule(2)

    def footer(self, *message, **kwargs):
        self.blank()
        self.rule(2)
        self.write(*message, **kwargs)
        self.blank()

    def json(self, value, indent=2):
        raw = json.dumps(value, indent=indent, default=str) \
            if isinstance(value, dict) else '-'
        self.__output.write(raw + '\n')
        self.flush()

    error = partialmethod(write, subffix='!')
    question = partialmethod(write, subffix='?')
    bullet = partialmethod(write, prefix='> ')


class CommandError(Exception):
    def __init__(self, command, message):
        self.command = command
        super().__init__("%s: %s" % (command, message))


class NoSuchCommandError(Exception):
    pass


class CommandExit(DocoptExit):
    def __init__(self, docstring):
        super().__init__(docstring)