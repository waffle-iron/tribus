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

from celery import task
from fabric.api import execute, env
from tribus.common.fabric.remote import (check_docker, update_packages,
                                         generate_docker_install,
                                         install_docker,
                                         docker_kill_all_remote_containers,
                                         put_charm_install,
                                         create_service_image,
                                         get_charm_base_image,
                                         stop_service, start_service,
                                         docker_kill_all_remote_images)


@task
def wipe_host_conts(*args):
    """ For the sake of developer's laziness. """
    env.user = args[0]['user']
    env.password = args[0]['pw']
    env.hosts = args[0]['ip']
    env.port = 22

    execute(docker_kill_all_remote_containers)
    execute(docker_kill_all_remote_images)


@task
def queue_stop_service(*args):
    env.user = args[0]['user']
    env.password = args[0]['pw']
    env.hosts = args[0]['ip']
    env.port = 22
    env.charm_name = args[0]['charm_name']
    env.service_instance = args[0]['service_instance']

    execute(stop_service)


@task
def queue_start_service(*args):
    env.user = args[0]['user']
    env.password = args[0]['pw']
    env.hosts = args[0]['ip']
    env.port = 22
    env.charm_name = args[0]['charm_name']
    env.service_instance = args[0]['service_instance']

    execute(start_service)


@task
def queue_charm_deploy(*args):
    env.port = 22
    env.user = args[0]['user']
    env.password = args[0]['pw']
    env.hosts = args[0]['ip']
    env.charm_name = args[0]['charm_name']

    docker_exists = execute(check_docker)[env.hosts]

    if docker_exists == 0:
        execute(put_charm_install)
        execute(create_service_image)

    elif docker_exists == 1:
        script_placed = execute(generate_docker_install)[env.hosts]

        if script_placed == 0:
            execute(update_packages)
            docker_installed = execute(install_docker)[env.hosts]
            execute(get_charm_base_image)
        else:
            return

        if docker_installed == 0:
            execute(put_charm_install)
            execute(create_service_image)

        else:
            print "Ocurrio un error, codigo de error es: %s " % docker_installed
            return
