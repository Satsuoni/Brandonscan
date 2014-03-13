import urllib2, httplib
import re
import sys
class SmartRedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_301(self, req, fp, code, msg, headers):
        ourl= req.get_full_url()
        result = urllib2.HTTPRedirectHandler.http_error_301(
                                                            self, req, fp, code, msg, headers)
        
        #
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
        print req.get_full_url()													
        result.status = code
        return result

		
class SmartErrorHandler(urllib2.HTTPDefaultErrorHandler):
 	def http_error_default(self, req, fp, code, msg, hdrs):
	 result=self
	 #print result
 	 result.url=req.get_full_url()
	 #print result.url
 	 #result = urllib2.HTTPDefaultErrorHandler.http_error_default(
                                                         #   self, req, fp, code, msg, hdrs)
 	 result.status = code
 	 return result
opener = urllib2.build_opener(SmartRedirectHandler(),SmartErrorHandler())
file=open('brandondata.txt','a')
pat=re.compile('<title>(.+?)</title>',re.MULTILINE+re.I)
for page_id in range(0,10000):
  try:
   #print page_id
   p=opener.open("http://brandonsanderson.com/?p="+str(page_id))
  except KeyboardInterrupt:
   exit()
  except:
      print str(page_id)+ ": Error: "+str(sys.exc_value)
  else:
   #if hasattr(p,status)
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
     if m1:
      m=m1.group(1)
      strg= str(page_id)+':{{'+m+'}}  {{'+p.url+'}}'
      file.write(strg+"\r\n")
      file.flush()
      print strg
    elif p.status==777:
	 hidden='hidden'
	 strg= str(page_id)+':{{'+hidden+'}}  {{'+p.url+'}}'
	 file.write(strg+"\r\n")
	 file.flush()
	 print strg
file.close()