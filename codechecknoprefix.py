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

strsplit=[111,8,2,5,101,11,2,7,1,2,4,9,151,2,10101,11,4,1,0,2,151,171,121,0,111,2,171,3,44,8,3,111,0,7,151,4,2,5,414,3,4,1,0,9,161,4,9,1,4,9,3,4,121,22,5,4,10101,2,5,1,2,7,101,5,191,0,111,2,3,4,1,2,55,11,525,121,575,5,111,2,3,4,101,11,2,9,151,2,1,0,6,1,5,3,4]

strng=[strng[k*2] for k in range(len(strng)/2)]
#strng=strng[:50]

def splitbylist(str,lst):
 kn=''
 ret=[]
 cnt=0
 for i in lst:
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

def ssegment(text,L=12):
   if not text: return (0,[])
   ret=[]
   rcnt=0
   for first,rem in splits(text,L):
     if first in twokdict:
       segm=ssegment(rem,L)
       score=len(first)+segm[0]
       if score>rcnt:
         ret=[first]+segm[1]
         rcnt=score
   return (rcnt,ret)

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
#for w in twokdict:
# twokdict[w]=float(twokdict[w])/float(N)
bgrams={}
NN=0
for bg, cnt in datafile("twok_2l.txt"):
    bgrams[bg]=cnt
    NN+=int(cnt)
for bg in bgrams:
   bgrams[bg]=float(bgrams[bg])/float(NN)

trigrams={}
NN=0
for bg, cnt in datafile("twok_3l.txt"):
    trigrams[bg]=cnt
    NN+=int(cnt)
for bg in trigrams:
    trigrams[bg]=float(trigrams[bg])/float(NN)

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
def mapFromCode(code,prevmap=None):
  ret={}
  lst=list(alphabet)
  if prevmap:
      ret={a:prevmap[a] for a in prevmap if a in code}
      for k in ret:
       if ret[k] in lst:
         lst.remove(ret[k])

  for k in code:
   if len(lst)==0:
     lst=list(alphabet)
   if not k in ret:
     ret[k]=random.choice(lst)
     lst.remove(ret[k])
  if len(code)<26:
   for rem in lst:
     ret[id_generator(5)]=rem
  return ret



#print ssegment('apearlytreeamedalrearconnvelinknmonesumsmsonrrkneerizethearonrfabidgiawnearstrexton')

def shift(msg, n=13):
    "Encode a message with a shift (Caesar) cipher."
    return encode(msg, alphabet[n:]+alphabet[:n])

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

def shift2(msg, n=13):
    "Encode with a shift (Caesar) cipher, yielding only letters [a,z]."
    return shift(just_letters(msg), n)

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
    csplit=[]
    cset=set([])
    ls=0
    ccode={}
    cscore=0
    spl=['1']
    annealevel=0
    maxcr=4
    def __init__(self,strn):
        self.strng=strn
        self.csplit=[1]*(len(self.strng)-1)
        self.ls=len(self.csplit)
        for k in range(10):
          rrr=random.randrange(len(self.csplit))
          self.csplit[rrr]=0
          if self.cmz()>self.maxcr:
             self.csplit[rrr]=1
        self.spl=splitbylist(self.strng,self.csplit)
        self.cset=set(self.spl)
        self.ccode=mapFromCode(self.cset)
        self.cscore=self.score()
    def string(self):
        return ''.join(self.ccode[k] for k in self.spl)
    
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
        if r1>perc: #do a split mutation
            r2=random.randint(0,self.ls-1)
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
            else: #revert
                self.csplit[r2]=1-self.csplit[r2]
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
            else: #revert
                inq=self.ccode[c1[0]]
                self.ccode[c1[0]]=self.ccode[c1[1]]
                self.ccode[c1[1]]=inq
    
    
    def score(self,pun=0.1):
        
        txt=self.string()
        return self.scoreat(txt,pun)

    def scoreat(self,txt,pun=0.01):
            scr=0
            sm=0
            trat=0
            rep=0
            tc='rareday'
            for cheat in range(len(tc)):
             if txt[cheat]==tc[cheat]:
              rep+=0.03
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
            return rep+(trat/sm)
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
for q in range(50):
   annealist.append(annealpoint(strng))
   annealist[-1].csplit[0:16]=[0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1]

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
loops=20
maxscore=-900
print "Start looping"
while True:
 for num in range(loops):
   for nap in range(len(annealist)):
     annealist[nap].mutate(0.95,anneaincr*num+annealist[nap].annealevel)
 annealist=heapq.nlargest(49,annealist,key = lambda p: p.cscore)
 for apn in heapq.nlargest(30,annealist,key = lambda p: p.cscore):
    apn.annealevel+=anneaincr
 mx=max(annealist,key = lambda p: p.cscore)
 mxa=max(annealist,key = lambda p: p.annealevel)
 sys.stdout.write("\r%05.3f" % mxa.annealevel)
 sys.stdout.flush()
 if maxscore<mx.cscore :#or mx.cscore>1:
  maxscore=mx.cscore
  print
  print mx.annealevel
 #sys.stdout.write("\r%s" % str(mx.cscore))
  print "Maxscore: "+str(mx.cscore)
  print mx.string()
  print mx.csplit
  sys.stdout.flush()
  
  sp=pickle.dumps(mx)
  flo=open("rndpickle.txt","a")
  flo.write(sp)
  flo.write("\n")
  flo.close()
 for q in range(1):
   annealist.append(annealpoint(strng))
   annealist[-1].csplit[0:16]=[0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1]


sys.exit()


def neighboring_msgs(msg):
    "Generate nearby keys, hopefully better ones."
    def swap(a,b): return msg.translate(string.maketrans(a+b, b+a))
    for bigram in heapq.nsmallest(20, set(ngrams(msg, 2)), P2l):
        b1,b2 = bigram
        for c in alphabet:
            if b1==b2:
                if P2l(c+c) > P2l(bigram): yield swap(c,b1)
            else:
                if P2l(c+b2) > P2l(bigram): yield swap(c,b1)
                if P2l(b1+c) > P2l(bigram): yield swap(c,b2)
    while True:
        yield swap(random.choice(alphabet), random.choice(alphabet))



englishLetterFreq = {'E': 12.70, 'T': 9.06, 'A': 8.17, 'O': 7.51, 'I': 6.97, 'N': 6.75, 'S': 6.33, 'H': 6.09, 'R': 5.99, 'D': 4.25, 'L': 4.03, 'C': 2.78, 'U': 2.76, 'M': 2.41, 'W': 2.36, 'F': 2.23, 'G': 2.02, 'Y': 1.97, 'P': 1.93, 'B': 1.29, 'V': 0.98, 'K': 0.77, 'J': 0.15, 'X': 0.15, 'Q': 0.10, 'Z': 0.07}
ETAOIN = 'ETAOINSHRDLCUMWFGYPBVKJXQZ'
LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

cl=0
dict={}
resz=''
for n in strsplit:
 if n in dict:
   resz=resz+dict[n]
 else:
   dict[n]=alphabet[cl]
   cl=cl+1
   resz=resz+dict[n]
print resz
resz="LIVITCSWPIYVEWHEVSRIQMXLEYVEOIEWHRXEXIPFEMVEWHKVSTYLX".lower()
rs=decode_subst(resz,4000,7000)
print rs
sys.exit()

maxcodelen=5

curclens=[]
for a in range(26):
 curclens.append(1)
dcts=[]

mxscore=0
itern=0
curenf=0
siter=0#245338
#fixed=['10','12', '13', '11','14','9','7','18','25']
fixed=[]
strnglist=[strng]
for fx in fixed:
        ct1=[]
        for sub in strnglist:
            ct1=ct1+sub.split(fx)
        strnglist=[c for c in ct1 if c!='']
print strnglist
#strnglist=[strng]
