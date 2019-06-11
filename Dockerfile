FROM python:3.7-stretch as base

# --- Back-end builder
FROM base as back-builder

WORKDIR /builder

# Copy required python dependencies
COPY . /builder/

# Upgrade pip to its latest release to speed up dependencies installation
RUN pip install --upgrade pip

RUN mkdir /install && \
    pip install --prefix=/install .

# ---- Core application image ----
FROM base as core

WORKDIR /app

# Copy installed python dependencies
COPY --from=back-builder /install /usr/local

# Copy runtime-required files
COPY ./docker/files/usr/local/bin/entrypoint /usr/local/bin/entrypoint
RUN mkdir -p /usr/local/etc/gunicorn
COPY ./docker/files/usr/local/etc/gunicorn/potsie.py /usr/local/etc/gunicorn/potsie.py

# Give the "root" group the same permissions as the "root" user on /etc/passwd
# to allow a user belonging to the root group to add new users; typically the
# docker user (see entrypoint).
RUN chmod g=u /etc/passwd

# Un-privileged user running the application
ARG DOCKER_USER
USER ${DOCKER_USER}

# We wrap commands run in this container by the following entrypoint that
# creates a user on-the-fly with the container user ID (see USER) and root group
# ID.
ENTRYPOINT [ "/usr/local/bin/entrypoint" ]

# ---- Development image ----
FROM core as development

# Switch back to the root user to install development dependencies
USER root:root

# Upgrade pip to its latest release to speed up dependencies installation
RUN pip install --upgrade pip

# Copy application sources (will be mounted as a volume in docker-compose)
COPY . /app

# Uninstall potsie and re-install it in editable mode along with development
# dependencies
RUN pip uninstall -y potsie
RUN pip install -e .[dev]

# Restore the un-privileged user running the application
ARG DOCKER_USER
USER ${DOCKER_USER}

# Run the development server
CMD python -m potsie.server

# ---- Production image ----
FROM core as production

# Run production wsgi server
CMD gunicorn -c /usr/local/etc/gunicorn/potsie.py potsie.server.wsgi:app
