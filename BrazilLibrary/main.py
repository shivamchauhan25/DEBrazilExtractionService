import os
import shutil
import sys
import traceback
from datetime import datetime

from py_zipkin.zipkin import zipkin_client_span

from BrazilLibrary.Extractor.helper import create_data_mapping, get_file_name, check_null_json, extract_error_logs, \
    extract_narrative_data, temp_file_remover
from BrazilLibrary.Extractor.brazil_extractor import main_function
from constants import SERVICE_NAME, EXTRACTION_FOLDER_PATH, LIBRARY_FOLDER_PATH
from Utilities.CheckboxLibrary.checkbox_module import main_function as checkbox_pdf_generator
# from HiLITDECoreLibraries.HCoreLoggerLibrary.constants.criticality import Criticality
# from HiLITDECoreLibraries.HCoreLoggerLibrary.service.logging_service import LoggingService
# from HiLITDECoreLibraries.Utilities.utils import get_span_id, get_trace_id
# from HiLITDECoreLibraries.Utilities.decorator import scrape_data
# from HiLITDECoreLibraries.HCoreDAO.Utilities.create_connection import create_connection
#@scrape_data
@zipkin_client_span(service_name=SERVICE_NAME, span_name='BrazilLibrary')
def main(source_path, request_id):
    #create_connection()
    # logger = LoggingService()
    # logger.print_log_level(Criticality.INFO, "[{}] -> Entering BrazilLibrary: {}".format(datetime.now(), main.__name__))
    # calling the Brazil extraction code
    filename = get_file_name(source_path)

    work_folder = os.path.abspath(os.path.join(EXTRACTION_FOLDER_PATH, "work"))

    final_folder = os.path.abspath(os.path.join(EXTRACTION_FOLDER_PATH, "final"))

    temp_work_folder = "work_" + str(request_id)
    temp_work_folder_path = os.path.abspath(os.path.join(work_folder, temp_work_folder))
    if not os.path.exists(temp_work_folder_path):
        os.makedirs(temp_work_folder_path)

    # json_file_name = str(request_id) + '.json'
    # json_file_path = os.path.join(final_folder, json_file_name)
    narrative_data = None
    try:
        # with open(os.path.join(temp_work_folder_path, "sh_log_file_path.txt"), 'w+') as fp:
        #     fp.write('%s' % temp_work_folder_path.strip())

        # Copying input file inside the extractor folder
        #extraction_pdf_path = os.path.join(EXTRACTION_FOLDER_PATH, filename)
        shutil.copy(source_path, temp_work_folder_path)

        # os.chdir(EXTRACTION_FOLDER_PATH)

        # Checkbox marked PDF
        file_path  = os.path.abspath(os.path.join(temp_work_folder_path, filename))
        checkbox_marked_file_path = checkbox_pdf_generator(file_path, "BRZ")

        #print(checkbox_marked_file_path)

        # main_batch_file = "bash extraction.sh"
        #
        # os.system(main_batch_file + ' "' + filename + '" ' + ' "' + str(request_id) + '" ')
        #
        # os.chdir(LIBRARY_FOLDER_PATH)

        # narrative_data = extract_narrative_data(temp_work_folder_path)

        # loading the main JSON
        # data_total = create_data_mapping(json_file_path)

        # Checking whether JSON is NULL if NULL then raise - before raise check if narrative exists and extract the
        # data from file
        # data_total = check_null_json(data_total)
        data_total, narrative_data = main_function(request_id, checkbox_marked_file_path)
        # if data_total is False:
        #     # shell_log_data = extract_error_logs(temp_work_folder_path, filename)
        #     logger.log_event("[{}] -> NULL JSON issue encountered in BrazilLibrary: {}".
        #                      format(datetime.now(), main.__name__), get_span_id(), get_trace_id(),
        #                      main.__name__, 60, service_name=SERVICE_NAME, criticality=Criticality.ERROR)
        temp_file_remover(temp_work_folder_path)
        return data_total, narrative_data
    except Exception as e:
        # shell_log_data = extract_error_logs(temp_work_folder_path, filename)
         # todo ask sahil about the allowed no of characters in the db col
        print(e)
        # logger.log_event("[{}] -> Exception in BrazilLibrary: {} - request id : {} - {} - {}".
        #                  format(datetime.now(), main.__name__, str(request_id), str(e),
        #                         traceback.format_exc()), get_span_id(), get_trace_id(), main.__name__,
        #                  sys.exc_info()[-1].tb_lineno, service_name=SERVICE_NAME, criticality=Criticality.ERROR)
        narrative_data = extract_narrative_data(temp_work_folder_path)
        temp_file_remover(temp_work_folder_path)
        return False, narrative_data
if __name__ == '__main__':
    finaljson, narrative = main(
        r"C:\Users\shivam.kumar\Downloads\Brazil Unit test cases files\brazil_3.pdf",
        "11111")
    print(finaljson)
