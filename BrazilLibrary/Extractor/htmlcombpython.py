import os
import PyPDF2
import sys
from shutil import copyfile
# from HiLITDECoreLibraries.Utilities.decorator import scrape_data

# @scrape_data
def find_lines(read_file, write_file, search_string):
    """
    Filter out lines containing 'position = absolute'
    :param read_file: <Str> HTML file to read
    :param write_file: <Str> Filename to write
    :return:
    """
    with open(write_file, 'w+', encoding='utf-8') as c:
        # finding all the lines with "position:absolute"
        for line in open(read_file, 'r', encoding='utf-8'):
            if line.find(search_string) != -1:
                c.write(line)

# @scrape_data
def splitting_top_coordinate(read_file, write_file):
    """
    Splits the HTML data after splitting the top coordinate
    :param read_file: <Str> HTML file to read
    :param write_file: <Str> Filename to write
    :return:
    """
    with open(write_file, 'w+', encoding='utf-8') as d:
        # finding all the lines with ";top:"
        for line in open(read_file, 'r', encoding='utf-8'):
            r = line.partition(';top:')[2]
            d.write(r)

# @scrape_data
def comb_page_data(read_file, write_file, ft, px):
    """
    Returns the combed content of the HTML page
    :param read_file: <Str> HTML file to read
    :param write_file: <Str> Filename to write
    :param ft: <List> List of font class
    :param px: <List> List of pixel values
    :return:
    """
    with open(write_file, 'w+', encoding='utf-8') as fp:
        # appending the pixel value with the other co-ordinates
        for line in open(read_file, 'r', encoding='utf-8'):
            for j in ft:
                if j in line:
                    ind1 = line.index('ft')
                    ind2 = line.index('"', ind1)
                    z = line[ind1:ind2]
                    ind3 = ft.index(z)
                    stf = line[:ind1]
                    stl = line[ind2:]
                    r = stf + "" + px[ind3] + "" + stl
                    r = r.replace('"', ' ').replace('>', ' ').replace('px ft', ' ')
                    fp.write(r)
                    break


# combing
#@scrape_data
def combing(inputpdf):
    """
    Creates a combed HTML file
    :param inputpdf: <Str> PDF file name
    :return:
    """
    add = 0
    page_data = "1.txt"
    data_row = "4.txt"
    combed_page_data = "5.txt"
    for y in range(inputpdf.getNumPages()):
        y += 1

        with open('datahtml-%d.html' % y, 'r', encoding='utf-8') as a:
            data = a.read()

        with open(page_data, 'w+', encoding='utf-8') as b:
            b.write(data)

        # Filtering the line containing 'position=absolute'
        find_lines(page_data, '2.txt', 'position:absolute')

        # splitting the top coordinate from the HTML data
        splitting_top_coordinate('2.txt', '3.txt')

        with open(data_row, 'w+', encoding='utf-8') as e:
            # finding all the lines with "px;left:" and removing all the garbage values(html tags)
            for line in open('3.txt', 'r', encoding='utf-8'):
                r = line.partition('px;left:')[0::2]
                r = ' '.join(r)
                r = r.partition(';white-space:nowrap\" class=\"')[0::2]
                r = ' '.join(r)
                r = r.replace('</p>', ' ').replace('&#160;', ' ').replace('</b>', ' ').replace('<br/>', ' ')
                r = r.replace('<b>', ' ').replace('<i', ' ').replace('</i', ' ').replace('<a href=', ' ')
                r = r.replace('</a', ' ')
                e.write(r)

        # Filtering the line containing 'font-family'
        find_lines(page_data, 'font.txt', 'font-family')

        ft = []
        px = []

        with open('font1.txt', 'w+', encoding='utf-8') as fp:
            # extracting only class name and font pixel values
            for line in open('font.txt', 'r', encoding='utf-8'):
                line = line.replace('p {margin: 0; padding: 0;}', '')
                line = line.partition('{font-size:')[0::2]
                line = ' '.join(line)
                line = line.partition('px')[0]
                line = line.partition('.')[2]
                fp.write(line + '\n')
                ft.append(line.partition(' ')[0])
                tmp = line.partition(' ')[0::2]
                tmp = ';'.join(tmp)
                px.append(tmp)

        # Returns combed HTML page
        comb_page_data(data_row, combed_page_data, ft, px)

        # making a copy of the file
        copyfile(combed_page_data, '6.txt')
        index = []
        sortedlist = []

        with open(combed_page_data, 'w+', encoding='utf-8') as fp:
            # removing garbage values and replacing spaces with pipes(||) in the co-ordinates
            for line in open(data_row, 'r', encoding='utf-8'):
                line = line.replace('"', ' ').replace('px ft', ' ').replace(';', '||')
                index.append(int(line.partition(' ')[0]))
                i = line.find('>') + 1
                st = line[:i]
                en = line[i:].strip()
                st = st.replace(' ', '||')
                line = st + en + '\n'
                line = line.replace('>', '')
                sortedlist.append(line)
                fp.write(line)

        # sorting the lines with respect to first column
        sortedlist = sorted(list(sortedlist), key=lambda x: int(x.partition('||')[0]))
        # sorting the lines with respect to first and second column
        fsortedlist = sorted(list(sortedlist), key=lambda x: (int(x.split('||')[0]), int(x.split('||')[1])))
        index.sort()

        with open(combed_page_data, 'w+', encoding='utf-8') as fp:
            for i in fsortedlist:
                fp.write(i)
        # writing all the changes to a new files(individual page combing)
        output = open('%d.comb' % y, 'w+', encoding='utf-8')
        i = 0

        for line in open(combed_page_data, 'r', encoding='utf-8'):
            r = str(add + index[i]) + '||' + line
            output.write(r)
            i += 1

        add += index[i - 1]
        output.close()

    # combing all the individual combing pages
    for i in range(inputpdf.getNumPages()):
        i += 1
        with open('htmlcomb.comb', 'a+', encoding='utf-8') as fp:
            for line in open('%d.comb' % i, 'r', encoding='utf-8'):
                fp.write(line)

#@scrape_data
def main_function(file):
    """
    Creates the combing file of the PDF file
    :param file: <Str> PDF filename
    :return:
    """
    curdir = os.getcwd()
    # removing text,comb,png,html files from the current directory
    text_files = [f for f in os.listdir(curdir) if f.endswith('.txt')]
    comb_files = [f for f in os.listdir(curdir) if f.endswith('.comb')]
    png_files = [f for f in os.listdir(curdir) if f.endswith('.png')]
    html_files = [f for f in os.listdir(curdir) if f.endswith('.html')]
    for i in text_files:
        os.remove(i)
    for i in comb_files:
        os.remove(i)
    for i in png_files:
        os.remove(i)
    for i in html_files:
        os.remove(i)
    os.system('pdftohtml -c "{}" datahtml'.format(file))
    # finding the number of pages in the pdf
    inputpdf = PyPDF2.PdfFileReader(open(file, "rb"))
    combing(inputpdf)


if __name__ == '__main__':
    filename = sys.argv[1]
    main_function(filename)
