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
