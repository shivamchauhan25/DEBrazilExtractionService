import os
import PyPDF2
import sys
# from HiLITDECoreLibraries.Utilities.decorator import scrape_data

#@scrape_data
def filter_lines(html_data, search_string):
    """
    Returns the list of HTML lines containing the search string
    :param html_data: <List> HTML lines
    :param search_string: <Str> String to search for in the HTML line
    :return:
    """
    filtered_content = []
    for line in html_data:
        if line.find(search_string) != -1:
            filtered_content.append(line)
    return filtered_content

# @scrape_data
def clean_line(line):
    """
    Cleans the data and removes the garbage values from the HTML line
    :param line: <Str> HTML line
    :return:
    """
    return line.replace('</p>', ' ').replace('&#160;', ' ').replace('</b>', ' ').replace('<br/>', ' ')\
        .replace('<b>', ' ').replace('<i', ' ').replace('</i', ' ').replace('<a href=', ' ').replace('</a', ' ')\
        .replace('"', ' ').replace('px||ft', '||').replace("&#34;", "")

#@scrape_data
def clean_text_data(data):
    """
    Cleans the coordinate and text of the HTML line
    :param data: <Str> HTML line
    :return:
    """
    coordinates = data.split(">")[0]
    text = ' '.join(data.split(">")[1:]).replace(">", "").replace("\n", "")
    text = coordinates + "||" + text
    return text

#@scrape_data
def append_cumulative_coordinate(sorted_content, top_coordinates, cumulative_coordinate):
    """
    Appends the cumulative coordinate to the combed HTML lines
    :param sorted_content: <List> Combed HTML lines sorted based on top and left coordinate
    :param top_coordinates: <List> Sorted top coordinates of the HTML lines
    :param cumulative_coordinate: <Int> Cumulative coordinate of the top coordinate of the HTML line
    :return:
    """
    counter = 0
    content = []
    for line in sorted_content:
        combed_line = str(cumulative_coordinate + top_coordinates[counter]) + '||' + line
        content.append(combed_line)
        counter += 1
    cumulative_coordinate += top_coordinates[counter - 1]
    return content, cumulative_coordinate

#@scrape_data
def get_combed_dictionary(combed_content, page):
    """
    Returns the combed content as a list of python dictionary
    :param combed_content: <List> Combed HTML lines
    :param page: <Int> PDF page number
    :return:
    """
    combed_dictionary = []
    for line in combed_content:
        combed_dictionary.append({
            "page_number": int(page),
            "cumulative_coordinate": int(line.split("||")[0]),
            "top": int(line.split("||")[1]),
            "left": int(line.split("||")[2]),
            "font": int(line.split("||")[3]),
            "text": line.split("||")[4].strip()
        })
    return combed_dictionary

#@scrape_data
def temp_files_remover(directory, filename):
    """
    Removes the temporary files from the work directory
    :param directory: <Str> Current working directory
    :param filename: <Str> PDF file name
    :return:
    """
    print("entering cleaner")
    temp_files = [f for f in os.listdir(directory) if f.startswith(filename) and not f.endswith('pdf')]
    for file in temp_files:
        print("removing filename: ", file)
        os.remove(file)

#@scrape_data
def combing(pdf_object, filename):
    """
    Creates a combed HTML file
    :param pdf_object: <Str> PDF reader object
    :param filename: <Str> PDF file name
    :return:
    """
    cumulative_coordinate = 0
    combed_list = []
    for page_number in range(pdf_object.getNumPages()):
        page_number += 1

        page_data = open('{}-%d.html'.format(filename) % page_number, 'r', encoding='utf-8').readlines()
        data_lines = filter_lines(page_data, "position:absolute")
        cleaned_html_lines = []
        top_coordinate_list = []

        # cleaning all the HTML lines and combing them based on the coordinates
        for line in data_lines:
            line = line.partition(';top:')[2]
            line = line.partition('px;left:')[0::2]
            line = '||'.join(line)
            line = line.partition(';white-space:nowrap\" class=\"')[0::2]
            line = '||'.join(line)
            cleaned_line = clean_line(line)
            cleaned_data = clean_text_data(cleaned_line)
            top_coordinate_list.append(int(cleaned_data.split("||")[0]))
            cleaned_html_lines.append(cleaned_data)

        # sorting the lines with respect to first column
        sortedlist = sorted(list(cleaned_html_lines), key=lambda item: int(item.partition('||')[0]))

        # sorting the lines with respect to first and second column
        re_sortedlist = sorted(list(sortedlist), key=lambda item: (int(item.split('||')[0]), int(item.split('||')[1])))

        # sorting the top coordinate list
        top_coordinate_list.sort()

        # adding cumulative coordinate to the list
        combed_page_lines, cumulative_coordinate = append_cumulative_coordinate(re_sortedlist, top_coordinate_list,
                                                                                cumulative_coordinate)
        combed_dictionary = get_combed_dictionary(combed_page_lines, page_number)
        combed_list.extend(combed_dictionary)
    return combed_list


#@scrape_data
def main_function(file):
    """
    Creates the combing file of the PDF file
    :param file: <Str> PDF filename
    :return:
    """
    current_directory = os.getcwd()
    pdf_filename = os.path.split(file)[1]
    pdf_filename_without_extension, extension = os.path.splitext(pdf_filename)
    os.system('pdftohtml -c "{}" "{}"'.format(file, pdf_filename_without_extension))
    input_pdf = PyPDF2.PdfFileReader(open(file, "rb"))
    combed_html_content = combing(input_pdf, pdf_filename_without_extension)

    # removing the temporary files
    temp_files_remover(current_directory, pdf_filename_without_extension)

    # saving the combing file in the input file path
    html_combing_path = os.path.join(os.path.split(file)[0], "{}_HTML_combing".format(pdf_filename_without_extension))
    with open(html_combing_path, "w", encoding="utf-8") as fp:
        fp.write(str(combed_html_content))

    return combed_html_content


if __name__ == '__main__':
    filepath = sys.argv[1]
    # filepath = r'C:\Users\somayao\Downloads\checkbox_marked_e2b_attachment_1.pdf'
    main_function(filepath)
