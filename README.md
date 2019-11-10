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

Al iniciar por primera vez la consola, se creará un archivo (ubicación: `~/.aysa/config.toml`) para definir la configuración de los entornos. 

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