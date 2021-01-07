errors = {
    # 0: '',                                                                     # 0 correct
    1: {
        'error_main': 'No worker has ever replied.',
        'error_secondary': 'Start workers on the RPis or be sure they are running.'
    },
    2: {
        'error_main': 'No other workers have replied in the last {ERASE_TIMER_STOP} seconds.',
        'error_secondary': 'Remaining workers finished the task with errors.'
    },    
    3: {
        'error_main': 'An error occurred at node with IP: {address}.',
        'error_secondary': 'Check the connection to the Nordic board.'
    },
    4: {
        'error_main': 'An exception {exc} was raised at node with IP: {address}.',
        'error_secondary': 'Inspect the board.'
    },
    5: {
        'error_main': 'A pexpect.Timeout error occurred at node with IP: {address}.',
        'error_secondary': 'Check the connection to the Nordic board.'
    },
    6: {
        'error_main': 'Only <i>.hex</i> format allowed.',
        'error_secondary': 'Submit a correct file.'
    },
    7: {
        'error_main': 'No selected file.',
        'error_secondary': 'Submit a file.'
    },
    8: {
        'error_main': 'File name cannot be empty.',
        'error_secondary': 'Rename the file.'
    },
    9: {
        'error_main': 'File name does not exists in the firmwares directory.',
        'error_secondary': 'Check the file name.'
    },
    10: {
        'error_main': 'None of the nodes specified during configuration is active.',
        'error_secondary': 'Retry the scan first. Then inspect the nodes or the network.'
    },
    11: {
        'error_main': 'An error occurred during retrieving of experiment with ID {id}.',
        'error_secondary': 'Retry the scan first. Then inspect the nodes or the network.'
    },
    12: {
        'error_main': 'An error occurred during deletion of experiment with ID {id}.',
        'error_secondary': 'Retry the scan first. Then inspect the nodes or the network.'
    },


    


    100: {
        'error_main': 'Response from other boards is taking longer than expected.',
        'error_secondary': 'Wait for other responses.'
    },
    101: {
        'error_main': 'The firmware directory is empty.',
        'error_secondary': 'Upload a file first.'
    },
    102: {
        'error_main': 'The nodes configuration file <i>{file}</i> is empty.',
        'error_secondary': 'Configure a node in the json file.'
    },
    103: {
        'error_main': 'The are no experiments.',
        'error_secondary': 'Configure one.'
    },
    104: {
        'error_main': 'The are no <i>Running</i> experiments.',
        'error_secondary': 'Configure one.'
    },
        
}

def set_error_from_code(error_code=None, task_type=None, **kwargs):
    if(error_code is None):
        return {0: ''}

    tmp_dict['error_type'] = 'warning' if error_code >= 100 else 'danger'
        
    tmp_dict = errors[error_code]
    tmp_dict['error_main'] = tmp_dict['error_main'].format(**kwargs)

    return tmp_dict


dangers = {
    0 : '',
    
    # sign up and login
    1 : 'Email address already exists. Try to Log in.',
    2 : 'Passwords do not match.',
    3 : 'Passwords fields can\'t be empty.',
    4 : 'Email field can\'t be empty.',
    5 : 'Name field can\'t be empty.',
    6 : 'Email field not valid.',
    7 : 'Check your login detail and try again.',
    8 : 'Name cannot contain special characters or numbers',
    9 : 'Lastame cannot contain special characters or numbers',
    10 : 'Email cannot contain special characters other than @ and .',

    # update user
    20 : 'User not found.',

    # experiments
    30 : 'An error occurred during deletion of experiment with ID <b>{id}</b>.',
    31 : 'An error occurred during retrieval of experiment with ID <b>{id}</b>.',
    32 : 'An error occurred during creation of experiment with name <b>{name}</b>.',
    33 : 'An error occurred during reloading of experiment with name <b>{name}</b>.',
    34 : 'Name <b>{name}</b> of the experiment already used and not unique.',

    # nodes
    40 : 'Node with ID <b>{id}</b> not found.',

    # firmwares
    50: 'Payload not containing a file.',
    51: 'Filename cannot be empty.',
    52: '<i>Hex</i> format only allowed.',
    53: 'Firmware <b>{filename}</b> not existing.',
    53: 'An error occurred during deletion of firmware <b>{filename}</b>.',


}

warnings = {
    0 : '',

    # sign up and login
    101 : 'Username is too short.',
    102 : 'Password is too short.',
    103 : 'Lastname is too short.',

    # experiments
    130 : 'Experiments list is empty.',
    131 : 'Running experiments list is empty.',

    # nodes
    140 : 'The are no configured nodes. Add them first.',
}


def error(error_code, **kwargs):
    
    err = {}
    
    try:
    
        if error_code >= 100:
            err['type'] = 'warning'
            err['message'] = warnings[error_code].format(**kwargs)
        else:
            err['type'] = 'danger'
            err['message'] = dangers[error_code].format(**kwargs)
    
    except IndexError:
        print(error_code, '****')
        return {
            'type': 'danger',
            'message': 'An unknown error occurred.'
        }
        

    return err