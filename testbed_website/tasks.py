from .run import celery

@celery.task(name='RPi_WebClient.add')
def add(a, b):
    # sleep(3000)
    # result = add.apply_async(args=[a, b])
    # result.wait()  # 65
    # print(a, b)
    return a + b

@celery.task(name='RPi_WebClient.terase_task2', bind=True, trail=True)
def terase_task2(self, addr=None):
    # result = add.apply_async(args=[a, b])
    # result.wait()  # 65
    return 40

import random
import time

@celery.task(name='RPi_WebClient.long_task', bind=True, trail=True)
def long_task(self):
    """Background task that runs a long function with progress reports."""
    verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking']
    adjective = ['master', 'radiant', 'silent', 'harmonic', 'fast']
    noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'bit']
    message = ''
    total = random.randint(10, 50)
    for i in range(total):
        if not message or random.random() < 0.25:
            message = '{0} {1} {2}...'.format(random.choice(verb),
                                              random.choice(adjective),
                                              random.choice(noun))
        self.update_state(state='PROGRESS',
                          meta={'current': i, 'total': total,
                                'status': message})
        time.sleep(1)
    return {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': 42}

@celery.task(name='RPi_WebClient.erase_task', bind=True, trail=True, ignore_result=True)
def erase_task(self, target):
    pass

@celery.task(name='RPi_WebClient.flash_task', bind=True, trail=True, ignore_result=True)
def flash_task(self, target, filename):
    pass

@celery.task(name='RPi_WebClient.send_task', bind=True, trail=True, ignore_result=True)
def send_task(self, target, code):
    pass

@celery.task(name='RPi_WebClient.reset_task', bind=True, trail=True, ignore_result=True)
def reset_task(self, start_time):
    pass

@celery.task(name='RPi_WebClient.stop_experiment_task', bind=True, trail=True, ignore_result=True)
def stop_experiment_task(self):
    pass

@celery.task(name='agent.stop_experiment_task', bind=True, trail=True, ignore_result=True)
def stop_experiment_task(self):
    pass

@celery.task(name='agent.launch_experiment_task', bind=True, trail=True, ignore_result=True)
def launch_experiment_task(self, id, associations, launch_time, flash_only=False):
    pass

@celery.task(name='agent.flash_node_task', bind=True, trail=True, ignore_result=True)
def flash_node_task(self, id, associations):
    pass

@celery.task(name='agent.dummy_task', bind=True, trail=True, ignore_result=True)
def dummy_task(self):
    pass