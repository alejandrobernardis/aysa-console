# Author: Alejandro M. BERNARDIS
# Email alejandro.bernardis at gmail.com
# Created: 2019/11/05 07:22

import re
import sys
import shlex
import logging
import tomlkit.api as tomlkit
from pathlib import Path
from docopt import DocoptExit
from dotted.collection import DottedDict
from aysa_console._common import docstring, docoptions, CommandExit, \
    NoSuchCommandError, Printer, Counter, flatten
from aysa_console._docker import Api, Image
from aysa_console.completer import DEVELOPMENT
from aysa_console._custom import input_dialog, yes_no_dialog
from prompt_toolkit.styles import Style
from fabric import Connection

log = logging.getLogger(__name__)
total = Counter('Total')
rx_login = re.compile(r'Login\sSucceeded$', re.I)
rx_service = re.compile(r'^[a-z](?:[\w_])+$', re.I)
rx_image = re.compile(r'^[a-z](?:[\w_])+_\d{1,3}\s{2,}[a-z0-9](?:[\w.-]+)'
                      r'(?::\d{1,5})?/[a-z0-9](?:[\w.-/])*\s{2,}'
                      r'(?:[a-z][\w.-]*)\s', re.I)


class BaseCommand:
    def __init__(self, session, environment, default=DEVELOPMENT,
                 options=None, printer=None, **kwargs):
        # env
        self.__cnx = {}
        self.__api = None
        self.__endpoint = None
        self.__session_style = kwargs.pop('style', None)

        if options is not None:
            self.set_logger(options)

        # settings
        self.__session = session
        self.__env = environment
        self.__environment = environment.document
        self.__printer = printer or Printer()
        self.set_endpoint(default)

        # fix
        sys.excepthook = self._except_hook

    @property
    def session(self):
        return self.__session

    @property
    def session_style(self):
        if self.__session_style is None:
            self.__session_style = Style.from_dict({
                '': '#ffffff', 'env': '#00ff00 bold'
            })
        return self.__session_style

    @property
    def environment(self):
        if not isinstance(self.__environment, DottedDict):
            self.__environment = DottedDict(self.__environment)
        return self.__environment

    @property
    def endpoint(self):
        return self.__endpoint

    @property
    def endpoints(self):
        return self.environment['endpoints']

    @property
    def registry(self):
        return self.environment['registry']

    @property
    def env(self):
        return self.endpoints[self.endpoint]

    @property
    def cwd(self):
        value = '' if self.env.username == '0x00' else self.env.remote_path
        return self.cnx.cd(value)

    @property
    def run(self):
        return self.cnx.run

    @property
    def out(self):
        return self.__printer

    def get_docstring(self, value=None):
        return docstring(value or self)

    def set_endpoint(self, value):
        value = str(value).lower()
        if value == self.endpoint:
            return
        if value not in self.endpoints:
            raise KeyError('El endpoint "{}" no es válido.'.format(value))
        self.__endpoint = value
        self.__set_completer()

    def set_logger(self, options):
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

    def get_cnx(self, endpoint):
        try:
            cnx = self.__cnx[endpoint]
        except KeyError:
            env = self.endpoints[endpoint]
            if env.username.lower() == 'root':
                raise SystemExit('No se permite el uso del usaurio "ROOT."')
            ppk = Path(env.private_key).expanduser()
            cnx = Connection(env.host, env.username, int(env.port),
                             connect_kwargs={'key_filename': str(ppk)})
            self.__cnx[endpoint] = cnx
        return cnx

    @property
    def cnx(self):
        return self.get_cnx(self.endpoint)

    @property
    def api(self) -> Api:
        if self.__api is None:
            self.__api = Api(**self.registry)
        return self.__api

    def yes_dialog(self, title=None, text=None, **kwargs):
        return kwargs.get('--yes', False) \
            or yes_no_dialog(title or 'ATENCIÓN',
                             text or 'Desea continuar?')

    def confirm_dialog(self, text, value, title=None, **kwargs):
        if kwargs.get('--yes', False) is False:
            answer = input_dialog(title or '[PRECAUCIÓN]', text)
            return str(answer).strip().lower() == value, answer
        return True, None

    def prompt(self, **kwargs):
        text = self.session.prompt([
            ('class:env', '({})'.format(self.endpoint)),
            ('class:', ' > ')
        ], style=self.session_style, **kwargs)
        self.parse(text, **kwargs)

    def parse(self, argv, *args, **kwargs):
        try:
            argv = shlex.split(argv or '')

        except Exception:
            argv = None

        if not argv:
            return

        cmd = argv[0].lower()

        if cmd.startswith('.'):
            cmd = '_{}'.format(cmd[1:])

        if not hasattr(self, cmd):
            cmd = 'help'

        for x in ('help', 'exit'):
            if x == cmd:
                return getattr(self, cmd)()

        if cmd == '_cmd':
            return getattr(self, cmd)(argv, **kwargs)

        hdr = getattr(self, cmd)
        doc = self.get_docstring(hdr)

        try:
            if 'help' in argv[1:]:
                raise CommandExit(None)
            opt, _ = docoptions(doc, argv[1:])
            return hdr(opt, **kwargs)
        except (DocoptExit, CommandExit, NoSuchCommandError):
            self.out(doc)
        except (SystemExit, Exception) as e:
            self.out(e)

    def _list(self, cmd, filter_line=None, obj=None):
        response = self.run(cmd, hide=True)
        for line in response.stdout.splitlines():
            if filter_line and not filter_line.match(line):
                continue
            yield obj(line) if obj is not None else line

    def _list_of_services(self, values=None, **kwargs):
        cmd = 'docker-compose ps --services'
        for x in self._list(cmd, rx_service, **kwargs):
            if values and x not in values:
                continue
            yield x

    def _norm_service(self, value, sep='_'):
        return sep.join(value.split(sep)[1:-1])

    def _services(self, values=None, **kwargs):
        if isinstance(values, dict):
            values = values['SERVICE']
        return set([x for x in self._list_of_services(values, **kwargs)])

    def _list_of_images(self, values=None, **kwargs):
        for x in self._list("docker-compose images", rx_image, **kwargs):
            container, image, tag = x.split()[:3]
            if values and self._norm_service(container) not in values:
                continue
            yield '{}:{}'.format(image, tag)

    def _images(self, values=None, **kwargs):
        if isinstance(values, dict):
            values = values['IMAGE']
        return set([x for x in self._list_of_images(values, **kwargs)])

    def _change_state(self, state, options, **kwargs):
        if self.yes_dialog(**options):
            with self.cwd:
                services = ' '.join(self._services(options))
                self.run('docker-compose {} {}'.format(state, services))

    def _login(self, **kwargs):
        try:
            cmd = 'docker login -u {username} -p {password} {host}' \
                  .format(**self.registry)
            res = self.run(cmd, hide=True).stdout
            return rx_login.match(res) is not None
        except Exception:
            return False

    def _raise_for_login(self, **kwargs):
        if not self._login():
            raise ValueError('No se pudo establecer la sesión '
                             'con la `registry`.')

    def _fix_image_name(self, value, namespace=None):
        value = value.strip()
        namespace = namespace or self.registry.namespace or ''
        if namespace and not value.startswith(namespace):
            return '{}/{}'.format(namespace, value)
        return value

    def _fix_images_list(self, values, namespace=None):
        values = values.split(',') if isinstance(values, str) else values or []
        return [self._fix_image_name(x.strip(), namespace) for x in values]

    def _reload_env(self):
        try:
            self.__environment = self.__env.load().document
            self.__cnx.clear()
            self.__api = None
            self.set_endpoint(self.endpoint)
        except Exception as e:
            self.out(e)

    def _setvar_env(self, variable, value):
        if variable not in self.environment:
            raise KeyError('La variable "{}" no está soportada.'
                           .format(variable))
        if isinstance(self.environment[variable], (DottedDict, dict)):
            raise ValueError('La variable "{}" es un diccionario, por lo que '
                             'no está permitido modificarla.'.format(variable))
        self.environment[variable] = value or ''

    def _savevar_env(self, variable, value):
        if variable:
            self._setvar_env(variable, value)
        self.__env.save(tomlkit.item(self.environment.to_python()),
                        reload=False)
        self._reload_env()

    def _except_hook(self, exception, value, traceback):
        if exception not in (KeyboardInterrupt, EOFError):
            return self.out(exception.__name__, ':', value)
        raise exception

    def __set_completer(self):
        with self.cwd:
            self.out('loading completers...', end='\r')

            variables = set(flatten(self.environment, sep='.').keys())
            self.session.completer.set_variables(variables)

            try:
                images = [Image(x).image for x in self._list_of_images()]
                self.session.completer.set_images(images)
            except Exception:
                pass

            try:
                self.session.completer.set_services(self._services())
            except Exception:
                pass


class Commands(BaseCommand):
    """
    AySA Command Line Interface.

    Usage:
        COMMAND [ARGS...]

    Comandos Despliegue:
        deploy      Inicia el proceso de despliegue.
        make        Crea las imágenes en la registry.
        prune       Detiene y elimina todos los servicios,
                    como así también las imágenes y volúmenes
                    aosicados.
        select      Selecciona el entorno de ejecución
                    [default: development]

    Comandos Contenedores:
        config      Muestra la configuración del compose.
        down        Detiene y elimina todos servicios.
        images      Lista las imágenes disponibles.
        ps          Muestra los servicios desplegados.
        restart     Reinicia uno o más servicios.
        rm          Elimina uno o más servicios detenidos.
        rm          Elimina uno o más imágenes.
        services    Lista los servicios disponibles.
        start       Inicia uno o más servicios.
        stop        Detiene uno o más servicios.
        up          Crea e inicia uno o más servicios.

    Comandos Generales:
        help        Muestra la ayuda del programa.
        exit        Sale del programa. (Ctrl + D)

    >> Consulte `COMMAND (-h|--help|help)` para obtener
       más información sobre un comando específico.
    """

    # Generales

    def help(self, **kwargs):
        self.out(self.get_docstring())

    def exit(self, code=0, **kwargs):
        sys.exit(code)

    # Entorno

    def deploy(self, options, **kwargs):
        """
        Inicia el proceso de despliegue.

            1. Purgado:
                1. Detiene y elimina los servicios.
                2. Elimina las imágenes.
                3. Purga los volumenes.
                4. Actualiza el repositorio (opcional).

            2. Creación
                1. Crea e inicia los servicios.

        usage:
            deploy [options] [SERVICE...]

        Argumentos Opcionales:
            -y, --yes       Responde "SI" a todas las preguntas.
            -u, --update    Actualiza el repositorio de la
                            configuración del compose.
        """
        if self.yes_dialog(**options):
            with self.cwd:
                self._raise_for_login()
                services = self._services(options)
                images = self._images(services)
                if services:
                    x = ' '.join(services)
                    self.run('docker-compose rm -fsv {}'.format(x))
                if images:
                    x = ' '.join(images)
                    self.run('docker rmi -f {}'.format(x))
                self.run('docker volume prune -f')
                if kwargs.pop('--update', False) is True:
                    self.run('git reset --hard')
                    self.run('git pull --rebase --stat')
                self.run('docker-compose up -d --remove-orphans')

    def make(self, options, **kwargs):
        """
        Crea las imágenes en la registry para el siguiente entorno.

        ex:
            (development) > make
             dev -> rc
             ...

        En caso de requerirse las imágenes para el entorno sleccionado,
        se puede utilziar el argumento `--force`.

        Usage:
            make [options] [IMAGE...]

        Opciones:
            -y, --yes      Responde "SI" a todas las preguntas.
            -f, --force    Fuerza la creación de la imágenes
                           para el entorno actual.
        """
        if self.yes_dialog(**options):
            total.reset()
            images = self._fix_images_list(options['IMAGE'])
            if self.env.force_tag and options.pop('--force', False) is True:
                source_tag = self.env.force_tag
                target_tag = self.env.source_tag
            else:
                source_tag = self.env.source_tag
                target_tag = self.env.target_tag
            self.out(source_tag, '->', target_tag)
            for x in self.api.catalog(self.registry.namespace):
                if images and x not in images:
                    continue
                i = Image('{}:{}'.format(x, source_tag))
                try:
                    rollback = '{}-rollback'.format(i.tag)
                    self.api.put_tag(i.repository, i.tag, rollback)
                except Exception:
                    pass
                try:
                    self.api.put_tag(i.repository, i.tag, target_tag)
                    self.out.bullet(i.repository)
                    total.increment()
                except Exception as e:
                    self.out(i.repository, e)
            self.out.footer(total)

    def prune(self, options, **kwargs):
        """
        Detiene y elimina todos los servicios, como así también
        las imágenes y volúmenes aosicados.

        Usage:
            prune [options]

        Opciones:
            -y, --yes    Responde "SI" a todas las preguntas.
        """
        message = 'Se procederá a "PURGAR" el entorno de "{0}", el ' \
                  'siguiente proceso es "IRRÉVERSIBLE". Desdea continuar?\n' \
                  'Por favor, escriba el nombre del entorno <{0}> para ' \
                  'continuar:'.format(self.endpoint)
        result, answer = self.confirm_dialog(message, self.endpoint)
        if result is False and answer is not None:
            message = 'El nombre de entorno "{}" no concuerda con "{}"' \
                      .format(answer, self.endpoint)
            raise ValueError(message)
        elif answer is None:
            return
        with self.cwd:
            self.run('docker-compose down -v --rmi all --remove-orphans')
            self.run('docker volume prune -f')

    def select(self, options, **kwargs):
        """
        Selecciona el entorno de ejecución.

        usage:
            select ENDPOINT
        """
        self.set_endpoint(options['ENDPOINT'])

    # Despliegue

    def config(self, options, **kwargs):
        """
        Muestra la configuración del compose.

        usage:
            config
        """
        with self.cwd:
            self.run('docker-compose config --resolve-image-digests')

    def down(self, options, **kwargs):
        """
        Detiene y elimina todos servicios.

        Usage:
            down [options]

        Opciones:
            -y, --yes    Responde "SI" a todas las preguntas.
        """
        if self.yes_dialog(**options):
            with self.cwd:
                self.run('docker-compose down -v --remove-orphans')

    def images(self, options, **kwargs):
        """
        Lista las imágenes disponibles.

        usage:
            images
        """
        total.reset()
        with self.cwd:
            for x in self._list_of_images():
                self.out.bullet(x)
                total.increment()
        self.out.footer(total)

    def ps(self, options, **kwargs):
        """
        Muestra los servicios desplegados.

        Usage:
            ps
        """
        with self.cwd:
            self.run('docker-compose ps')

    def restart(self, options, **kwargs):
        """
        Reinicia uno o más servicios.

        usage:
            restart [options] SERVICE [SERVICE...]

        Opciones:
            -y, --yes    Responde "SI" a todas las preguntas.
        """
        self._change_state('restart', options, **kwargs)

    def rm(self, options, **kwargs):
        """
        Elimina uno o más servicios.

        usage:
            rm [options] SERVICE [SERVICE...]

        Opciones:
            -y, --yes    Responde "SI" a todas las preguntas.
        """
        if self.yes_dialog(**options):
            with self.cwd:
                services = ' '.join(self._services(options))
                self.run('docker-compose rm -fsv {}'.format(services))

    def rmi(self, options, **kwargs):
        """
        Elimina uno o más imágenes.

        usage:
            rmi [options] IMAGE [IMAGE...]

        Opciones:
            -y, --yes    Responde "SI" a todas las preguntas.
        """
        if self.yes_dialog(**options):
            with self.cwd:
                images = ' '.join(self._images(options))
                self.run('docker rmi -f {}'.format(images))

    def services(self, options, **kwargs):
        """
        Lista los servicios disponibles.

        usage:
            services
        """
        total.reset()
        with self.cwd:
            for x in self._list_of_services():
                self.out.bullet(x)
                total.increment()
        self.out.footer(total)

    def start(self, options, **kwargs):
        """
        Inicia uno o más servicios.

        usage:
            start [options] SERVICE [SERVICE...]

        Opciones:
            -y, --yes    Responde "SI" a todas las preguntas.
        """
        self._change_state('start', options, **kwargs)

    def stop(self, options, **kwargs):
        """
        Detiene uno o más servicios.

        usage:
            stop [options] SERVICE [SERVICE...]

        Opciones:
            -y, --yes    Responde "SI" a todas las preguntas.
        """
        self._change_state('stop', options, **kwargs)

    def up(self, options, **kwargs):
        """
        Crea e inicia uno o más servicios.

        usage:
            up [options] SERVICE [SERVICE...]

        Opciones:
            -y, --yes    Responde "SI" a todas las preguntas.
        """
        if self.yes_dialog(**options):
            with self.cwd:
                self._raise_for_login()
                services = ' '.join(self._services(options))
                self.run('docker-compose up -d --remove-orphans {}'
                         .format(services))

    # hiden

    def _reload(self, options, **kwargs):
        """
        Recarga la configuración del entorno.

        usage: .reload
        """
        self._reload_env()

    def _save(self, options, **kwargs):
        """
        Actualiza el valor de la variable y
        guarda el documento en el archivo
        de configuración.

        En caso de no definirse una variable,
        guarda el documento completo.

        usage: .save [VARIABLE [VALUE]]
        """
        self._savevar_env(options['VARIABLE'], options['VALUE'])

    def _set(self, options, **kwargs):
        """
        Actualiza el valor de la variable.

        usage: .set VARIABLE [VALUE]
        """
        self._setvar_env(options['VARIABLE'], options['VALUE'])

    def _show(self, options, **kwargs):
        """
        Muestra la configuración del entorno.

        usage: .show [VARIABLE]
        """
        value = options['VARIABLE']
        value = self.environment if not value else self.environment[value]
        if isinstance(value, (DottedDict, dict)):
            if hasattr(value, 'to_python'):
                value = value.to_python()
            self.out.json(value)
        else:
            self.out(value)

    # OJO!

    def _cmd(self, options, **kwargs):
        """
        Ejecuta comando de forma remota.

        usage: .cmd [ARGS...]
        """
        try:
            with self.cwd:
                if not options:
                    return
                cmd = options[1]
                if cmd.replace('-', '') == 'help':
                    self.out(self.get_docstring(self._cmd))
                elif cmd in ('docker', 'docker-compose', 'git'):
                    self.run(' '.join(options[1:]))
                else:
                    self.out('[NO SEAS PICARÓN] NO permitido ->', cmd)
        except Exception as e:
            self.out(e)
