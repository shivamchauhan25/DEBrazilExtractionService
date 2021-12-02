import stomp
import json
import time
import traceback
import sys
import os
import logging

from datetime import datetime
from multiprocessing import Pool
from multiprocessing import cpu_count

from BrazilExtraction import main as brz_main
from constants import SERVICE_NAME, QUEUE_ADDRESS, QUEUE_PORT, QUEUE_USER, QUEUE_PASSWORD, QUEUE_DEST, EFS_PATH
from HiLITDECoreLibraries.Utilities.utils import get_span_id, get_trace_id, s3_enabled_download, check_queue_consumer,\
    push_in_queue
from constants import SERVICE_NAME, QUEUE_ADDRESS, QUEUE_PORT, QUEUE_USER, QUEUE_PASSWORD, QUEUE_DEST, users_queue, \
    passwords_queue, QUEUE_id
from HiLITDECoreLibraries.Utilities.utils import get_span_id, get_trace_id, s3_enabled_download
from HiLITDECoreLibraries.Utilities.decorator import zipkin_parent
from HiLITDECoreLibraries.HCoreLoggerLibrary.constants.criticality import Criticality
from HiLITDECoreLibraries.HCoreDAO.Utilities.create_connection import create_connection, close_all_session
from HiLITDECoreLibraries.HCoreLoggerLibrary.service.logging_service import LoggingService
from HiLITDECoreLibraries.Utilities.helper import move_file
from HiLITDECoreLibraries.Utilities.decorator import scrape_data
from HiLITDECoreLibraries.Utilities.authenticate_decorator import authenticate_func
from HiLITDECoreLibraries.Utilities.utils import check_queue_consumer


stomp_logger = logging.getLogger('stomp.py')
stomp_logger.setLevel(level=logging.DEBUG)
stomp_logger_stream_handler = logging.StreamHandler()
stomp_logger_stream_handler_formatter = logging.Formatter('%(asctime)s %(levelname)s %(lineno)d:%(filename)s(%(process)d) - %(message)s')
stomp_logger_stream_handler.setFormatter(stomp_logger_stream_handler_formatter)
stomp_logger.addHandler(stomp_logger_stream_handler)

@scrape_data
def connect_and_subscribe(conn):
    logger = LoggingService()
    conn.connect(QUEUE_USER, QUEUE_PASSWORD, wait=True)
    conn.subscribe(destination=QUEUE_DEST, id=int(QUEUE_id), ack='client-individual')
    logger.print_log_level(Criticality.INFO,
                           "[{}] Brazil queue: - Connected and Subscribed".format(datetime.now()))


class MyListener(stomp.ConnectionListener):
    msg = []
    @scrape_data
    def __init__(self, conn):
        self.conn = conn
        # self.msg = []
        self.pool= Pool(cpu_count())
        self.logger = LoggingService()

    @scrape_data
    def on_error(self, frame):
        self.logger.print_log_level(Criticality.INFO,
                               "[{}] Brazil queue: - Received an error - {} ".format(
                                   datetime.now(), frame.body))
    @scrape_data
    def on_message(self, frame):
        headers = frame.headers
        queue_object = json.loads(frame.body)
        self.logger.print_log_level(Criticality.INFO,
                               "[{}] Brazil queue: - Message received - {} ".format(
                                   datetime.now(), queue_object))
        # self.msg.append(frame.body)
        # self.pool.starmap_async(brazil, zip([queue_object]))
        brazil(queue_object)
        self.conn.ack(id=headers["message-id"], subscription=headers["subscription"])

    @scrape_data
    def on_disconnected(self):
        self.logger.print_log_level(Criticality.ERROR,
                               "[{}] Exception in Brazil queue: - disconnected ".format(
                                   datetime.now()))
        # connect_and_subscribe(self.conn)

@scrape_data
def listen_queue():
    create_connection()
    conn = stomp.Connection([(QUEUE_ADDRESS, QUEUE_PORT)])
    a = MyListener(conn)
    conn.set_listener('', a)
    connect_and_subscribe(conn)
    try:
        while True:
            time.sleep(5)
            if check_queue_consumer(QUEUE_DEST.split('/')[-1], QUEUE_USER, QUEUE_PASSWORD):
                print("[{}] Trying to reconnect".format(datetime.now()))
                try:
                    try:
                        conn.disconnect()
                    except Exception as e:
                        print("[{}] Error in disconnecting - {}".format(datetime.now(), str(traceback.format_exc())))
                    connect_and_subscribe(conn)
                    print("[{}] Connected".format(datetime.now()))
                except Exception as e:
                    print("[{}] Error in connecting - {}".format(datetime.now(), str(traceback.format_exc())))
    except KeyboardInterrupt:
        print('interrupted - so exiting!')
    conn.disconnect()

@scrape_data
@zipkin_parent('BrazilQueue')
def brazil(data):
    logger = LoggingService()
    try:
        file_path = data['file_path']
        s3_flag = data['s3_flag']
        request_id = data['request_id']
        s3_key = None
        if s3_flag:
            s3_key = file_path
        INPUT_PATH = os.path.abspath(os.path.join('.', 'input'))
        input_file_path = s3_enabled_download(s3_flag, s3_key, file_path, INPUT_PATH)
        output = brz_main(input_file_path, request_id)
        logger.print_log_level(Criticality.INFO,
                               "[{}] Inside BrazilQueue: - {} - request id - {} output - {}".format(
                                   datetime.now(), brazil.__name__, str(request_id), output))
        # if output['success']:
        #     move_file(input_file_path, EFS_PATH, 'archive/brazil')
        # else:
        #     move_file(input_file_path, EFS_PATH, 'error/brazil')
        close_all_session()
    except Exception as e:
        try:
            push = push_in_queue('DE_ERROR', data, QUEUE_USER, QUEUE_PASSWORD,
                                 zipkin_service_name='BrazilExtractionQueue', new_span_name='InsertingInQueue',
                                 new_span=True)
            logger.print_log_level(Criticality.ERROR,
                                   "[{}] Entered data in Error queue. ".format(
                                       datetime.now()))
        except Exception as exp:
            logger.print_log_level(Criticality.ERROR,
                                   "[{}] Unable to enter data in Error queue: {} ".format(
                                       datetime.now(),str(traceback.format_exc())))
        logger.log_event("[{}] Exception in GatmQueue: {} - {} - Exception {}".format(
            datetime.now(), brazil.__name__, str(traceback.format_exc()), str(e)), get_span_id(),
            get_trace_id(), brazil.__name__, sys.exc_info()[-1].tb_lineno, service_name=SERVICE_NAME,
            criticality=Criticality.ERROR)
        close_all_session()


@authenticate_func
def start_up(flask_api_status=False, users=users_queue,passwords=passwords_queue):
    listen_queue()


if __name__ == '__main__':
    start_up(flask_api_status=False, users=users_queue,passwords=passwords_queue)