# AySA Console

Consola interactiva para el despliegue de contendores.

## Instalación

Se requiere la versión de `python` **>=3.6**, en adelante.

### Con entorno virtual

```bash
# creamos el entorno virtual
> virtualenv --python=python37 aysax

# ingresamos al directorio del entorno
> cd aysax

# iniciamos el entorno
> source ./bin/activate

# instalamos dentro del entorno
> pip install https://github.com/alejandrobernardis/aysa-console/archive/master.zip

# test
> aysax -v
... 2.0.0.pyChu.0
```

### Sin entorno virtual

```bash
> pip install https://github.com/alejandrobernardis/aysa-console/archive/master.zip
```

### Desde el código fuente

```bash
# clonamos el repositorio
> git clone https://github.com/alejandrobernardis/aysa-console.git

# ingresamos al directorio del repositorio
> cd aysa-console

# instalamos
> python setup.py install
```

## Configuración

Al iniciar por primera vez la consola se creará un archivo (ubicación: `~/.aysa/config.toml`) para definir la configuración de los entornos.

```toml
[endpoints]
[endpoints.development]
host = "scosta01.aysa.ad"
port = 22
username = "0x00"
private_key = "~/.aysa/0x00_rsa.ppk"
remote_path = "/data/deploy/dashbaord"
force_tag = ""
source_tag = "dev"
target_tag = "rc"

...

[registry]
host = "sdwsta01.aysa.ad:5000"
insecure = 1
verify = 0
username = "dashboard"
password = "******"
namespace = "dash"
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

# Desarrollo

## Repositorio

```bash
# clonación
> git clone https://github.com/alejandrobernardis/aysa-console.git

# acceso al proyecto
> cd aysa-console
```

## Dependencias

Las dependencias se encuentran definidas en el archivo `Pipfile`, para la gestión de las mismas es requerido tener instalado `pipenv`, visitar [**site**](https://pipenv.readthedocs.io/).

### Pipenv

* Documentación: [**usage**](https://pipenv.readthedocs.io/en/latest/#pipenv-usage).
* Instalación: `pip install pipenv`.

#### Instalación de las dependencias:

```bash
> pipenv install
```

#### Iniciar el Shell:

```bash
> pipenv shell
```

#### Crear el archivo `requirements.txt`

```bash
> pipenv lock --requirements > requirements.txt
```

## Estructura del proyecto:

### /aysa_console

Código fuente del proyecto, el mismo representa un `package` de python.

### /aysa_console/__init__.py

Es el responsable de inicializar la consola interactiva, en el mismo se cargan los datos del environment y la configuración de los comandos.

### /aysa_console/\_docker.py

`Api` de conexión para la `registry` de desarrollo. Los objetos `Api`, `Image` y `Manifest` permiten interactuar con las imágenes:

* `Api` establece la conexión contra la `registry` y habilita los métodos necesarios para interactuar con el catálogo, tags y manifiestos.
* `Image` descompone un string con la información la imagen y retorna la partes de la misma.
* `Manifest` permite interactuar con el manifiesto mediante una api definida.

### /aysa_console/commands.py

El objeto `Commands` establece los comando permitidos dentro de la consola interactiva.

### /aysa_console/completer.py

Define las opciones para el autocompletado de los comandos.

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
