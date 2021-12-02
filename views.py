

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

import traceback
import socket
import sys
import os

from BrazilExtraction import main as brz_main

from HiLITDECoreLibraries.HCoreDAO.models.db_procs import DBProcs
from HiLITDECoreLibraries.Utilities.cryptoengine import decrypt_with_AES
from constants import APPLICATION_NAME, APPLICATION_INSTANCE, APPLICATION_PORT, SERVICE_NAME, users_view, passwords_view
from HiLITDECoreLibraries.Utilities.decorator import zipkin_child, eureka_registration
from HiLITDECoreLibraries.Utilities.authenticate_decorator import authenticate_func
from HiLITDECoreLibraries.Utilities.utils import s3_enabled_download
from HiLITDECoreLibraries.HCoreLoggerLibrary.constants.criticality import Criticality
from HiLITDECoreLibraries.Utilities.utils import get_span_id, get_trace_id
from HiLITDECoreLibraries.HCoreDAO.Utilities.create_connection import create_connection
from HiLITDECoreLibraries.HCoreLoggerLibrary.service.logging_service import LoggingService
from HiLITDECoreLibraries.Utilities.auth_token import set_tenant_id, set_env_key

from HiLITDECoreLibraries.Utilities.helper import move_file
from HiLITDECoreLibraries.Utilities.decorator import scrape_data

app = Flask(__name__)
app.config["DEBUG"] = True
CORS(app)

@scrape_data
@app.route('/brazil_extract/', methods=['POST'])
@zipkin_child('BrazilExtractionAPI', port=APPLICATION_PORT)
def main_extraction():
    # env_key = 'default'
    # tenant_id = 1
    # if 'env' in request.json:
    #     env_key = request.json['env']
    # if 'tenant_id' in request.json:
    #     tenant_id = request.json['tenant_id']
    # create_connection(env_key)
    # set_env_key(env_key, True)
    # set_tenant_id(tenant_id, True)
    # # create_connection()
    logger= LoggingService()
    try:
        file_path = request.json['file_path']
        s3_key = request.json['s3_key']
        is_file_uploaded_on_s3 = request.json['is_file_uploaded_on_s3']
        request_id = request.json['request_id']
        meta_dict = None
        if 'meta_dict' in request.json:
            meta_dict = request.json['meta_dict']
        logger.print_log_level(Criticality.INFO,
                               "[{}] Inside BrazilExtractionAPI: - {} - request id - {}".format(
                                   datetime.now(), main_extraction.__name__, str(request_id)))
        INPUT_PATH = os.path.abspath(os.path.join('.', 'input'))
        input_file_path = s3_enabled_download(is_file_uploaded_on_s3, s3_key, file_path, INPUT_PATH)
        output = brz_main(input_file_path, request_id, meta_dict)
        logger.print_log_level(Criticality.INFO,
                              "[{}] Inside BrazilExtractionAPI: - {} - request id - {} -- ouput - {}".format(
                                  datetime.now(), main_extraction.__name__, str(request_id), output))
        return jsonify(output)
    except Exception as e:
        logger.log_event("[{}] Exception in BrazilExtractionAPI: {} - {} - Exception {}".format(
            datetime.now(), main_extraction.__name__, str(traceback.format_exc()), str(e)), get_span_id(),
            get_trace_id(), main_extraction.__name__, sys.exc_info()[-1].tb_lineno, service_name=SERVICE_NAME,
            criticality=Criticality.ERROR)
        return jsonify({})


@app.before_request
def before_request():
    env_key = 'default'
    tenant_id = 1
    if 'env' in request.json:
        env_key = request.json['env']
    if 'tenant_id' in request.json:
        tenant_id = request.json['tenant_id']
    create_connection(env_key)
    set_env_key(env_key, True)
    set_tenant_id(tenant_id, True)
    logger = LoggingService()
    try:
        auth_token = request.headers['authentication_token']
        auth_token = decrypt_with_AES(auth_token)
        logger.print_log_level(Criticality.INFO,
                               "[{}] Inside Brazil http interceptor: - {}".format(
                                   datetime.now(), before_request.__name__))
        db_auth_object = DBProcs(request_id=0)
        auth_user_name = db_auth_object.authenticate(auth_token)
        if auth_user_name:
            logger.print_log_level(Criticality.INFO,
                                   "[{}] Authentication Successful: - {}".format(
                                       datetime.now(), before_request.__name__))
        else:
            logger.print_log_level(Criticality.INFO,
                                   "[{}] Authentication Failed: - {}".format(
                                       datetime.now(), before_request.__name__))
            print('Unauthorised Access')
            return {'success': False,'message':'Unauthorised Access'}
    except Exception as e:
        logger.print_log_level(Criticality.ERROR,
                               "[{}] Authentication failed dur to error - {}. Redirecting to service.".format(
                                   datetime.now(), str(traceback.format_exc)))

@scrape_data
@eureka_registration
def main(host_ip=socket.gethostbyname(socket.gethostname()), port=APPLICATION_PORT,
         application_name=APPLICATION_NAME, instance=APPLICATION_INSTANCE):
    print("Registered on Eureka")
    # app.run(host=host_ip, port=port, debug=True, threaded=True, use_reloader=False)


@authenticate_func
def start_up(flask_api_status=True,users=users_view, passwords=passwords_view):
    main(host_ip=socket.gethostbyname(socket.gethostname()), port=int(APPLICATION_PORT),
         application_name=APPLICATION_NAME, instance=APPLICATION_INSTANCE)


if __name__ == '__main__':
    start_up(flask_api_status=True,users=users_view, passwords=passwords_view)
