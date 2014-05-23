from celery import task
from fabric.api import run, execute, env, settings



def configure_tribus_user():
    with settings(command='adduser' % env):
        run('%(command)s' % env, capture=False)

def check_for_tribus_user():
    with settings(command='getent passwd tribus', warn_only=True):
        exit_status = run('%(command)s' % env)
    return exit_status.return_code
  
@task
def queue_charm_deploy(*args):

    env.user = args[0]['user']
    env.password = args[0]['pw']
    env.hosts = [args[0]['ip']]
    
    exit_status = execute(check_for_tribus_user)

    if exit_status.get(env.hosts[0]) != 0:
        
        
    
    
    