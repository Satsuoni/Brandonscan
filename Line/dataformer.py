import sqlite3
import datetime
import os
import re
#print(
#    datetime.datetime.fromtimestamp(
#        int("1284101485")
#    ).strftime('%Y-%m-%d %H:%M:%S')
#)
db=sqlite3.connect("talk.sqlite")
cur=db.cursor()
cur.execute("Select ZCHAT, ZSENDER from ZMESSAGE ORDER BY ZTIMESTAMP ASC")
print "Fetching messages..."
messages=cur.fetchall()
print "Done."
chatmembers={}
chats=[]
print "Sorting messages"
for msg in messages:
 if not msg[0] in chats:
  chats.append(msg[0])
  chatmembers[msg[0]]=[]
 if not msg[1] in chatmembers[msg[0]]:
  chatmembers[msg[0]].append(msg[1])

print "Done."
#copy css
print "Preparing directories"
if not os.path.exists("output"):
 os.makedirs("output")
if not os.path.exists("output/images"):
 os.makedirs("output/images")
if not os.path.exists("output/chats"):
 os.makedirs("output/chats")
if not os.path.exists("output/bins"):
 os.makedirs("output/bins")
sfile=open("style.css",'r')
s=sfile.read()
sfile.close()
sfile=open("output/style.css","wb")
sfile.write(s)
sfile.close()
tfile=open("template.html",'rb')
template=tfile.read()
tfile.close()
print "Done."
print "Processing chats..."
chContTempl="""
<h1> List of chats</h1>
<ul>
<%NEXTCHAT%>
</ul>
"""
nextchattempl="""<li><%CHAT%></li>
<%NEXTCHAT%>"""

class mdata:
 templ=u"""
 <br />
 <h3>DB ID: <%PK%> <br />
 Current name:  <%CName%> <br />
 Address book name: <%ABName%> <br />
 User name: <%UName%> <br />
 Phone Number: <%PN%> <br />
 Key: <%Key%> <br /></h3>
 <br />
 """
 data={}
 def __init__(self,dat, additional):
  self.data={}
  if dat==None: return
  if len(dat)==0: return
  dat=dat[0]
  self.data["PK"]=dat[0]
  self.data["ABName"]=dat[1]
  self.data["CName"]=dat[2] if dat[2]!=None else dat[3]
  self.data["UName"]=dat[3]
  if additional!=None and len(additional)>0:
   self.data["PN"]=additional[0][1]
   self.data["Key"]=additional[0][0]

 def toString(self):
  cst=self.templ
  for key in self.data:
    cst=re.sub("<%{0}%>".format(key),unicode(self.data[key]),cst)
  cst=re.sub("<%\w+?%>".format(key),u"",cst)
  return cst
  
 def cname(self):
  return u"\"{0}:{1}\"".format(self.data["PK"],self.data["CName"])


chattemplate=u"""
<h2>PARTICIPANTS:</h2><br />
<%USERS%>
<h2>Messages:</h2><br />
<%MESSAGES%>
"""
messagetemplate=u"""<b>{0}, {1}:</b><br />
<div class="{2}">{3}{4}  {5}</div><br />
<%MESSAGES%>
"""
memberdata={}
imid=0
binid=0
def toint(i):
 try:
  return int(i)
 except:
  return 0
mfile=open("output/main.html","wb")
for chat in chats:
 print "Chat #{0}".format(chat)
 cur.execute("Select ZSENDER, ZTEXT, ZCONTENTMETADATA, ZTIMESTAMP, ZTHUMBNAIL from ZMESSAGE WHERE ZCHAT={0} ORDER BY ZTIMESTAMP ASC".format(chat))
 msgs=cur.fetchall()
 members=chatmembers[chat]
 print members
 for mem in members:
  if toint(mem)==0:
   if not toint(mem) in memberdata:
    memberdata[toint(mem)]=mdata(((0,"You","You",""),),None)
   continue
  if mem not in memberdata:
    cur.execute("Select Z_PK, ZADDRESSBOOKNAME, ZCUSTOMNAME, ZNAME, ZMID from ZUSER where Z_PK={0}".format(mem))
    dat=cur.fetchall()
    cur.execute("Select ZKEY, ZPHONENUMBER from ZCONTACT where ZMID=\"{0}\"".format(dat[0][4]))
    add=cur.fetchall()
    memberdata[mem]=mdata(dat,add)
    #print memberdata[mem].toString()
 chatft=re.sub("<%TITLE%>","",template)
 chfilename="chats/chat_{0}.html".format(chat)
 gg=u', '.join([unicode(memberdata[toint(a)].cname()) for a in members])
 cchat=u"<b><a href=\"{0}\">{1}. Chat with: {2}</a></b>".format(chfilename,chat,gg)
 chatft=re.sub("<%TITLE%>",u"Chat with: {0}".format(gg),template)
 chatft=re.sub("style.css","../style.css",chatft)

 ntl=re.sub("<%CHAT%>",cchat,nextchattempl)
 chContTempl=re.sub("<%NEXTCHAT%>",ntl,chContTempl)
 chatft=re.sub("<%CONTENT%>",chattemplate,chatft)
 chatft=re.sub("<%USERS%>",u' '.join([memberdata[toint(a)].toString() for a in members]),chatft)
 for msg in msgs:
  cls="answer"
  if toint(msg[0])==0: cls="mine"
  tm=datetime.datetime.fromtimestamp(toint(msg[3])/1000).strftime('%Y/%m/%d %H:%M:%S')
  img=""
  bns=""
  if msg[2]!=None:
   imfl=open("output/bins/bin_%06d.bin"%(binid),"wb")
   imfl.write(msg[2])
   imfl.close()
   img="<a href=\"../bins/bin_%06d.bin\" />(Binary)</a>"%(binid)
   binid=binid+1
  if msg[4]!=None:
   imfl=open("output/images/%06d.jpg"%(imid),"wb")
   imfl.write(msg[4])
   imfl.close()
   img="<img src=\"../images/%06d.jpg\" />"%(imid)
   imid=imid+1
  mst=messagetemplate.format(tm,memberdata[toint(msg[0])].cname(),cls,msg[1],img,bns)
  chatft=re.sub("<%MESSAGES%>",mst,chatft)
 chatft=re.sub("<%MESSAGES%>","",chatft)
 chfl=open("output/chats/chat_{0}.html".format(chat),"wb")
 chfl.write(chatft.encode("utf8"))
 chfl.close()
chContTempl=re.sub("<%NEXTCHAT%>","",chContTempl)
ttl=re.sub("<%TITLE%>", "Main chat list",template)
mfile.write(re.sub("<%CONTENT%>",chContTempl,ttl).encode("utf8"))
mfile.close()
#chat=629
#cur.execute("Select ZADDRESSBOOKNAME, ZCUSTOMNAME, ZNAME, ZMID from ZUSER where Z_PK="+string(chat))
#cur.execute("Select ZKEY, ZPHONENUMBER, from ZUSER where Z_MID="+string(mid))
# <h1> List of chats</h1>
# <ul>
#  <li>Coffee</li>
#   </ul>
db.close()
# <div class="mine">do things</div><br />
# <div class="answer">undo things</div>
