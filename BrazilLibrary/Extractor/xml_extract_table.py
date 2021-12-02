import re
import traceback
from datetime import datetime
from operator import itemgetter
#from xml_file import xml_file

def get_sub_html_file(html_comb_sorted, start_header, end_header, left_coordinate=None, right_coordinate=None):
    """
    sub html file based on start- title, left- coordinate, right - coordinate and end - title
    """
#     LOGGER = LoggingService()
#     LOGGER.print_log_level(Criticality.INFO,
#                            "[{}] Inside GATM Extraction:{} request id - {}".format(
#                                datetime.now(), get_sub_html_file.__name__, request_id))
    limitng_header_coord = 2000
    header_coord = 0
    try:
        if start_header:
            start_header = r"{}".format(start_header)
            header = list(
                filter(lambda x: re.search(start_header, x['text'], re.IGNORECASE) is not None, html_comb_sorted))
#             if 'male' in str(header[0]['text']).lower():
#                 header_coord = header[0]['cumulative_coordinate'] + 30
        #else:
            header_coord = header[0]['cumulative_coordinate'] - 5
        if end_header:
            end_header = r"{}".format(end_header)
            limitng_header = list(
                filter(lambda x: re.search(end_header, x['text'], re.IGNORECASE) is not None, html_comb_sorted))
            if limitng_header:
                limitng_header_coord = limitng_header[0]['cumulative_coordinate']
        sub_file = list(filter(lambda x: header_coord <= x["cumulative_coordinate"] <= limitng_header_coord,
                               html_comb_sorted))
        if left_coordinate is not None:
            sub_file = list(filter(lambda x:left_coordinate <= x["left"] <= right_coordinate, sub_file))
        return sub_file
    except Exception as e:
#         LOGGER.print_log_level(Criticality.ERROR,
#                                "[{}] Exception in GATM Extraction: {} - request id- {} {} - {}".format(
#                                    datetime.now(), get_sub_html_file.__name__,  str(e),
#                                    traceback.format_exc()))
        return html_comb_sorted

def get_header_coord_list(headers, file_name):
    """
    returns list of the coordinates of all the headers extracted from file_name
    """
    #LOGGER = LoggingService()
    # print('INFO',
    #                        "[{}] Inside GATM Extraction:{} ".format(
    #                            datetime.now(), get_header_coord_list.__name__))
    header_coord = {}
    shift = None
    try:
        for key, values in headers.items():
            if 'shift' in values:
                shift = values['shift']
            coord_name = key.lower().replace(' ', '') + '_coord'
            header_coord[coord_name] = [get_header_coord_html(file_name, key, values['coord_position'], shift), key]
    except Exception as e:
        print('ERROR',
                               "[{}] Exception in GATM Extraction: {} -  {} - {}".format(
                                   datetime.now(), get_header_coord_list.__name__, str(e),
                                   traceback.format_exc()))
    return header_coord

def get_header_coord_html(html_file, start_header, coord_position, coord_shift=None, occurrence=None,
                          default_value=None):
    """
    coordinate of a label
    :param html_file: input file
    :param start_header:header title
    :param coord_position:coordinate you want - top, left
    :param coord_shift: shift in the coordinate
    :param occurrence:what occurrence of the title is required
    :param default_value: if not found then default value
    :return:coordinate of the title
    """
    #LOGGER = LoggingService()
    # print('INFO',
    #                        "[{}] Inside GATM Extraction:{} ".format(
    #                            datetime.now(), get_header_coord_html.__name__))
    try:
        start_header = r"\b\n*{}".format(start_header)
        header = list(
            filter(lambda x: re.search(start_header, x['text'], re.IGNORECASE) is not None, html_file))
        if header:
            if occurrence is None:
                occurrence = 0
            header_coord = header[occurrence][coord_position]
            if coord_shift:
                header_coord = header_coord + coord_shift
            return header_coord
    except Exception as e:
        print('ERROR',
                               "[{}] Exception in GATM Extraction: {} -  {} - {}".format(
                                   datetime.now(), get_header_coord_html.__name__, str(e),
                                   traceback.format_exc()))
    return default_value


def table_delimiter_rules(header_coord, fields, work_file, data_loop):
    """
    rules for fields of table with delimiters
    :param header_coord: lis of header and their coordinates
    :param fields: header config
    :param work_file: temporary file with data of one row
    :param data_loop: dict in which data is to be updated
    :return: updated dict
    """
    #LOGGER = LoggingService()
    # print('INFO',
    #                        "[{}] Inside GATM Extraction:{} ".format(
    #                            datetime.now(), table_delimiter_rules.__name__))
    try:
        for key, values in header_coord.items():
            if fields[values[1]]['extract'] != 'No':
                start_coord_1 = fields[values[1]]['start'][0]
                start_coord_2 = fields[values[1]]['start'][1]
                end_coord_1 = fields[values[1]]['end'][0]
                end_coord_2 = fields[values[1]]['end'][1]
                start_coord, end_coord = table_coords( start_coord_1, start_coord_2, end_coord_1, end_coord_2,
                                                      header_coord)
                data = get_table_data( work_file, start_coord, end_coord, 'left')
                data = sorted(data, key=itemgetter('cumulative_coordinate', 'left'))
                if 'remove_words' in fields[values[1]]:
                    data = replace_words_func( data, fields[values[1]]['remove_words'])
                data = clean_cell_value( data)




                data_loop = insert_dict_values( data, fields[values[1]], data_loop)
    except Exception as e:
        print('ERROR',
                               "[{}] Exception in GATM Extraction: {} - {} - {}".format(
                                   datetime.now(), table_delimiter_rules.__name__,  str(e),
                                   traceback.format_exc()))
    return data_loop


def replace_words_func(file_name, replace_words):
    """
    :param file_name: input file
    :param replace_words: words to be replaced
    :return: cleaned string
    """
    # LOGGER = LoggingService()
    # LOGGER.print_log_level(Criticality.INFO,
    #                        "[{}] Inside GATM Extraction:{} request id - {}".format(
    #                            datetime.now(), replace_words_func.__name__, request_id))
    refined_data = ''
    replace_words = r"{}".format(replace_words)
    try:
        if isinstance(file_name, list):
            file_name = "\n".join([x['text'] for x in file_name])
        elif isinstance(file_name, dict):
            file_name = file_name['text']
        if file_name:
            refined_data = file_name.replace('\n', ' ')
            refined_data = re.sub(replace_words, '', refined_data, re.IGNORECASE)
            refined_data = re.sub(r'DD[ ]*M+[ ]*Y+', '', refined_data)
        return refined_data
    except Exception as e:
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in GATM Extraction: {} - request id- {} {} - {}".format(
        #                            datetime.now(), replace_words_func.__name__, request_id, str(e),
        #                            traceback.format_exc()))
        return ''





def table_coords(start_coord_1, start_coord_2, end_coord_1, end_coord_2, header_coord):
    """
    :param start_coord_1: starting coordinate of header
    :param start_coord_2: shift in header
    :param end_coord_1: ending coordinate of header
    :param end_coord_2: shift in end header
    :param header_coord: list of all header coords
    :return:
    """
    #LOGGER = LoggingService()
    # print('INFO',
    #                        "[{}] Inside GATM Extraction:{} ".format(
    #                            datetime.now(), table_coords.__name__))
    try:
        if not str(start_coord_1).replace('-', '').isdigit():
            start_coord_1 = header_coord[start_coord_1.lower().replace(' ', '') + '_coord'][0]
        if not str(start_coord_2).replace('-', '').isdigit():
            start_coord_2 = header_coord[start_coord_2.lower().replace(' ', '') + '_coord'][0]
        if not str(end_coord_1).replace('-', '').isdigit():
            end_coord_1 = header_coord[end_coord_1.lower().replace(' ', '') + '_coord'][0]
        if not str(end_coord_2).replace('-', '').isdigit():
            end_coord_2 = header_coord[end_coord_2.lower().replace(' ', '') + '_coord'][0]
        left_coord = start_coord_1 + start_coord_2
        right_coord = end_coord_1 + end_coord_2
        return left_coord, right_coord
    except Exception as e:
        print('ERROR',
                               "[{}] Exception in GATM Extraction: {} -  {} - {}".format(
                                   datetime.now(), table_coords.__name__,str(e),
                                   traceback.format_exc()))
        return None, None


def get_table_data(file_name, start_coord, end_coord, position):
    """
    :param file_name:input file
    :param start_coord: coordinate of start header
    :param end_coord: coordinate of end header
    :param position: left or top
    :return:list
    """
    #LOGGER = LoggingService()
    # print('INFO',
    #                        "[{}] Inside GATM Extraction:{}".format(
    #                            datetime.now(), get_table_data.__name__))
    try:
        sub_file = list(filter(lambda x: start_coord <= x[position] < end_coord, file_name))
        return sub_file
    except Exception as e:
        print('ERROR',
                               "[{}] Exception in GATM Extraction: {} -  {} - {}".format(
                                   datetime.now(), get_table_data.__name__,str(e),
                                   traceback.format_exc()))
        return None

def insert_dict_values(data, config, data_loop, other_field=None, temp_loop=None):
    """
    :param data:value to be updated
    :param config: config
    :param data_loop:dict in which data needs to be updated
    :param other_field:field names for which extra rules to be added
    :param temp_loop:dict in which all the multiple values will be saved - in case of multiple mapping
    :return:updated dict
    """
    #LOGGER = LoggingService()
    # print('INFO',
    #                        "[{}] Inside GATM Extraction:{} ".format(
    #                            datetime.now(), insert_dict_values.__name__))
    try:
        if 'table_name' in config:
            if config['table_name'] not in data_loop:
                data_loop[config['table_name']] = {}
            if 'multiple_mapping' in config:
                dtd_elements = config['dtd_element']
                index = 0
                if isinstance(data, str):
                    data = temp_loop
                for key, value in data.items():
                    data_loop[config['table_name']][dtd_elements[index]] = value
                    index += 1
            elif other_field == 'Frequency':
                for dose_dict in data_loop[config['table_name']]:
                    dose_dict[config['dtd_element']] = data
            else:
                data_loop[config['table_name']][config['dtd_element']] = data
        else:
            data_loop[config['dtd_element']] = data
        return data_loop
    except Exception as e:
        print('ERROR',
                               "[{}] Exception in GATM Extraction: {} -  {} - {}".format(
                                   datetime.now(), insert_dict_values.__name__, str(e),
                                   traceback.format_exc()))
        return data_loop


def clean_cell_value(file):
    """
    create a string if file is list and removed new line character
    :param file: input file - can be list or str
    :return: refined value - str
    """
    #LOGGER = LoggingService()
    # print('INFO',
    #                        "[{}] Inside GATM Extraction:{} ".format(
    #                            datetime.now(), clean_cell_value.__name__))
    try:
        if isinstance(file, list):
            file = "\n".join([x['text'] for x in file])
        refined_data = file.replace('\n', ' ')
        return refined_data
    except Exception as e:
        print('ERROR',
                               "[{}] Exception in GATM Extraction: {} -  {} - {}".format(
                                   datetime.now(), clean_cell_value.__name__,str(e),
                                   traceback.format_exc()))
        return ''


def coordinate_correcter(sub_html_file):
    index = 0
    length = len(sub_html_file)
    for index in range(length):
        if sub_html_file[index]['text'] == "Valor de referência":
            break
    index += 1
    # print("****************", sub_html_file[index])
    while(index < length):
        top = sub_html_file[index]['top']
        cumulative_coordinate = sub_html_file[index]['cumulative_coordinate']
        #print(top, cumulative_coordinate)
        for i in range(4):
            if index >= length:
                continue
            # if(sub_html_file[i]['text'] == "NI"):
            #     print("mil gya", sub_html_file[i])
            sub_html_file[index]['top'] = top
            sub_html_file[index]['cumulative_coordinate'] = cumulative_coordinate
            index += 1

    return sub_html_file


#
# if __name__ == '__main__':
#     try:
#         html_file = xml_file()
#         #print(html_file)
#         #print(html_file)
#         sub_html = get_sub_html_file(html_file,'Exames laboratoriais realizados em decorrência dos eventos','Medicamentos Concomitantes')
#         sub_html = coordinate_correcter(sub_html)
#         # sub_html[10]['top'] = sub_html[10]['top']-1
#         # sub_html[10]['cumulative_coordinate'] = sub_html[10]['cumulative_coordinate'] - 1
#         # sub_html[11]['top'] = sub_html[11]['top'] - 1
#         #sub_html[11]['cumulative_coordinate'] = sub_html[11]['cumulative_coordinate'] - 1
#         #print(sub_html[10]['top'])
#         print((sub_html))
#         data = sorted(sub_html, key=itemgetter('cumulative_coordinate')) #sorted according to cumulative
#         # list_of_headers = "'Nome do exame', 'Data de realização', 'Resultado', 'Valor de referência'"
#         # h1 = list(filter(lambda x:re.search(x['text'], list_of_headers) , data))
#         # test_data = list( filter(lambda x: x['text'] not in list_of_headers, data))
#         # processed_test_data = list( filter(lambda x: x['text'] != ' ' and x['text']!="", test_data))
#         # remove_test_data = "'Exames laboratoriais realizados em decorrência dos eventos','Não aplicável','Medicamentos Concomitantes'"
#         # test_data_after_delete = list(filter(lambda x: not (re.search(x['text'], remove_test_data)), processed_test_data))
#         # test_data_sorted = sorted(test_data_after_delete, key=itemgetter('cumulative_coordinate'))
#         # count = len(test_data_sorted)
#         #
#         # if count > 4:
#         #     count /= 4
#         # else:
#         #     count = 1
#         #
#         # for i in range(int(count)):
#         #     row_data = test_data_sorted[0]['text']+test_data_sorted[1]['text']+test_data_sorted[2]['text']+test_data_sorted[3]['text']
#         #     h1.append(row_data)
#         #print(h1)
#     except Exception as e:
#         print(e)
#     headers = {'Nome do exame':{
#     "coord_position": "left",
#     "start": [0,0],
#     "end": ["Data de realização", -10],
#     "extract": "Yes",
#     "table_name": "RT_LABTEST",
#     "dtd_element": "TESTNAME",
#     "remove_words": "Exames laboratoriais realizados em decorrência dos eventos",
#     "text_type": "nom"
#     },'Data de realização':{
#     "coord_position": "left",
#     "start": ['Data de realização', 0],
#     "end": ["Resultado", -210],
#     "extract": "Yes",
#     "table_name": "RT_LABTEST",
#     "dtd_element": "TESTDATE",
#         "remove_words": "",
#         "text_type": "date"
#     },'Resultado':{
#     "coord_position": "left",
#     "start": ['Resultado', -200],
#     "end": ["Valor de referência", -10],
#     "extract": "Yes",
#     "table_name": "RT_LABTEST",
#     "dtd_element": "TESTRESULT",
#         "remove_words": "Não aplicável"
#     },'Valor de referência':{
#     "coord_position": "left",
#     "start": ['Valor de referência', -15],
#     "end": [1000, 0],
#     "extract": "Yes",
#     "table_name": "RT_LABTEST",
#     "dtd_element": "LOWTESTRANGE",
#         "remove_words": ""
#     }
#     }
#     list_header_coord = get_header_coord_list(headers, sub_html)
#     all_coordinates = list(set([x['cumulative_coordinate'] for x in sub_html]))
#     all_coordinates.sort()
#     l = len(all_coordinates)
#     starting_coord = 0
#     final_output = []
#     for i in range(l):
#         data_loop = {}
#         ending_coord = all_coordinates[i]
#         work_product = list(filter(lambda x: starting_coord < x['cumulative_coordinate'] <= ending_coord, sub_html))
#         starting_coord = all_coordinates[i]
#         data_loop = table_delimiter_rules(list_header_coord, headers, work_product, data_loop)
#         final_output.append((data_loop))
#     # print(list_header_coord)
#     # data_loop = {}
#     # product_table = table_delimiter_rules(list_header_coord,headers,sub_html,data_loop)
#     print(final_output)


if __name__ == '__main__':
    pass
    # #html_file = xml_file()
    # try:
    #    # html_file = xml_file()
    #     #print(html_file)
    #     #sub_html = get_sub_html_file(html_file,'Nome do exame','Page 4 of 4')
    #     #sub_html = coordinate_correcter((sub_html))
    #    # print(sub_html)
    # except Exception as e:
    #     print(e)

