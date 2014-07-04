from celery import task
from fabric.api import run, execute, env, settings, sudo

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
    with settings(command='which docker.io', warn_only=True):
        exit_status = run('%(command)s' % env)
    return exit_status.return_code


def update_packages():

    with settings(command='aptitude update', warn_only=True):
        exit_status = sudo('%(command)s' % env)
    return exit_status.return_code


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
        'apt-get %(APTGETOPTS)s install -t wheezy iptables perl libapparmor1 libdevmapper1.02.1 libsqlite3-0 adduser libc6 \n'
        'echo \'deb %(DEBIAN_MIRROR)s wheezy-backports main\' > /etc/apt/sources.list \n'
        'apt-get %(APTGETOPTS)s update \n'
        'apt-get %(APTGETOPTS)s install -t wheezy-backports init-system-helpers fabric \n'
        'echo \'deb %(DEBIAN_MIRROR)s jessie main\' > /etc/apt/sources.list \n'
        'apt-get update \n'
        'apt-get %(APTGETOPTS)s install -t jessie docker.io \n'
        'mv /etc/apt/sources.list.bk /etc/apt/sources.list \n'
        'mv /etc/apt/sources.list.d.bk /etc/apt/sources.list.d \n'
        'apt-get %(APTGETOPTS)s update \n'
        'exit 0'
        '" > /tmp/docker_install.sh'
        ) % env):
        sudo('%(command)s' % env)


def install_docker():

    #env.user = ''
    #env.password = ''

    with settings(command='export DEBIAN_FRONTEND=noninteractive && aptitude install -y docker.io',
        warn_only=True):
        exit_status = sudo('%(command)s' % env)
    return exit_status.return_code


@task
def queue_charm_deploy(*args):

    env.user = args[0]['user']
    env.password = args[0]['pw']
    env.hosts = args[0]['ip']

    #docker_exists = execute(check_docker)[env.hosts]

    execute(generate_docker_install)

    '''

    if docker_exists == 0:
        # Docker existe, puedo proceder a desplegar el contenedor
        print ">> Docker ya esta instalado, instale el contenedor <<"
    elif docker_exists == 1:
        # Docker no existe debo proceder a instalarlo

        print ">> Docker no esta instalado, instalando... <<"
        execute(update_packages)
        docker_installed = execute(install_docker)[env.hosts]

        if docker_installed == 0:
            # Si docker se instalo correctamente puedo proceder a desplegar
            # el contenedor
            print ">> Docker se ha instalado, instale el contenedor <<"
        else:
            # Si no se instala correctamente puede deberse a varias razones
            # - Falta de permisos, - Algun otro error no previsto
            print ">> Ocurrio un error instalando docker <<"
            print "El codigo de error es: %s " % docker_installed
    '''

