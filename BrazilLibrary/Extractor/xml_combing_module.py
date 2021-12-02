from glob import glob
import os
import sys
import xml.etree.ElementTree as ET


def get_text_item_list(text_item_list, page, page_num):
    """
    Returns the list of all the text tags in the page
    :param text_item_list: text item list <list>
    :param page: page object of XML <xml.etree.ElementTree.Element>
    :param page_num: page number <str>
    :return:
    """

    for text_item in page:
        if text_item.tag == "text":
            text_item_list.append((page_num, text_item))
    return text_item_list


def get_text(text_item):
    """
    Accessing all the text in the text_item tag
    :param text_item: text tag <xml.etree.ElementTree.Element>
    :return:
    """
    text_data = ""
    if text_item.text and text_item.text.strip():
        text_data += text_item.text.strip()
    for child_item in text_item.findall('.//'):
        if child_item.text and child_item.text.strip() and child_item.text.strip() not in text_data:
            text_data += " " + child_item.text.strip()
        if child_item.tail and child_item.tail.strip() and child_item.tail.strip() not in text_data:
            text_data += " " + child_item.tail.strip()
    if text_data and text_data.strip():
        return text_data.strip()

    return text_data


def get_combed_content(text_item_list):
    """
    Returns the combed content as per all the text tags
    :param text_item_list: List of all the text tags <list>
    :return:
    """
    combed_content = []
    page_no = add = max = 0
    for page_num, text_item in text_item_list:
        if int(page_num) > page_no:
            page_no = int(page_num)
            add = max + add
        y_coord = text_item.attrib["top"]
        x_coord = text_item.attrib["left"]
        width = text_item.attrib["width"]
        height = text_item.attrib["height"]
        font = text_item.attrib["font"]
        text_data = get_text(text_item)
        if int(y_coord) > max:
            max = int(y_coord)
        combed_content.append({
            "page_num": int(page_num),
            "top": int(y_coord),
            "left": int(x_coord),
            "text": text_data.strip(),
            "width": width,
            "height": height,
            "font": font,
            "cumulative_coordinate": int(y_coord) + int(add)
        })

    return combed_content


def remove_temp_files(pdf_name_without_extension):
    """
    Removing the temporary files created during combing file creation
    :param pdf_name_without_extension: PDF name without any extension <str>
    :return:
    """
    temp_file_paths = glob(os.path.join(os.path.curdir,"{}*".format(pdf_name_without_extension)))
    for path in temp_file_paths:
        os.remove(path)


def main_function(pdf_file_path):
    """
    Returns the combed content of the input PDF file
    :param pdf_file_path: Input PDF path <str>
    :return:
    """
    # Inputting the PDF file path (temp work location)
    pdf_file = os.path.split(pdf_file_path)[1]
    pdf_name_without_extension = os.path.splitext(pdf_file)[0]

    # Converting the PDF to XML
    os.system("pdftohtml -xml '{}' '{}'.xml".format(pdf_file_path, pdf_name_without_extension))
    xml_file_path = "{}.xml".format(pdf_name_without_extension)

    # Executing combing of the XML file
    xml_content = ET.parse(xml_file_path)
    main_root = xml_content.getroot()

    # Fetching the text tag from the XML file
    text_item_list = []
    for page in main_root:
        page_num = page.attrib.get("number")
        if page_num:
            text_item_list = get_text_item_list(text_item_list, page, page_num)

    # Creation of combed file
    combed_content = get_combed_content(text_item_list)

    # Sorting of combed content as per the page number, y_coordinate and x_coordinate
    combed_content = sorted(combed_content, key=lambda i: (i["page_num"], i["top"], i["left"]))



    # Copying the file in the work location
    xml_combing_path = os.path.join(os.path.split(pdf_file_path)[0], "{}_XML_combing".format(pdf_name_without_extension))
    with open(xml_combing_path, "w", encoding="utf-8") as fp:
        fp.write(str(combed_content))
        print("Copied XML combed file to: ", xml_combing_path)

    # Removing the temporary files created (images and XML file)
    #remove_temp_files(pdf_name_without_extension)

    return combed_content


if __name__ == "__main__":
    pdf_path = r'C:\Users\shivam.kumar\Desktop\DEBrazilExtractionService\BrazilLibrary\Extractor\checkbox_marked_e2b_attachment_1.pdf'
    combed_content = main_function(pdf_path)
    print(combed_content)
