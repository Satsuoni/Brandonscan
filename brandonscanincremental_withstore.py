import urllib2, httplib
import re
import sys
class SmartRedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_301(self, req, fp, code, msg, headers):
        ourl= req.get_full_url()
        result = urllib2.HTTPRedirectHandler.http_error_301(
                                                            self, req, fp, code, msg, headers)
        
        print "301"
        if not hasattr(result, 'chain'):
          result.chain=[]
        result.chain.append(req.get_full_url())
        if hasattr(result, 'status'):	
         if result.status!=404:		
          result.status = code
         else:
		  nurl=result.url
		  #print "from "+ourl
		  #print " to  "+nurl
  		  if ourl!=nurl:
  		   result.status = 777
        else:
  		  result.status=code
        return result
    
    def http_error_302(self, req, fp, code, msg, headers):
        #print req.get_full_url()
        result = urllib2.HTTPRedirectHandler.http_error_302(
                                                            self, req, fp, code, msg, headers)
        if not hasattr(result, 'chain'):
          result.chain=[]
        print "302"    
        result.chain.append(req.get_full_url())        												
        result.status = code
        return result

		
class SmartErrorHandler(urllib2.HTTPDefaultErrorHandler):
 	def http_error_default(self, req, fp, code, msg, hdrs):
	 result=self
	 #print result
 	 result.url=req.get_full_url()
 	 if not hasattr(result, 'chain'):
          result.chain=[]
 	 result.chain.append(req.get_full_url()) 
 	 #result.chain.append(result.url)
	 #print result.url
 	 #result = urllib2.HTTPDefaultErrorHandler.http_error_default(
                                                         #   self, req, fp, code, msg, hdrs)
 	 result.status = code
 	 return result

fromnum=1
try:
 fl=open('brandondata.txt','r')
 dat=fl.read()
 pat=re.compile("(\d+?):\{\{(.+?)\}\}  \{\{(.+?)\}\}")
 k=pat.findall(dat)
 fromnum=int(k[-1][0])+1
 print "Starting from "+str(fromnum)
except:
 fromnum=1
opener = urllib2.build_opener(SmartRedirectHandler(),SmartErrorHandler())
file=open('brandondata.txt','a')
pat=re.compile('<title>(.*?)</title>',re.MULTILINE+re.I)
for page_id in range(fromnum,12000):
  try:
   #print page_id
   p=opener.open("http://brandonsanderson.com/?p="+str(page_id))
  except KeyboardInterrupt:
   exit()
  except:
      print str(page_id)+ ": Error: "+str(sys.exc_value)
  else:
    redirchain=[]
    if hasattr(p,"chain"):
     #print p.chain
     #print p.url     
     p.chain.pop()
     while len(p.chain)>0:
      redirchain.append(p.chain.pop()) 
    p.chain=[]
    if (len(redirchain)>=1 and redirchain[-1]!= p.url) or(len(redirchain)==0) :
     redirchain.append(p.url)
    strp=' :-> '.join(redirchain)
    
    #print redirchain    
    canread=False
    try:
	 http=p.read()
	 canread=True
    except:
     canread=False	
    #print canread 
   # print p.status
    
    if (p.status==301 or p.status==302 ) and canread==True:
     #print p.status
     #http=p.read()
     m1=pat.search(http)
     sfname="store/brandon_%06d.html"%(page_id)
     fll=open(sfname,"wb")
     fll.write(http)
     fll.close()
     if m1:
      m=m1.group(1)
      strg= str(page_id)+':{{'+m+'}}  {{'+strp+'}}'
      file.write(strg+"\r\n")
      file.flush()
      print strg
    elif p.status==777:
	 hidden='hidden'
	 sfname="store/brandon_hdn_%06d.html"%(page_id)
	 fll=open(sfname,"wb")
	 fll.write(http)
	 fll.close()     
	 strg= str(page_id)+':{{'+hidden+'}}  {{'+strp+'}}'
	 file.write(strg+"\r\n")
	 file.flush()
	 print strg
file.close()