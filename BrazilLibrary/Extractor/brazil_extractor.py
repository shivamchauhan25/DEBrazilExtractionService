import json
import re
import os
from copy import deepcopy
import traceback
from datetime import datetime
from BrazilLibrary.Extractor.extract_checkbox import get_sub_html_file, sub_comb, get_sub_xml_file
#from html_file import html_file
from BrazilLibrary.Extractor.extract_table import get_header_coord_list, table_delimiter_rules
#from xml_file import xml_file
from BrazilLibrary.Extractor.xml_extract_table import coordinate_correcter
#from BrazilLibrary.Extractor.splittextarea import split_combdata
from Utilities.html_comb import main_function as html_comb
from Utilities.xml_combing_module import main_function as xml_comb
import Utilities.helper as helper
#from Utilities.utils import translate_text

# from HiLITDECoreLibraries.HCoreLoggerLibrary.constants.criticality import Criticality
# from HiLITDECoreLibraries.HCoreLoggerLibrary.service.logging_service import LoggingService

def split_layout(start_header, end_header, layout_path=None):
    '''
    :split_layout: It is a function which is used for splitting the layout file.
    :param start_header: Starting string
    :param end_header: ending string
    :param layout_path: path of the layout file
    :return: It will return the string between start_header and end_header from the layout file.
    '''
    #LOGGER = LoggingService()
    try:

        file_name = ""
        if layout_path:
            with open(layout_path, encoding="utf-8", errors = "ignore") as layout:
                layout_file = layout.read()
            start_regex = re.compile(start_header, re.DOTALL)
            end_regex = re.compile(end_header, re.DOTALL)
            header_data = start_regex.search(layout_file)
            if len(header_data.groups()) >= 1:
                file_name = header_data.group(1)
            end_header_data = end_regex.search(file_name)
            if len(end_header_data.groups()) >= 1:
                file_name = end_header_data.group(1)
        return file_name
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in main brazil function: {}  {} - {}".format(
        #                            datetime.now(), split_layout.__name__, str(e),
        #                            traceback.format_exc()))

def main_function(request_id, source_path):
    '''
    It is the main function of the code which is using for the whole extraction.
    :param request_id: Any number
    :param source_path: Path of the pdf form
    :return: finaljson and narrative
    '''
    #LOGGER = LoggingService()
    try:
        folder, file_name = helper.get_filename(source_path)
        layout_path = os.path.abspath(os.path.join(folder, "layout"))
        os.system('pdftotext -layout "{}" "{}"'.format(source_path, layout_path))
        html_file = html_comb(source_path)
        xml_file = xml_comb(source_path)
        finaljson, narrative = extract_layout_file(html_file, xml_file, layout_path, request_id)
        return finaljson, narrative
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in main brazil function: {} - request id- {} {} - {}".format(
        #                            datetime.now(), main_function.__name__, request_id, str(e),
        #                            traceback.format_exc()))
        return None, None

def date_corrector(date=None):
    #LOGGER = LoggingService()
    try:
        if date == None:
            return None
        else:
            months = {"jan": "1", "fev": "2", "mar": "3", "abr": "4", "mai": "5", "jun": "6", "jul": "7", "ago": "8", "set": "9", "oct": "10","out": "10",
                      "nov": "11", "dez": "12"}
            for key in months.keys():
                date = date.lower().replace(key, months[key])
            return date
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in main brazil function: {} -  {} - {}".format(
        #                            datetime.now(), date_corrector().__name__, str(e),
        #                            traceback.format_exc()))

def extract_layout_file(html_file,xml_file,layout_path, request_id=None):
    '''
    extract_layout_file: This function exract the field from the file along with checkboxes and table too.
    :param html_file: html_file is using for extraction of checkboxes and for big text.
    :param xml_file: xml_file file is using for the table extraction.
    :param layout_path: It is the path for the layout file which is using for the string extraction.
    :return: It will return finaljson and event_data
    '''
    #LOGGER = LoggingService()
    finaljson = []
    RT_REPORTER = {
        'table_name': 'RT_REPORTER',
        'parent_tag': 'Reporter',
        'seq_num': None,
        'REPORTSENTBYHCP_EXTENSION': None,
        'PRIMARYFLG': 'Yes',
        'REPORTERSTREET': None,
        'REPORTERFAX_EXTENSION': None,
    }
    RT_PATIENT = {'table_name': 'RT_PATIENT', 'parent_tag': 'Patient', 'PATIENTINITIAL': None,
                  'PATIENTAGEGROUP': None}
    suspect_product = {"table_name": "RT_PRODUCT",
                       "parent_tag": "Product Information",
                       "DRUGCHARACTERIZATION": "Suspect"}
    suspect_indication = {"table_name": "RT_PRODUCT_INDICATION",
                        "parent_tag": "Product Indication"}
    table_indication = {"table_name": "RT_PRODUCT_INDICATION",
                        "parent_tag": "Product Indication"}
    RT_INDICATION = []
    suspect_dose = {"table_name": "RT_Dose",
                    "parent_tag": "Dose Information"}
    suspect_dose_2 = {"table_name": "RT_Dose",
                    "parent_tag": "Dose Information"}
    concomitant_product = {"table_name": "RT_PRODUCT",
                           "parent_tag": "Product Information",
                           "DRUGCHARACTERIZATION": "Concomitant",
                           "DRUGBATCHNUMB": None,
                           "DRUGINDICATION": None,
                           "EXPIRATIONDATE_EXTENSION": None,
                           "EXPIRATIONDATE_EXTENSIONRES": None,
                           "DRUGACTIONTAKEN_EXTENSION": None,
                           "LASTDOSEAE": None,
                           "LASTDOSEAERES": None,
                    }
    concomitant_dose = {"table_name": "RT_Dose",
                        "parent_tag": "Dose Information",
                        "DRUGADMINISTRATIONROUTE": None}
    RT_PRODUCT = []
    RT_EVENT_dict = {"table_name": "RT_EVENT",
                "parent_tag": "Event(s)",
                "seq_num": None,
                "REACTIONSTARTDATE": None,
                "REACTIONSTARTDATERES": None,
                "PRIMARYSOURCEREACTION": None,
                "REACTIONMEDDRALLT": None,
                "REACTIONOUTCOME": None,
                "SERIOUSNESSDISABLING": None,
                "SERIOUSNESSLIFETHREATENING": None,
                "SERIOUSNESSCONGENITALANOMALI": None,
                "SERIOUSNESSOTHER": None,
                "REACTIONENDDATE": None,
                "REACTIONENDDATERES": None,
                "REACTIONONGOING_EXTENSION": None
                }
    RT_EVENT = []
    RT_REFERENCES = {"table_name": "RT_REFERENCES",
                        "parent_tag": "RT_REFERENCES"}
    RT_DEATH = {"table_name": "RT_DEATH",
                "parent_tag": "Death",
                "PATIENTDEATHREPORT": None,
                "PATIENTDEATHDATE": None}
    RT_MASTER = {"table_name": "RT_MASTER",
                 "parent_tag": "patient",
                 "REPORTTYPE": None,
                 "CASEREPORTTYPE": "I",
                 "OCCURCOUNTRY": "BRAZIL"}
    RT_PAT_RELEVANT_HISTORY_dict = {"table_name": "RT_PAT_RELEVANT_HISTORY",
                               "parent_tag": "RT_PAT_RELEVANT_HISTORY",
                               "seq_num": None}
    RT_PAT_RELEVANT_HISTORY = []

    RT_VACCINE_dict = {
        "table_name": "RT_VACCINE",
        "parent_tag": "vaccine",
        "seq_num": None,
    }
    RT_VACCINE = []
    RT_DEATH_DETAIL = {"table_name": "RT_DEATH_DTL",
                       "parent_tag": "Death detail",
                       "seq_num": None}
    RT_SUMMARY = {"table_name": "RT_SUMMARY",
                    "parent_tag": "Summary_Information",
                    "PATINFO_EXTENSION": None,
                    "HCPINFO_EXTENSION": None,
                  "SENDERCOMMENT": None}
    RT_DOSE = []



    # reporter information
    # alexion reporter
    reporter_info = split_layout(r"(Relator.*)", r"(.*Paciente\n)", layout_path)
    try:
        for reporter_info_it in reporter_info.split('\n'):
            if 'Nome do relator:' in reporter_info_it:
                rep_name = reporter_info_it.split('relator:', 1)[-1].strip().split(' ')  # reporter name
                name_len = len(rep_name)
                # Splitting name into first, middle, last name
                if name_len == 1:
                    rep_fn = rep_name[0]
                    rep_mn = None
                    rep_ln = None
                elif name_len == 2:
                    rep_fn = rep_name[0]
                    rep_mn = rep_name[1]
                    rep_ln = None
                else:
                    rep_fn = rep_name[0]
                    rep_mn = rep_name[1]
                    rep_ln = ' '.join(map(str, rep_name[2:]))
                RT_REPORTER['REPORTERGIVENAME'] = rep_fn
                RT_REPORTER['REPORTERMIDDLENAME'] = rep_mn
                RT_REPORTER['REPORTERFAMILYNAME'] = rep_ln

            # reporter type
            # if 'Grau de relacionamento:' in reporter_info:
            #     reporter_relation = reporter_info.split('relacionamento:', 1)[-1].strip().lower()
            #
            #     if reporter_relation == 'm\xc3\xa3\xc2\xa9dico':
            #         relationship = 'Physician'
            #     elif reporter_relation == 'filha' \
            #             or 'fam\xc3\xa3-lia/ cuidador':
            #         relationship = 'Family / Caregiver'
            #     elif reporter_relation \
            #             == 'outro profissional da sa\xc3\xa3\xc2\xbade':
            #         relationship = 'Other health professional'
            #
            #     RT_REPORTER['REPORTERTYPE'] = relationship

            # reporter profession
            # if 'Profissão:' in reporter_info:
            #     occupation = reporter_info.split('Profissão:', 1)[-1].strip()
            #
            #     RT_REPORTER['QUALIFICATION'] = occupation

            # reporter email
            # if 'E-mail:' in reporter_info:
            #     rep_mail = [reporter_info.split('E-mail:',
            #                                     1)[-1].strip().split('\n')]
            #     if RT_REPORTER.get('REPORTEREMAIL_EXTENSION') is None:
            #         RT_REPORTER['REPORTEREMAIL_EXTENSION'] = rep_mail[0][0]

            # reporter phone number
            # if 'Telefone:' in reporter_info:
            #     rep_phone = [reporter_info.split('Telefone:', 1)[-1].strip().split('\n')]
            #     if RT_REPORTER.get('REPORTERPHONE_EXTENSION') is None:
            #         RT_REPORTER['REPORTERPHONE_EXTENSION'] = rep_phone[0][0]

            # Alexion reporter name
            # if 'Relator Alexion' in reporter_info:
            #     alx_name = reporter_info.split('Alexion', 1)[-1].strip()
            #     RT_REPORTER['INTERMEDIARYNAME'] = alx_name
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))

    try:
        reporter_type = split_layout(r"(Grau de relacionamento:.*)", r"(.*Profissão:)", layout_path)
        reporter_type = reporter_type.split('Grau de relacionamento:', 1)[-1].strip().split("\n")[0]
        # if "família" in reporter_type:
        #     reporter_type = "Family / Caregiver"
        # elif reporter_type == "médico":
        #     reporter_type = "Physician"
        # elif "outro" in reporter_type:
        #     reporter_type = "Other health professional"
        # else:
        #     reporter_type = None
        RT_REPORTER['REPORTERTYPE'] = reporter_type
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))
    #reporter mail
    try:
        rep_mail = split_layout(r"(E-mail:.*)", r"(.*Nome do paciente:)", layout_path)
        rep_mail = rep_mail.split('E-mail:', 1)[-1].strip().split("\n")[0]
        if rep_mail == "Telefone:":
            rep_mail = None
        RT_REPORTER['REPORTEREMAIL_EXTENSION'] = rep_mail
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))

    # repoter telephone
    try:

        rep_phone = split_layout(r"(Telefone:.*)", r"(.*Nome do paciente:)", layout_path)
        rep_phone = rep_phone.split('Telefone:', 1)[-1].strip().split("\n")[0]
        if rep_phone == "Paciente":
            rep_phone = None
        RT_REPORTER['REPORTERPHONE_EXTENSION'] = rep_phone
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))
    # return RT_REPORTER
    try:
        qualification = split_layout(r"(Profissão:.*)", r"(.*Contato p/ Farmacovigilância:)", layout_path)
        qualification = qualification.split('Profissão:', 1)[-1].strip().split("\n")[0]
        if qualification == "Contato p/ Farmacovigilância:":
            qualification = None
        RT_REPORTER['QUALIFICATION'] = qualification
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))

    # intermediaryname
    try:
        inter_name = split_layout(r"(Nome do Relator Alexion.*)", r"(.*Data de Conhecimento)", layout_path)
        inter_name = inter_name.split('Nome do Relator Alexion', 1)[-1].strip().split("\n")[0]
        if inter_name == 'Data de Conhecimento':
            inter_name = None
        RT_REPORTER['INTERMEDIARYNAME'] = inter_name
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))

    # Patient Information
    # RT_Patient
    # patient name
    try:
        patient_info = split_layout(r"(Paciente.*)", r"(.*Exposição)",layout_path)
        for patient_info in patient_info.split('\n'):
            if "Nome do paciente:" in patient_info:
                patient_name = patient_info.split('paciente:', 1)[-1].strip().split(' ')  # patient name
                patient_name_len = (len(patient_name))
                # Splitting name into first, middle, last name
                if patient_name_len == 1:
                    patient_fn = patient_name[0]
                    patient_mn = None
                    patient_ln = None
                elif patient_name_len == 2:
                    patient_fn = patient_name[0]
                    patient_mn = patient_name[1]
                    patient_ln = None
                else:
                    patient_fn = patient_name[0]
                    patient_mn = patient_name[1]
                    patient_ln = ' '.join(map(str, patient_name[2:]))

                RT_PATIENT['PATIENTFIRSTNAME'] = patient_fn
                RT_PATIENT['PATIENTMIDDLENAME'] = patient_mn
                RT_PATIENT['PATIENTLASTNAME'] = patient_ln

    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))

    # patient weight
    try:
        weight = split_layout(r"(Peso:.*)", r"(.*Altura:)", layout_path)
        weight = weight.split('Peso:',1)[-1].strip().split(" ")[0]
        if bool(re.search(r'\d', weight)) is True:
            weight = re.search(pattern="[0-9]+", string=weight).group()
        else:
            weight = None
        RT_PATIENT['PATIENTWEIGHT'] = weight
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))


    # Patient Height
    try:
        height_co = split_layout(r"(Altura:.*)", r"(.*Idade:)", layout_path)
        #todo
        height = re.findall(r'[0-9][0-9,.]+', height_co)[0]
        RT_PATIENT['PATIENTHEIGHT'] = height
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))

    # patient dob
    try:
        pat_dob_co = split_layout(r"(Não Questionado.*)", r"(.*Idade:)", layout_path)
        pat_dob = pat_dob_co.split('Data de', 1)[-1].strip().split(" ")[0]
        if pat_dob == "Idade:":
            pat_dob = None
        # date_pattern = r'([0-9]{2}\/[0-9]{2}\/[0-9]{4})'
        # pat_dob = re.search(date_pattern, pat_dob_co)
        pat_dob = date_corrector(pat_dob)
        RT_PATIENT['PATIENTBIRTHDATE'] = pat_dob
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))

    # patient age
    try:
        pat_age_co = split_layout(r"(Idade:.*)", r"(.*nascimento:)", layout_path)
        pat_age = pat_age_co.split('Idade:', 1)[-1].strip().split("\n")[0]
        if 'Desconhecido' in pat_age:
            pat_age = pat_age.replace("Desconhecido", "").split()
            pat_age = ' '.join(pat_age)
        else:
            pat_age = None
        # if bool(re.search(r'\d', pat_age)) is True:
        #     pat_age = re.search(pattern="[0-9]+", string=pat_age).group()
        # else:
        #     pat_age = None
        RT_PATIENT['PATIENTONSETAGE'] = pat_age
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))

    # patient_id
    try:
        patient_id = split_layout(r"(Número do PM:.*)", r"(.*Gestação)", layout_path)
        patient_id = patient_id.split('Número do PM:', 1)[-1].strip().split("\n")[0]
        if patient_id == "Gestação":
            patient_id = None
        RT_PATIENT['PATIENTID'] = patient_id
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))

    # Gestação / Lactação
    # Data da última menstruação
    try:
        mensuration_date = split_layout(r"(Data da última menstruação.*)", r"(.*Data estimada do parto)", layout_path)
        mensuration_date = mensuration_date.split('Data da última menstruação',1)[-1].strip().split("\n")[0]
        if bool(re.search(r'\d',mensuration_date)) is True:
            date_pattern = r'([0-9]{2}\/[0-9]{2}\/[0-9]{4})'
            mensuration_date = re.search(date_pattern, mensuration_date).group()
        else:
            mensuration_date = None
        mensuration_date = date_corrector(mensuration_date)
        RT_PATIENT['PATIENTLASTMENSTRUALDATE'] = mensuration_date
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))

    # Semanas de gestação na data do relato:
    try:
        gestation_period = split_layout(r"(Semanas de gestação na data do relato:.*)", r"(.*Paciente está lactante?)", layout_path)
        if bool(re.search(r'\d', gestation_period)) is True:
            gestation_period = re.search(pattern="[0-9]+", string=gestation_period).group()
        else:
            gestation_period = None
        RT_PATIENT['GESTATIONPERIOD'] = gestation_period
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))

    # gestation period unit
    try:

        gestation_period_unit = split_layout(r"(Semanas de gestação na data do relato:.*)", r"(.*Paciente está lactante?)", layout_path)
        gestation_period_unit = \
        gestation_period_unit.split('Semanas de gestação na data do relato:', 1)[-1].strip().split("\n")[0]
        gestation_period_unit = "".join(re.split("[^a-zA-Z]*", gestation_period_unit))
        if gestation_period_unit == "semanas":
            RT_PATIENT['GESTATIONPERIODUNIT'] = 'Weeks'
        elif gestation_period_unit == "semana":
            RT_PATIENT['GESTATIONPERIODUNIT'] = 'Week'
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))
    # Data estimada do parto
    try:
        estimate_delivery_date = split_layout(r"(Data estimada do parto.*)", r"(.*Exposição paterna?)", layout_path)
        estimate_delivery_date = estimate_delivery_date.split('Data estimada do parto', 1)[-1].strip().split("\n")[0]
        #todo
        if re.search('\\(DD-MM-AAAA\\):', estimate_delivery_date):
            estimate_delivery_date = estimate_delivery_date.replace("(DD-MM-AAAA):", "").split()
            if len(estimate_delivery_date) == 1:
                estimate_delivery_date = estimate_delivery_date[0]
            else:
                estimate_delivery_date = None
        elif re.search('(DD/MM/AAAA)', estimate_delivery_date):
            estimate_delivery_date = estimate_delivery_date.replace("(DD/MM/AAAA)", "").split()
            if len(estimate_delivery_date) == 1:
                estimate_delivery_date = estimate_delivery_date[0]
            else:
                estimate_delivery_date = None
        else:
            estimate_delivery_date = None
        estimate_delivery_date = date_corrector(estimate_delivery_date)
        RT_PATIENT['ESTIMATEDDELIVERYDATE'] = estimate_delivery_date
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))
    seq=1
    # Suspect product information
    # product name
    # Produto Alexion
    # Nome do produto:
    try:
        product_name = split_layout(r"(Nome do produto:.*)", r"(.*Dose atual:)", layout_path)
        product_name = product_name.split('produto:', 1)[-1].strip().split(" ")[0]
        if product_name == "Dose":
            product_name = None
        suspect_product['MEDICINALPRODUCT'] = product_name
        suspect_product['seq_num'] = seq
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))


    # Indicação
    try:
        recommandation = split_layout(r"(Indicação:.*)", r"(.*Frequência atual:)", layout_path)
        recommandation = recommandation.split('Indicação:', 1)[-1].strip().split(" ")[0]
        if recommandation == "Frequência":
            recommandation = None
        suspect_indication['DRUGINDICATION'] = recommandation

        suspect_indication['prod_seq_num'] = seq
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))

    # Frequência atual:
    try:
        freq_atual = split_layout(r"(Frequência atual:.*)", r"(.*Via de administração:)", layout_path)
        freq_atual = re.search(pattern="[0-9]+", string=freq_atual)
        freq_atual = freq_atual.group()

    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))

    # Via de administração:
    try:
        route_of_admin = split_layout(r"(Via de administração:.*)", r"(.*Data da última dose:)",layout_path)
        route_of_admin = route_of_admin.split('Via de administração:', 1)[-1].strip().split("\n")[0]
        if route_of_admin == "Data da última dose:":
            route_of_admin = None
        suspect_dose['DRUGADMINISTRATIONROUTE'] = route_of_admin
        suspect_dose_2['DRUGADMINISTRATIONROUTE'] = route_of_admin
        suspect_dose['prod_seq_num'] = seq
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))

    # Data da última dose:
    try:
        last_date_of_dose = split_layout(r"(Data da última dose:.*)", r"(.*Fase Inicial)", layout_path)
        last_date_of_dose = last_date_of_dose.split('Data da última dose:', 1)[-1].strip().split("\n")[0]
        if last_date_of_dose == "Fase Inicial":
            last_date_of_dose = None
        #RT_PRODUCT['LASTDOSEAE'] = last_date_of_dose
        last_date_of_dose = date_corrector(last_date_of_dose)
        suspect_product['LASTDOSEAE'] = last_date_of_dose

    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))

    # Fase Inicial
    # Dose:
    try:
        dose = "None"
        dose_area = split_layout(r"(Fase Inicial.*)", r"(.*Data de início:)", layout_path)
        dose_unit = dose_area.split('Dose:', 1)[-1].strip().split(" ")[1]
        if dose_unit == "de":
            dose_unit = "None"
        if len(re.findall(r'[0-9][0-9,.]+', dose_area)) != 0:
            dose = re.findall(r'[0-9][0-9,.]+', dose_area)[0]
            suspect_dose['DRUGSTRUCTUREDOSAGENUMB'] = dose
        suspect_dose['DRUGSTRUCTUREDOSAGEUNIT'] = dose_unit
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))(e)

    # Data de início
    try:
        start_date = split_layout(r"(Data de início:.*)", r"(.*Frequência:)", layout_path)
        start_date = start_date.split('Data de início:', 1)[-1].strip().split("\n")[0]
        if re.search('\\(DD-MM-AAAA\\)', start_date):
            start_date = start_date.replace("(DD-MM-AAAA)", "").split()
            if len(start_date) == 1:
                start_date = start_date[0]
            else:
                start_date = None
        elif "Frequência" in start_date:
            start_date = None
        start_date = date_corrector(start_date)
        suspect_dose['DRUGSTARTDATE'] = start_date
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))(e)

    # Frequência:
    try:
        frequency = split_layout(r"(Frequência:.*)", r"(.*Data de término:)", layout_path)
        frequency = frequency.split('Frequência:', 1)[-1].strip().split(" ")[0]
        if frequency == "Data":
            frequency = None

        if frequency == '7':
            suspect_dose['RX_FREQUENCY'] = 'qw'
            suspect_dose['DRUGDOSAGETEXT'] = dose + " " + dose_unit + " " + 'qw'
        elif frequency == '14':
            suspect_dose['RX_FREQUENCY'] = 'q2w'
            suspect_dose['DRUGDOSAGETEXT'] = dose + " " + dose_unit + " " + 'q2w'
        else:
            suspect_dose['RX_FREQUENCY'] = None
            suspect_dose['DRUGDOSAGETEXT'] = dose + " " + dose_unit

    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))(e)

    # Data de término:
    try:
        end_date = split_layout(r"(Data de término:.*)", r"(.*Fase de Manutenção)", layout_path)
        end_date = end_date.split('Data de término:', 1)[-1].strip().split("\n")[0]
        if re.search('\\(DD-MM-AAAA\\)', end_date):
            end_date = end_date.replace("(DD-MM-AAAA)", "").split()
            if len(end_date) == 1:
                end_date = end_date[0]
            else:
                end_date = None
        elif "Fase" in end_date:
            end_date = None
        end_date = date_corrector(end_date)
        suspect_dose['DRUGENDDATE'] = end_date
        # if bool(re.search(r'\d', end_date)) is True:
        #     end_date
        # else:
        #     end_date = None

        if "continua" == end_date:
            suspect_dose['DOSEONGOING_EXTENSION'] = "Yes"
        else:
            suspect_dose['DOSEONGOING_EXTENSION'] = None
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))(e)


    # Fase de Manutenção

    # Dose

    try:

        maintenance_dose = split_layout(r"(Fase de Manutenção.*)", r"(.*Data de início:)", layout_path)
        maintenance_dose_comb = maintenance_dose.split('Dose:', 1)[-1].strip().split(" ")
        maintenance_dose = maintenance_dose_comb[0]
        maintenance_dose_unit = maintenance_dose_comb[1]
        if maintenance_dose == "Data":
            maintenance_dose = str(None)
            maintenance_dose_unit = str(None)
        # else:
        #     maintenance_dose_unit = maintenance_dose_comb[1]
        # maintenance_dose = re.search(pattern="[0-9]+", string=maintenance_dose).group()
        suspect_dose_2['DRUGSTRUCTUREDOSAGENUMB'] = maintenance_dose
        suspect_dose_2['DRUGSTRUCTUREDOSAGEUNIT'] = maintenance_dose_unit
        if maintenance_dose != None:
            if freq_atual == '7':
                suspect_dose_2['RX_FREQUENCY'] = 'qw'
                suspect_dose_2['DRUGDOSAGETEXT'] = maintenance_dose + " " + maintenance_dose_unit + " " + 'qw'
            elif freq_atual == '14':
                suspect_dose_2['RX_FREQUENCY'] = 'q2w'
                suspect_dose_2['DRUGDOSAGETEXT'] = maintenance_dose + " " + maintenance_dose_unit + " " + 'q2w'
            else:
                suspect_dose_2['RX_FREQUENCY'] = None
                suspect_dose_2['DRUGDOSAGETEXT'] = maintenance_dose + " " + maintenance_dose_unit
            suspect_dose_2['prod_seq_num'] = seq
        else:
            suspect_dose_2['RX_FREQUENCY'] = None
            suspect_dose_2['DRUGDOSAGETEXT'] = None
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))(e)

    # Data de início:
    try:
        maintenance_start_date = split_layout(r"(Fase de Manutenção.*)", r"(.*Frequência:)", layout_path)
        maintenance_start_date = maintenance_start_date.split('Data de início:', 1)[-1].strip().split("\n")[0]
        if re.search('\\(DD-MM-AAAA\\)', maintenance_start_date):
            maintenance_start_date = maintenance_start_date.replace("(DD-MM-AAAA)", "").split()
            if len(maintenance_start_date) == 1:
                maintenance_start_date = maintenance_start_date[0]
            else:
                maintenance_start_date = None
        elif "Frequência" in maintenance_start_date:
            maintenance_start_date = None
        maintenance_start_date = date_corrector(maintenance_start_date)
        suspect_dose_2['DRUGSTARTDATE'] = maintenance_start_date
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))(e)

    # Frequência:
    # try:
    #     maintenance_freq = split_layout(r"(Fase de Manutenção.*)", r"(.*Frequência:)", layout_path)
    #     maintenance_freq = maintenance_freq.split('Frequência:', 1)[-1].strip().split("\n")[0]
    #     maintenance_freq = re.search(pattern="[0-9]+", string=maintenance_freq).group()
    #
    # except Exception as e:
    #     LOGGER.print_log_level(Criticality.ERROR,
    #                            "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
    #                                datetime.now(), extract_layout_file.__name__, request_id, str(e),
    #                                traceback.format_exc()))(e)


    # Data de término:
    try:
        maintenance_end_date = split_layout(r"(Fase de Manutenção.*)", r"(.*Data de término:)", layout_path)
        maintenance_end_date = maintenance_end_date.split('Data de término:', 1)[-1].strip().split("\n")[0]
        if re.search('\\(DD-MM-AAAA\\)', maintenance_end_date):
            maintenance_end_date = maintenance_end_date.replace("(DD-MM-AAAA)", "").split()
            if len(maintenance_end_date) == 1:
                maintenance_end_date = maintenance_end_date[0]
            else:
                maintenance_end_date = None
        elif "(se aplicável)" in maintenance_end_date:
            maintenance_end_date = None
        maintenance_end_date = date_corrector(maintenance_end_date)
        suspect_dose_2['DRUGENDDATE'] = maintenance_end_date
        if "continua" in maintenance_end_date:
            suspect_dose_2['DOSEONGOING_EXTENSION'] = "Yes"
        else:
            suspect_dose_2['DOSEONGOING_EXTENSION'] = None
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))

    # Vacinação Meningocócica
    # Nome da Vacina:
    try:
        vaccination_name = split_layout(r"(Vacinação Meningocócica.*)", r"(.*Dose:)", layout_path)
        vaccination_name = vaccination_name.split('Nome da Vacina:', 1)[-1].strip().split(" ")[0]
        if vaccination_name == "Dose:":
            vaccination_name = None
        RT_VACCINE_dict['PATIENTDRUGNAME'] = vaccination_name
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))

    # Dose:
    try:
        vaccination_name_dose = split_layout(r"(Nome da Vacina:.*)", r"(.*Sorotipos:)", layout_path)
        vaccination_name_dose = vaccination_name_dose.split('Dose:', 1)[-1].strip().split("\n")[0]
        if vaccination_name_dose == "Sorotipos:":
            vaccination_name_dose = None
        RT_VACCINE_dict['PATIENTDRUGDOSE'] = vaccination_name_dose
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))

    # Sorotipos:
    try:
        serotypes = split_layout(r"(Sorotipos:.*)", r"(.*Data da vacinação:)", layout_path)
        serotypes = serotypes.split('Sorotipos:', 1)[-1].strip().split("\n")[0]
        if serotypes == "Data da vacinação:":
            serotypes = None
        RT_VACCINE_dict['SEROTYPE_EXTENSION'] = serotypes
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))

    # Data da vacinação:
    try:
        vaccination_date = split_layout(r"(Data da vacinação:.*)", r"(.*Antibioticoprofilaxia)", layout_path)
        vaccination_date = vaccination_date.split('Data da vacinação:', 1)[-1].strip().split("\n")[0]
        if vaccination_date == "(DD/MM/AAAA)":
            vaccination_date = None
        vaccination_date = date_corrector(vaccination_date)
        RT_VACCINE_dict['PATIENTDRUGSTARTDATE'] = vaccination_date
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))
    #appending RT_Vaccine_dict to list
    RT_VACCINE.append(RT_VACCINE_dict)
    # Antibioticoprofilaxia

    # Nome do Antibiótico:
    try:
        antibiotic_name = split_layout(r"(Nome do Antibiótico:.*)", r"(.*Dose/Frequência:)", layout_path)
        antibiotic_name = antibiotic_name.split('Nome do Antibiótico:', 1)[-1].strip().split("\n")[0]
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))

    # Dose/Frequência:
    try:

        dose_freq = split_layout(r"(Dose/Frequência:.*)", r"(.*Data de início)", layout_path)
        dose_freq = dose_freq.split('Dose/Frequência:', 1)[-1].strip().split("\n")[0]
        if bool( re.search(r'\d',dose_freq)) is True:
            dose_freq =re.search(pattern="[0-9]+", string=dose_freq).group()
        else:
            dose_freq = None
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))




    #dose_freq = re.search(pattern="[0-9]+", string=dose_freq).group()

    # Data de início
    try:
        anti_start_date = split_layout(r"(Dose/Frequência:.*)", r"(.*Data de término:)", layout_path)
        anti_start_date = anti_start_date.split('Data de início',1)[-1].strip().split("\n")[0]
        if bool(re.search(r'\d',anti_start_date)) is True:
            date_pattern = r'([0-9]{2}\/[0-9]{2}\/[0-9]{4})'
            anti_start_date = re.search(date_pattern, anti_start_date).group()
        else:
            anti_start_date = None
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))


    # Data de término:
    try:
        anti_end_date = split_layout(r"(Dose/Frequência:.*)", r"(.*Page 2 of 4)", layout_path)
        anti_end_date = anti_end_date.split('Data de término:', 1)[-1].strip().split("\n")[0]
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))

    # Hospitalização
    # Motivo da hospitalização:
    try:
        hospitalization_reason = split_layout(r"(Motivo da hospitalização:.*)", r"(.*hospitalização:)", layout_path)
        hospitalization_reason = hospitalization_reason.split('Motivo da hospitalização:', 1)[-1].strip().split("\n")[0]
        if hospitalization_reason == "Data de":
            hospitalization_reason = None
        RT_EVENT_dict['HOSPITALIZATIONREASON'] = hospitalization_reason
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))


    # Data de hospitalização:
    try:
        hospitalization_date = split_layout(r"(hospitalização:.*)", r"(.*Óbito)", layout_path)
        hospitalization_date = hospitalization_date.split('hospitalização:', 2)[-1].strip().split(" ")[0]
        if hospitalization_date == "(DD/MM/AAAA)\n":
            hospitalization_date = None
        hospitalization_date = date_corrector(hospitalization_date)
        RT_EVENT_dict['HOSPADMISSIONDATE_EXTENSION'] = hospitalization_date
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))

    # Data de alta:
    try:
        discharge_date = split_layout(r"(hospitalização:.*)", r"(.*Óbito)", layout_path)
        discharge_date = discharge_date.split('hospitalização:', 2)[-1].strip().split("\n")[0]
        discharge_date = discharge_date.split(" ")[-1]
        if discharge_date == "(DD/MM/AAAA)":
            discharge_date = None
        discharge_date = date_corrector(discharge_date)
        RT_EVENT_dict['HOSPDISCHARGEDATE_EXTENSION'] = discharge_date
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))

    # RT_MASTER
    # Data de Conhecimento
    try:
        receit_date = split_layout(r"(Nome do Relator Alexion.*)", r"(.*Tipo de contato)", layout_path)
        receit_date = receit_date.split('Data de Conhecimento', 2)[-1].strip().split("\n")[0]
        if "(DD-MM-AAAA)" in receit_date:
            receit_date = receit_date.replace("(DD-MM-AAAA)", "").split()

            if len(receit_date) == 1:
                receit_date = receit_date[0]
            else:
                receit_date = None
        if "Tipo " in receit_date:
            receit_date = None
        receit_date = date_corrector(receit_date)
        RT_MASTER['RECEIPTDATE'] = receit_date
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))

    # Número Case Alex
    try:
        alx_case__number = split_layout(r"(Número Case Alex PS.*)", r"(.*Nome do relator:)", layout_path)
        alx_case__number = alx_case__number.split('Número Case Alex PS', 2)[-1].strip().split("\n")[0]
        if alx_case__number == "Relator" or "Tipo de contato" in alx_case__number:
            alx_case__number = None
        RT_MASTER['LOCALCASEREF_EXTENSION'] = alx_case__number
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))

    # STUDYNAME
    RT_MASTER['STUDYNAME'] = product_name

    # RT_PAT_RELEVANT_HISTORY_dict
    try:
        pat_relevant_hist = split_layout(r"(Histórico Médico.*)", r"(.*Produto Alexion)", layout_path)
        pat_relevant_hist = pat_relevant_hist.split(
            'Informe se o paciente possui alguma outra patologia ou condição clínica prévia ao início do tratamento com medicamento',
            1)[-1].strip().split("\n")[2]
        RT_PAT_RELEVANT_HISTORY_dict['PATIENTEPISODENAME'] = pat_relevant_hist
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))
    # Óbito

    # Data do óbito:
    try:
        death_date = split_layout(r"(Data do óbito:.*)", r"(.*Causa do óbito:)", layout_path)
        death_date = death_date.split('Data do óbito:', 1)[-1].strip().split(" ")[0]
        if death_date == "Causa":
            death_date = None
        death_date = date_corrector(death_date)
        RT_DEATH['PATIENTDEATHDATE'] = death_date
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))

    # Causa do óbito:
    try:
        death_cause = split_layout(r"(Causa do óbito:.*)", r"(.*Possui relatório de autópsia?)", layout_path)
        death_cause = death_cause.split('Causa do óbito:', 1)[-1].strip().split("\n")[0]
        if death_cause == "(DD/MM/AAAA)" or death_cause == "(DD-MMM-AAAA)":
            death_cause = None
        RT_DEATH_DETAIL['PATIENTDEATHCAUSE'] = death_cause
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))


    # checkboxex

    # Tipo de contato
    common_html_file = html_file
    sub_xml_new_pdf = get_sub_html_file(xml_file, 'Medicamentos Concomitantes',
                                        '')
    is_new_pdf = [True for elem in sub_xml_new_pdf if 'Avaliação do atendimento PSP' in elem.values()]
    if any(is_new_pdf):
        # Lote Chekbox
        # New PDF Detected
        try:
            lote_area = get_sub_html_file(common_html_file, "Relator não soube informar lote e validade", "Causalidade")

            lote_mapping = {"Causalidade": {"left": "Relator não soube informar lote e validade"}}
            for key, value in lote_mapping.items():
                file_checkbox = sub_comb(lote_area, value.get("left"))
                checkbox = "\n".join([x['text'] for x in file_checkbox])
                checkbox_marked = re.search(r'X|☒|✔', checkbox)
                if checkbox_marked:
                    lote = None
                else:
                    lote = split_layout(r"(Lote:.*)", r"(.*Validade:)", layout_path)
                    lote = lote.split('Lote:', 1)[-1].strip().split("\n")[0]

                    if "Validade" in lote:
                        lote = lote.replace("Validade:", "").split()
                        lote = ' '.join(lote)
                    else:
                        lote = None
                suspect_product['DRUGBATCHNUMB'] = lote
        except Exception as e:
            print(e)
            # LOGGER.print_log_level(Criticality.ERROR,
            #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
            #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
            #                            traceback.format_exc()))

        try:
            expiry_date = split_layout(r"(Validade:.*)", r"(.*Causalidade)", layout_path)
            expiry_date = expiry_date.split('Validade:', 1)[-1].strip().split("\n")[0]
            if len(expiry_date) < 11:
                expiry_date

            elif 'com relação' not in expiry_date:

                if "Relator" in expiry_date:
                    expiry_date = expiry_date.replace("Relator não soube informar lote e validade", "").split()
                    expiry_date = ' '.join(expiry_date)
                else:
                    expiry_date = None
            else:
                expiry_date = None
            expiry_date = date_corrector(expiry_date)
            suspect_product['EXPIRATIONDATE_EXTENSION'] = expiry_date
        except Exception as e:
            print(e)
            # LOGGER.print_log_level(Criticality.ERROR,
            #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
            #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
            #                            traceback.format_exc()))

    else:
        # Old pdf detected
        try:
            lote_area = get_sub_html_file(common_html_file, "Relator não soube informar lote e validade", "Causalidade")

            lote_mapping = {"Causalidade": {"left": "Relator não soube informar lote e validade"}}
            for key, value in lote_mapping.items():
                file_checkbox = sub_comb(lote_area, value.get("left"))
                checkbox = "\n".join([x['text'] for x in file_checkbox])
                checkbox_marked = re.search(r'X|☒|✔', checkbox)
                if checkbox_marked:
                    lote = None
                else:
                    lote = split_layout(r"(Lote:.*)", r"(.*Causalidade)", layout_path)
                    lote = lote.split('Lote:', 1)[-1].strip().split("\n")[0]
                    if "Validade:" in lote or "recebeu" in lote:
                        lote = None
                suspect_product['DRUGBATCHNUMB'] = lote
        except Exception as e:
            print(e)
            # LOGGER.print_log_level(Criticality.ERROR,
            #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
            #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
            #                            traceback.format_exc()))

        try:
            expiry_date = split_layout(r"(Lote:.*)", r"(.*Causalidade)", layout_path)
            expiry_date = re.findall(r'(\d+/\d+/\d+)', expiry_date)
            if any(expiry_date):
                expiry_date = expiry_date[0]
            else:
                expiry_date = None
            # expiry_date = date_corrector(expiry_date)
            suspect_product['EXPIRATIONDATE_EXTENSION'] = expiry_date
        except Exception as e:
            print(e)
            # LOGGER.print_log_level(Criticality.ERROR,
            #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
            #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
            #                            traceback.format_exc()))


    #Ação tomada com o produto Alexion em decorrência dos eventos
    try:
        action_taken_area = get_sub_html_file(common_html_file, "quência, etc.", "Page 3 of 4")
        action_taken_area = action_taken_area[3]['text']
        if "não" or "nÃo" or "nenhuma" or "nenhuma ação tomada" in action_taken_area:
            action_taken_area = "Unchanged"
        else:
            action_taken_area
        suspect_product['DRUGACTIONTAKEN_EXTENSION'] = action_taken_area
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))

    #Antibioticoprofilaxia
    antibiotic_checkbox_area = get_sub_html_file(common_html_file, "Antibioticoprofilaxia", "Nome do Antibiótico:")
    antibiotic_checkbox_mapping = {"Antibioticoprofilaxia": {"left": "Antibioticoprofilaxia", "right": "Não aplicável (Strensiq e Kanuma)"}}
    for key, value in antibiotic_checkbox_mapping.items():
        file_checkbox = sub_comb(antibiotic_checkbox_area, value.get("left"), value.get("right"))
        checkbox = "\n".join([x['text'] for x in file_checkbox])
        checkbox_marked = re.search(r'X|☒|✔', checkbox)
        if not checkbox_marked:
            try:
                antibiotic_name = split_layout(r"(Nome do Antibiótico:.*)", r"(.*Dose/Frequência:)", layout_path)
                antibiotic_name = antibiotic_name.split('Nome do Antibiótico:', 1)[-1].strip().split("\n")[0]
                if "Sim" in antibiotic_name:
                    antibiotic_name = None
                concomitant_product['MEDICINALPRODUCT'] = antibiotic_name

            except Exception as e:
                print(e)
                # LOGGER.print_log_level(Criticality.ERROR,
                #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
                #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
                #                            traceback.format_exc()))
            if antibiotic_name != None:
                try:

                    dose_freq = split_layout(r"(Dose/Frequência:.*)", r"(.*Data de início)", layout_path)
                    dose_freq_unit = dose_freq.split('Dose/Frequência:', 1)[-1].strip().split("\n")[0]
                    if "Não" in dose_freq_unit:
                        dose_freq_unit = None
                    else:
                        dose_freq_unit = " ".join(re.findall("[a-zA-Z]+", dose_freq_unit))
                    dose_freq = dose_freq.split('Dose/Frequência:', 1)[-1].strip().split("\n")[0]
                    if bool(re.search(r'\d', dose_freq)) is True:
                        dose_freq = re.search(pattern="[0-9]+", string=dose_freq).group()
                    else:
                        dose_freq = None
                    concomitant_product['seq_num'] = seq + 1
                    seq += 1
                    concomitant_dose['DRUGSTRUCTUREDOSAGENUMB'] = dose_freq
                    concomitant_dose['DRUGSTRUCTUREDOSAGEUNIT'] = dose_freq_unit
                    concomitant_dose['DRUGDOSAGETEXT'] = dose_freq + " " + dose_freq_unit
                    concomitant_dose['prod_seq_num'] = seq
                except Exception as e:
                    print(e)
                    # LOGGER.print_log_level(Criticality.ERROR,
                    #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
                    #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
                    #                            traceback.format_exc()))
                try:
                    anti_start_date = split_layout(r"(Dose/Frequência:.*)", r"(.*Data de término:)", layout_path)
                    anti_start_date = anti_start_date.split('Data de início', 1)[-1].strip().split("\n")[0]
                    if bool(re.search(r'\d', anti_start_date)) is True:
                        date_pattern = r'([0-9]{2}\/[0-9]{2}\/[0-9]{4})'
                        anti_start_date = re.search(date_pattern, anti_start_date).group()
                    else:
                        anti_start_date = None
                    anti_start_date = date_corrector(anti_start_date)
                    concomitant_dose['DRUGSTARTDATE'] = anti_start_date
                except Exception as e:
                    print(e)
                    # LOGGER.print_log_level(Criticality.ERROR,
                    #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
                    #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
                    #                            traceback.format_exc()))
                try:
                    anti_end_date = split_layout(r"(Dose/Frequência:.*)", r"(.*Page 2 of 4)", layout_path)
                    anti_end_date = anti_end_date.split('Data de término:', 1)[-1].strip().split("\n")[0]
                    if anti_end_date == "Page 2 of 4":
                        anti_end_date = None
                    anti_end_date = date_corrector(anti_end_date)
                    concomitant_dose['DRUGENDDATE'] = anti_end_date
                    if "continua" in anti_end_date:
                        concomitant_dose['DOSEONGOING_EXTENSION'] = "Yes"
                    else:
                        concomitant_dose['DOSEONGOING_EXTENSION'] = None
                except Exception as e:
                    print(e)
                    # LOGGER.print_log_level(Criticality.ERROR,
                    #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
                    #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
                    #                            traceback.format_exc()))


    try:
        commu_corres_area = get_sub_html_file(common_html_file, "Nome do Relator Alexion", "Nome do relator:")
        communication_mapping = {"Efetuado": {"left": "Tipo de contato", "right": "Efetuado"},
                                 "Recebido": {"left": "Efetuado", "right": "Recebido"}}
        for key, value in communication_mapping.items():
            file_checkbox = sub_comb(commu_corres_area, value.get("left"), value.get("right"))
            checkbox = "\n".join([x['text'] for x in file_checkbox])
            checkbox_marked = re.search(r'X|☒|✔', checkbox)
            if checkbox_marked:
                if key == "Efetuado":
                    RT_REPORTER['COMMUNICATIONCORRESPONDENCE'] = "I"

                elif key == "Recebido":
                    RT_REPORTER['COMMUNICATIONCORRESPONDENCE'] = "O"

                else:
                    RT_REPORTER['COMMUNICATIONCORRESPONDENCE'] = None
                break
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))

    # Gênero/Gender
    try:
        gender_area = get_sub_html_file(common_html_file, "Nome do paciente:",
                                        "Interrompido  Em andamento Não Questionado Desconhecido")
        gender_mapping = {"Masculino": {"left": "Gênero", "right": "Masculino"},
                          "Feminino": {"left": "Masculino", "right": "Feminino"},
                          "Desconhecido": {"left": "Feminino", "right": "Desconhecido"}}
        for key, value in gender_mapping.items():
            file_checkbox = sub_comb(gender_area, value.get("left"), value.get("right"))
            checkbox = "\n".join([x['text'] for x in file_checkbox])
            checkbox_marked = re.search(r'X|☒|✔', checkbox)
            if checkbox_marked:
                if key == "Masculino":
                    RT_PATIENT['PATIENTSEX'] = 'Male'
                elif key == "Feminino":
                    RT_PATIENT['PATIENTSEX'] = 'Female'
                elif key == "Desconhecido":
                    RT_PATIENT['PATIENTSEX'] = 'UNK'
                else:
                    RT_PATIENT['PATIENTSEX'] = None

                break
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))

    # Paciente é membro do PSP
    try:
        member_psp_area = get_sub_html_file(common_html_file, "Paciente é membro do PSP?", "Gestação / Lactação")
        psp_mapping = {"Sim": {"left": "Paciente é membro do PSP?", "right": "Sim"}, "Não": {"left": "Sim", "right": "Não"}}
        for key, value in psp_mapping.items():
            file_checkbox = sub_comb(member_psp_area, value.get("left"), value.get("right"))
            checkbox = "\n".join([x['text'] for x in file_checkbox])
            checkbox_marked = re.search(r'X|☒|✔', checkbox)
            if checkbox_marked:
                if key == "Sim":
                    RT_PATIENT['ISPSPMEMBER'] = 'Yes'
                elif key == "Não":
                    RT_PATIENT['ISPSPMEMBER'] = 'No'
                else:
                    RT_PATIENT['ISPSPMEMBER'] = None
                break
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))

    # Gestação / Lactação
    # Paciente está gestante?/Pregnant
    try:
        pregnant_area = get_sub_html_file(common_html_file, "Paciente está gestante?", "Exposição paterna?")
        pregnant_mapping = {"Sim": {"left": "Paciente está gestante?", "right": "Sim"},
                            "Não": {"left": "Sim", "right": "Não"}}
        for key, value in pregnant_mapping.items():
            file_checkbox = sub_comb(pregnant_area, value.get("left"), value.get("right"))
            checkbox = "\n".join([x['text'] for x in file_checkbox])
            checkbox_marked = re.search(r'X|☒|✔', checkbox)
            if checkbox_marked:
                if key == "Sim":
                    RT_PATIENT['PREGNANT_EXTENSION'] = '1'
                elif key == "Não":
                    RT_PATIENT['PREGNANT_EXTENSION'] = '0'
                else:
                    RT_PATIENT['PREGNANT_EXTENSION'] = None
                break
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))

    # Paciente está lactante?
    try:
        lactating_area = get_sub_html_file(common_html_file, "Paciente está lactante?",
                                           "Formulário de reporte de eventos adversos - PSP")
        lactating_mapping = {"Sim": {"left": "Paciente está lactante?", "right": "Sim"},
                             "Não": {"left": "Sim", "right": "Não"}}
        for key, value in lactating_mapping.items():
            file_checkbox = sub_comb(lactating_area, value.get("left"), value.get("right"))
            checkbox = "\n".join([x['text'] for x in file_checkbox])
            checkbox_marked = re.search(r'X|☒|✔', checkbox)
            if checkbox_marked:
                if key == "Sim":
                    RT_PATIENT['BREASTFEEDING_EXTENSION'] = '1'
                elif key == "Não":
                    RT_PATIENT['BREASTFEEDING_EXTENSION'] = '0'
                else:
                    RT_PATIENT['BREASTFEEDING_EXTENSION'] = None
                break
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))

    # Causalidade
    # O relator considera os eventos relacionados ao uso do medicamento Alexion?/DRUGRESULT
    try:
        drugresult_area = get_sub_html_file(common_html_file,
                                            "O relator considera os eventos relacionados ao uso do medicamento Alexion?",
                                            "O médico está ciente dos eventos apresentados pelo paciente?")
        drugresult_value = {
            "Sim": {"left": "O relator considera os eventos relacionados ao uso do medicamento Alexion?", "right": "Sim"},
            "Não": {"left": "Sim", "right": "Não"}, "Desconhecido": {"left": "Não", "right": "Desconhecido"},
            "Não Questionado": {"left": "Desconhecido", "right": "Não Questionado"}}
        for key, value in drugresult_value.items():
            file_checkbox = sub_comb(drugresult_area, value.get("left"), value.get("right"))
            checkbox = "\n".join([x['text'] for x in file_checkbox])
            checkbox_marked = re.search(r'X|☒|✔', checkbox)
            if checkbox_marked:
                if key == "Sim":
                    RT_EVENT_dict['DRUGRESULT'] = 'Related'
                elif key == "Não":
                    RT_EVENT_dict['DRUGRESULT'] = 'Not Related'
                elif key == "Desconhecido":
                    RT_EVENT_dict['DRUGRESULT'] = 'Unknown'
                elif key == "Não Questionado":
                    RT_EVENT_dict['DRUGRESULT'] = 'Not Reported'
                break
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))

    # O médico está ciente dos eventos apresentados pelo paciente?/ HCP_Extention
    try:
        hcp_extention_area = get_sub_html_file(common_html_file,
                                               "O médico está ciente dos eventos apresentados pelo paciente?",
                                               "A Farmacovigilância pode entrar em contato com o médico?")
        hcp_extention_value = {
            "Sim": {"left": "O médico está ciente dos eventos apresentados pelo paciente?", "right": "Sim"},
            "Não": {"left": "Sim", "right": "Não"}, "Desconhecido": {"left": "Não", "right": "Desconhecido"},
            "Não Questionado": {"left": "Desconhecido", "right": "Não Questionado"}}
        for key, value in hcp_extention_value.items():
            file_checkbox = sub_comb(hcp_extention_area, value.get("left"), value.get("right"))
            checkbox = "\n".join([x['text'] for x in file_checkbox])
            checkbox_marked = re.search(r'X|☒|✔', checkbox)
            if checkbox_marked:

                if key == "Sim":
                    RT_PATIENT['HCPCONSENT'] = 'Yes'
                elif key == "Não":
                    RT_PATIENT['HCPCONSENT'] = 'No'
                elif key == "Desconhecido" or key == "Não Questionado":
                    RT_PATIENT['HCPCONSENT'] = 'Unknown'
                break
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))

    # Hospitalização

    # Paciente foi hospitalizado?
    try:
        hospitalization_area = get_sub_html_file(common_html_file, "Paciente foi hospitalizado?",
                                                 "Motivo da hospitalização:")
        hospitalization_maping = {"Sim": {"left": "Paciente foi hospitalizado?", "right": "Sim"},
                                  "Não": {"left": "Sim", "right": "Não"},
                                  "Desconhecido": {"left": "Não", "right": "Desconhecido"},
                                  "Não Questionado": {"left": "Desconhecido", "right": "Não Questionado"}}
        for key, value in hospitalization_maping.items():
            file_checkbox = sub_comb(hospitalization_area, value.get("left"), value.get("right"))
            checkbox = "\n".join([x['text'] for x in file_checkbox])
            checkbox_marked = re.search(r'X|☒|✔', checkbox)
            if checkbox_marked:
                if key == "Sim":
                    RT_EVENT_dict['SERIOUSNESSHOSPITALIZATION'] = 'Yes'
                elif key == "Não" or key == "Desconhecido" or key == "Não Questionado":
                    RT_EVENT_dict['SERIOUSNESSHOSPITALIZATION'] = 'No'
                break
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))

    # Paciente não teve alta/patient discharged
    try:
        hospitalization_status = get_sub_html_file(common_html_file, "Paciente não teve alta", "Paciente foi a óbito?")
        hospitalization_status_maping = {"Paciente não teve alta": {"left": "Paciente não teve alta", "right": "Óbito"}}
        for key, value in hospitalization_status_maping.items():
            file_checkbox = sub_comb(hospitalization_status, value.get("left"), value.get("right"))
            checkbox = "\n".join([x['text'] for x in file_checkbox])
            checkbox_marked = re.search(r'X|☒|✔', checkbox)

            if checkbox_marked:
                if key == "Sim":
                    RT_EVENT_dict['HOSPITALIZATIONONGOING'] = 'Yes'
                else:
                    RT_EVENT_dict['HOSPITALIZATIONONGOING'] = 'No'
                break
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))

    # Óbito
    # Paciente foi a óbito?
    try:
        patient_death_area = get_sub_html_file(common_html_file, "Paciente foi a óbito?", "Data do óbito:")
        patient_death_mapping = {"Sim": {"left": "Paciente foi a óbito?", "right": "Sim"},
                                 "Não": {"left": "Sim", "right": "Não"}}
        for key, value in patient_death_mapping.items():
            file_checkbox = sub_comb(patient_death_area, value.get("left"), value.get("right"))
            checkbox = "\n".join([x['text'] for x in file_checkbox])
            checkbox_marked = re.search(r'X|☒|✔', checkbox)
            if checkbox_marked:
                if key == "Sim":
                    RT_EVENT_dict['SERIOUSNESSDEATH'] = 'Yes'
                elif key == "Não":
                    RT_EVENT_dict['SERIOUSNESSDEATH'] = 'No'

                break
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))

    #appending RT_EVENT_dict to list
    RT_EVENT.append(RT_EVENT_dict)

    # Possui relatório de autópsia?
    try:
        autopsy_area = get_sub_html_file(common_html_file, "Possui relatório de autópsia?",
                                         "Exames laboratoriais realizados em decorrência dos eventos")
        autopsy_mapping = {"Sim": {"left": "Possui relatório de autópsia??", "right": "Sim"},
                           "Não": {"left": "Sim", "right": "Não"}}
        for key, value in autopsy_mapping.items():
            file_checkbox = sub_comb(autopsy_area, value.get("left"), value.get("right"))
            checkbox = "\n".join([x['text'] for x in file_checkbox])
            checkbox_marked = re.search(r'X|☒|✔', checkbox)
            if checkbox_marked:
                if key == "Sim":
                    RT_DEATH['PATIENTAUTOPSYYESNO'] = 'Yes'
                else:
                    RT_DEATH['PATIENTAUTOPSYYESNO'] = 'No'
                break
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))

    # Table Extraction
    # Exames laboratoriais realizados em decorrência dos eventos

    extract_xml_file = xml_file
    try:
        sub_xml = get_sub_html_file(extract_xml_file, 'Exames laboratoriais realizados em decorrência dos eventos',
                                    'Medicamentos Concomitantes')
        sub_xml = coordinate_correcter(sub_xml)
        first_table_headers = {'Nome do exame': {
            "coord_position": "left",
            "start": [0, 0],
            "end": ["Data de realização", -10],
            "extract": "Yes",
            "dtd_element": "TESTNAME",
            "remove_words": "Exames laboratoriais realizados em decorrência dos eventos|Nome do exame|Medicamentos Concomitantes",
            "text_type": "nom"
        }, 'Data de realização': {
            "coord_position": "left",
            "start": ['Data de realização', -10],
            "end": ["Resultado", -210],
            "extract": "Yes",
            "dtd_element": "TESTDATE",
            "remove_words": "Data de realização",
            "text_type": "date"
        }, 'Resultado': {
            "coord_position": "left",
            "start": ['Resultado', -200],
            "end": ["Valor de referência", -10],
            "extract": "Yes",

            "dtd_element": "TESTRESULT",
            "remove_words": "Não aplicável|Resultado|\\✔|X"
        }, 'Valor de referência': {
            "coord_position": "left",
            "start": ['Valor de referência', -15],
            "end": [1000, 0],
            "extract": "Yes",
            "dtd_element": "LOWTESTRANGE",
            "remove_words": "Valor de referência"
        }
        }
        list_header_coord_table_one = get_header_coord_list(first_table_headers, sub_xml)
        all_coordinates_table_one = list(set([x['cumulative_coordinate'] for x in sub_xml]))
        all_coordinates_table_one.sort()
        len_table_one = len(all_coordinates_table_one)
        starting_coord_table_one = 0
        RT_LABTEST = []
        for i in range(len_table_one):
            table_one = {}
            ending_coord_table_one = all_coordinates_table_one[i]
            work_product_table_one = list(
                filter(lambda x: starting_coord_table_one < x['cumulative_coordinate'] <= ending_coord_table_one, sub_xml))
            starting_coord_table_one = all_coordinates_table_one[i]
            table_one = table_delimiter_rules(list_header_coord_table_one, first_table_headers, work_product_table_one,
                                              table_one)


            RT_LABTEST.append((table_one))


        #LABTEST after delettion of empty values
        #RT_LABTEST = [d for d in RT_LABTEST if all(d.values())]
        #Added Static values
        RT_LABTEST = [dict(item, table_name='RT_LABTEST', parent_tag='Labtest_Information', seq_num=None) for item in RT_LABTEST]
        for obj in RT_LABTEST:
            intval, strval = re.findall("(\d+)?\s*([a-zA-z]+)?", obj['TESTRESULT'])[0]
            obj['TESTRESULTUNIT'] = strval if len(strval) and len(intval) else None
            obj['TESTRESULT'] = intval if len(intval) else obj['TESTRESULT']
            obj['TESTDATE'] = date_corrector(obj['TESTDATE'])
        #print(RT_LABTEST)
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))


    # table two
    # Outros medicamentos utilizados pelo paciente que não sejam os medicamentos utilizados para o tratamento dos eventos

    try:
        sub_xml = get_sub_html_file(extract_xml_file, 'Medicamentos Concomitantes',
                                    '')


        # sub_xml = coordinate_correcter(sub_xml)

        old_form_second_table_headers = {'Nome do medicamento': {
            "coord_position": "left",
            "start": [0, 0],
            "end": ["Data início", -45],
            "extract": "Yes",
            "table_name": "RT_PRODUCT",
            "dtd_element": "MEDICINALPRODUCT",
            "remove_words": "Nome do exame|Medicamentos Concomitantes|Outros medicamentos utilizados pelo paciente que não sejam os medicamentos utilizados para o tratamento dos eventos|Nome do medicamento"
        }, 'Data início': {
            "coord_position": "left",
            "start": ['Data início', -45],
            "end": ["Data término", -15],
            "extract": "Yes",
            "table_name": "RT_DOSE",
            "dtd_element": "DRUGSTARTDATE",
            "remove_words": "Data de realização|Data início"
        }, 'Data término': {
            "coord_position": "left",
            "start": ['Data término', -15],
            "end": ["Dose/ frequência", -20],
            "extract": "Yes",
            "table_name": "RT_DOSE",
            "dtd_element": "DRUGENDDATE",
            "remove_words": "Resultado|Data término|Page 4 of 4"
        }, 'Dose/ frequência': {
            "coord_position": "left",
            "start": ['Dose/ frequência', -20],
            "end": ['Indicação', -48],
            "extract": "Yes",
            "table_name": "RT_DOSE",
            "dtd_element": "DRUGDOSAGETEXT",
            "remove_words": "Valor de referência|Dose/ frequência"
        }, 'Indicação': {
            "coord_position": "left",
            "start": ['Indicação', -48],
            "end": [2000, 0],
            "extract": "Yes",
            "table_name": "RT_PRODUCT",
            "dtd_element": "DRUGINDICATION",
            "remove_words": "Indicação"
        }
        }
        new_form_second_table_headers = {'Nome do medicamento': {
            "coord_position": "left",
            "start": [0, 0],
            "end": ["Data início", -213],
            "extract": "Yes",
            "table_name": "RT_PRODUCT",
            "dtd_element": "MEDICINALPRODUCT",
            "remove_words": "Nome do exame|Medicamentos Concomitantes|Outros medicamentos utilizados pelo paciente que não sejam os medicamentos utilizados para o tratamento dos eventos|Nome do medicamento|Avaliação do atendimento PSP|Sua atenção estava focada?|Sim Não|\\?|\\✔|Hemograma|NI"
        }, 'Data início': {
            "coord_position": "left",
            "start": ['Data início', -50],
            "end": ["Data término", -120],
            "extract": "Yes",
            "table_name": "RT_DOSE",
            "dtd_element": "DRUGSTARTDATE",
            "remove_words": "Data de realização|Data início"
        }, 'Data término': {
            "coord_position": "left",
            "start": ['Data término', -45],
            "end": ["Dose/ frequência", -125],
            "extract": "Yes",
            "table_name": "RT_DOSE",
            "dtd_element": "DRUGENDDATE",
            "remove_words": "Resultado|Data término|Page 4 of 4"
        }, 'Dose/ frequência': {
            "coord_position": "left",
            "start": ['Dose/ frequência', -30],
            "end": ['Indicação', -140],
            "extract": "Yes",
            "table_name": "RT_DOSE",
            "dtd_element": "DRUGDOSAGETEXT",
            "remove_words": "Valor de referência|Dose/ frequência"
        }, 'Indicação': {
            "coord_position": "left",
            "start": ['Indicação', -58],
            "end": [2000, 0],
            "extract": "Yes",
            "table_name": "RT_PRODUCT",
            "dtd_element": "DRUGINDICATION",
            "remove_words": "Indicação"
        }
        }
        is_new_pdf = [True for elem in sub_xml if 'Avaliação do atendimento PSP' in elem.values()]
        if any(is_new_pdf):
            second_table_headers = new_form_second_table_headers
        else:
            second_table_headers = old_form_second_table_headers

        list_header_coord_table_two = get_header_coord_list(second_table_headers, sub_xml)
        all_coordinates_table_two = list(set([x['cumulative_coordinate'] for x in sub_xml]))
        all_coordinates_table_two.sort()
        len_table_two = len(all_coordinates_table_two)
        starting_coord_table_two = 0
        RT_PRODUCT_one = []
        for i in range(len_table_two):
            table_two = {}
            ending_coord_table_two = all_coordinates_table_two[i]
            work_product_table_two = list(
                filter(lambda x: starting_coord_table_two < x['cumulative_coordinate'] <= ending_coord_table_two, sub_xml))
            starting_coord_table_two = all_coordinates_table_two[i]
            table_two = table_delimiter_rules(list_header_coord_table_two, second_table_headers, work_product_table_two,
                                              table_two)
            RT_PRODUCT_one.append((table_two))
        RT_PRODUCT_one = [i for i in RT_PRODUCT_one if not (i['RT_PRODUCT']['MEDICINALPRODUCT']=='')]


        for i in RT_PRODUCT_one:
            #adding static values
            i['RT_PRODUCT']['table_name'] = "RT_PRODUCT"
            i['RT_PRODUCT']['parent_tag'] = "Product Information"
            i['RT_PRODUCT']['DRUGCHARACTERIZATION'] = "Concomitant"
            i['RT_PRODUCT']['DRUGBATCHNUMB'] = None
            i['RT_PRODUCT']['EXPIRATIONDATE_EXTENSION'] = None
            i['RT_PRODUCT']['EXPIRATIONDATE_EXTENSIONRES'] = None
            i['RT_PRODUCT']['DRUGACTIONTAKEN_EXTENSION'] = None
            i['RT_PRODUCT']['LASTDOSEAE'] = None
            i['RT_PRODUCT']['LASTDOSEAERES'] = None
            i['RT_DOSE']['table_name'] = 'RT_Dose'
            i['RT_DOSE']['parent_tag'] = 'Dose Information'
            i['RT_DOSE']['DRUGADMINISTRATIONROUTE'] = None
            i['RT_PRODUCT']['seq_num'] = seq+1
            i['RT_DOSE']['prod_seq_num'] = seq+1
            i['RT_DOSE']['DRUGSTARTDATE'] = date_corrector(i['RT_DOSE']['DRUGSTARTDATE'])
            i['RT_DOSE']['DRUGENDDATE'] = date_corrector(i['RT_DOSE']['DRUGENDDATE'])


            #i.setdefault('seq_num', count)
            seq += 1
            #i['RT_PRODUCT']['seq_num']  = i

            #Replace comp with Tablet
            if 'comp' in i['RT_DOSE']['DRUGDOSAGETEXT']:
                i['RT_DOSE']['DRUGDOSAGETEXT'] = i['RT_DOSE']['DRUGDOSAGETEXT'].replace("comp", "Tablet")
            #adding indication

            table_indication['prod_seq_num'] = i['RT_PRODUCT']['seq_num']
            # RT_INDICATION.append(())
            table_indication['DRUGINDICATION'] = i['RT_PRODUCT']['DRUGINDICATION']
            temp_table_indication = deepcopy(table_indication)
            RT_INDICATION.append((temp_table_indication))
        #Dose and Unit
        for i in RT_PRODUCT_one:
            if len(i['RT_DOSE']['DRUGDOSAGETEXT']) >5:
                dose_quantity = i['RT_DOSE']['DRUGDOSAGETEXT'].split(" ")[0]
                i['RT_DOSE']['DRUGSTRUCTUREDOSAGENUMB'] = dose_quantity
            else:
                i['RT_DOSE']['DRUGSTRUCTUREDOSAGENUMB'] = None
            table_dose_unit = i['RT_DOSE']['DRUGDOSAGETEXT'].split(" ")
            if len(table_dose_unit)>2:
                table_dose_unit = table_dose_unit[1]
                i['RT_DOSE']['DRUGSTRUCTUREDOSAGEUNIT'] = table_dose_unit
            else:
                i['RT_DOSE']['DRUGSTRUCTUREDOSAGEUNIT'] = None

            #adding continue date DOSEONGOING_EXTENSION
            if 'continua' in i['RT_DOSE']['DRUGENDDATE']:
                i['RT_DOSE']['DOSEONGOING_EXTENSION'] = "Yes"
            else:
                i['RT_DOSE']['DOSEONGOING_EXTENSION'] = None



            #print(i['RT_DOSE']['DRUGDOSAGETEXT'])

        #RT_PRODUCT_one = [dict(item, seq_num=seq_num+1) for item in RT_PRODUCT_one]
        # appending suspect and concomitant produt
        RT_PRODUCT.append(suspect_product)
        RT_PRODUCT.append(concomitant_product)
        # appending suspect and concomitant dose
        RT_DOSE.append((suspect_dose))
        RT_DOSE.append(suspect_dose_2)
        RT_DOSE.append(concomitant_dose)
        for i in RT_PRODUCT_one:
            RT_DOSE.append(i['RT_DOSE'])
            RT_PRODUCT.append(i['RT_PRODUCT'])

        #RT_P_new.append((RT_PRODUCT))
        #print(RT_P_new)

        #appending indication into final table
        RT_INDICATION.append(suspect_indication)
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))
    #RT_INDICATION.append(table_indication)
    # print(RT_PRODUCT)
    # print(RT_DOSE)
    # Histórico Médico
    # history_checkbox = get_sub_html_file(common_html_file, "Histórico Médico", "Informe se o paciente possui alguma outra patologia ou condição clínica prévia ao início do tratamento com medicamento")
    #
    # history_checkbox_mapping = {"Histórico Médico": {"left": "Histórico Médico", "right": "Histórico Médico"}}
    # for key, value in history_checkbox_mapping.items():
    #     file_checkbox = sub_comb(history_checkbox, value.get("left"), value.get("right"))
    #     checkbox = "\n".join([x['text'] for x in file_checkbox])
    #     checkbox_marked = re.search(r'X|☒|✔', checkbox)
    #     if checkbox_marked:
    #         if key == "Histórico Médico":
    #

    #Medical History
    try:
        medical_history_area = get_sub_html_file(common_html_file,
                                                 "Informe se o paciente possui alguma outra patologia ou condição clínica prévia ao início do tratamento com medicamento",
                                                 "Nome do produto:")
        medical_history_area = medical_history_area[2]['text']
        if medical_history_area == "Produto Alexion":
            medical_history_area = None
        RT_PAT_RELEVANT_HISTORY_dict['PATIENTEPISODENAME'] = medical_history_area
        RT_PAT_RELEVANT_HISTORY.append(RT_PAT_RELEVANT_HISTORY_dict)
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))

    # Eventos
    try:
        event_data_area = get_sub_html_file(common_html_file, "cada evento descrito.",
                                            "Lote:")
        event_data_area = event_data_area[1]['text'] + event_data_area[2]['text']
    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))

    # Tratamento
    try:
        treatment_area = get_sub_html_file(common_html_file, "procedimentos, etc.",
                                           "Ação tomada com o produto Alexion em decorrência dos eventos")
        treatment_area = treatment_area[2]['text']
        if "Ação tomada" in treatment_area:
            treatment_area = str(None)

        RT_REFERENCES['CASENARRATIVE'] = event_data_area + "/n === /n" + treatment_area
        RT_SUMMARY['NARRATIVEINCLUDECLINICAL'] = event_data_area + "/n === /n" + treatment_area

    except Exception as e:
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in Brazil Extractor: {} - request id- {} {} - {}".format(
        #                            datetime.now(), extract_layout_file.__name__, request_id, str(e),
        #                            traceback.format_exc()))

    #appending all list into final list
    finaljson.append(RT_REPORTER)
    finaljson.append(RT_PATIENT)
    finaljson.append(RT_DEATH)
    finaljson.append(RT_DEATH_DETAIL)
    finaljson.append(RT_VACCINE)
    finaljson.append(RT_PRODUCT)
    finaljson.append(RT_INDICATION)
    finaljson.append(RT_DOSE)
    finaljson.append(RT_MASTER)
    finaljson.append(RT_EVENT)
    finaljson.append(RT_LABTEST)
    finaljson.append(RT_PAT_RELEVANT_HISTORY)
    finaljson.append(RT_REFERENCES)
    finaljson.append(RT_SUMMARY)

    return finaljson, event_data_area
    #return RT_PAT_RELEVANT_HISTORY
    #return RT_PAT_RELEVANT_HISTORY_dict
    #return RT_DEATH,RT_DEATH_DETAIL,RT_DOSE, RT_EVENT, RT_INDICATION, RT_LABTEST, RT_MASTER,RT_PAT_RELEVANT_HISTORY,RT_PATIENT,RT_PRODUCT,RT_REFERENCES,RT_REPORTER,RT_SUMMARY,RT_VACCINE

if __name__ == '__main__':
    # file_path = 'layout'
    # info = extract_layout_file()
    # # out_file = open("finaljson.json", "w")
    # # json.dump(info,out_file, indent = 6)
    # # out_file.close()
    # print(info)
    finaljson, narrative = main_function()
