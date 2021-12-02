import base64
import os
import sys
import traceback
from datetime import datetime
from copy import deepcopy
import json

from BrazilLibrary.main import main as extractor
from constants import SERVICE_NAME, MAIL_BODY_PATH, SOURCE_LANGUAGE, VALIDATION, REDACTION, NARRATIVE
from Utilities.utils import get_filename, translate_text, find_ae, \
    get_form_redaction_request_json, get_email_redaction_request_json, get_validation_input_json, \
    get_narrative_library_input_json
from HiLITDECoreLibraries.HCoreDAO.models.db_procs import DBProcs
from HiLITDECoreLibraries.HCoreLoggerLibrary.constants.criticality import Criticality
from HiLITDECoreLibraries.HCoreLoggerLibrary.service.logging_service import LoggingService
from HiLITDECoreLibraries.Utilities.convert_json import json_converter
from HiLITDECoreLibraries.Utilities.decorator import try_except
from HiLITDECoreLibraries.Utilities.update_pqc import update_pqc
from HiLITDECoreLibraries.Utilities.utils import do_service, get_null_json, get_span_id, get_trace_id, \
    s3_enabled_download, translate_json
from HiLITDECoreLibraries.Utilities.upload_s3 import s3_sns_de
from HiLITDECoreLibraries.Utilities.decorator import scrape_data

# def listen_queue():
#     try:
#         async.call(main)
#
#     except:

@scrape_data
@try_except
def main(source_path, request_id, meta_dict=None):
    logger = LoggingService()
    logger.print_log_level(Criticality.INFO, "[{}] -> Entering BrazilExtraction: {} - Request ID - {}".
                           format(datetime.now(), main.__name__, str(request_id)))
    filename = get_filename(source_path)
    db_obj = DBProcs(request_id)
    attachment_list = []
    json_insert_flag = False
    try:
        db_obj.initialize_process()
        db_obj.update_locale("PORTUGUESE")
        # json_insert_flag = True

        # calling the extraction library
        data_total, narrative = extractor(source_path, request_id)
        # if extraction fails, update the flag
        if data_total is False:
            data_total = get_null_json()
            json_insert_flag = False

        # Translation of JSON - Portuguese to English
        translated_json = translate_json(data_total, SOURCE_LANGUAGE)

        # Translation of the Narrative
        translated_narrative = translate_text(narrative, SOURCE_LANGUAGE)

        # Processing the Narrative
        narrative_library_input_json = get_narrative_library_input_json(translated_json, translated_narrative,
                                                                        request_id)
        try:
            translated_json = do_service(application_name=NARRATIVE, service="/process_json",
                                         data=narrative_library_input_json, method="POST", zipkin_service_name=SERVICE_NAME,
                                         new_span_name="ProcessNarrative", new_span=True)
        except Exception as e:
            logger.print_log_level(Criticality.ERROR, "[{}] -> Error in Calling narrative: {} - Request ID - {} error - {} - {}".
                                   format(datetime.now(), main.__name__, str(request_id), str(e), str(traceback.format_exc())))

        # call validation service(API cal with eureka) inputting the JSON and request ID - returns validated JSON
        validation_input_json = get_validation_input_json(translated_json, request_id)
        try:
            validated_translated_json = do_service(application_name=VALIDATION, service="/validate_json",
                                                   data=validation_input_json, method="POST",
                                                   zipkin_service_name=SERVICE_NAME, new_span_name="Validation",
                                                   new_span=True)
            validated_translated_json = validated_translated_json["output"]
        except Exception as e:
            validated_translated_json=deepcopy(translated_json)
            logger.print_log_level(Criticality.ERROR, "[{}] -> Error in Calling validation:  {} - Request ID - {}  error - {} - {}".
                                   format(datetime.now(), main.__name__, str(request_id), str(e), str(traceback.format_exc())))

        coi = "BRAZIL"
        has_ae = find_ae(validated_translated_json)

        # Converting the Json to RT_ENTITY JSON
        validated_translated_json = json_converter(validated_translated_json)
        validated_translated_json = update_pqc(db_obj, validated_translated_json)

        # Insert the Json to the DataBase
        json_insert_flag = db_obj.insert_json(json.dumps(validated_translated_json), meta_dict)

        # todo - later
        # logger.info("Coded Cols : %s" % str(coded_cols))
        # if coded_cols:
        #     db_obj.insert_verbatim_coded('CIOMS', db_obj.parent_id, coded_cols, 0)

        if not json_insert_flag:
            data_total = None

        # redact form
        redacted_entities = db_obj.get_coi_fields(coi)
        request_json, redacted_file_name,original_byte_array = get_form_redaction_request_json(source_path, data_total, narrative,
                                                                           redacted_entities, coi, request_id)
        try:
            redacted_pdf_bytes = do_service(application_name=REDACTION, service="/redact/", data=request_json,
                                            method="POST", zipkin_service_name=SERVICE_NAME,
                                            new_span_name="CallingFormRedaction", new_span=True)
        except Exception as e:

            logger.print_log_level(Criticality.ERROR, "[{}] -> Error in Calling Redaction of forms: {} - Request ID - {} -error - {} - {}".
                                   format(datetime.now(), main.__name__, str(request_id), str(e), str(traceback.format_exc())))
            redacted_pdf_bytes = {"success":True, "redacted_byte_array":original_byte_array}
        if redacted_pdf_bytes["success"]:
            redacted_pdf_bytes = base64.b64decode(redacted_pdf_bytes["redacted_byte_array"])
            efs_file_path, file_key, is_s3_enabled = db_obj.proc_e2b_email_attachment_insert(redacted_file_name,
                                                                                             redacted_pdf_bytes,
                                                                                             "global")
            attachment_list.append({'filename': redacted_file_name, 'filepath': efs_file_path, 's3_key': file_key,
                                    'is_file_uploaded_on_s3': is_s3_enabled})
        else:
            logger.print_log_level(Criticality.ERROR, "[{}] -> BrazilExtraction: {} - Request ID - {} - Redaction "
                                                      "failed".format(datetime.now(), main.__name__, str(request_id)))

        # redact email_content
        # mail_body = None
        mail_body, mail_body_byte_array= db_obj.get_e2b_mail()
        # mail_body_dict = db_obj.get_e2b_mail()
        # if mail_body_dict:
        #     input_path = s3_enabled_download(mail_body_dict["s3_enabled"], mail_body_dict["file_key"],
        #                                      mail_body_dict["file_path"], MAIL_BODY_PATH)
        #
        #     if os.path.exists(input_path):
        #         with open(input_path, "rb") as f:
        #             html = f.read()
        #             mail_body = html.decode()
        #         os.remove(input_path)

        if mail_body:
            request_json, redacted_file_name = get_email_redaction_request_json(mail_body, data_total,
                                                                                redacted_entities, request_id,
                                                                                source_lang=None)
            try:
                redacted_pdf_dict = do_service(application_name=REDACTION, service="/redact_email/", data=request_json,
                                               method="POST", zipkin_service_name=SERVICE_NAME,
                                               new_span_name="CallingEmailRedaction", new_span=True)
            except Exception as e:
                logger.print_log_level(Criticality.ERROR, "[{}] -> Error in Calling Redaction of email body: {} - Request ID - {} -error - {} - {}".
                                       format(datetime.now(), main.__name__, str(request_id), str(e), str(traceback.format_exc())))
                redacted_pdf_dict = {'global': None, 'original': mail_body_byte_array, 'translated_pdf': None}
            global_redacted = redacted_pdf_dict['global']
            original_redacted = redacted_pdf_dict['original']


            if original_redacted is not None:
                original_redacted = base64.b64decode(original_redacted)
                efs_file_path, file_key, is_s3_enabled = db_obj.proc_e2b_email_attachment_insert(redacted_file_name,
                                                                                                 original_redacted,
                                                                                                 "global")
                attachment_list.append({'filename': redacted_file_name, 'filepath': efs_file_path, 's3_key': file_key,
                                        'is_file_uploaded_on_s3': is_s3_enabled})
            # if global_redacted is not None:
            #     global_redacted = base64.b64decode(global_redacted)
            #     translated_redacted_filename = redacted_file_name.split("_redacted.pdf")[0] + '_translated_redacted.pdf'
            #     efs_file_path, file_key, is_s3_enabled = db_obj.proc_e2b_email_attachment_insert(
            #         translated_redacted_filename, global_redacted, "global")
            #     attachment_list.append({'filename': translated_redacted_filename, 'filepath': efs_file_path,
            #                             's3_key': file_key, 'is_file_uploaded_on_s3': is_s3_enabled})

        if not json_insert_flag:
            logger.print_log_level(Criticality.WARN, "[{}] -> BrazilExtraction: {} - Request ID - {} - Inserting NUll "
                                                     "JSON".format(datetime.now(), main.__name__, str(request_id)))
            null_json = get_null_json()
            json_insert_flag = db_obj.insert_json(json.dumps(null_json), meta_dict)
            db_obj.update_status(2)
        else:
            db_obj.update_status(3)

        db_obj.update_parent(coi=coi, has_ae=has_ae)

        logger.print_log_level(Criticality.INFO, "[{}] -> Exiting BrazilExtraction: {} - Request ID - {}".
                               format(datetime.now(), main.__name__, str(request_id)))
        db_obj.close()

        return {'success': True,
                'attachments': attachment_list,
                'json': validated_translated_json}

    except Exception as e:
        logger.log_event("[{}] Exception in BrazilExtraction: {} - Request id : {} - {} - Exception {}".format(
            datetime.now(), main.__name__, str(request_id), str(traceback.format_exc()), str(e)), get_span_id(),
            get_trace_id(), main.__name__, sys.exc_info()[-1].tb_lineno, service_name=SERVICE_NAME,
            criticality=Criticality.ERROR)
        null_json = get_null_json()
        if not json_insert_flag:
            db_obj.insert_json(json.dumps(null_json), meta_dict)
        s3_sns_de(request_id, 'BRAZIL', str(traceback.format_exc()))
        db_obj.update_status(2)
        db_obj.update_parent()
        db_obj.close()

        return {'success': False}
