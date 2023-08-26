################
# Envs Image
# Image containing all base environment requirements
################

FROM python:3.8-slim as envs
LABEL maintainer="Maxcotec <maxcotec.com/learning>"

# Set arguments to be used throughout the image
ARG OPERATOR_HOME="/home/op"
# Bitbucket-pipelines uses docker v18, which doesn't allow variables in COPY with --chown, so it has been statically set where needed.
# If the user is changed here, it also needs to be changed where COPY with --chown appears
ARG OPERATOR_USER="op"
ARG OPERATOR_UID="50000"


# Attach Labels to the image to help identify the image in the future
LABEL com.jagex.docker=true
LABEL com.jagex.docker.distro="debian"
LABEL com.jagex.docker.module="dynamodb-readiness"
LABEL com.jagex.docker.component="dynamodb-readiness"
LABEL com.jagex.docker.uid="${OPERATOR_UID}"

# Add environment variables based on arguments
ENV OPERATOR_HOME ${OPERATOR_HOME}
ENV OPERATOR_USER ${OPERATOR_USER}
ENV OPERATOR_UID ${OPERATOR_UID}

# Make sure noninteractive debian install is used and language variables set
ENV DEBIAN_FRONTEND=noninteractive LANGUAGE=C.UTF-8 LANG=C.UTF-8 LC_ALL=C.UTF-8 \
    LC_CTYPE=C.UTF-8 LC_MESSAGES=C.UTF-8

# Add user for code to be run as (we don't want to be using root)
RUN useradd -ms /bin/bash -d ${OPERATOR_HOME} --uid ${OPERATOR_UID} ${OPERATOR_USER}

################
# Build Image
# Build the virtualenv that contains our python dependencies
################

FROM envs as build

# Make our home dir be owned by root for now - https://jira.atlassian.com/browse/BCLOUD-17319
RUN chown -R root:root ${OPERATOR_HOME}

# Copy in our Pipfile and Pipfile.lock
COPY Pipfile Pipfile.lock ${OPERATOR_HOME}/

# Move into our home directory and install our python requirements into a local virtualenv (.venv)
WORKDIR ${OPERATOR_HOME}
RUN set -ex \
    && pip install --no-cache-dir pipenv \
    && PIP_NO_CACHE_DIR=0 PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy

################
# Dist Image
# Copy the virtualenv and deploy in an image with minimal dependencies
################

FROM envs as dist

# Install our apt dependencies
RUN set -ex \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        tini wget unzip\
    && apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf \
        /var/lib/apt/lists/* \
        /tmp/* \
        /var/tmp/* \
        /usr/share/man \
        /usr/share/doc \
        /usr/share/doc-base

# Copy the virtualenv from the build image
# Fix: Bitbucket-pipelines uses docker v18, which doesn't allow variables in --chown.
COPY --from=build --chown=op ${OPERATOR_HOME} ${OPERATOR_HOME}

# Copy in the operator files from the project directory
# Fix: Bitbucket-pipelines uses docker v18, which doesn't allow variables in --chown.
COPY --chown=op main.py ${OPERATOR_HOME}
COPY --chown=op readiness_check.py ${OPERATOR_HOME}

# Set our user to the operator user
USER ${OPERATOR_USER}

# Switch to OPERATOR_HOME
WORKDIR ${OPERATOR_HOME}

RUN printf '#!/usr/bin/env bash  \n\
source ${OPERATOR_HOME}/.venv/bin/activate   \n\
exec python main.py "$@" \
' >> ${OPERATOR_HOME}/entrypoint.sh

RUN chmod 700 entrypoint.sh
ENTRYPOINT [ "/home/op/entrypoint.sh" ]
