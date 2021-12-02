#coding = utf-8
import re
import traceback
from datetime import datetime
from operator import itemgetter
#from html_file import html_file
# from HiLITDECoreLibraries.HCoreLoggerLibrary.constants.criticality import Criticality
# from HiLITDECoreLibraries.HCoreLoggerLibrary.service.logging_service import LoggingService

def get_sub_html_file(html_comb_sorted, start_header, end_header, left_coordinate=None, right_coordinate=None):
    """
    sub html file based on start- title, left- coordinate, right - coordinate and end - title
    """
    #LOGGER = LoggingService()
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
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in GATM Extraction: {} - request id- {} {} - {}".format(
        #                            datetime.now(), get_sub_html_file.__name__,  str(e),
        #                            traceback.format_exc()))
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
        print(e)
        # LOGGER.print_log_level(Criticality.ERROR,
        #                        "[{}] Exception in GATM Extraction: {} - request id- {} {} - {}".format(
        #                            datetime.now(), get_header_coord_list.__name__, str(e),
        #                            traceback.format_exc()))
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
    # LOGGER = LoggingService()
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
                # data = table_delimiter_field_rules( fields, values[1], data, work_file, start_coord, end_coord)
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



if __name__ == '__main__':
    pass
    #html_file = html_file()
