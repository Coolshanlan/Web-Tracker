import os, logging

def get_logger(name, filepath = None, overwrite_print=False):
    global print
    if logging.getLogger(name).hasHandlers():
        return logging.getLogger(name)
    
    if filepath is None:
        filepath = './logfile'
        if not os.path.exists(filepath):
            os.mkdir(filepath)
        filepath = f'./logfile/{name}.log'
    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(filepath,mode='w')


    console_format = logging.Formatter('%(asctime)10s  %(levelname)s  %(name)s  %(message)s')
    file_format = logging.Formatter('%(asctime)s  %(levelname)s  %(pathname)s -> %(funcName)s, line %(lineno)d  %(message)s'.expandtabs(30))


    console_handler.setFormatter(console_format)
    file_handler.setFormatter(file_format)

    console_handler.setLevel(logging.INFO)
    file_handler.setLevel(logging.DEBUG)

    logger = logging.getLogger(name)
    if overwrite_print:
        print = logger.info
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger