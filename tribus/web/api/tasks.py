from celery import task
from fabric.api import run, execute, env, settings

from random import randint
import crypt
import string

salt_chars = './' + string.ascii_letters + string.digits

def crypt_password(password):
    salt = salt_chars[randint(0, 63)] + salt_chars[randint(0, 63)]
    return crypt(password, salt)

def bootstrap():
    with settings(command='echo \'%(user)s ALL= NOPASSWD: ALL\' > /etc/sudoers.d/tribus; chmod 0440 /etc/sudoers.d/tribus'):
        run('%(command)s' % env, capture=False)


def configure_tribus_sudo():
    with settings(command='echo \'%(user)s ALL= NOPASSWD: ALL\' > /etc/sudoers.d/tribus; chmod 0440 /etc/sudoers.d/tribus'):
        run('%(command)s' % env, capture=False)


def configure_tribus_user():
    with settings(command='adduser --password="%s" tribus' % crypt_password(env.password)):
        run('%(command)s' % env, capture=False)


def check_for_tribus_user():
    with settings(command='getent passwd tribus', warn_only=True):
        exit_status = run('%(command)s' % env)
    return exit_status.return_code


def has_sudo():
    #with settings(command='echo "123456" | sudo -v', warn_only=True):
    with settings(command='ls', warn_only=True):
        exit_status = run('%(command)s' % env)
    return exit_status.return_code


def check_docker():
    # with settings(command='dpkg-query -l <pkgname>', warn_only=True):
    # Devuelve 0 si el paquete esta instalado, 1 si no
    with settings(command='dpkg-query -l docker.io', warn_only=True):
        exit_status = run('%(command)s' % env)
    return exit_status.return_code


@task
def queue_charm_deploy(*args):

    env.user = args[0]['user']
    env.password = args[0]['pw']
    env.hosts = [args[0]['ip']]

    docker_exists = execute(check_docker)

    print ">>>>>", docker_exists

    #exit_status = execute(check_for_tribus_user)

    #print exit_status
    #if exit_status.get(env.hosts[0]) != 0:
    #    execute(configure_tribus_user)
    #    execute(configure_tribus_sudo)

    # execute(bootstrap)
