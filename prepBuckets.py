import os, codecs
path = ""
def process(filename, prefix):
   """this will read twitter posts from the file and place each post in a
   separate file"""
   fp = codecs.open(filename, 'r', 'iso8859-1')
   lines = fp.readlines()
   fp.close()
   i = 1
   os.mkdir(prefix)
   for j in range(10):
      os.mkdir("%s/%i" % (prefix, j))
   for line in lines:
      fp = codecs.open("%s/%i/%s%03i" %(prefix, i % 10, prefix, i), 'w', 'iso8859-1')
      i += 1
      fp.write(line)
      fp.close()

process('male.txt', 'male')
process('female.txt', 'female')
