import os
import sys
import re
from urlparse import urljoin
import urllib2 as ul2
list=os.listdir("store")
ptn=re.compile(r"(\'|\")([^\'\"]*?)(\.jpg|\.png|\.gif)(\'|\")")
for fname in list:
 ffn="store/"+fname
 print "Processing "+fname
 if os.path.isfile(ffn):
  fl=open(ffn,"rb")
  txt=fl.read()
  fl.close
  images=re.findall(ptn,txt)
  for imgd in images:
   iml=imgd[1]+imgd[2]
   imurl=urljoin("http://brandonsanderson.com/",iml)
   spl=iml.split('/')[-1]
   if len(spl)>3:
    fullname="store/images/"+spl
    if not os.path.isfile(fullname):
     try:
      rs=ul2.urlopen(imurl)
      downed_image=rs.read()
      imfile=open(fullname,"wb")
      imfile.write(downed_image)
      imfile.close()
      print "Got "+iml
     except Exception as e:
      print e
      print "Couldn't get "+imurl

  
  