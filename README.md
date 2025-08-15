# Máster UCM - TFM Grupo 4

Este repositorio contiene el código fuente para el Trabajo de Fin de Máster (TFM) del Grupo 4.

---

## Requisitos previos

* Antes de instalar el repositorio, se recomienda tener instalado `Git Large File Storage (LFS)`. Dado que trabajaremos con Chroma DB, y que esta base de datos vectorial puede persisitir fichero `*.bin` de más de 100MB (tamaño soportado por git sin requerir LFS). Para instalar esta extensión, simplemente alcanza con ejecutar el siguiente comando

    ```bash
    git lfs install
    ```

    En caso de requerir más información sobre esta extensión, puede hacerlo consultando [el siguiente enlace](https://git-lfs.com/).

## Inicialización del Repositorio

Sigue estos pasos para configurar tu entorno de desarrollo y comenzar a trabajar en el proyecto:

1. Clonar el Repositorio
    Primero, clona el repositorio a tu máquina local usando Git:

    ```bash
    git clone https://github.com/tu-usuario/ucm-tfm-grupo-4.git
    cd ucm-tfm-grupo-4
    ```

    Asegúrate de reemplazar `https://github.com/tu-usuario/ucm-tfm-grupo-4.git` con la URL real de tu repositorio.

2. Actualizar `pip`
    Es una buena práctica asegurarse de que `pip` esté actualizado:

    ```bash
    pip install --upgrade pip
    ```

3. Instalar `uv`
    Este proyecto utiliza `uv` para la gestión de dependencias, que es una herramienta moderna y rápida. Instálalo globalmente:

    ```bash
    pip install uv
    ```

4. Crear el Entorno Virtual
    `uv` creará un entorno virtual y lo activará automáticamente en la ubicación por defecto (`.venv`):

    ```bash
    uv venv
    ```

    Si deseas especificar una ruta diferente para tu entorno virtual, puedes hacerlo con:

    ```bash
    uv venv /ruta/a/tu/entorno
    ```

5. Sincronizar Dependencias
    Con el entorno virtual activado, sincroniza todas las dependencias del proyecto especificadas en `pyproject.toml` y `uv.lock`:

    ```bash
    uv sync
    ```

    Este comando asegurará que todas las bibliotecas necesarias estén instaladas en tu entorno virtual.

6. Configuración de Variables de Entorno (`.env`)
    El proyecto utiliza archivos `.env` para gestionar variables de entorno sensibles o específicas del entorno. Encontrarás archivos `*.env.example` en el repositorio que sirven como plantillas.

    Copia los archivos `.env.example` a `.env` y edítalos con tus propias configuraciones:

    ```bash
    cp .env.example .env
    ```

    Abre el archivo `.env` recién creado con tu editor de texto preferido y rellena los valores necesarios (por ejemplo, claves API, configuraciones de base de datos, etc.). Nunca subas tus archivos `.env` al control de versiones.

7. Pasos Adicionales

    **¿Cuándo usar `uv add` y `uv lock`?**

    * `uv add <paquete>`: Utiliza este comando cuando necesites añadir una nueva dependencia a tu proyecto. `uv` no solo instalará el paquete, sino que también lo añadirá automáticamente a `pyproject.toml` y actualizará el archivo `uv.lock`.

        ```bash
        uv add requests
        ```

    * `uv lock`: Debes ejecutar uv lock cuando:

      * Has modificado manualmente pyproject.toml (por ejemplo, has cambiado la versión de una dependencia o añadido una nueva sin usar uv add).
      * Necesitas regenerar el archivo uv.lock para reflejar los cambios en pyproject.toml o para obtener las últimas versiones compatibles de tus dependencias.

        ```bash
        uv lock
        ```

        `uv lock` garantiza que `uv.lock` sea una representación precisa y reproducible de las dependencias de tu proyecto. Después de ejecutar `uv lock`, asegúrate de confirmar los cambios en `uv.lock` en Git, ya que es crucial para la reproducibilidad del entorno entre desarrolladores.

## Configuración y Ejecución de la Base de Datos con Docker

Este proyecto utiliza Docker para gestionar la base de datos PostgreSQL, lo que facilita su configuración y garantiza un entorno consistente.

La configuración de Docker para la base de datos se encuentra en la carpeta data/database/postgres/docker/. Dentro de esta carpeta, encontrarás los siguientes archivos:

* `docker-compose.yml`: Define los servicios de Docker, en este caso, el contenedor de PostgreSQL y cualquier servicio adicional relacionado con la base de datos.

* `.env.example`: Contiene variables de entorno de ejemplo para la configuración de PostgreSQL (como usuario, contraseña, nombre de la base de datos, etc.).

Sigue estos pasos para levantar la base de datos:

1. Navega a la carpeta de Docker de la base de datos:

    ```bash
    cd data/database/postgres/docker/
    ```

2. Copia y configura el archivo `.env`:
    Al igual que con el `.env` principal del proyecto, debes crear un archivo `.env` para la base de datos a partir del ejemplo.

    ```bash
    cp .env.example .env
    ```

    Abre este nuevo archivo `.env` y ajusta las variables de entorno de PostgreSQL según sea necesario para tu entorno de desarrollo.

    **Aclaración importante:** Cuando trabajes con la versión contenerizada de la base de datos, es crucial que la variable de entorno `DB_PORT` en tu archivo `.env` se establezca en `5433`. Esto se debe a que el contenedor de Docker mapea el puerto interno de PostgreSQL (5432) a un puerto diferente en tu máquina host para evitar conflictos con posibles instalaciones locales de PostgreSQL.

    `DB_PORT=5433`

3. Asegúrate de que el script `restore_on_startup.sh` sea ejecutable (Solo para Linux/Mac):

    Si estás trabajando en un entorno Linux o macOS, es crucial que el script `restore_on_startup.sh` tenga permisos de ejecución para que Docker pueda ejecutarlo correctamente. En Windows, este paso no es necesario.

    ```bash
    chmod +x restore_on_startup.sh
    ```

4. Levanta y restaura la base de datos:

    Ahora, puedes iniciar los servicios de Docker y restaurar la base de datos utilizando los siguientes comandos. El comando `docker compose down -v` se asegura de limpiar cualquier instancia anterior y sus volúmenes asociados, mientras que d`ocker compose run --rm db-restore` inicia el servicio de restauración de la base de datos.

    ```bash
    docker compose down -v
    docker compose run --rm db-restore
    ```

    Estos comandos iniciarán el contenedor de PostgreSQL y ejecutarán cualquier script de restauración de datos que esté configurado en `docker-compose.yml`.
