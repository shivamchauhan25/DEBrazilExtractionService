import base64
import json
import os
import re
import requests
import traceback
from datetime import datetime

from constants import EXCLUDE_TRANSLATION_JSON_KEYS, TRANSLATE, FILE_TYPE, SOURCE_LANGUAGE, SERVICE_NAME
from HiLITDECoreLibraries.HCoreLoggerLibrary.constants.criticality import Criticality
from HiLITDECoreLibraries.HCoreLoggerLibrary.service.logging_service import LoggingService
from HiLITDECoreLibraries.Utilities.decorator import try_except
from HiLITDECoreLibraries.Utilities.utils import translate_codelist_data, do_service
from HiLITDECoreLibraries.Utilities.auth_token import get_tenant_id, get_env_key, get_flask_api
from HiLITDECoreLibraries.Utilities.decorator import scrape_data

@scrape_data
def get_filename(filepath):
    logger = LoggingService()
    try:
        logger.print_log_level(Criticality.INFO, "[{}] -> Entering utils: {}".format(datetime.now(),
                                                                                     get_filename.__name__))
        folder, filename = os.path.split(filepath)
        logger.print_log_level(Criticality.INFO, "[{}] -> Exiting utils: {}".format(datetime.now(),
                                                                                    get_filename.__name__))
        return filename
    except Exception as e:
        logger.print_log_level(Criticality.ERROR, "[{}] -> Exception in utils : {} - {} - {}".
                               format(datetime.now(), get_filename.__name__, str(e), traceback.format_exc()))
        return filepath

@scrape_data
def get_ext(filename):
    logger = LoggingService()
    try:
        logger.print_log_level(Criticality.INFO, "[{}] -> Entering utils: {}".format(datetime.now(), get_ext.__name__))
        file_name, ext = os.path.splitext(filename)
        ext = re.sub(r"\.", "", ext)
        logger.print_log_level(Criticality.INFO, "[{}] -> Exiting utils: {}".format(datetime.now(), get_ext.__name__))
        return ext
    except Exception as e:
        logger.print_log_level(Criticality.ERROR, "[{}] -> Exception in utils : {} - {} - {}".
                               format(datetime.now(), get_ext.__name__, str(e), traceback.format_exc()))
        return False

@scrape_data
@try_except
def generate_byte_array(file_path):
    logger = LoggingService()
    logger.print_log_level(Criticality.INFO, "[{}] -> Entering utils: {}".format(datetime.now(),
                                                                                 generate_byte_array.__name__))
    fp = open(file_path, "rb")
    byte_array = fp.read()
    fp.close()
    logger.print_log_level(Criticality.INFO, "[{}] -> Exiting utils: {}".format(datetime.now(),
                                                                                generate_byte_array.__name__))
    return byte_array

@scrape_data
def translate_text(text, src_lang_code='auto', target_lang='en'):
    logger = LoggingService()
    logger.print_log_level(Criticality.INFO, "[{}] -> Entering utils: {}".format(datetime.now(),
                                                                                 translate_text.__name__))
    # using translation API
    #url = TRANSLATE_TEXT
    data = {'srcLang': src_lang_code, 'tgtLang': target_lang, 'text': text}
    try:
        result = do_service(TRANSLATE, service='/hilittranslatorservice/translate/translateText',
                            method='POST', data=data,
                            zipkin_service_name=SERVICE_NAME, new_span_name='CallingTranslate', new_span=True)
        if result:
            translated_text = result['message']
            translated_text = re.sub(r"<span.*\n?.*'>", "", translated_text)
            translated_text = re.sub(r"</span>", "", translated_text)
            if src_lang_code == 'auto':
                src_lang_code = result['project']['detectedLanguage']
            logger.print_log_level(Criticality.INFO,
                                   "[{}] -> Exiting translation: {}".format(datetime.now(), translate_text.__name__))
            return (translated_text, src_lang_code)
        logger.print_log_level(Criticality.WARN,
                               "[{}] -> Exiting translation without translation success: {}".
                               format(datetime.now(), translate_text.__name__))
        return text, 'en'
    except Exception as e:
        logger.print_log_level(Criticality.ERROR, "[{}] -> Exception in utils : {} - {} - {}".
                               format(datetime.now(), translate_text.__name__, str(e), traceback.format_exc()))
        return text, 'en'

@scrape_data
@try_except
def translate_dict(data, excluded_keys, src_lang_code='auto'):
    logger = LoggingService()
    try:
        logger.print_log_level(Criticality.INFO, "[{}] -> Entering utils: {}".format(datetime.now(),
                                                                                     translate_dict.__name__))
        for key, val in data.items():
            if val and key not in excluded_keys:
                # logger.info("Original: %s " % str(data[key]))
                translated_data = translate_codelist_data(val, source_lang_code=src_lang_code, target_lang_code='en')

                # NR is getting translated as No
                if translated_data and val.strip() != "NR":
                    data[key] = translated_data[0].replace("\'", "")
                    # logger.info("Translated: %s" % str(data[key]))

        logger.print_log_level(Criticality.INFO, "[{}] -> Exiting utils: {}".format(datetime.now(),
                                                                                    translate_dict.__name__))
        return data
    except Exception as e:
        logger.print_log_level(Criticality.ERROR, "[{}] -> Exception in utils : {} - {} - {}".
                               format(datetime.now(), translate_dict.__name__, str(e), traceback.format_exc()))
        return data

@scrape_data
@try_except
def translate_json(data_total, src_lang_code='auto'):
    logger = LoggingService()
    try:
        logger.print_log_level(Criticality.INFO, "[{}] -> Entering utils: {}".format(datetime.now(),
                                                                                     translate_json.__name__))
        with open(EXCLUDE_TRANSLATION_JSON_KEYS, "r") as fp:
            excluded_keys = fp.readlines()

        # Removing the new line from the excluded_keys
        excluded_keys = [i.replace('\n', '') for i in excluded_keys]
        for i in range(0, len(data_total)):
            data = data_total[i]
            # logger.info("Data: %s" % str(data))
            if type(data) == list:
                translated_data = []
                for list_val in data:
                    translated_data.append(translate_dict(list_val, excluded_keys, src_lang_code))
                data_total[i] = translated_data
            elif type(data) == dict:
                data_total[i] = translate_dict(data, excluded_keys, src_lang_code)
        logger.print_log_level(Criticality.INFO, "[{}] -> Exiting utils: {}".format(datetime.now(),
                                                                                    translate_json.__name__))
        return data_total
    except Exception as e:
        logger.print_log_level(Criticality.ERROR, "[{}] -> Exception in utils : {} - {} - {}".
                               format(datetime.now(), translate_json.__name__, str(e), traceback.format_exc()))
        return data_total

@scrape_data
def find_coi(data_total):
    logger = LoggingService()
    try:
        logger.print_log_level(Criticality.INFO, "[{}] -> Entering utils: {}".format(datetime.now(), find_coi.__name__))
        coi_list = [x['OCCURCOUNTRY'] for x in data_total if isinstance(x, dict) and 'OCCURCOUNTRY' in x]
        if coi_list:
            coi = coi_list[0]
            logger.print_log_level(Criticality.INFO,
                                   "[{}] -> Exiting utils: {}".format(datetime.now(), find_coi.__name__))
            return coi
        logger.print_log_level(Criticality.WARN, "[{}] -> Exiting utils: {}".format(datetime.now(), find_coi.__name__))
        return None
    except Exception as e:
        logger.print_log_level(Criticality.ERROR, "[{}] -> Exception in utils : {} - {} - {}".
                               format(datetime.now(), find_coi.__name__, str(e), traceback.format_exc()))
        return None

@scrape_data
def find_ae(data_total):
    logger = LoggingService()
    try:
        logger.print_log_level(Criticality.INFO, "[{}] -> Entering utils: {}".format(datetime.now(), find_ae.__name__))
        ae_dict = [x['PRIMARYSOURCEREACTION'] for x in data_total if isinstance(x, dict) and
                   'PRIMARYSOURCEREACTION' in x]
        ae_list = [y['PRIMARYSOURCEREACTION'] for x in data_total if isinstance(x, list) for y in x if
                   'PRIMARYSOURCEREACTION' in y]
        if ae_dict:
            if ae_dict[0] is not None:
                return 1
        elif len(ae_list) > 0:
            if ae_list[0] is not None:
                return 1
        logger.print_log_level(Criticality.INFO, "[{}] -> Exiting utils: {}".format(datetime.now(), find_ae.__name__))
        return 0
    except Exception as e:
        logger.print_log_level(Criticality.ERROR, "[{}] -> Exception in utils : {} - {} - {}".
                               format(datetime.now(), find_ae.__name__, str(e), traceback.format_exc()))
        return 0

@scrape_data
def get_form_redaction_request_json(filepath, json_data, narrative_data, redacted_entities, country, request_id):
    logger = LoggingService()
    flask_status = get_flask_api()
    logger.print_log_level(Criticality.INFO, "[{}] -> Entering utils: {}".format(
        datetime.now(), get_form_redaction_request_json.__name__))
    file_name = get_filename(filepath)
    file_name_without_extension = os.path.splitext(file_name)[0]
    extension = get_ext(file_name)
    redacted_file_name = file_name_without_extension + "_" + str(request_id)+ "_redacted." + extension
    byte_pdf = generate_byte_array(filepath)
    base64_encoded_string = base64.b64encode(byte_pdf)
    decoded_byte_array = base64_encoded_string.decode('ascii')
    data = {"pdf": decoded_byte_array, "file_type": FILE_TYPE, "json": json_data, "extension": extension,
            "narrative_text": narrative_data, "source_lang": SOURCE_LANGUAGE, "redacted_entities": redacted_entities,
            "coi": country, "env":get_env_key(flask_status),
                        "tenant_id": get_tenant_id(flask_status)}
    json_input = json.dumps(data)

    logger.print_log_level(Criticality.INFO, "[{}] -> Exiting utils: {}".format(
        datetime.now(), get_form_redaction_request_json.__name__))
    return json_input, redacted_file_name, decoded_byte_array

@scrape_data
def get_email_redaction_request_json(mail_body, json_data, redacted_entities, request_id, source_lang):
    logger = LoggingService()
    flask_status = get_flask_api()
    logger.print_log_level(Criticality.INFO, "[{}] -> Entering utils: {}".format(
        datetime.now(), get_email_redaction_request_json.__name__))
    # file_extension = get_ext(file_name)
    redacted_filename = "EmailContent_" + str(request_id) + "_redacted.pdf"
    data = {"merged_html": mail_body, "content": None, "json": json_data, "extension": 'html',
            "signature": None, "source_lang": source_lang, "redacted_entities": redacted_entities, "env":get_env_key(flask_status),
                        "tenant_id": get_tenant_id(flask_status)}
    json_input = json.dumps(data)

    logger.print_log_level(Criticality.INFO, "[{}] -> Exiting utils: {}".format(
        datetime.now(), get_email_redaction_request_json.__name__))
    return json_input, redacted_filename

@scrape_data
def get_validation_input_json(data_total, request_id):
    logger = LoggingService()
    flask_status = get_flask_api()
    logger.print_log_level(Criticality.INFO, "[{}] -> Entering utils: {}".format(datetime.now(),
                                                                                 get_validation_input_json.__name__))
    validation_input = {"input_json": data_total, "request_id": request_id, "env":get_env_key(flask_status),
                        "tenant_id": get_tenant_id(flask_status)}
    validation_input = json.dumps(validation_input)
    logger.print_log_level(Criticality.INFO, "[{}] -> Exiting utils: {}".format(datetime.now(),
                                                                                get_validation_input_json.__name__))
    return validation_input

@scrape_data
def get_narrative_library_input_json(data_total, narrative_data, request_id):
    flask_status = get_flask_api()
    logger = LoggingService()
    logger.print_log_level(Criticality.INFO, "[{}] -> Entering utils: {}".
                           format(datetime.now(), get_narrative_library_input_json.__name__))
    narrative_library_input = {"json_data": data_total, "narrative_data": narrative_data, "request_id": request_id,"env":get_env_key(flask_status),
                        "tenant_id": get_tenant_id(flask_status)}
    narrative_library_input = json.dumps(narrative_library_input)
    logger.print_log_level(Criticality.INFO, "[{}] -> Exiting utils: {}".
                           format(datetime.now(), get_narrative_library_input_json.__name__))
    return narrative_library_input
if __name__ == '__main__':
    ek = ['OCCURCOUNTRY', 'table_name', 'parent_tag', 'seq_num', 'prod_seq_num', 'PATIENTDRUGSTARTDATE', 'REACTIONSTARTDATE', 'REACTIONSTARTDATERES', 'REACTIONENDDATE', 'REACTIONENDDATERES', 'HOSPADMISSIONDATE_EXTENSION', 'HOSPDISCHARGEDATE_EXTENSION', 'HOSPADMISSIONDATERES', 'HOSPDISCHARGEDATERES', 'SERIOUSNESSDEATH', 'SERIOUSNESSDISABLING', 'SERIOUSNESSLIFETHREATENING', 'SERIOUSNESSCONGENITALANOMALI', 'SERIOUSNESSOTHER', 'SERIOUSNESSHOSPITALIZATION', 'DRUGRESULT', 'REACTIONOUTCOME', 'PATIENTONSETAGE', 'PATIENTWEIGHT', 'PATIENTHEIGHT', 'PRIMARYFLG', 'PATIENTAGEGROUP', 'PATIENTSEX', 'REPORTERPHONE_EXTENSION', 'REPORTEREMAIL_EXTENSION', 'REPORTERGIVENAME', 'REPORTERMIDDLENAME', 'REPORTERFAMILYNAME', 'INTERMEDIARYNAME', 'COMMUNICATIONCORRESPONDENCE', 'PATIENTID', 'PATIENTBIRTHDATE', 'PATIENTBIRTHDATERES', 'PATIENTFIRSTNAME', 'PATIENTMIDDLENAME', 'PATIENTLASTNAME', 'ISPSPMEMBER', 'PREGNANT_EXTENSION', 'PATIENTLASTMENSTRUALDATE', 'GESTATIONPERIOD', 'GESTATIONPERIODUNIT', 'BREASTFEEDING_EXTENSION', 'PATIENTDEATHDATE', 'PATIENTDEATHDATERES', 'PATIENTAUTOPSYYESNO', 'PATIENTDRUGSTARTDATE', 'PATIENTDRUGSTARTDATERES', 'DRUGBATCHNUMB', 'EXPIRATIONDATE_EXTENSION', 'EXPIRATIONDATE_EXTENSIONRES', 'DRUGCHARACTERIZATION', 'DOSEONGOING_EXTENSION', 'DRUGSTARTDATE', 'DRUGSTARTDATERES', 'DRUGENDDATE', 'DRUGENDDATERES', 'DRUGSTRUCTUREDOSAGENUMB', 'DRUGSTRUCTUREDOSAGEUNIT', 'RECEIPTDATE', 'REPORTTYPE', 'LOCALCASEREF_EXTENSION', 'SAFETYREPORTVERSION', 'HCP_EXTENSION', 'HOSPITALIZATIONONGOING', 'PSPLOCALID', 'PSPID', 'PSPRELATEDREFNUMBER', 'HCPCONSENT', 'PATIENTCONSENT', 'PATIENTINITIAL', 'REPORTSENTBYHCP_EXTENSION', 'PATIENTONSETAGEUNIT', 'PATIENTLASTMENSTRUALDATE', 'PATIENTLASTMENSTRUALDATERES', 'LASTDOSEAE', 'TESTDATE', 'TESTDATERES', 'PATIENTDRUGSTARTDATE', 'PATIENTDRUGSTARTDATERES', 'CASENARRATIVE', 'RX_FREQUENCY']
    translate_dict({'table_name': 'RT_PAT_RELEVANT_HISTORY', 'parent_tag': 'RT_PAT_RELEVANT_HISTORY', 'seq_num': None, 'PATIENTEPISODENAME': 'Realiza hemodilise desde Novembro/2017 (antes de iniciar o tratamento com Soliris).'},ek,'pt')