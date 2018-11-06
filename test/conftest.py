import os
import subprocess
import time
import pytest
import socket
import sys


PYTHON_COMMAND = f'python{sys.version[:3]}'

@pytest.fixture(scope='session')
def django_server():
    """
    Before test start django server and returns host:post
    After test stops the server
    """
    env = dict(os.environ, **{'PYTHONUNBUFFERED':'1'})
    host_and_port = '127.0.0.1:8084'
    print(f'Starting django test server at {host_and_port}')
    django_process = subprocess.Popen(
        [PYTHON_COMMAND, 'manage.py', 'runserver', host_and_port],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env
    )

    signature_to_wait_for = 'Quit the server with CONTROL-C.'
    max_wait_seconds = 20
    django_ready = False

    start_time = time.time()
    while not django_ready:
        line = django_process.stdout.readline().decode()
        django_ready = signature_to_wait_for in line
        assert time.time() - start_time < max_wait_seconds, 'Timeout waiting django server to start'

    yield host_and_port

    # finalization
    django_process.terminate()


@pytest.fixture(scope='session')
def redis_server():
    redis_ip = '127.0.0.1'
    redis_port = 6379
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5)
    try:
        s.connect((redis_ip, redis_port))
    except ConnectionRefusedError:
        assert False, f'Please start local redis server on port {redis_port}'

    print(f'Sending ping to redis server at {redis_ip}:{redis_port}')
    redis_check_command = ['redis-cli', 'PING']
    redis_client_process = subprocess.Popen(
        redis_check_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    out, err = redis_client_process.communicate()
    assert 'PONG' in out.decode(), \
        f'You should start local redis server.\n"{" ".join(redis_check_command)}" returns\n{out.decode()}'

    yield f'{redis_ip}:{redis_port}'

    # no finalization needed


@pytest.fixture(scope='session')
def fake_kinozal():
    env = dict(os.environ, **{'PYTHONUNBUFFERED':'1'})
    print(f'Starting kinozal fake server')
    kinozal_process = subprocess.Popen(
        [PYTHON_COMMAND, 'test/fake_kinozal_server.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env
    )

    signature_to_wait_for = '(Press CTRL+C to quit)'
    max_wait_seconds = 2
    kinozal_ready = False

    start_time = time.time()
    while not kinozal_ready:
        line = kinozal_process.stdout.readline().decode()
        assert time.time() - start_time < max_wait_seconds, 'Timeout waiting fake kinozal server to start'
        if not line:
            continue
        kinozal_ready = signature_to_wait_for in line
        print(line)


    yield None  # the tests do not need any server descriptions

    # finalization
    kinozal_process.terminate()


fake_kinozal()
