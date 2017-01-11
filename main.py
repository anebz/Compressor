# Imports
import operator
import json
import ast

# Global Variables
zeros = 0

# should be a .txt
def readfile(filename):
  return open(filename, encoding='utf-8').read()

def writefile(filename, tree, string):
  f = open(filename, 'w', encoding='utf-8')
  json.dump(tree, f) # dump tree
  f.write(string)
  f.close()

# returns a list with the frequencies of each letter in the string
def frequency(string):
  freq, leng = {}, len(string)
  for i in range(10000):
    if string.count(chr(i)):
      freq[chr(i)] = string.count(chr(i))*1.0/leng
  if string.count('’'):
    freq['’'] = string.count('’')*1.0/leng
  return freq

# returns the second smallest element in a numeric list
def second_smallest(numbers):
  return sorted(numbers,key=float)[1]

# returns a list with the Huffman-encoded ASCII table
def constructHuffmanTree(text, count):
  savedCoding = dict.fromkeys(count.keys(), '')
  aux = dict(count)
  for ii in range(len(count) - 1):
    flag = 0
    dictValues = list(aux.values())
    smallestElementValue = min(dictValues)
    secondSmallestElementValue = second_smallest(dictValues)
    for key,value in aux.items():
      if value == smallestElementValue or value == secondSmallestElementValue:
        flag += 1
        if flag == 1:
          node1 = key
          for jj in key:
            savedCoding[jj] = '0' + savedCoding[jj]
        elif flag == 2:
          node2 = key
          for jj in key:
            savedCoding[jj] = '1' + savedCoding[jj]
          break
    aux[node1] = aux[node1] + aux[node2]
    newLetter = node1 + node2
    aux[newLetter] = aux[node1]
    del aux[node1]
    del aux[node2]
  return savedCoding

# given a tree in this format: {'a':0, 'b':10, 'c':11}
# and words being the string read from the file
def encode(tree,words):
  code = ''
  for let in words:
    if let in tree.keys():
      code = code + str(tree[let])
  return code

def code_to_string(code):
  global zeros 
  zeros = len(code)%8
  compressed = ''
  if zeros != 0: # not a multiple of 8
    code = code + '0'*zeros # add zeroes, redundancies
  #print(code.find(tree['-'],0))
  for i in range(0,len(code),8):
    compressed = compressed + chr(int(code[i:i+8],2))
  return compressed

#Decoding function
def decode(tree2, code):
  tree = {value:key for key,value in tree2.items()}
  text,add = '',''
  for i in range(len(code)):    
    add += code[i]
    if add in tree.keys():
      text += tree[add]
      add = ''
  return text

def string_to_code(text):
  code = ''
  for e in text:
    code0 = bin(ord(e))[2:]
    if len(code0) != 8 and e != text[len(text)-1]:
      code0 = '0'*(8-len(code0)) + code0
    code += code0
  return code   
  
  
##ENCODING

# open file
file = 'a1.txt'
original_text = readfile(file)

#Constructing the tree
characterCounter = frequency(original_text)
tree = constructHuffmanTree(original_text, characterCounter)

words = original_text
code = encode(tree,words)

compressed = code_to_string(code)
print("Compresion rate:", len(compressed)/len(original_text))

print(compressed[:55])

# write in file
extension = 'hff'
ex_filename = 'result' + '.' + extension
tree['999'] = zeros
writefile(ex_filename, tree, compressed)

## DECODING
file = 'result.hff'
text2 = readfile(file)
limit = text2.find('}')
tree2 = ast.literal_eval(text2[:limit+1])
zeros2 = tree2['999']

text2 = text2[limit+1:] # the encoded text

#problem with end of lines

code2 = string_to_code(text2)
code2 = code2[:(len(code2)-zeros2+1)] # deleting the redundancies

print(tree)
print(tree2)

print("comparing texts")
print(text2[:55])
cont = 0
for i in range(len(text2)):
  if compressed[i] != text2[i]:
    print(i,compressed[i],text2[i])
    cont += 1
    if cont == 10:
      break

print(compressed[i-1:i+50])
print(text2[i-1:i+50])

decoded = decode(tree2, code2)

f = open('decompressed.txt', 'w', encoding='utf-8')
f.write(decoded)
f.close()

g = open('a1.txt', encoding='utf-8').read()

#print(len(decoded),len(g))

##for i in range(len(g)):
##  if decoded[i] != g[i]:
##    print(i,decoded[i],g[i])
##    break
##
