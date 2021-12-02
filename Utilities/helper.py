import copy
import os
import json
import shutil
import traceback
from datetime import datetime
from functools import reduce
# from HiLITDECoreLibraries.HCoreLoggerLibrary.constants.criticality import Criticality
# from HiLITDECoreLibraries.HCoreLoggerLibrary.service.logging_service import LoggingService


def get_file_name(file_path):
    return os.path.split(file_path)[1]


def create_data_mapping(json_file_path):
    # logger = LoggingService()
    # logger.print_log_level(Criticality.INFO, "[{}] -> Entering helper: {}".format(datetime.now(),
    #                                                                               create_data_mapping.__name__))
    try:

        with open(json_file_path, 'r', encoding="utf-8", errors='ignore') as json_file:
            data_total = json.load(json_file)
        # logger.print_log_level(Criticality.INFO, "[{}] -> Exiting helper: {}".format(datetime.now(),
        #                                                                               create_data_mapping.__name__))
        return data_total
    except Exception as e:
        print(e)
        # logger.print_log_level(Criticality.ERROR, "[{}] -> Exception in helper : {} - {} - {}".
        #                        format(datetime.now(), create_data_mapping.__name__, str(e), traceback.format_exc()))
        raise e


def extract_error_logs(temp_work_file_path, filename):
    # logger = LoggingService()
    # logger.print_log_level(Criticality.INFO, "[{}] -> Entering helper: {}".format(datetime.now(),
    #                                                                               extract_error_logs.__name__))
    log_file_path = os.path.join(temp_work_file_path, filename + ".log")

    if os.path.isfile(log_file_path):
        with open(log_file_path, "r", encoding="utf-8") as fp:
            log_data = fp.read()
            # logger.print_log_level(Criticality.INFO, "[{}] -> Exiting helper: {}".format(datetime.now(),
            #                                                                               extract_error_logs.__name__))
            return log_data
    else:
        # logger.print_log_level(Criticality.WARN, "[{}] -> Error in helper: {} Log file not formed"
        #                        .format(datetime.now(), extract_error_logs.__name__))
        return ""


def extract_narrative_data(temp_work_folder_path):
    # logger = LoggingService()
    # logger.print_log_level(Criticality.INFO, "[{}] -> Entering helper: {}".format(datetime.now(),
    #                                                                               extract_narrative_data.__name__))
    narrative_path = os.path.join(temp_work_folder_path, 'NarrativeFile.txt')
    if os.path.exists(narrative_path):
        with open(narrative_path, "r") as f:
            narrative_data = f.read()
    else:
        narrative_data = False
    # logger.print_log_level(Criticality.INFO, "[{}] -> Exiting helper: {}".format(datetime.now(),
    #                                                                               extract_narrative_data.__name__))
    return narrative_data


def check_null_json(json_data):
    #logger = LoggingService()
    # logger.print_log_level(Criticality.INFO, "[{}] -> Entering helper: {}".format(datetime.now(),
    #                                                                               check_null_json.__name__))
    data_total = copy.deepcopy(json_data)
    for i in range(len(data_total)):
        # Making every dict a list of dict
        if type(data_total[i]) is not list:
            data_total[i] = [data_total[i]]

    # Flattening all the list of lists to list of dict
    data_total = list(reduce(lambda x, y: x + y, data_total))

    for block in data_total:
        for key, val in block.items():
            if key.isupper() and val:
                return json_data
    # logger.print_log_level(Criticality.INFO, "[{}] -> Exiting helper: {}".format(datetime.now(),
    #                                                                              check_null_json.__name__))
    return False


def temp_file_remover(work_folder):
    #logger = LoggingService()
    try:
        # logger.print_log_level(Criticality.INFO, "[{}] -> Entering helper: {}".format(datetime.now(),
        #                                                                               temp_file_remover.__name__))
        if os.path.isdir(work_folder):
            shutil.rmtree(work_folder)
        # if os.path.isfile(json_file_path):
        #     os.remove(json_file_path)
        # logger.print_log_level(Criticality.INFO, "[{}] -> Exiting helper: {}".format(datetime.now(),
        #                                                                              temp_file_remover.__name__))
    except Exception as e:
        print(e)
        # logger.print_log_level(Criticality.ERROR, "[{}] -> Exception in helper : {} - {} - {}".
        #                        format(datetime.now(), temp_file_remover.__name__, str(e), traceback.format_exc()))

def get_filename(filepath):
    try:
        folder, filename = os.path.split(filepath)
        return folder, filename
    except Exception as e:
        return '', filepath