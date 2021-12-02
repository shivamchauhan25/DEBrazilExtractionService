import sys

import cv2
import numpy as np
import os
from datetime import datetime

import fitz
import imutils

from constants import CONFIG_CHECKBOX
# from HiLITDECoreLibraries.HCoreLoggerLibrary.constants.criticality import Criticality
# from HiLITDECoreLibraries.HCoreLoggerLibrary.service.logging_service import LoggingService
# from HiLITDECoreLibraries.Utilities.decorator import scrape_data

#@scrape_data
def update_box_dict(temp_val, box_dict):
    # logger = LoggingService()
    # logger.print_log_level(Criticality.INFO, "[{}] -> Entering checkbox_module: {}".format(datetime.now(),
    #                                                                                        update_box_dict.__name__))
    for attr in temp_val:
        if attr in box_dict:
            box_dict[attr].append(temp_val[attr])
        else:
            box_dict[attr] = [temp_val[attr]]
    # logger.print_log_level(Criticality.INFO, "[{}] -> Exiting checkbox_module: {}".format(datetime.now(),
    #                                                                                       update_box_dict.__name__))

#@scrape_data
def update_all_box(prev_center, center, all_boxes, temp_val):
    # logger = LoggingService()
    # logger.print_log_level(Criticality.INFO, "[{}] -> Entering checkbox_module: {}".format(datetime.now(),
    #                                                                                        update_all_box.__name__))
    if (prev_center is not None) and (prev_center[0] - 1 <= center[0] <= prev_center[0] + 1) and \
            (prev_center[1] - 1 <= center[1] <= prev_center[1] + 1):
        key = prev_center
        if key in all_boxes:
            box_dict = all_boxes[key]
            update_box_dict(temp_val, box_dict)

    else:  # found a new box
        key = center
        if key not in all_boxes:
            all_boxes[key] = {}
            for attr in temp_val:
                all_boxes[key][attr] = [temp_val[attr]]
        prev_center = center

    # logger.print_log_level(Criticality.INFO, "[{}] -> Exiting checkbox_module: {}".format(datetime.now(),
    #                                                                                       update_all_box.__name__))
    return all_boxes, prev_center

#@scrape_data
def get_boxes(file, threshold_min_area, threshold_max_area, lower_aspect_ratio, higher_aspect_ratio):
    """
    Returns the boxes detected from the PNG file
    :param file: cv2 file object
    :param threshold_min_area: Minimum threshold area
    :param threshold_max_area: Maximum threshold area
    :param lower_aspect_ratio: Minimum Aspect ratio
    :param higher_aspect_ratio: Maximum Aspect ratio
    :return:
    """
    # logger = LoggingService()
    # logger.print_log_level(Criticality.INFO, "[{}] -> Entering checkbox_module: {}".format(datetime.now(),
    #                                                                                        get_boxes.__name__))
    all_boxes = {}
    original_image = file
    image = original_image.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # instead of using canny, we use threshold function for edge detection
    edged = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    cnts = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    prev_center = None

    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.035 * peri, True)
        if len(approx) == 4:  # i.e. either a square/rectangle
            (x, y, w, h) = cv2.boundingRect(approx)
            aspect_ratio = w / float(h)
            area = cv2.contourArea(c)
            center = (x + w/2), (y + h/2)
            test_area = [(center[0]-w/4), (center[1]-w/4), (center[0]+w/4), (center[1]+w/4)]

            if threshold_min_area < area < threshold_max_area and \
                    (aspect_ratio >= lower_aspect_ratio) and (aspect_ratio <= higher_aspect_ratio):  # roughly a square
                temp_val = {"perimeter": peri,
                            "area": area,
                            "asp_ratio": aspect_ratio,
                            "center": center,
                            "contour": c,
                            "test_area": test_area,
                            "checked": 0}
                all_boxes, prev_center = update_all_box(prev_center, center, all_boxes, temp_val)

    # logger.print_log_level(Criticality.INFO, "[{}] -> Exiting checkbox_module: {}".format(datetime.now(),
    #                                                                                       get_boxes.__name__))
    return all_boxes

#@scrape_data
def get_cropped_box(rect_coords, image):
    """
    Returns the cropped image of the coordinates provided in rect_coords from the image
    :param rect_coords: coordinates of the cropped area
    :param image: input image
    :return:
    """
    # logger = LoggingService()
    # logger.print_log_level(Criticality.INFO, "[{}] -> Entering checkbox_module: {}".format(datetime.now(),
    #                                                                                        get_cropped_box.__name__))
    xmin = int(rect_coords[0])
    ymin = int(rect_coords[1])
    xmax = int(rect_coords[2])
    ymax = int(rect_coords[3])

    pts = np.array([[xmin, ymin], [xmin, ymax], [xmax, ymin], [xmax, ymax]])

    rect = cv2.boundingRect(pts)
    x, y, w, h = rect
    cropped = image[y:y+h, x:x+w].copy()

    # logger.print_log_level(Criticality.INFO, "[{}] -> Exiting checkbox_module: {}".format(datetime.now(),
    #                                                                                       get_cropped_box.__name__))
    return cropped

#@scrape_data
def get_pixel_ratio(cropped_image):
    """
    Returns the pixel ratio between the black and white pixels in the cropped_image
    :param cropped_image: input image
    :return:
    """
    # logger = LoggingService()
    # logger.print_log_level(Criticality.INFO, "[{}] -> Entering checkbox_module: {}".format(datetime.now(),
    #                                                                                        get_pixel_ratio.__name__))
    white_ct = 0
    black_ct = 0
    for y in cropped_image:
        for x in y:
            if x == 255:
                white_ct += 1
            else:
                black_ct += 1
    if white_ct == 0:
        # logger.print_log_level(Criticality.INFO, "[{}] -> Exiting checkbox_module: {} - Returning only the black pixels"
        #                        .format(datetime.now(), get_pixel_ratio.__name__))
        return black_ct
    else:
        # logger.print_log_level(Criticality.INFO, "[{}] -> Exiting checkbox_module: {} - Returning the ratio of black : "
        #                                          "white pixels".format(datetime.now(), get_pixel_ratio.__name__))
        return black_ct / white_ct

#@scrape_data
def checked_unchecked(test_area, file):
    """
    Returns whether the test_area in the file is checked or not
    :param test_area: coordinates of the image
    :param file: image file object (cv2 object)
    :return:
    """
    # logger = LoggingService()
    # logger.print_log_level(Criticality.INFO, "[{}] -> Entering checkbox_module: {}".format(datetime.now(),
    #                                                                                        checked_unchecked.__name__))
    checked = 0
    image = file.copy()
    grayscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # important to load the image in grey scale
    cropped = get_cropped_box(test_area, grayscale_image)

    p_ratio = get_pixel_ratio(cropped)
    if p_ratio > 0.5:
        checked = 1

    # logger.print_log_level(Criticality.INFO, "[{}] -> Exiting checkbox_module: {}".format(datetime.now(),
    #                                                                                       checked_unchecked.__name__))
    return checked

#@scrape_data
def eliminate_extras(boxes, file):
    """
    Returns the final checkboxes after removing the unchecked boxes
    :param boxes: Dict of the boxes detected
    :param file: image object(cv2)
    :return:
    """
    # logger = LoggingService()
    # logger.print_log_level(Criticality.INFO, "[{}] -> Entering checkbox_module: {}".format(datetime.now(),
    #                                                                                        eliminate_extras.__name__))
    final = []
    for key in boxes:
        each = boxes[key]
        index = each['perimeter'].index(min(each['perimeter']))

        test_area = each["test_area"][index]
        checked = checked_unchecked(test_area, file)

        temp = {"checked": checked,
                # "perimeter" : each["perimeter"][index],
                # "area" : each["area"][index],
                "center": each["center"][index],
                # "asp_ratio" : each["asp_ratio"][index],
                "contour": each["contour"][index]
                # "test_area" : each["test_area"][index]
                }
        final.append(temp)

    # logger.print_log_level(Criticality.INFO, "[{}] -> Exiting checkbox_module: {}".format(datetime.now(),
    #                                                                                       eliminate_extras.__name__))
    return final

#@scrape_data
def draw_checkboxes(file_name, png_file, final_boxes):
    """
    This function is used to draw the boxes detected on the PNG images as per the page number and saves them as
    markedBoxes.png
    :param file_name: File name of the original PNG
    :param png_file: original image object (cv2 object)
    :param final_boxes: contours that are to be marked on it
    :return:
    """
    # logger = LoggingService()
    # # DRAW CONTOURS AND WRITE TO NEW PNG
    # logger.print_log_level(Criticality.INFO, "[{}] -> Entering checkbox_module: {}".format(datetime.now(),
    #                                                                                        draw_checkboxes.__name__))
    og_img = png_file
    contours = [x['contour'] for x in final_boxes]

    for c in contours:
        cv2.drawContours(og_img, [c], 0, (0, 255, 0), 2)

    print(">> got file : ", file_name)

    write_file = file_name + "_markedBoxes.png"
    print(">> writing as : ", write_file)
    cv2.imwrite(write_file, og_img)
    # logger.print_log_level(Criticality.INFO, "[{}] -> Exiting checkbox_module: {}".format(datetime.now(),
    #                                                                                       draw_checkboxes.__name__))
    return True

#@scrape_data
def get_png_dimensions(png_file):
    """
    Returns the shape(rows, columns, channels) of the image
    :param png_file: Input Image
    :return: shape(rows, columns, channels) of png_file
    """
    # logger = LoggingService()
    # logger.print_log_level(Criticality.INFO, "[{}] -> Entering checkbox_module: {}".format(datetime.now(),
    #                                                                                        get_png_dimensions.__name__))
    og_img = png_file
    dimensions = og_img.shape
    # logger.print_log_level(Criticality.INFO, "[{}] -> Exiting checkbox_module: {}".format(datetime.now(),
    #                                                                                       get_png_dimensions.__name__))
    return dimensions

#@scrape_data
def name_without_extension(filename):
    """
    Returns the name of the file after removing the extension from the file name
    :param filename: Filename with extension
    :return: Filename without extension
    """
    #logger = LoggingService()
    # logger.print_log_level(Criticality.INFO, "[{}] -> Entering checkbox_module: {}".
    #                        format(datetime.now(), name_without_extension.__name__))
    name, ext = os.path.splitext(filename)
    # logger.print_log_level(Criticality.INFO, "[{}] -> Entering checkbox_module: {}".
    #                        format(datetime.now(), name_without_extension.__name__))
    return name

#@scrape_data
def get_png_index(png_filename, pdf_filename):
    """
    Returns the pg_index of the png image
    :param png_filename: PNG file name
    :param pdf_filename: PDF file name
    :return:
    """
    # logger = LoggingService()
    # logger.print_log_level(Criticality.INFO, "[{}] -> Entering checkbox_module: {}".format(datetime.now(),
    #                                                                                        get_png_index.__name__))
    pdf_name = name_without_extension(pdf_filename)
    png_name = name_without_extension(png_filename)

    pg_num = png_name.replace(pdf_name, "")

    if "_" in pg_num:
        pg_num = pg_num.lstrip("_")
    pg_num = pg_num.lstrip("0")

    pg_index = int(float(pg_num)) - 1

    # logger.print_log_level(Criticality.INFO, "[{}] -> Exiting checkbox_module: {}".format(datetime.now(),
    #                                                                                       get_png_index.__name__))
    return pg_index

#@scrape_data
def main_checkbox(pdf_file_obj, box_parameters):
    """
    Main function that executed checkbox extraction workflow
    :param pdf_file_obj: PDF byte object
    :param box_parameters: Minimum threshold
    :return:
    """
    # logger = LoggingService()
    # logger.print_log_level(Criticality.INFO, "[{}] -> Entering checkbox_module: {}".format(datetime.now(),
    #                                                                                        main_checkbox.__name__))
    text_to_replace_checkbox = CONFIG_CHECKBOX["default"]["text_to_replace"]
    # these parameters can be altered as per the PDF template
    # box_parameters = [min_threshold_area, max_threshold_area, 0.8, 1.2]  # reduced the minimum threshold to 100

    # OPEN PDF
    # pdf_path = os.path.abspath(os.path.join(directory, pdf_filename))

    # SET PARAMS for box retrieval (defaults given)
    threshold_min_area = box_parameters[0]  # 200
    threshold_max_area = box_parameters[1]  # 1000
    lower_aspect_ratio = box_parameters[2]  # 0.8
    higher_aspect_ratio = box_parameters[3]  # 1.2

    for page in pdf_file_obj:
        zoom = 2
        mat = fitz.Matrix(zoom, zoom)
        pix = page.getPixmap(matrix=mat)
        img_data = pix.getImageData("png")
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Get Checkboxes
        all_boxes = get_boxes(img, threshold_min_area, threshold_max_area, lower_aspect_ratio, higher_aspect_ratio)
        final_boxes = eliminate_extras(all_boxes, img)

        # GET PNG dimensions
        dimensions = get_png_dimensions(img)
        png_height = dimensions[0]
        png_width = dimensions[1]

        # GET FITZ dimensions
        # page = pdf_fitz_object[png_index]
        fitz_height = page.rect.height
        fitz_width = page.rect.width
        # print("fitz height, width : ", fitz_height, ",", fitz_width)

        # Text for CHECKED check-boxes
        text = text_to_replace_checkbox

        for x in final_boxes:
            # print(x['center'], ">", x['checked'])
            if x['checked'] == 1:
                indent = (x['center'][0] / png_width) * fitz_width
                depth = (x['center'][1] / png_height) * fitz_height
                where = fitz.Point(indent, depth)    # text starts here
                page.insertText(where, text,
                                fontsize=2,        # default
                                overlay=True)      # text in foreground

    checked_pdf_bytes = pdf_file_obj.write()
    # logger.print_log_level(Criticality.INFO, "[{}] -> Exiting checkbox_module: {}".format(datetime.now(),
    #                                                                                       main_checkbox.__name__))
    return checked_pdf_bytes

#@scrape_data
def main_function(pdf, template_type=None):
    # logger = LoggingService()
    # logger.print_log_level(Criticality.INFO, "[{}] -> Entering checkbox_module: {}".format(datetime.now(),
    #                                                                                        main_function.__name__))
    box_parameters = [CONFIG_CHECKBOX["default"]["minimum_threshold"], CONFIG_CHECKBOX["default"]["maximum_threshold"],
                      CONFIG_CHECKBOX["default"]["lower_aspect_ratio"], CONFIG_CHECKBOX["default"]
                      ["higher_aspect_ratio"]]
    # identification of template
    if template_type and template_type in CONFIG_CHECKBOX.keys():
        box_parameters[0] = CONFIG_CHECKBOX[template_type]["minimum_threshold"]
        box_parameters[1] = CONFIG_CHECKBOX[template_type]["maximum_threshold"]

    # if pdf is path then change it to byte array
    if type(pdf) is bytes:
        pdf_obj = fitz.Document(stream=pdf, filetype="pdf")
        checked_pdf_byte = main_checkbox(pdf_obj, box_parameters)
        # logger.print_log_level(Criticality.INFO, "[{}] -> Exiting checkbox_module: {} - Returning checkbox marked PDF "
        #                                          "byte array".format(datetime.now(), main_function.__name__))
        return checked_pdf_byte
    else:
        if os.path.exists(pdf):
            pdf_path = os.path.split(pdf)[0]
            checkbox_pdf_name = "checkbox_marked_" + os.path.split(pdf)[1]
            pdf_obj = fitz.Document(pdf)
            checked_pdf_byte = main_checkbox(pdf_obj, box_parameters)
            checkbox_pdf_path = os.path.join(pdf_path, checkbox_pdf_name)
            with open(checkbox_pdf_path, "wb") as fp:
                fp.write(checked_pdf_byte)
                print("Checkbox marked pdf path: ", checkbox_pdf_path)
            # logger.print_log_level(Criticality.INFO, "[{}] -> Exiting checkbox_module: {} - Copying the checkbox marked"
            #                                          " PDF to the destination file folder".
                              #     format(datetime.now(), main_function.__name__))
            return checkbox_pdf_path
        else:
            # logger.print_log_level(Criticality.INFO, "[{}] -> Exiting checkbox_module: {} - Returning None as File path"
            #                                          " does not exist".format(datetime.now(), main_function.__name__))
            return None


if __name__ == "__main__":
    pdf_path = sys.argv[1]

    if len(sys.argv) == 3:
        template_type = sys.argv[2]
        result = main_function(pdf_path, template_type)
    else:
        result = main_function(pdf_path)

    print("Result: ", result)
