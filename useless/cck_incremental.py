import time
import sys
import re, string, random, glob, operator, heapq
from math import log10
import math
import copy
import pickle
f=open("code.txt","r")
strng=f.read()
f.close()
#strng=strng[:30]

strng=[strng[k*2] for k in range(len(strng)/2)]
#strng=strng[:40]

def splitbylist(str,lst):
 kn=''
 ret=[]
 cnt=0
 for ii in range(len(lst)):
  i=lst[ii]
  kn+=str[cnt]
  cnt+=1
  if i==1:
   ret.append(kn)
   kn=''
 return ret
#print splitbylist('abcde',[0,1,1,1])

def segment(text):
    "Return a list of words that is the best segmentation of text."
    if not text: return []
    candidates = ([first]+segment(rem) for first,rem in splits(text))
    return max(candidates, key=Pwords)

def splits(text, L=10):
    "Return a list of all possible (first, rem) pairs, len(first)<=L."
    return [(text[:i+1], text[i+1:])
            for i in range(min(len(text), L))]

def ssegment(text,L=12, lam= lambda x:x):
   if not text: return (0,0,[])
   ret=[]
   rcnt=0
   clen=0
   for first,rem in splits(text,L):
     if first in twokdict:
       segm=ssegment(rem,L)
       score=lam(len(first))+segm[0]
       if score>rcnt:
         ret=[first]+segm[2]
         clen=segm[1]+len(first)
         rcnt=score
   return (rcnt,clen,ret)

def Pwords(words):
    "The Naive Bayes probability of a sequence of words."
    return product(Pw(w) for w in words)


def product(nums):
    "Return the product of a sequence of numbers."
    return reduce(operator.mul, nums, 1)

class Pdist(dict):
    "A probability distribution estimated from counts in datafile."
    def __init__(self, data=[], N=None, missingfn=None):
        for key,count in data:
            self[key] = self.get(key, 0) + int(count)
        self.N = float(N or sum(self.itervalues()))
        self.missingfn = missingfn or (lambda k, N: 1./N)
    def __call__(self, key):
        if key in self: return self[key]/self.N
        else: return self.missingfn(key, self.N)

def datafile(name, sep='\t'):
    "Read key,value pairs from file."
    for line in file(name):
        yield line.split(sep)

def avoid_long_words(key, N):
    "Estimate the probability of an unknown word."
    return 10./(N * 10**len(key))

def encode(msg, key):
    "Encode a message with a substitution cipher."
    return msg.translate(string.maketrans(ul(alphabet), ul(key)))

def ul(text): return text.upper() + text.lower()

twokdict=[]
NN=0
for wrd, cnt in datafile("twokwords.txt"):
    twokdict.append(wrd)
    NN+=int(cnt)



ngramz=[]
for a in [1,2,3,4,5,6,7,8]:
    igrams={}
    NN=0
    for bg, cnt in datafile("twok_%dl.txt" % (a)):
      igrams[bg]=cnt
      NN+=int(cnt)
    for bg in igrams:
     igrams[bg]=log10(1+float(igrams[bg])/float(NN))
    ngramz.append(igrams)

Pw  = Pdist(datafile('twokwords.txt'), None, avoid_long_words)

def id_generator(size=6, chars=string.ascii_lowercase+string.ascii_uppercase):
    return ''.join(random.choice(chars) for x in range(size))

alphabet = 'abcdefghijklmnopqrstuvwxyz'
alphabetlist=list(alphabet)#+['th','ch','sh']
def mapFromCode(code,prevmap=None):
  ret={}
  lst=copy.copy(alphabetlist)
  if prevmap:
      ret={a:prevmap[a] for a in prevmap if a in code}
      for k in ret:
       if ret[k] in lst:
         lst.remove(ret[k])

  for k in code:
   if len(lst)==0:
     lst=copy.copy(alphabetlist)
   if not k in ret:
     ret[k]=random.choice(lst)
     lst.remove(ret[k])
  if len(code)<26:
   for rem in lst:
     ret[id_generator(5)]=rem
  return ret


def logPwords(words):
    "The Naive Bayes probability of a string or sequence of words."
    if isinstance(words, str): words = allwords(words)
    return sum(log10(Pw(w)) for w in words)

def allwords(text):
    "Return a list of alphabetic words in text, lowercase."
    return re.findall('[a,z]+', text.lower())

def decode_shift(msg):
    "Find the best decoding of a message encoded with a shift cipher."
    candidates = [shift(msg, n) for n in range(len(alphabet))]
    return max(candidates, key=logPwords)

def just_letters(text):
    "Lowercase text and remove all characters except [a,z]."
    return re.sub('[^a,z]', '', text.lower())

def logP3letters(text):
    "The log,probability of text using a letter 3,gram model."
    return sum(log10(P3l(g)) for g in ngrams(text, 3))

def logP2letters(text):
    "The log,probability of text using a letter 3,gram model."
    return sum(log10(P2l(g)) for g in ngrams(text, 2))

def ngrams(seq, n):
    "List all the (overlapping) ngrams in a sequence."
    return [seq[i:i+n] for i in range(0,1+len(seq),n) if i+n<len(seq)]

P3l = Pdist(datafile('twok_3l.txt'))
P2l = Pdist(datafile('twok_2l.txt')) ## We'll need it later

def hillclimb(x, f, neighbors, steps=10000):
    "Search for an x that miximizes f(x), considering neighbors(x)."
    fx = f(x)
    neighborhood = iter(neighbors(x))
    for i in range(steps):
        x2 = neighborhood.next()
        fx2 = f(x2)
        if fx2 > fx:
            x, fx = x2, fx2
            neighborhood = iter(neighbors(x))
    if debugging: print 'hillclimb:', x, int(fx)
    return (x,fx)

debugging = False

def scoretwok(txt,delfen=40):
 score=0
 txcut=txt[:min(delfen,len(txt))]
 #ssg=ssegment(txcut)
 #return (ssg[0]/len(txcut),txt)
 for str in twokdict:
  if str in txt:
    score+=len(str)
 return (float(score)/float(len(txt)),txt)

def decode_subst(msg, steps=1000, restarts=20):
    "Decode a substitution cipher with random restart hillclimbing."
    #msg = cat(allwords(msg))
    candidates = [hillclimb(encode(msg, key=cat(shuffled(alphabet))),
                            logP2letters, neighboring_msgs, steps)
                  for _ in range(restarts)]
    #print scoretwok(candidates[0][0])
    p, words = max(scoretwok(c[0]) for c in candidates)
    #print words
    #print p
    return (words,p)

def shuffled(seq):
    "Return a randomly shuffled copy of the input sequence."
    seq = list(seq)
    random.shuffle(seq)
    return seq

cat = ''.join


minnealscore=0.6

class annealpoint:
    strng='1'
    fullstring='1'
    strpos=0
    csplit=[]
    cset=set([])
    ls=0
    ccode={}
    cscore=0
    spl=['1']
    annealevel=0
    maxcr=5
    window=[0,0]
    newwordsplit=0
    wordsplit=0
    tc=''
    nextincr=1
    naught=0
    def __init__(self,strn,strlen=None):
        if strlen:
         self.strng=strn[:strlen]
         self.fullstring=strn
         self.strpos=strlen
        else:
         self.strng=strn
         self.strpos=len(strn)
        self.csplit=[1]*(len(self.strng)-1)
        self.ls=len(self.csplit)
        self.window[1]=self.ls-1
        for k in range(10):
          rrr=random.randrange(len(self.csplit))
          self.csplit[rrr]=0
          if self.cmz()>self.maxcr:
             self.csplit[rrr]=1
        self.spl=splitbylist(self.strng,self.csplit)
        self.cset=set(self.spl)
        self.ccode=mapFromCode(self.cset)
        self.cscore=self.score()
    def inc_move(self,num):
      if len(self.fullstring)==self.strpos: return
      pn=min(self.strpos+num,len(self.fullstring))
      sub=self.fullstring[self.strpos:pn]
      self.increment(sub) 
      self.shiftwindow(pn-self.strpos)
      self.nextincr=self.wordsplit+1
      self.strpos=pn      
      
    def string(self):
        return ''.join(self.ccode[k] for k in self.spl)
    def shiftwindow(self,len):
       self.window[0]+=len
       self.window[1]+=len
       self.window=[min(k,self.ls-1) for k in self.window]
    def expandwindow(self,len):
       self.window[1]+=len
       self.window=[min(k,self.ls-1) for k in self.window]
       
    def increment(self,str):
       ln=len(str)
       self.strng=self.strng+str
       for a in range(ln):
        if random.random()>0.5:
         self.csplit.append(1)
        else:
         self.csplit.append(0)
         if self.cmz()>self.maxcr:
             self.csplit[-1]=1        
       self.ls=len(self.csplit)
       self.resplit()
       self.cscore=self.score()
    def resplit(self):
        self.spl=splitbylist(self.strng,self.csplit)
        self.cset=set(self.spl)
        self.ccode=mapFromCode(self.cset,self.ccode)
    
    def cmz(self):
      mx=0
      cr=0
      for l in self.csplit:
       if l==0:
        cr+=1
       else:
        if cr>mx: mx=cr
        cr=0
      if cr>mx: mx=cr
      return mx
    
    def mutate(self, perc,rprobdecay,deprecator=1):
        r1=random.random()
        if r1>perc+1: #do a split mutation
            self.window=[min(k,self.ls-1) for k in self.window]
            r2=random.randint(self.window[0],self.window[1])
            #print r2
            #print len(self.ls)
            #print self.window[1]
            self.csplit[r2]=1-self.csplit[r2]
            if self.cmz>self.maxcr:
              self.csplit[r2]=1-self.csplit[r2]
              return
            ocode=copy.copy(self.ccode)
            self.resplit()
            nscr=self.score()
            r3=random.random()
            if nscr>self.cscore or math.exp(rprobdecay*(nscr-self.cscore))*deprecator>r3:
                self.cscore=nscr
                self.wordsplit=self.newwordsplit
            else: #revert
                self.csplit[r2]=1-self.csplit[r2]
                self.ccode=ocode
                self.resplit()
                self.ccode=ocode

        else: #do a code swap mutation
            c1=random.sample(self.ccode.keys(),2)
            inq=self.ccode[c1[0]]
            self.ccode[c1[0]]=self.ccode[c1[1]]
            self.ccode[c1[1]]=inq
            nscr=self.score()
            r3=random.random()
            #print r3
            if nscr>self.cscore or math.exp(rprobdecay*(nscr-self.cscore))*deprecator>r3:
                self.cscore=nscr
                self.wordsplit=self.newwordsplit
            else: #revert 
                inq=self.ccode[c1[0]]
                self.ccode[c1[0]]=self.ccode[c1[1]]
                self.ccode[c1[1]]=inq 
    
    def score(self,pun=0.0):
        
        txt=self.string()
        return self.scoreat(txt,pun)

    def scoreat(self,txt,pun=0.01):
            scr=0
            sm=0
            trat=0
            rep=0
            #tc='raredaywant'
            for cheat in range(len(self.tc)):
             if txt[cheat]==self.tc[cheat]:
              rep+=0.07
             else :
               break
            for a in range(2,8):
              totgram=0
              propgram=0
              sm+=a
              for ng in ngrams(txt,a):
                 if len(ng)!=a:
                   print len(ng)
                   continue
                 totgram+=1
                 if ng in ngramz[a-1]:
                  propgram+=1
                 else:
                  propgram-=pun*(6-a)
              if(totgram==0): continue
              rat=float(propgram)/float(totgram)
              trat+=a*rat
            scr=rep+(trat/sm)
            if scr>0.7:
             sg=ssegment(txt,10,lambda x: (x-1)*(x-1)*x)
             scr+=sg[0]*0.1
             #if sg[1]>2:
             #  print sg[2]
             self.newwordsplit=sg[1]
            else:
              self.newwordsplit=0
            return scr
        #    for a in range(1,7):
        #        for ng in ngrams(txt,a):
        #            try:
        #                scr+=ngramz[a-1][ng]*(a*a*a)+(a-1)*0.1
                    #if a>4:
                    # print ng
        #            except:
        #                scr-=pun
            #        if scr > minnealscore:
            #    for wrd in twokdict:
            #     if wrd in txt:
            #         scr+=len(wrd)*0.1
            #return scr


annealist=[]
rlogfile="rlog_even.txt"
def rlogn(strn):
   fl=open(rlogfile,"a")
   fl.write(str(strn))
   fl.write("\n")
   fl.close()   
for q in range(50):
   annealist.append(annealpoint(strng,20))
   annealist[-1].csplit[0:16]=[0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1]
   annealist[-1].resplit()
increlist=[]
fl=open("twor.txt","r")
twok=fl.read()
fl.close()
def just_letterss(text):
    "Lowercase text and remove all characters except [a-z]."
    return re.sub('[^a-z]', '', text.lower())

wl="AhbuttheywereleftbehindItisobviousfromthenatureofthebondButwherewherewherewhereSetoffObviousRealizationlikeapricityTheyarewiththeShinWemustfindoneCanwemaketouseaTruthlessCanwecraftaweapon"
wl=wl.lower()
#wl=wl[2000:2155]


print ngrams(wl,3)
print wl
k=annealpoint('hjghjhhjjgfujhfuuuvyt')
print k.scoreat(wl)
#sys.exit()
anneaincr=0.1
loops=50
cloops=20
maxscore=-900
print "Start looping"
rem=5
mv=5
while True:
 for num in range(loops):
   for nap in range(len(annealist)):
     annealist[nap].mutate(0.95,anneaincr*num+annealist[nap].annealevel)
 movel=[]    
 for ap in annealist:    
   if ap.nextincr<=ap.wordsplit:
     movel.append(ap)
 for ap in movel:
   rlogn( "Moving: " +str(ap.csplit)+ "   "+ap.string() )
   annealist.remove(ap)
   ap.inc_move(mv)
   increlist.append(ap)
 annealist=heapq.nlargest(max(len(annealist)-rem,1),annealist,key = lambda p: p.cscore)
 for apn in annealist:
    apn.annealevel+=anneaincr
 reml=[]   
 for ap in increlist:
   if ap.wordsplit>=len(strng)-4:
    strq="Nice split: " +str(ap.csplit)+"  "+ap.string()
    print strq
    rlogn( strq )
    sg=str(ssegment(ap.string()))
    rlogn( sg )
    print sg
    reml.append(ap)
   if ap.nextincr<=ap.wordsplit:
     ap.inc_move(mv)
     rlogn(  "Incrementing: " +ap.string()+" to "+str(ap.strpos) )
     
   osc=ap.cscore
   for a in range(cloops):
    ap.mutate(0.94,anneaincr*a+ap.annealevel)
   if osc!=ap.cscore:
    ap.naught=0
    ap.annealevel+=anneaincr
   else:
    ap.naught+=1
    if ap.naught>30:
      reml.append(ap)
 for r in reml:
   rlogn(  "Removing: " +str(r.csplit)+ "   "+r.string() )
   increlist.remove(r)
 del reml
 if len(increlist)>200:
   increlist=heapq.nlargest(180,increlist,key = lambda p: p.cscore) 
 mx=max(annealist+increlist,key = lambda p: p.cscore)
 mxa=max(annealist+increlist,key = lambda p: p.annealevel)
 sys.stdout.write("\r%05.3f" % mxa.annealevel)
 sys.stdout.flush()
 if maxscore<mx.cscore :#or mx.cscore>1:
  maxscore=mx.cscore
  print
  print mx.annealevel
 #sys.stdout.write("\r%s" % str(mx.cscore))
  print "Maxscore: "+str(mx.cscore)
  rlogn("Maxscore: "+str(mx.cscore))
  rlogn( mx.string())
  rlogn(mx.csplit)
  print mx.string()
  print ssegment(mx.string())
  print mx.scoreat(mx.string())
  print mx.score()
  print mx.csplit
  sys.stdout.flush()
  
  sp=pickle.dumps(mx)
  flo=open("rndeven_mini.txt","a")
  flo.write(sp)
  flo.write("\n")
  flo.close()
 ll=50-len(annealist) 
 for q in range(ll):
   annealist.append(annealpoint(strng,20))
   if random.random()>0.7:
    annealist[-1].tc="rareday"
   annealist[-1].csplit[0:16]=[0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1]
   annealist[-1].resplit()


sys.exit()

