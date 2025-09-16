# Máster UCM - TFM Grupo 4

Este repositorio contiene el código fuente para el Trabajo de Fin de Máster (TFM) del Grupo 4.

---

<div align="center">
    <img src="./assets/logo-ucm-6.png" alt="Logo UCM" height="50" style="margin: 10px;"/>
    <img src="./assets/logo_BIAI.png" alt="Logo BIAI" height="50" style="margin: 10px;"/>
    <img src="./assets/logo-nticmaster-6.png" alt="Logo Ntic Master" height="50" style="margin: 10px;"/>
</div>

<div align="center">
  <video controls width="800">
    <source src="./assets/Ejemplo NL-2-SQL - Corto.mp4" type="video/mp4">
    Tu navegador no soporta la etiqueta de video.
  </video>
</div>

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

    Asegúrate de reemplazar `https://github.com/grimbano/ucm-tfm-grupo-4.git` con la URL real de tu repositorio.

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
    uv pip sync pyproject.toml
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

## Configuración y Ejecución de los Servicios con Docker

Este proyecto utiliza **Docker** y **Docker Compose** para gestionar tanto la base de datos **PostgreSQL** como la base de datos vectorial **ChromaDB**. Esto facilita la configuración de ambos servicios y asegura un entorno de desarrollo consistente.

El archivo `docker-compose.yml`, que se encuentra en la raíz del repositorio, define y configura ambos servicios de manera independiente.

---

### Preparación del Entorno

1. **Variables de Entorno (`.env`):**
    El `docker-compose.yml` utiliza variables de entorno definidas en el archivo `.env` para la configuración de los servicios. Siguiendo los pasos indicados en la sección anterior, copia el archivo de ejemplo a la raíz del repositorio y rellena las variables necesarias.

    **Aclaración importante:** Cuando trabajes con la versión contenerizada de la base de datos, es crucial que la variable de entorno `DB_PORT` en tu archivo `.env` se establezca en `5433`. Esto se debe a que el contenedor de Docker mapea el puerto interno de PostgreSQL (`5432`) a un puerto diferente en tu máquina host para evitar conflictos con posibles instalaciones locales de PostgreSQL.

    `DB_PORT=5433`

2. **Permisos de ejecución para el script:**

    El script `entrypoint.sh` debe tener los permisos de ejecución correctos para que Docker pueda ejecutarlo. El script se encuentra en la ruta `data/database/postgres/docker/`.

    * **Para Linux/macOS:**

        ```Bash
        dos2unix data/database/postgres/docker/entrypoint.sh
        chmod +x data/database/postgres/docker/entrypoint.sh
        ```

    * **Para Windows:**

        ```DOS
        dos2unix data/database/postgres/docker/entrypoint.sh
        ```

        (El comando `chmod` no es necesario en Windows, ya que su sistema de permisos de archivos es diferente).

---

### Comandos Docker Compose

Una vez que hayas configurado el entorno, puedes utilizar los siguientes comandos para gestionar los servicios de Docker:

1. **Levantar los servicios:**

    Utiliza el archivo `docker-compose.yml` para levantar los servicios de **PostgreSQL** y **ChromaDB** en segundo plano.

    ```Bash
    docker compose down -v
    docker compose up -d --build
    ```

    El comando `docker compose down -v` se asegura de detener y eliminar cualquier instancia anterior y sus volúmenes asociados, mientras que `docker compose up -d` construye y levanta los servicios definidos en el `docker-compose.yml`.

2. **Ver el estado de los servicios:**

    Para verificar que los servicios se están ejecutando correctamente, puedes revisar sus logs.

    ```Bash
    docker compose logs tfm-postgres-db
    docker compose logs tfm-chroma-db
    docker compose logs tfm-gradio-app
    ```
