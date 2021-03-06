# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

FROM ubuntu:16.04

ENV DEBIAN_FRONTEND noninteractive

# Ensure local Python is preferred over distribution Python.
ENV PATH /usr/local/bin:$PATH

# http://bugs.python.org/issue19846
# At the moment, setting "LANG=C" on a Linux system fundamentally breaks
# Python 3.
ENV LANG C.UTF-8

# Install dependencies.
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    sudo \
    ca-certificates \
    build-essential \
    git \
    libreadline-dev \
    libssl-dev \
    libffi-dev \
    ssh \
    tcl \
    tcl-dev \
    tk \
    tk-dev \
    wget \
    libsnappy-dev \
  && apt-get clean autoclean \
  && apt-get autoremove -y \
  && rm -rf /var/lib/apt/lists/* \
  && rm -f /var/cache/apt/archives/*.deb

# Install the desired versions of Python.
RUN for PYTHON_VERSION in 2.7.13 3.3.6 3.4.6 3.5.3 3.7.0b3 3.6.0; do \
  set -ex \
    && wget --no-check-certificate -O python-${PYTHON_VERSION}.tar.xz "https://www.python.org/ftp/python/${PYTHON_VERSION%%[a-z]*}/Python-$PYTHON_VERSION.tar.xz" \
    && wget --no-check-certificate -O python-${PYTHON_VERSION}.tar.xz.asc "https://www.python.org/ftp/python/${PYTHON_VERSION%%[a-z]*}/Python-$PYTHON_VERSION.tar.xz.asc" \
    && export GNUPGHOME="$(mktemp -d)" \
    && gpg --keyserver ha.pool.sks-keyservers.net --recv-keys \
      # 2.7.13
      C01E1CAD5EA2C4F0B8E3571504C367C218ADD4FF \
      # 3.3.6
      26DEA9D4613391EF3E25C9FF0A5B101836580288 \
      # 3.4.6
      97FC712E4C024BBEA48A61ED3A5CA953F73C700D \
      # 3.5.3
      97FC712E4C024BBEA48A61ED3A5CA953F73C700D \
      # 3.6.0, 3.7.0
      0D96DF4D4110E5C43FBFB17F2D347EA6AA65421D \
    && gpg --batch --verify python-${PYTHON_VERSION}.tar.xz.asc python-${PYTHON_VERSION}.tar.xz \
    && rm -r "$GNUPGHOME" python-${PYTHON_VERSION}.tar.xz.asc \
    && mkdir -p /usr/src/python-${PYTHON_VERSION} \
    && tar -xJC /usr/src/python-${PYTHON_VERSION} --strip-components=1 -f python-${PYTHON_VERSION}.tar.xz \
    && rm python-${PYTHON_VERSION}.tar.xz \
    \
    && cd /usr/src/python-${PYTHON_VERSION} \
    && ./configure \
        --enable-shared \
      # This works only on Python 2.7 and throws a warning on every other
      # version, but seems otherwise harmless.
        --enable-unicode=ucs4 \
        --with-system-ffi \
        --without-ensurepip \
    && make -j$(nproc) \
    && make install \
    && ldconfig \
  ; done \
  && rm -rf /usr/src/python* \
  && rm -rf ~/.cache/


# Install pip on Python 3.6 only.
# If the environment variable is called "PIP_VERSION", pip explodes with
# "ValueError: invalid truth value '<VERSION>'"
ENV PYTHON_PIP_VERSION 10.0.1
RUN wget --no-check-certificate -O /tmp/get-pip.py 'https://bootstrap.pypa.io/get-pip.py' \
    && python3.6 /tmp/get-pip.py "pip==$PYTHON_PIP_VERSION" \
    && rm /tmp/get-pip.py \

  # we use "--force-reinstall" for the case where the version of pip we're trying to install is the same as the version bundled with Python
  # ("Requirement already up-to-date: pip==8.1.2 in /usr/local/lib/python3.6/site-packages")
  # https://github.com/docker-library/python/pull/143#issuecomment-241032683
    && pip3 install --no-cache-dir --upgrade --force-reinstall "pip==$PYTHON_PIP_VERSION" \

  # then we use "pip list" to ensure we don't have more than one pip version installed
  # https://github.com/docker-library/python/pull/100
    && [ "$(pip list |tac|tac| awk -F '[ ()]+' '$1 == "pip" { print $2; exit }')" = "$PYTHON_PIP_VERSION" ]


# Install "virtualenv", since the vast majority of users of this image
# will want it.
RUN pip install --no-cache-dir virtualenv

CMD ["python3.6"]
