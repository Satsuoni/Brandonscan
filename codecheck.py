f=open("code.txt","r")
str=f.read()
f.close()
kd={}
for a in range(0,len(str)):
 st=str[a:a+1]
 if st in kd:
   kd[st]=kd[st]+1
 else:
   kd[st]=1
print kd
print len(kd)   
 