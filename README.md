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

[endpoints.quality]
host = "scosta02.aysa.ad"
port = 22
username = "0x00"
private_key = "~/.aysa/0x00_rsa.ppk"
remote_path = "/data/deploy/dashbaord"
force_tag = "dev"
source_tag = "rc"
target_tag = "latest"

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
    rm          Elimina uno o más imágenes.
    services    Lista los servicios disponibles.
    start       Inicia uno o más servicios.
    stop        Detiene uno o más servicios.
    up          Crea e inicia uno o más servicios.

Comandos Generales:
    help        Muestra la ayuda del programa.
    exit        Sale del programa. (Ctrl + D)

>> Consulte `COMAND (-h|--help|help)` para obtener más información 
       sobre un comando específico. 
```