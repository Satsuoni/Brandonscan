import time
import sys
import re, string, random, glob, operator, heapq
from math import log10
import copy
f=open("code.txt","r")
strng=f.read()
f.close()
#strng=strng[:30]

strsplit=[111,8,2,5,101,11,2,7,1,2,4,9,151,2,10101,11,4,1,0,2,151,171,121,0,111,2,171,3,44,8,3,111,0,7,151,4,2,5,414,3,4,1,0,9,161,4,9,1,4,9,3,4,121,22,5,4,10101,2,5,1,2,7,101,5,191,0,111,2,3,4,1,2,55,11,525,121,575,5,111,2,3,4,101,11,2,9,151,2,1,0,6,1,5,3,4]

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
for wrd, cnt in datafile("twokwords.txt"):
    twokdict.append(wrd)

Pw  = Pdist(datafile('twokwords.txt'), None, avoid_long_words)

alphabet = 'abcdefghijklmnopqrstuvwxyz'
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
    return [seq[i:i+n] for i in range(1+len(seq),n)]

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
while True:
 curcode=0
 
 curmaindct={}
 cdct=curmaindct
 dlen=0
 clen=0
 still=True
 for ca in range(0, len(curclens)):
   curclens[ca]=curclens[ca]+1
   if(curclens[ca]<=maxcodelen):
     still=False
     #print ca
     #print
     break
   else:
    curclens[ca]=1
    if ca==curenf:
       curenf+=1
 if still:
     print "done"
     sys.exit()

 itern=itern+1
 #if curclens[0]==1: continue
 #print str(sum(curclens))+" ",
 if itern<siter: continue
 #print str(len(curclens)) +" ",
 if  len(curclens)>26:#sum(curclens)>len(strng)/1.5 or
  print "done"
  sys.exit()

 prefixlist=[]+fixed
 pref=True
 curcode=0
 sys.stdout.write("\r%s" % str(curclens))
 sys.stdout.flush()
 #print strnglist
 #print curclens
 #print
 for stw in strnglist:
  accum=''
  #print stw,
  for i in range(len(stw)):
   accum+=stw[i]
   if accum in prefixlist:#found prefix
    accum=''
    continue
   if(len(accum)>=curclens[curcode]):#check if it happens to be prefix first!
     nopref=True
     for ap in prefixlist:
       if len(ap)>=len(accum) and ap[:len(accum)]==accum:
         nopref=False
         break
     if nopref:
      prefixlist.append(accum)
      accum=''
      curcode=curcode+1
     else:
      if curcode<=curenf:
       pref=False
       break
      else:
       continue
      #pref=False
      #break
     if curcode>=len(curclens):
       pref=False
       break
  if accum!='':
     nopref=True
     for ap in prefixlist:
       if len(ap)>=len(accum) and ap[:len(accum)]==accum:
                  nopref=False
                  break
     if nopref:
       prefixlist.append(accum)
     else:
      pref=False
  if pref==False:
    break
 if len(prefixlist)>len(alphabet):
   pref=False
 if pref:
   #print strnglist
   #print prefixlist
   #sys.exit()
   #fl=flattendct(curmaindct)
   
   #srt=sorted(fl, key=fl.get)
   #vl=fl.values()
   #print
   #print fl[srt[0]]
   #nsum=sum(vl)
   #nl=heapq.nlargest(3,vl)
   #mn=float(min(nl))/float(nsum)
   sm1=0
   #for v in vl:
   # if v==1:
   #  sm1+=1
   
   #if len(fl)<=26 and len(fl)>10 and mn>0.09 and sm1<7:
   nd={}
   cl=0
   for ky in prefixlist:
        nd[ky]=alphabet[cl]
        cl=cl+1
   cstr=''
   crez=''
   #print
   #print prefixlist
   #print
   for az in range(0, len(strng)):
         cstr+=strng[az]
         #print cstr
         if cstr in nd:
           crez=crez+nd[cstr]
           cstr=''
   #print crez
       #if len(crez)*1.5<len(strng):
   rs=decode_subst(crez)
        
       #rs=getCipher(crez)
       #if rs[0]>9:
   if rs[1]>0.4:
         if rs[1]>mxscore:
          mxscore=rs[1]
          print "new max score"
          print mxscore
          print rs[0]
         print itern
         print rs
         #print rs[1]/len(rs[0])
         fileo=open("rnd_cut.txt","a")
         fileo.write(str(prefixlist)+"\n")
         fileo.write(str(rs)+"\n\n")
         fileo.close()
       #  print rs[1]
       #  print

   #sys.exit()




 