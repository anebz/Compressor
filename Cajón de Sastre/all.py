import os
import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import operator
import json
import ast
import math

# ~~~~ GLOBAL VARIABLES ~~~~
origin_path = ''
first_ext = ''  # first extension of the origin file
zeros = 0  # redundancies to be added in the code
num = 7  # # bits to be used for encoding
b = [0, 0]  # global variable for the buttons
e = [0, 0]  # global variable for the entries
foldername = ''
allinfo = ''
files = []
dirs = []
dirpath = ''


# ~~~~ COMPRESSION FUNCTIONS ~~~~
# returns a list with the Huffman-encoded ASCII table
def constructHuffmanTree(text, progress):

    # returns a list with the frequencies of each letter in the string
    def frequency(string, progress):
        freq, leng = {}, len(string)
        progress["maximum"] += len(set(string)) * 50
        for i in set(string):
            progress["value"] += 50
            progress.update()
            if string.count(i):
                freq[i] = string.count(i) * 1.0 / leng
        return freq

    count = frequency(text, progress)
    auxTree = dict.fromkeys(count.keys(), '')
    savedCoding = dict()
    numbers = range(len(count) - 1)
    progress["maximum"] += len(numbers) * 50
    for ii in numbers:
        progress["value"] += 50
        progress.update()
        flag = 0
        auxDict = dict()
        dictValues = list(count.values())
        smallestElementValue = min(dictValues)
        secondSmallestElementValue = sorted(dictValues, key=float)[1]
        for key, value in count.items():
            if value == smallestElementValue or value == secondSmallestElementValue:
                flag += 1
                if flag == 1:
                    node1 = key
                    for jj in key:
                        auxTree[jj] = '0' + auxTree[jj]
                    if node1 in savedCoding.keys() and ii != numbers[-1]:
                        auxDict['0'] = savedCoding[node1]
                    elif ii != numbers[-1]:
                        auxDict['0'] = node1
                elif flag == 2:
                    node2 = key
                    for jj in key:
                        auxTree[jj] = '1' + auxTree[jj]
                    if node2 in savedCoding.keys() and ii != numbers[-1]:
                        auxDict['1'] = savedCoding[node2]
                    elif ii != numbers[-1]:
                        auxDict['1'] = node2
                    break
        count[node1] = count[node1] + count[node2]
        newLetter = node1 + node2
        count[newLetter] = count[node1]
        if ii != numbers[-1]:
            savedCoding[newLetter] = auxDict
        del count[node1]
        del count[node2]
        del auxDict
        if node1 in savedCoding.keys() and ii != numbers[-1]:
            del savedCoding[node1]
        if node2 in savedCoding.keys() and ii != numbers[-1]:
            del savedCoding[node2]
    finalKeys = list(savedCoding.keys())
    savedCoding['0'] = savedCoding.pop(finalKeys[0])
    savedCoding['1'] = savedCoding.pop(finalKeys[1]) # PETA CUANDO HAY 3 LETRAS
    return savedCoding, auxTree

# given a tree and words being the string read from the file, returns a compressed string
def encode(tree, words, progress):
    global zeros
    code = ''
    counter = 0
    for let in words:
        counter += 1
        if let in tree.keys():
            code = code + str(tree[let])
        if counter > len(words) / 100:
            counter = 0
            progress["value"] += 50
            progress.update()

    # add redundant zeroes
    zeros = num - len(code) % num
    if len(code) % num != 0 and zeros != num:
        code = code + '0000000'[len(code) % num:num]
    else:
        zeros = 0

    # from binary string to char string
    compressed = ''
    for i in range(0, len(code), num):
        compressed = compressed + chr(int(code[i:i + num], 2) + 40)
    return compressed


def getallinfo(dirpath):
    global allinfo
    for (dirpath, dirnames, filenames) in os.walk(dirpath):
        dirs = dirnames
        files = filenames
        break
    foldername = dirpath[dirpath.rfind('/') + 1:]
    for file in files:
        if '.txt' in file:
            allinfo += open(dirpath + '/' + file, 'r', encoding='utf-8').read()
    # allinfo: now we have all the strings together, we need to create the tree for all files
    for folder in dirs:
        getallinfo(dirpath + '/' + folder)


def recursive_compression(dirpath, f, encodingTree):
    for (dirpath, dirnames, filenames) in os.walk(dirpath):
        dirs = dirnames
        files = filenames
        break

    # write foldername
    f.write('{foldername: ' + dirpath[dirpath.rfind('/') + 1:] + '}')  # name of folder we're in

    # loop for all folders
    for folder in dirs:
        recursive_compression(dirpath + '/' + folder, f, encodingTree)

    # loop for all the files
    for filename in files:
        if '.txt' in filename:
            f.write('{file' + str(zeros) + ': ' + filename + '}')  # writing filename and zeros at the same time
            compressed = encode(encodingTree, open(dirpath + '/' + filename, 'r', encoding='utf-8').read(), progress)
            f.write(compressed)
    f.write('{}')  # keyword to represent end of folder


def foldercompression():
    global dirpath
    # dump tree
    progress["maximum"] = 5000
    progress["value"] = 0

    # create tree with all info from all files
    getallinfo(dirpath)
    tree, encodingTree = constructHuffmanTree(allinfo, progress)

    f = open(destination_path, 'w', encoding='utf-8')
    json.dump(tree, f)  # dump tree

    recursive_compression(dirpath, f, encodingTree)


def compression(progress):
    # progress bar
    global destination_path
    progress.grid(row=2, column=2, sticky='ew', padx=5)
    progress.pack()
    progress["value"] = 0
    progress.update()
    progress["maximum"] = 5000

    # get the values from the entries
    destination_path = e[1].get()
    if dirpath != '':
        foldercompression()
        return
    origin_data = open(e[0].get(), 'r', encoding='utf-8').read()
    print(origin_data)
    # Tree generation and encoding
    tree, encodingTree = constructHuffmanTree(origin_data, progress)
    compressed = encode(encodingTree, origin_data, progress)
    print("Compresion rate:", math.fabs(1 - (len(compressed) / len(origin_data))) * 100, "%")

    tree['999'] = zeros  # save zeros in tree for future use

    # write in file
    f = open(destination_path, 'w', encoding='utf-8')
    json.dump(tree, f)  # dump tree
    f.write(compressed)
    f.close()
    progress["value"] += 50
    progress.update()
    messagebox.showinfo("Message", "Compression finished")


# ~~~~ DECOMPRESSION FUNCTIONS ~~~~
def decode(text, tree, progress):
    # string to code
    progress["maximum"] = 90500
    code = ''
    cont = 0
    for e in text:
        cont += 1
        if cont > len(text) / 100:
            progress["value"] += 100
            progress.update()
            cont = 0
        auxcode = bin(ord(e) - 40)[2:]
        if len(auxcode) != num:
            auxcode = '0' * (num - len(auxcode)) + auxcode
        code += auxcode
    code = code[:(len(code) - zeros)]  # deleting the redundancies

    # code to decompressed string
    node = tree
    text = ''
    cont = 0
    for ii in code:
        cont += 1
        if cont > len(code) / 800:
            progress["value"] += 100
            progress.update()
            cont = 0
        if ii not in node:
            return text
        elif type(node[ii]) is dict:
            node = node[ii]
        elif type(node[ii]) is str:
            text += node[ii]
            node = tree
    return text


def folderdecompression(dirpath):
    return


def decompression(progress):
    global zeros

    # progress bar
    progress["value"] = 0
    progress.update()
    # get the values from the entries
    origin_data = open(e[0].get(), 'r', encoding='utf-8').read()
    destination_path = e[1].get()

    text_from_file = 'r' + origin_data  # to escape newline characters

    # extract dict (tree) from the string read from the file
    cnt = 0
    for i in range(1, len(text_from_file)):
        if text_from_file[i] == '{':
            cnt += 1
        elif text_from_file[i] == '}':
            cnt -= 1
        if cnt == 0:
            tree2 = ast.literal_eval(text_from_file[1:i + 1])
            break;
    text_from_file = text_from_file[i + 1:]  # the encoded text

    # POSSIBLE BREAKPOINT

    if text_from_file.startswith('{foldername: '):  # protocol: we're in 1+ file mode
        text_from_file = text_from_file[:-2]  # delete the last '{}'
        foldername = text_from_file[13:text_from_file.find('}')]
        # create folder
        newdir = destination_path[:destination_path.rfind('/') + 1] + foldername
        if os.path.exists(newdir):
            messagebox.showinfo("Error", "Folder already exists! Choose another directory")
            return

        # decompress and write file for each file
        os.makedirs(newdir)
        while (1):
            zeros = int(text_from_file[text_from_file.find('{file') + 5])
            text_from_file = text_from_file[text_from_file.find('{file') + 5:]
            lastpoint = text_from_file.find('}')
            filename = text_from_file[3:lastpoint]
            text_from_file = text_from_file[lastpoint + 1:]

            if text_from_file.find('{file') != -1:
                decoded = decode(text_from_file[:text_from_file.find('{file')], tree2)
                f = open(newdir + '/' + filename, 'w', encoding='utf-8')
                f.write(decoded)
            else:
                decoded = decode(text_from_file, tree2)
                f = open(newdir + '/' + filename, 'w', encoding='utf-8')
                f.write(decoded)
                f.close()
                break;

    else:  # single text mode
        zeros = tree2['999']
        decoded = decode(text_from_file, tree2, progress)

        f = open(destination_path, 'w', encoding='utf-8')
        f.write(decoded)
        f.close()

    progress["value"] = progress["maximum"]
    progress.update()
    messagebox.showinfo("Message", "Decompression finished")



# ~~~~ GUI FUNCTIONS ~~~~
def open_origin_file():
    global origin_path
    options = {}
    options['filetypes'] = [('text files [.txt]', '.txt'), ('Huffman-compressed files [.hff]', '.hff')]
    options['initialdir'] = os.getcwd()
    options['title'] = 'Choose file'

    filename = filedialog.askopenfilename(**options)

    if filename:  # if filename exists
        first_ext = filename[-3:]  # get extension
        e[1].delete(0, END)
        # change button states depending on the extension of the origin file
        if first_ext == 'txt':
            b[0].config(state='active')
            b[1].config(state='disabled')
            e[1].insert(0, filename[:-3] + 'hff')
        elif first_ext == 'hff':
            b[0].config(state='disabled')
            b[1].config(state='active')
            e[1].insert(0, filename[:-3] + 'txt')
        origin_path = filename
        e[0].delete(0, END)
        e[0].insert(0, origin_path)


# open all files under dir
def open_origin_dir():
    global origin_path, foldername, allinfo, dirpath
    dirpath = filedialog.askdirectory()
    files = []

    e[0].delete(0, END)
    e[0].insert(0, dirpath)


def open_destination_file():
    options = {}
    if first_ext == 'txt':
        options['defaultextension'] = '.hff'
        options['filetypes'] = [('Huffman-compressed files [.hff]', '.hff')]
    elif first_ext == 'hff':
        options['defaultextension'] = '.txt'
        options['filetypes'] = [('text files [.txt]', '.txt')]
    options['initialdir'] = 'C:\\' + origin_path
    options['title'] = 'Choose file'

    filename = filedialog.asksaveasfilename(**options)

    if filename:
        e[1].delete(0, END)
        e[1].insert(0, filename)




        # ~~~~~~ MAIN ~~~~~~~~


root = Tk()
root.title('Huffman Compressor')
# geometry of the window
# "width x height + hor_pos + ver_pos"
root.geometry("750x150+250+300")

mf = Frame(root)
mf.pack()

f1 = Frame(mf, width=500, height=50)
f1.pack(fill=X)  # make all widgets as wide as the parent widget
f2 = Frame(mf, width=500, height=50)
f2.pack()
f3 = Frame(mf, width=500, height=50, pady=10)
f3.pack()

# sticky: to change the fact that widgets are centered in their cells
# N(north), S(south), E(east), W(west)
Label(f1, text="Select origin file").grid(row=0, column=0, sticky='e')
e[0] = Entry(f1, width=75, textvariable=origin_path)  # entry for origin file
e[0].grid(row=0, column=1, padx=2, pady=1, sticky='ew', columnspan=25)

Label(f1, text="Select destination file").grid(row=1, column=0, sticky='e')
e[1] = Entry(f1, width=75, textvariable='')  # entry for destination file
e[1].grid(row=1, column=1, padx=2, pady=1, sticky='ew', columnspan=25)

progress = ttk.Progressbar(f3, orient="horizontal", length=700, mode="determinate")

b[0] = Button(f2, text="Compress", width=25, command=lambda: compression(progress))  # compression button
b[0].grid(row=2, column=2, sticky='ew', padx=5)
b[1] = Button(f2, text="Decompress", width=25, command=lambda: decompression(progress))  # decompression button
b[1].grid(row=2, column=3, sticky='ew', padx=5)

Button(f1, text="file", command=lambda: open_origin_file()).grid(row=0, column=27, sticky='ew', padx=8, pady=4)
Button(f1, text="...", command=lambda: open_destination_file()).grid(row=1, column=27, sticky='ew', padx=8, pady=4)
Button(f1, text="dir", command=lambda: open_origin_dir()).grid(row=0, column=35, sticky='ew', padx=8, pady=4)

# do this as last thing
root.mainloop()  # so that the GUI is always waiting for input
