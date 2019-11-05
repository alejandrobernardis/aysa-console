# Author: Alejandro M. BERNARDIS
# Email alejandro.bernardis at gmail.com
# Created: 2019/11/05 07:22
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


def main():
    print(__doc__)


if __name__ == '__main__':
    main()
