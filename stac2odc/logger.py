

def logger_message(message: str, logger_op, is_verbose: bool):
    """Function to log operations more easily. This function verify if stac2odc
    is in a verbose mode and log.
    Args:
        message (str): Text to be logged
        logger_op (function): Logger operation. Function will be call to log the message
        is_verbose (bool): Flag indicates if stac2odc library is in a verbose mode
    """

    if is_verbose:
        logger_op(message)
