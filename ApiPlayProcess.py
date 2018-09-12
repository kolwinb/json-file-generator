#!/usr/bin/env python
import os
import signal
import MySQLdb as mdb
from multiprocessing import Process
from threading import Timer
import csv
import time
import datetime
import pymongo
import pprint 
import copy #class duplication
import sys
import linecache #fetch lines
import itertools #fetch lines
import logging
  
class ApiChannel():
    logging.basicConfig(filename='/var/log/mobile.log',level=logging.DEBUG,format='%(asctime)s %(name)s %(levelname)s %(message)s')
#    curday=datetime.date.today().day #reference is self.curday 
    
    def __init__(self):
        #global initialization, define variable class itself
        self.client = pymongo.MongoClient('mongodb://192.168.0.0:27017/',connect=False)
        self.monthn = self.getMonth() # get current month
        self.curday = self.getDay()  #get current day 
        self.totline = "" #assign empty variable
        self.db = self.client.learntvapi
        self.coll = self.db.channels
        self.subjects=["pirith","sutta","dhammapada","bhavana","sermon","benchmark","blender","ccena","german-sinhala","german-tamil","java","java-colombo","sl2college","pima","refresh-colombo","royal-asiatic-society","slasscom","doctype","electronic","gimp","go-open","inkscape","neda","org","the-wood-whisper","system","young-inventers","civics","commerce","ict","entrepreneurship","revision","civics","history","maths","english","geography","health","pts","science","sinhala","tamil"]      
        #initailize variable for filler and subject mongodb updates
        
    
    #convert time to second
    def getSec(self,time_str):
        #calculate total seconds
	h,m,s = time_str.split(":")
        return int(h) * 3600 + int(m)*60 + int(s)

    # get current month
    def getMonth(self):
        now=datetime.datetime.now()
        monthn=datetime.datetime.strftime(now,'%b')
        return monthn.lower()
   
    def getDay(self):
        return datetime.date.today().day

#    def getDesc(self):
    def getDb(self,pname):
        try:
	    con = mdb.connect("192.168.1.120","user","password","db")
#            con.set_character_set('utf8')
            cur = con.cursor()
            cur.execute('SET NAMES utf8;')
#            cur.execute('SET CHARACTER SET utf8;')
#            cur.execute('SET character_set_connection=utf8;')
            cur.execute("SELECT sdesc,edesc FROM lesson WHERE filename='{0}'".format(pname))
            rec = cur.fetchone()
            rsdesc = rec[0].decode('utf-8')
            redesc = rec[1]
            return rec[0].decode('utf-8'),rec[1]            
        except mdb.Error,e:
            logging.ERROR('database not return values %d: %s' % (e.args[0],e.args[1]))
            return "None","None"
        finally:
             #return self.checkNone(rsdesc),self.checkNone(redesc)             
             if con:
                 con.close()
      
    def checkNone(self,pdesc):
        if pdesc is None:
             return "Null"
        else:
             return pdesc

    def readFile(self,channel):
        self.totline=self.getTotLine(channel) #get total line of a playlist
        with open ("%s/%s-%s.csv" % (channel,self.getMonth(), self.curday)) as file:
            readCsv=csv.reader(file,delimiter=',')
            for line in readCsv:
                ln_num=self.getLineNo(readCsv) #get current line number
                self.getWord(channel,ln_num) #get word assign with line number
                coltime=line[0]
		coldur=line[1]
		colfile=line[2]
                cursec=self.getSec(self.getTime()) #calculate total seconds
        	dursec=self.getSec(coldur)
                endsec=cursec + dursec
                #extract subject name
                subject=self.getSubject(colfile,0) #replace colfile
		lesson="None"
                sdesc="None"
                edesc="None"
                if self.getSubState(subject):
                     #get sinhala and english description from mysql 
                     try:
                         sdesc,edesc=self.getDb(colfile)
                     except:
                         print channel+" "+subject+" no descriptions"
                         sdesc="None"
                         edesc="None"
                        # logging.INFO('sinhala and english description not available from database')              
                     #check file name split field
                     finally:
                         upd = self.coll.update({"_id":channel},{'$set':{"_id":channel,"subject":subject,"lesson":self.getLesson(colfile),"duration":coldur,"start_time":self.getTime(),"end_time":self.getEndTime(endsec),"description":[sdesc,edesc],"image_url":["http://www.learntv.lk/video/"+self.getThumbPath(channel,subject)+self.getFileVerify(colfile,str("medium")),"http://www.learntv.lk/video/"+self.getThumbPath(channel,subject)+self.getFileVerify(colfile,str("small")),"http://www.learntv.lk/video/"+self.getThumbPath(channel,subject)+self.getFileVerify(colfile,str("xsmall"))],"video_url":["http://learntv.lk/playlists/"+channel+"_playlist_medium.m3u8","http://learntv.lk/playlists/"+channel+"_playlist_small.m3u8","http://www.learntv.lk/playlists/"+channel+"_playlist_xsmall.m3u8"]}})
                time.sleep(dursec)

    def getLesson(self,colfile):
        word=colfile.split("-")
        conctstr=""
        list=["bhavana","dhammapada","sermon"]
        if word[0] in list:
	    for i in word[2:]: #start from send index sermon-sinhala-6432
	        if not i.isdigit(): # check numberics
		    if i == "thero":
		        conctstr=conctstr+" "+i
		        break
	            else:
		        conctstr=conctstr+" "+i #concaternate text
	    return conctstr.title()
	    print conctstr.title() #cap first letter
        else:
            return "-".join(word[2:])
 

    #put image directory for pirith
    def getThumbPath(self,channel,subject):
        if subject == self.subjects[0]:
            return "edu-fillers"
#        elif subject == self.subjects[1]:
#            return "fillers/thumb/"
        else:
            return channel+"/"+subject

    #get line word
    def getWord(self,channel,ln_num):
        nextline=self.findNext(channel,ln_num+1,"next")
        self.findNext(channel,nextline,"latest")

    #get next and latest program
    def findNext(self,channel,ln_num,mode):
        tot_line=self.totline
        print channel,": Total lines",tot_line
        if ln_num == tot_line: #jump to next playlist
            varmonth=self.getMonth() #assign mont after 12.00pm
            varday=self.getDay() #assign day after 12.00pm
            vartotline=self.getTotLine(channel) # get totline of next day
            if mode == "next":
                varline=1 # next
            else:
                varline=2 # for latest
            return self.findNextLoop(channel,varline,vartotline,self.monthn,self.curday,mode) #get from local variable           
        elif ln_num is not None: # this return None
            return self.findNextLoop(channel,ln_num,tot_line,self.monthn,self.curday,mode) #get from global variable
 
    def findNextLoop(self,channel,lnum,tline,month,day,mode):
        for i in range(lnum,tline):
#            try:
            ln_word=linecache.getline("%s/%s-%s.csv" % (channel,month,day),i)
#            except IOError: 
#                print "file error"
#                 ctime="00:00:00"
#                subject="Not-Available"
#            else:#no exception occures
            field=self.getField(ln_word,2) #extract file name
            ctime=self.getField(ln_word,0) #extract playing time
            subject=self.getSubject(field,0) #extract only subject name   
#            finally:

            if self.getSubState(subject):
                udp = self.coll.update({"_id":channel},{'$set':{mode:[subject,ctime]}})
                print(mode+" program is :"+subject+" time : "+ctime+" updated")
                return i+1
 #               print(udp)
 
                
    #get specific index in line array
    def getField(self,row,index):
        field=row.split(',')
        return field[index]
   
    #get total line in one playlist
    def getTotLine(self,channel):
#        try:
         with open ("%s/%s-%s.csv" % (channel,self.monthn, self.curday)) as file:
             return len(file.readlines())
#        except IOError:
#            print "file not found"
       

    #get line number
    def getLineNo(self,readCsv):
        line_no=readCsv.line_num
        return line_no
 
    # compare subject array if meet requirement
    def getSubState(self,subject):
        if subject in self.subjects:
           return True
        else:
           return False

    #filter given index
    def getSubject(self,colfile,index):
        word=colfile.split('-')
        return word[index]

    def getFileVerify(self,colfile,imode):
        #print imode
        if imode == "medium": 
            return self.getImgExt(colfile,"-632x395-1.jpg",".jpg")
        elif imode == "small":
            return self.getImgExt(colfile,"-416x260-1.jpg",".d.jpg")
        elif imode == "xsmall":
            return self.getImgExt(colfile,"-168x105-1.jpg",".m.jpg")
        
    def getImgExt(self,colfile,sizea,sizeb):
        word=colfile.split('-') # assign array sutta-sattipattana       
        subd=['sermon','bhavana','dhammapada'] #sermon-sinhala
        if word[0] in subd:        # match sinhala
            return "/"+word[1]+"/thumb/"+"-".join(word[2:])+sizea # /sinhala/thumbs/
        elif word[0] == "sutta": #sutta-sattipattana
            return "/thumb/"+"-".join(word[1:])+sizeb #dharmavahini /thumbs/
        else:            
            return "/thumb/"+colfile+sizeb #learntv thumb/

  

    #get current time
    def getTime(self):
        return time.strftime('%H:%M:%S')

    #convert end time to second
    def getEndTime(self,endsec):
        return time.strftime('%H:%M:%S',time.gmtime(endsec))

 #   def getCollection(self,channel):
 #      cur = self.coll.find({"_id":"grade-05"})
 #      for coll in cur:
 #           pprint.pprint(coll)
#       pprint.pprint(self.coll.find( { "channels:" { "_id":"dhamma" } } ) )



#def funcStart():

grade_05=ApiChannel()
grade_06=ApiChannel()
grade_07=ApiChannel()
grade_08=ApiChannel()
grade_09=ApiChannel()
grade_10=ApiChannel()
grade_11=ApiChannel()
higher_edu=ApiChannel()
vocational=ApiChannel()
dharmavahini=ApiChannel()

processes = []


processes.append(Process(target=grade_05.readFile,args=('grade-05',)))
processes.append(Process(target=grade_06.readFile,args=('grade-06',)))
processes.append(Process(target=grade_07.readFile,args=('grade-07',)))
processes.append(Process(target=grade_08.readFile,args=('grade-08',)))
processes.append(Process(target=grade_09.readFile,args=('grade-09',)))
processes.append(Process(target=grade_10.readFile,args=('grade-10',)))
processes.append(Process(target=grade_11.readFile,args=('grade-11',)))
   #grade12=Process(target=grade_12.readFile,args=('grade-12',))
processes.append(Process(target=higher_edu.readFile,args=('higher-education',)))
processes.append(Process(target=vocational.readFile,args=('vocational-education',)))
   #bhavana=Process(target=bhawana.readFile,args=('bhavana',))

processes.append(Process(target=dharmavahini.readFile,args=('dharmavahini',)))


for prl in processes:
    prl.start()


