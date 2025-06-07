# Custom Notebooks

Sometimes you face limitations of default VSCode and Notebook instances because, for example, you need:
- additional software to be installed system-wide
- root access
- user to be present on the system
- password for root access

To overcome those limitations you can use a custom Notebook image built by yourself.

For inspiration, you can use examples provided by Kubeflow on its [github](https://github.com/kubeflow/kubeflow/tree/master/components/example-notebook-servers).

Further, we'll provide simpler examples you can use right away.

In listed below case you'll have:
- root access
- user `jovyan`
- user's password `jovyan`


```dockerfile
# Use base image with GPU support.
FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04

# common environemnt variables
ENV NB_USER jovyan
ENV NB_UID 1000
ENV NB_PREFIX /
ENV HOME /home/$NB_USER
ENV SHELL /bin/bash

# args - software versions
ARG KUBECTL_ARCH="amd64"
ARG KUBECTL_VERSION=v1.21.0

# set shell to bash
SHELL ["/bin/bash", "-c"]

# install - usefull linux packages
# feel free to add your own here
RUN export DEBIAN_FRONTEND=noninteractive \
   && apt-get -yq update \
   && apt-get -yq install --no-install-recommends \
   apt-transport-https \
   bash \
   bzip2 \
   ca-certificates \
   curl \
   git \
   gnupg \
   gnupg2 \
   htop \
   locales \
   lsb-release \
   nano \
   ncdu \
   nvtop \
   python3-venv \
   python3-pip \
   software-properties-common \
   sudo \
   tzdata \
   unzip \
   vim \
   wget \
   xz-utils \
   zip \
   && apt-get clean \
   && rm -rf /var/lib/apt/lists/*

# install - kubectl
RUN curl -sL "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/${KUBECTL_ARCH}/kubectl" -o /usr/local/bin/kubectl \
   && curl -sL "https://dl.k8s.io/${KUBECTL_VERSION}/bin/linux/${KUBECTL_ARCH}/kubectl.sha256" -o /tmp/kubectl.sha256 \
   && echo "$(cat /tmp/kubectl.sha256) /usr/local/bin/kubectl" | sha256sum --check \
   && rm /tmp/kubectl.sha256 \
   && chmod +x /usr/local/bin/kubectl

# create user and set required ownership
RUN useradd -M -s /bin/bash -N -u ${NB_UID} ${NB_USER} \
   && echo ${NB_USER}:${NB_USER} | chpasswd \
   && adduser ${NB_USER} sudo \
   && mkdir -p ${HOME} \
   && chown -R ${NB_USER}:users ${HOME} \
   && chown -R ${NB_USER}:users /usr/local/bin

# set locale configs
RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen \
   && locale-gen
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8
ENV LC_ALL en_US.UTF-8

# change user to root
USER root

RUN pip3 install jupyterlab notebook ipykernel

USER $NB_UID

RUN jupyter lab --generate-config

EXPOSE 8888

CMD [ "sh", "-c", "\
    cd $HOME && \
    jupyter lab \
    --notebook-dir=$HOME \
    --ip=0.0.0.0 \
    --no-browser \
    --allow-root \
    --port=8888 \
    --ServerApp.token=\"\" \
    --ServerApp.password=\"\" \
    --ServerApp.allow_origin=\"*\" \
    --ServerApp.base_url=$NB_PREFIX \
    --ServerApp.authenticate_prometheus=False" ]
```

Save the code snipped to a local `Dockerfile`, build and push it to your docker registry:

```bash
docker build -t <REGISTRY>/<IMAGE_NAME>:<TAG> -t <REGISTRY>/<IMAGE_NAME>:latest -f ./Dockerfile .
docker push <REGISTRY>/<IMAGE_NAME>:<TAG>
docker push <REGISTRY>/<IMAGE_NAME>:latest
```

After that, you'll be able to use your image to create a custom VSCode instance:
- select `JupyterLab`
- click `Custom Notebook`
- click `Advanced Options`
- click the checkbox `Custom Image`
- input `<REGISTRY>/<IMAGE_NAME>:latest` to the text field


And you're ready to use it!
