#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2013-2014 Tribus Developers
#
# This file is part of Tribus.
#
# Tribus is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Tribus is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import json
from contextlib import nested
from tribus.common.logger import get_logger
from fabric.api import run, env, settings, sudo, hide, put, cd

log = get_logger()


def check_docker():
    with settings(command='which docker.io', warn_only=True):
        exit_status = run('%(command)s' % env)
    return exit_status.return_code


def update_packages():
    with settings(command='aptitude update', warn_only=True):
        exit_status = sudo('%(command)s' % env)
    return exit_status.return_code


def put_charm_install():
    env.install_orig = os.path.join(env.basedir, 'tribus/data/charms',
                                    env.charm_name, 'hooks/install')
    env.start_orig = os.path.join(env.basedir, 'tribus/data/charms',
                                  env.charm_name, 'hooks/start')
    env.stop_orig = os.path.join(env.basedir, 'tribus/data/charms',
                                 env.charm_name, 'hooks/stop')

    env.install_dest = os.path.join('/tmp', env.charm_name, 'install')
    env.start_dest = os.path.join('/tmp', env.charm_name, 'start')
    env.stop_dest = os.path.join('/tmp', env.charm_name, 'stop')

    run('mkdir /tmp/%(charm_name)s' % env)

    put(env.install_orig, env.install_dest)
    run('chmod +x %s' %  env.install_dest)
    put(env.start_orig, env.start_dest)
    run('chmod +x %s' % env.start_dest)
    put(env.stop_orig, env.stop_dest)
    run('chmod +x %s' % env.stop_dest)


def generate_docker_install():
    env.APTGETOPTS = ("-qq -o Apt::Install-Recommends=false "
                      "-o Apt::Get::Assume-Yes=true "
                      "-o Apt::Get::AllowUnauthenticated=true "
                      "-o DPkg::Options::=--force-confmiss "
                      "-o DPkg::Options::=--force-confnew "
                      "-o DPkg::Options::=--force-overwrite "
                      "-o DPkg::Options::=--force-unsafe-io ")
    env.DEBIAN_MIRROR = "http://http.us.debian.org/debian"

    with settings(command=(
        'echo "#!/usr/bin/env bash\n'
        'export DEBIAN_FRONTEND=noninteractive \n'
        'mv /etc/apt/sources.list /etc/apt/sources.list.bk \n'
        'mv /etc/apt/sources.list.d /etc/apt/sources.list.d.bk \n'
        'echo \'deb %(DEBIAN_MIRROR)s wheezy main\' > /etc/apt/sources.list \n'
        'apt-get %(APTGETOPTS)s update \n'
        'apt-get %(APTGETOPTS)s install -t wheezy iptables perl libapparmor1 '
        'libdevmapper1.02.1 libsqlite3-0 adduser libc6 \n'
        'echo \'deb %(DEBIAN_MIRROR)s wheezy-backports main\' > '
        '/etc/apt/sources.list \n'
        'apt-get %(APTGETOPTS)s update \n'
        'apt-get %(APTGETOPTS)s install -t '
        'wheezy-backports init-system-helpers fabric \n'
        'echo \'deb %(DEBIAN_MIRROR)s jessie main\' > /etc/apt/sources.list \n'
        'apt-get update \n'
        'apt-get %(APTGETOPTS)s install -t jessie docker.io \n'
        'mv /etc/apt/sources.list.bk /etc/apt/sources.list \n'
        'mv /etc/apt/sources.list.d.bk /etc/apt/sources.list.d \n'
        'apt-get %(APTGETOPTS)s update \n'
        'exit 0'
        '" > /tmp/docker_install.sh') % env):
        exit_status = sudo('%(command)s' % env)
    return exit_status.return_code


def install_docker():
    with settings(command='bash /tmp/docker_install.sh', warn_only=True):
        exit_status = sudo('%(command)s' % env)
    return exit_status.return_code


def get_charm_base_image():
    env.baseimage = 'phusion/baseimage'
    with nested(hide('warnings', 'stderr', 'running'),
        settings(warn_only=True)):
        sudo('bash -c ' '"docker.io pull %(baseimage)s"' % env)


def docker_kill_all_remote_containers():
    """
    Destroy all remote containers listed with ``docker ps -aq``.

    .. versionadded:: 0.2
    """
    with hide('warnings', 'stderr', 'running'):

        log.info('Listing available containers ...')

        containers = sudo(('bash -c "%(docker)s ps -aq"') % env).split('\n')

        for container in containers:

            if container:

                # log.info('Checking if container "%s" exists ...' % container)


                # var = sudo(('bash -c "%s inspect %s"') % (env.docker, container))

                # print var, type(var)
                # print dir(var)

                # inspect = json.loads(sudo(('bash -c '
                #                             '"%s inspect %s"') % (env.docker,
                #                                                   container)))
                
                # if inspect:

                    log.info('Destroying container "%s" ...' % container)

                    sudo(('bash -c '
                           '"%s stop --time 1 %s"') % (env.docker, container))
                    sudo(('bash -c '
                           '"%s rm -fv %s"') % (env.docker, container))


def docker_kill_all_remote_images():
    """
    Destroy all Docker images.

    .. versionadded:: 0.2
    """
    with hide('warnings', 'stderr', 'running'):

        log.info('Listing available images ...')

        images = sudo(('sudo bash -c "%(docker)s images -aq"') % env,
                       ).split('\n')

        for image in images:

            if image:

                # log.info('Checking if image "%s" exists ...' % image)

                # inspect = json.loads(sudo(('sudo bash -c '
                #                             '"%s inspect %s"') % (env.docker,
                #                                                   image),
                #                            ))
                # if inspect:

                    log.info('Destroying image "%s" ...' % image)

                    sudo(('sudo bash -c '
                           '"%s rmi -f %s"') % (env.docker, image),
                          )


def query_host_containers():
    with hide('warnings', 'stderr', 'running'):
        containers = sudo(('bash -c "%(docker)s ps -aq"') % env).split('\n')
        container_names = []
        for container in containers:
            if container:
                inspect = json.loads(sudo(('bash -c '
                                            '"%s inspect %s"') % (env.docker,
                                                                  container)))
                for cont in inspect:
                    container_names.append(cont['Name'].strip("/"))
        return container_names


def query_host_images():
    with hide('warnings', 'stderr', 'running'):
        containers = sudo(('bash -c "%(docker)s images -aq"') % env).split('\n')
        container_names = []
        for container in containers:
            if container:
                inspect = json.loads(sudo(('bash -c '
                                           '"%s inspect %s"') % (env.docker,
                                                                  container)))
                for cont in inspect:
                    container_names.append(cont['Name'].strip("/"))
        return container_names


def start_service():
    # Iniciar servcio
    sudo('docker.io run -it --name %(charm_name)s-%(service_instance)s '
         '--volume %(mount_place)s %(charm_name)s-%(service_instance)s '
         'bash %(start_place)s && tail -f /dev/null' % env)


def stop_service():
    # Detener servicio
    sudo('docker.io run -it --name %(charm_name)s-%(service_instance)s '
         '--volume %(mount_place)s '
         '%(charm_name)s-%(service_instance)s bash %(stop_place)s' % env)

    # Hacer commit en una imagen
    sudo(command='docker.io commit %(charm_name)s-%(instance)s '
                 '%(charm_name)s-%(service_instance)s' % env)

    # Borrar el contenedor
    sudo(command='docker.io rm %(charm_name)s-%(service_instance)s ' % env)


def create_service_image():
    env.mount_place = '/tmp/:/tmp/:rw'
    env.charm_place = os.path.join('/tmp', env.charm_name)
    env.install_place = os.path.join('/tmp', env.charm_name, 'install')
    env.start_place = os.path.join('/tmp', env.charm_name, 'start')
    env.stop_place = os.path.join('/tmp', env.charm_name, 'stop')
    env.baseimage = 'phusion/baseimage'
    env.charm_apt_deps = 'python-apt python-yaml python-yaml'
    env.charm_py_deps = 'charmhelpers'

    with hide('warnings', 'stderr', 'running'):
        base_exists = sudo('%(docker)s inspect %(charm_name)s-base:base' % env)
        if base_exists.return_code == 1:
            # Instalar python en el contenedor y ejecutar script de instalacion
            sudo(command='docker.io run -it --name %(charm_name)s-base '
                 '--volume %(mount_place)s '
                 '%(baseimage)s bash -c "apt-get update && apt-get install -y '
                 '%(charm_apt_deps)s && pip install %(charm_py_deps)s && '
                 'cd %(charm_place)s && ./install "' % env)

            # Hacer commit en una imagen
            sudo(command='docker.io commit %(charm_name)s-base '
                         '%(charm_name)s-base:base' % env)

            # Borrar el contenedor
            sudo(command='docker.io rm %(charm_name)s-base ' % env)

        env.service_base_image = env.charm_name + '-base:base'
        env.instance = 0

        # Asignar numero de instancia correcto
        while sudo('%(docker)s inspect '
                   '%(charm_name)s-%(instance)s' % env).return_code == 0:
            env.instance += 1

        # Hacer correr el contenedor
        with cd(env.charm_place):
            sudo('docker.io run -it --name %(charm_name)s-%(instance)s '
                 '--volume %(mount_place)s '
                 '%(service_base_image)s bash -c "cd %(charm_place)s '
                 '&& ./start && tail -f /dev/null"' % env)
