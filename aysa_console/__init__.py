# Author: Alejandro M. BERNARDIS
# Email alejandro.bernardis at gmail.com
# Created: 2019/11/05 07:22
"""
AySA Command Line Interface

usage:
    aysax [options] [development|quality]

Argumentos Opcionales:
    -h, --help                     Muestra la `ayuda` del programa.
    -v, --version                  Muestra la `versión` del programa.
    -D, --debug                    Activa el modo `debug`.
    -V, --verbose                  Activa el modo `verbose`.
    -E filename, --env=filename    Archivo de configuración del entorno (`.toml`),
                                   el mismo será buscado en la siguiente ruta
                                   de no ser definido: `~/.aysa/config.toml`.
"""
import sys

# version
SEGMENT = 'pyChu'
VERSION = (2, 0, 0, SEGMENT, 0)

# doc
__title__ = 'aysa-console'
__summary__ = 'Consola interactiva para la administración remota de entornos.'
__uri__ = 'https://github.com/alejandrobernardis/aysa-console/'
__issues__ = 'https://github.com/alejandrobernardis/aysa-console/issues/'
__version__ = '.'.join([str(x) for x in VERSION])
__author__ = 'Alejandro M. BERNARDIS and individual contributors.'
__email__ = 'alejandro.bernardis@gmail.com'
__license__ = 'MTI License, Version 2.0'
__copyright__ = 'Copyright 2019-% {}'.format(__author__)


# dispatcher
def main():
    try:
        from prompt_toolkit import PromptSession
        from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
        from prompt_toolkit.key_binding import KeyBindings
        from prompt_toolkit.history import FileHistory
        from aysa_console._common import load_env
        from aysa_console.commands import Commands
        from aysa_console.completer import DEVELOPMENT, QUALITY, \
            CommandCompleter
        from pathlib import Path
        from docopt import docopt, DocoptExit

        opt = docopt(__doc__, version=__version__)
        env = load_env(opt.pop('--env', None))

        print('starting...', end='\r')

        session = PromptSession(
            completer=CommandCompleter(),
            history=FileHistory(str(Path('~/.aysax_history').expanduser())),
            auto_suggest=AutoSuggestFromHistory(),
            key_bindings=KeyBindings()
        )

        default = QUALITY if opt.get(QUALITY, False) else DEVELOPMENT
        commands = Commands(session, env, default, opt)

    except DocoptExit:
        sys.exit(__doc__)

    except FileNotFoundError:
        print('creating configuration file...', end='\r')

        import os
        import shutil

        filename = 'config.toml'
        user_path = Path('~/.aysa').expanduser()
        os.makedirs(str(user_path), exist_ok=True)

        tmpl_file = Path(__file__).parent.joinpath(filename)
        shutil.copyfile(str(tmpl_file), str(user_path.joinpath(filename)))

        sys.exit('\n[ATENCIÓN]: Por favor, debes editar el archivo "{}" para '
                 'definir correctamente los parámetros de conexión.\n'
                 .format(tmpl_file))

    except Exception as e:
        sys.exit(str(e))

    else:
        while 1:
            try:
                commands.prompt()
            except KeyboardInterrupt:
                continue
            except EOFError:
                break
            except Exception as e:
                commands.out(e)


if __name__ == '__main__':
    sys.exit(main())
