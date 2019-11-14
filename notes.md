# Notes

## Screens

![screen](/assets/01.help.PNG)

![screen](/assets/02.autocomplete.PNG)

![screen](/assets/03.comando-help.PNG)

![screen](/assets/04.prune-confirm.PNG)

![screen](/assets/05.prune.PNG)

![screen](/assets/07.deploy.PNG)

## Configuración de la Consola

```bash
AySA Command Line Interface

usage:
    aysax [-D|-V][options] [development|quality]

Argumentos Opcionales:
    -h, --help                              Muestra la `ayuda` del programa.
    -v, --version                           Muestra la `versión` del programa.
    -D, --debug                             Activa el modo `debug`.
    -V, --verbose                           Activa el modo `verbose`.
    -O filename, --debug-output=filename    Archivo de salida para el modo `debug` o `verbose`.
    -E filename, --env=filename             Archivo de configuración del entorno (`.toml`),
                                            el mismo será buscado en la siguiente ruta
                                            de no ser definido: `~/.aysa/config.toml`.
```

### Definición de los Entornos

```bash
> aysax -E ./config.toml
```

### Debug Output

```bash
# debug
> aysax -D -O ./logs.log

# verbose (info)
> aysax -V -O ./logs.log
```

### Selección del Entorno

```bash
> aysax quality
```

## Help

```bash
(development) > help

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
    rmi         Elimina uno o más imágenes.
    services    Lista los servicios disponibles.
    start       Inicia uno o más servicios.
    stop        Detiene uno o más servicios.
    up          Crea e inicia uno o más servicios.

Comandos Generales:
    help        Muestra la ayuda del programa.
    version     Muestra la versión del programa.
    exit        Sale del programa. (Ctrl + D)

>> Consulte `COMMAND (-h|--help|help)` para obtener
   más información sobre un comando específico.
```

### Comando: `deploy`

```bash
(development) > deploy --help

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
```

#### Cómo lo hace...

```python

# confirma la acción
if self.yes_dialog(**options):
    # se posiciona en el directorio de trabajo
    with self.cwd:
        # verifica la sesión contra la registry
        self._raise_for_login()
        # obtiene los servicios
        services = self._services(options)
        # obtiene las imágenes
        images = self._images(services)
        # elimina los contenedores
        if services:
            x = ' '.join(services)
            self.run('docker-compose rm -fsv {}'.format(x))
        # elimina las imágenes
        if images:
            x = ' '.join(images)
            self.run('docker rmi -f {}'.format(x))
        # purga los volumenes
        self.run('docker volume prune -f')
        # actualiza el repositorio en caso de ser necesario
        if kwargs.pop('--update', False) is True:
            self.run('git reset --hard')
            self.run('git pull --rebase --stat')
        # inicia la creación de los contenedores.
        self.run('docker-compose up -d --remove-orphans')
```

### Comando: `make`

```bash
(development) > make --help

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
```

## Estructura del proyecto:

### /aysa_console

Código fuente del proyecto, el mismo representa un `package` de python.

### /aysa_console/__init__.py

Es el responsable de inicializar la consola interactiva, en el mismo se cargan los datos del entorno y la configuración de los comandos.

### /aysa_console/\_docker.py

`Api` de conexión para la `registry` de desarrollo. Los objetos `Api`, `Image` y `Manifest` permiten interactuar con las imágenes:

* `Api` establece la conexión contra la `registry` y habilita los métodos necesarios para interactuar con el catálogo, tags y manifiestos.
* `Image` descompone un string con la información la imagen y retorna la partes de la misma.
* `Manifest` permite interactuar con el manifiesto mediante una api definida.

#### Formato del string para el objeto `Image`

```python
"""
{url:port}/{namespace}/{repository}:{tag}

Ex: 127.0.0.1:5000/dash/web:dev
    127.0.0.1/dash/ad:latest
    localhost.local:5000/dash/rp:rc
"""
i = Image('localhost.local:5000/dash/rp:rc')
print(i.registry)
# ...
# localhost.local:5000
i = get_parts('localhost.local:5000/dash/rp:rc')
print(i)
# ...
# {'registry': 'localhost.local:5000/', 'repository': 'dash/rp', 'namespace': 'dash', 'image': 'rp', 'tag': 'rc'}
```

### /aysa_console/commands.py

El objeto `Commands` establece los comandos permitidos dentro de la consola interactiva. Aquí se respalada la lógica detrás de cada comando, lo métodos compartido se definen en el objeto `BaseCommand`.

### /aysa_console/completer.py

Define las opciones para el `autocompletado` de los comandos.

## Entorno

La configuración del entorno seleccionado se obtiene mediante la propiedad `env` (solo lectura).

```python
print(self.env)
...
{
  "force_tag": "",
  "host": "scosta01.aysa.ad",
  "port": 22,
  "private_key": "~/.aysa/0x00_rsa.ppk",
  "remote_path": "/data/deploy/dashbaord",
  "source_tag": "dev",
  "target_tag": "rc",
  "username": "0x00"
}
```

y el nombre del entorno se obtiene mediante la propiedad `endpoint` (solo lectura).

```python
print(self.endpoint)
...
development
```

## Impresión en pantalla

Para la impresión de mensajes, se contruyó un objeto denominado `Printe`, el cual provee una `api` para lo diferente formatos de impresión.

* done
* blank
* rule
* header
* footer
* json
* error
* question
* bullet

## Ejecución remota

Los comandos relacionados con `docker-compose` se deben ejecutar dentro del directorio (`/data/deploy/dashboard`) donde se encuentran los archivos `docker-compose.yml` y `.env`.

### Ejemplo (bash):

```bash
> cd /data/deploy/dashboard
> docker-compose up -d
...
```

### Ejemplo (python):

```python
with self.cwd:
    self.run('docker-compose up -d')
...
```


