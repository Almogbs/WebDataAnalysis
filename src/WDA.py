"""
Almog Ben shaul

March 2018

TODO:c
- add proccesbar bug
"""

from bs4 import BeautifulSoup
from bs4.element import Comment
from tkinter import *
import tkinter.ttk as ttk
from tkinter import messagebox
import urllib.request
import re
import time
import csv
import matplotlib.pyplot as plt
import numpy as np
from imageai.Detection import ObjectDetection
from imageai.Prediction import ImagePrediction
import os
import re
import requests



# "list of "junk words"
junk_words = ["class", "href", "item", "li", "com", "span", "www", "gri"
              "depth", "the", "of", "and", "to", "or", "within", "has", "must", "these", "under", "from", "such",
              "have", "with", "will", "your", "are", "which", "at", "as", "may", "other", "use", "this", "that",
              "we", "be", "not", "on", "site", "by", "you", "for", "is", "a", "our", "in", "any", "div", "group",
              "menu", "wp", "id", "type", "https", "data", "llp", "no", "yes", "ul", "line", "path", "script",
              "src", "js", "javascript", "link", "rel", "content", "title", "wiki", "svg", "org", "width", "mw",
              "wikimedia", "thumb", "png", "ii", 'abstract', 'arguments', 'await', 'boolean', 'break', 'byte', 'case',
              'catch', 'char', 'class', 'const', 'continue', 'debugger', 'default', 'delete', 'dodouble', 'else',
              'enum', 'eval', 'export', 'extends', 'false', 'final', 'finally', 'float', 'for', 'function', 'goto',
              'if', 'implements', 'import', 'in', 'instanceof', 'int', 'interfacelet', 'long', 'native', 'newnull',
              'package', 'private', 'protected', 'public', 'return', 'short', 'static', 'super', 'switch',
              'synchronized', 'this', 'throw', 'throws', 'transient', 'truetry', 'typeof', 'var', 'void', 'volatile',
              'while', 'with', 'yield', 'abbr', 'acronym', 'address', 'applet', 'area', 'article', 'aside', 'audio',
              'audio', 'base', 'basefont', 'bdi', 'bdo', 'tr', 'track', 'tt','read', 'ul', 'var', 'wbr', 'true',
              'big', 'blockquote', 'body', 'br', 'button', 'canvas', 'caption', 'center', 'cite', 'code', 'col',
              'colgroup', 'datalist', 'dd', 'del', 'details', 'dfn', 'dialog', 'dir', 'div', 'dl', 'dt', 'em',
              'embed', 'fieldset', 'figcaption', 'figure', 'font', 'footer', 'form', 'frame', 'frameset', 'h1',
              'h6', 'head', 'header', 'hr', 'html', 'iframe', 'img', 'input', 'ins', 'kbd', 'label', 'legend',
              'li', 'link', 'main', 'map', 'mark', 'menu', 'menuitem', 'meta', 'meter', 'nav', 'noframes',
              'noscript', 'object', 'ol', 'optgroup', 'option', 'output', 'param', 'pre', 'progress',
              'rp', 'rt', 'ruby', 'samp', 'section', 'select', 'small', 'source', 'span', 'strike',
              'strong', 'style', 'sub', 'summary', 'sup', 'svg', 'table', 'tbody', 'td', 'template', 'textarea',
              'tfoot', 'th', 'thead', 'time', 'title', 'name', 'env', 'stage', 'color', 'text', 'page',
              'margin', 'padding', 'error', 'found', 'require', 'null', 'searchbox', 'gettime', 'end', 'more', 'what']

def getTimeName():
    return time.strftime("%H-%M-%S_%d-%m-%Y", time.gmtime())

def getImages(url_addr, folder):
    os.makedirs(folder)
    response = requests.get(url_addr)
    soup = BeautifulSoup(response.text, 'html.parser')
    img_tags = soup.find_all('img')
    urls = [img['src'] for img in img_tags] 

    ctr = 0
    for url in urls:
        filename = re.search(r'/([\w_-]+[.](jpg|gif|png|jpeg))$', url)
        if filename is not None:
            path = os.path.join(folder, filename.group(1))
            with open(path, 'wb') as f:
                if 'http' not in url:
                    url = '{}{}'.format(url_addr, url)
                response = requests.get(url)
                f.write(response.content)
        else:
            if 'http' not in url:
                continue
            path = os.path.join(folder, "{}.jpg".format(ctr))
            ctr += 1
            with open(path, 'wb') as f:
                response = requests.get(url)
                f.write(response.content)


def finder(element):
    """ check if element contain text """
    if element.parent.name in ['[document]', 'head', 'title', 'style', 'script', 'meta']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def parser(source):
    """ find only the visible text """
    soup = BeautifulSoup(source, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(finder, texts)  
    return u" ".join(t.strip() for t in visible_texts)


def _mainact(self, url, tree, fvar, svar):
    """ The Main action of the Program """
    # deleting the pre search( if exists)
    try:
        tree.delete(*tree.get_children())

    except Exception as e:
        pass

    try:
        #extacting the images from the website
        image_folder = getTimeName() + " images"
        getImages(url, image_folder)
        md = ObjectDetection()
        md.setModelTypeAsYOLOv3()
        md.setModelPath(os.path.join(os.getcwd() ,"models", "yolo.h5"))
        md.loadModel()

        detections_list = []


        for file in os.listdir(image_folder):
            if(file.endswith(".jpg") or file.endswith(".png") or file.endswith(".jpeg")):
                detections = md.detectObjectsFromImage(input_image=os.path.join(image_folder , file), output_image_path=os.path.join(image_folder , "new" + file), minimum_percentage_probability=50)
                for eachObject in detections:
                	detections_list.append(eachObject["name"])
					    

        detections_ht = {word: detections_list.count(word) for word in detections_list}
        objectss = [*detections_ht.keys()]
        amounts = [*detections_ht.values()]


        html = urllib.request.urlopen(url).read()
        soure_string = parser(html).lower()
        # regex to find all valid words
        regex = r'\b([a-zA-Z]+)\b'
        word_list = re.findall(regex, soure_string)


        # removing the name of the site from the word list (by adding them to the junk word list)
        matches = re.findall(r'\b([a-zA-Z]+)\b', url)
        junk_words.append(matches[0])
        junk_words.append(matches[1])
        junk_words.append(matches[2])
        #print(junk_words)

        filterd_word_list = []

        for word in word_list:
            if len(word) >= 3:
                filterd_word_list.append(word)

        listed_dict = {word: filterd_word_list.count(word) for word in filterd_word_list}

        # crete list with all items(key and value) in the dict
        listfinished = list(listed_dict.items())

        # sorting the list by the second index
        listfinished.sort(key=lambda tup: tup[1])


        # Calcuclating the total "good" words
        tot = 0.0

        for key, value in listfinished:

            if key not in junk_words:
                tot += value

        plist = []

        for key, value in listfinished:

            # check if the word not in "JUNK WORDS"
            if key not in junk_words:
                # 1.WORD 2.FREQUANCY 3.PERCENT
                plist.append(tuple((key, str(value), str(float((value / tot) * 100)) + "%")))

        plist = reversed(plist)

        # insert the values in the treelist box by add_to_listbox fuction (in main class)

        steps = 0
        for item in plist:
            self._add_to_listbox(item)
            steps += 1
            if steps == 50:
                break
        yy_pos = np.arange(len(objectss))
        plt.figure(100)
        plt.bar(yy_pos, amounts)
        plt.xticks(yy_pos, objectss)
        plt.xlabel('Object')
        plt.ylabel('Frequency')
        plt.title('Frequency of Objects from images - ' + url)
        plt.show()

        # Graph Drawing (if checked)
        if svar.get():

            maxresult = 0

            objects = []
            performance = []

            for key, value in reversed(listfinished):
                if key not in junk_words:
                    objects.append(key)
                    performance.append(value)
                    maxresult += 1
                    if maxresult == 10:
                        break

            y_pos = np.arange(len(objects))
            plt.figure(200)
            plt.bar(y_pos, performance)
            plt.xticks(y_pos, objects)
            plt.xlabel('Word')
            plt.ylabel('Frequency')
            plt.title('Frequency of Words - ' + url)
            plt.show()

        # if user put V in check to export
        if fvar.get():

            csvlist = []

            for key, value in listfinished:

                if key not in junk_words:
                    # add to csvlist in scv format (word,word)
                    csvlist.append((key + "," + str(value) + "," + str(float((value / tot) * 100)) + "%"))

            # var with current time
            nowt = getTimeName();
            # creat csv file
            with open('exportFile_{}.csv'.format(nowt), 'w', newline='') as newf:
                csv_writer = csv.writer(newf, delimiter='\t')
                # heading of the tables in csv
                csv_writer.writerow("Result of:        ,    {}".format(url))
                csv_writer.writerow("Word:             ,    Frequency:      ,        Stats:                ")

                for i in reversed(csvlist):
                    csv_writer.writerow(i)

    # if something goes wrong pop error message
    except Exception as r:
        
        messagebox.showinfo('Error', r)


# declare the main class
class _Main:

    def __init__(self, title, size, tek, frame, frame1):

        self.title = title
        self.size = size
        self.tek = tek
        self.frame = frame
        self.frame1 = frame1

        # the theme of the gui
        style = ttk.Style()
        style.theme_use('clam')

        self.tek.title(self.title)
        self.tek.geometry(self.size)
        self.tek.resizable(0, 0)

        # widget without frame:
        fk = ('FONTWIGHT_BOLD', 20, 'bold')
        self.tek.configure(background='grey')
        tit = Label(self.tek, text=self.title)
        tit.config(font=fk, foreground='black', bg='grey')
        tit.grid(row=0, column=1)
        lurl = Label(self.tek, text="Enter The URL With https Prefix & Without www.\n e.g: https://example.com")
        lurl.configure(background='grey')
        lurl.grid(row=1, column=1)
        eurl = Entry(self.tek, width=50)
        eurl.grid(pady=5, row=2, column=1)

        # first frame:
        var = IntVar()
        var1 = IntVar()

        c = Checkbutton(
            self.frame, text="Export result to external file",
            variable=var)
        c.configure(background='grey')
        c.grid(row=1, column=1)

        c2 = Checkbutton(
            self.frame, text="Create bar chart file",
            variable=var1)
        c2.configure(background='grey')
        c2.grid(row=2, column=1)

        # second frame:
        cols = ['Word', 'Frequency', 'Stats']
        self.tree_listbox = ttk.Treeview(self.frame1, height=23, columns=cols, show="headings")
        self.tree_listbox.grid(row=0, column=1)

        for col in cols:

            self.tree_listbox.column(col, anchor='c')
            self.tree_listbox.heading(col, text=col.title())

        scroll_bar = Scrollbar(self.frame1, orient='vertical', command=self.tree_listbox.yview)
        scroll_bar.grid(row=0, column=1, sticky='nse')
        self.tree_listbox.config(yscrollcommand=scroll_bar.set)

        self.frame.configure(background='grey')
        self.frame1.configure(background='grey')
        self.frame.grid(row=3, column=1)
        self.frame1.grid(pady=10, row=4, column=1)

        bu = Button(self.frame, text="GO!", width=30,
                    command=lambda: _mainact(self, eurl.get(), self.tree_listbox, var, var1),
                    bg="white", relief="flat")
        bu.grid(pady=10, row=3, column=1)

    # adding items to the treeview list widget
    def _add_to_listbox(self, x):

        self.tree_listbox.insert('', 'end', values=x)

    def start(self):

        """ starting the mainloop """
        self.tek.mainloop()

def MainFunction():
        MainWin = _Main("Websites Data Analysis ", "605x650", tek=Tk(), frame=Frame(), frame1=Frame())
        MainWin.start()

def NoteFunction():
        messagebox.showinfo('NOTE!', 'Enter The URL With https Prefix & Without www.\n e.g: https://example.com')





if __name__ == '__main__':

    MainFunction()
