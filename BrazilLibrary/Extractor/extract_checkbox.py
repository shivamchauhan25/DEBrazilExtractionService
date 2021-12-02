import re
#from html_file import html_file
def get_sub_html_file(html_comb_sorted, start_header, end_header, left_coordinate=None, right_coordinate=None):
    """
    sub html file based on start- title, left- coordinate, right - coordinate and end - title
    """
#     LOGGER = LoggingService()
#     LOGGER.print_log_level(Criticality.INFO,
#                            "[{}] Inside GATM Extraction:{} request id - {}".format(
#                                datetime.now(), get_sub_html_file.__name__, request_id))
    limitng_header_coord = 6000
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
#                                    datetime.now(), get_sub_html_file.__name__, request_id, str(e),
#                                    traceback.format_exc()))
        return html_comb_sorted

def get_sub_xml_file(html_comb_sorted, start_header, end_header, left_coordinate=None, right_coordinate=None):
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
            header_coord = header[0]['top'] - 5
        if end_header:
            end_header = r"{}".format(end_header)
            limitng_header = list(
                filter(lambda x: re.search(end_header, x['text'], re.IGNORECASE) is not None, html_comb_sorted))
            if limitng_header:
                limitng_header_coord = limitng_header[0]['top']
        sub_file = list(filter(lambda x: header_coord <= x["top"] <= limitng_header_coord,
                               html_comb_sorted))
        if left_coordinate is not None:
            sub_file = list(filter(lambda x:left_coordinate <= x["left"] <= right_coordinate, sub_file))
        return sub_file
    except Exception as e:
#         LOGGER.print_log_level(Criticality.ERROR,
#                                "[{}] Exception in GATM Extraction: {} - request id- {} {} - {}".format(
#                                    datetime.now(), get_sub_html_file.__name__, request_id, str(e),
#                                    traceback.format_exc()))
        return html_comb_sorted

def sub_comb(file,left,right=None):
    '''
    using this function for the checkboxes extraction
    :param file: details regarding the particular checkbox.
    :param left: left coordinate value
    :param right: right coordinate value
    :return: sub_file_comb
    '''
    limitng_header_coord = 2000
    header_coord = 0

    if left:
        left = r"{}".format(left)
        header = list(
            filter(lambda x: re.search(left, x['text'], re.IGNORECASE) is not None, file))
        #             if 'male' in str(header[0]['text']).lower():
        #                 header_coord = header[0]['cumulative_coordinate'] + 30
        # else:
        header_coord = header[0]['left'] - 5
    if right:
        right = r"{}".format(right)
        limitng_header = list(
            filter(lambda x: re.search(right, x['text'], re.IGNORECASE) is not None, file))
        if limitng_header:
            limitng_header_coord = limitng_header[0]['left']
    sub_file_comb = list(filter(lambda x: header_coord <= x["left"] <= limitng_header_coord,
                           file))
    # if left is not None:
    #     sub_file_comb = list(filter(lambda x: left <= x["left"] <= right, sub_file_comb))
    return sub_file_comb



if __name__ == '__main__':
    pass
