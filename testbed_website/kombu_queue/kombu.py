from flask import session
from ..run import celery, queue_recv_broadcast
from kombu import Consumer
from time import time
import socket

# results_exchange = Exchange('myres', type='fanout')
# queue = Queue(name="response-queue", exchange=results_exchange, routing_key="kombu_routing")

def process_message(body, message):
    message.ack()
    print('******************************')
    print(body)
    
    return

    message_type = body['type']             # can be erase, flash, send, ...
    address = body['address']
    status = 1 if body['status'] else 0     # 1 if operation was successful, 0 if an error occurred
    error = None
    if('error' in body):
        error = body['error']

    if(message_type not in session):        # session[message_type] not existing yet --> must be created

        session[message_type] = {
            address: status,
            # 'status': status,             # setting session data
            'counter': status,              # counts successful tasks
            'last_recv_time': time()        # interval from the last receive
            # 'task_type': message_type
        }

        if(error is not None):
            session[message_type]['error'] = error
            session[message_type]['error_address'] = address  # saving where the error occurred

    else:
        if(address not in session[message_type]):         # first response from the node with the given address, otherwise is a copy
            
            session[message_type][address] = status       # update the list of IPs that replied
            session[message_type]['counter'] += status

            if(error is not None):
                session[message_type]['error'] = error    # saving error string
                session[message_type]['error_address'] = address  # saving where the error occurred
        
        session[message_type]['last_recv_time'] = time()

def check_for_kombu_messages():
    
    with celery.connection_or_acquire() as conn:
        try:
            with Consumer(conn, queues=queue_recv_broadcast, callbacks=[process_message], accept=['json']):
                conn.drain_events(timeout=1)
                
        except socket.timeout:
            # print('0) ', session.get('erase'))
            pass
    


from ..db.models import ExperimentsData

def process_rpi_response(body, message):
    message.ack()
    print('*************** RPI response ***************')
    print(body)
    if body['status'] == True:
        experiment = ExperimentsData.query.filter_by(_id=body['experiment_id']).first()
        if experiment:
            pass
    
    return
    
with celery.connection_or_acquire() as conn:
    try:
        with Consumer(conn, queues=queue_recv_broadcast, callbacks=[process_rpi_response], accept=['json']):
            conn.drain_events(timeout=1)
            
    except socket.timeout:
        # print('0) ', session.get('erase'))
        pass
