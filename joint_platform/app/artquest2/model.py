# coding: utf-8

# Author: Sujatha and Mingzhe Du
# Date: 2022-09-14


import os
import sys
import random
import model_utils

def loadAZs(subsf, plines):
    azlines=open(subsf, "r").readlines()

    azones={}
    az2atype={}
    for lx, line in enumerate(azlines):
        if line.strip().startswith("MAXAZONE"):
            azone = line.replace("MAXAZONE", "").strip()
            atype = azlines[lx+1].replace("MAXTYPE", "").strip()
            azones[azone]=[]
            az2atype[azone]=atype

    l2az={}
    qc2l={}
    for pline in plines:
        counts={"C1":0, "C2":0, "C3":0, "C4":0, "C5":0}
        temp=[]
        for azone in azones:
            if azone in pline:
                temp.append((azone, az2atype[azone]))
                counts[az2atype[azone].strip()] += 1
        l2az[pline]=temp

        if len(temp)==0:
            az_np, az_ner = model_utils.getGenericAZs(pline)
            for azone in az_np:
                temp.append((azone, "NP"))
                counts["C2"]+=1
                counts["C3"]+=1
                counts["C5"]+=1
            for azone in az_ner:
                temp.append((azone, "NER"))
                counts["C1"]+=1
                counts["C4"]+=1

            l2az[pline]=temp

        maxt=""
        maxc=0
        for t in counts:
            if counts[t]>maxc:
                maxc=counts[t]
                maxt=t
        if maxt=="":
            maxt="C1"

        if maxt not in qc2l:
            qc2l[maxt]=[]
        qc2l[maxt].append(pline)
    
    print ("DEBUG #plines/l2az/qc2l "+str(len(plines))+" "+str(len(l2az))+" "+str(len(qc2l)))
    return l2az, qc2l


def get_engaging_question(amessage, vmessage, azone):
    inp_string = "ArtQuest: "+amessage.strip()+" Viewer: "+vmessage.strip()+" [SEP] Azone: "+azone.strip()
    #inp_string = amessage.strip()+" [SEP] "+azone.strip()+" [SEP] "+vmessage.strip()
    #print ("DEBUG in GEQ "+inp_string)
    return model_utils.generate_engaging_question(inp_string)

def getSession(title, artist, psgf, subsf):
    # seed_value = random.randrange(sys.maxsize)
    # random.seed(seed_value)

    plines = open (psgf, "r").readlines()
    q2qc, qembeddings, questions = model_utils.getQuestionEmbeddings2()
    seen = {}

    l2az, qc2l = loadAZs(subsf, plines)

    ##CHOOSE RANDOMLY AMONG AVAILABLE OPENING AND CLOSING LINES
    openings = model_utils.opening_cues
    if artist!="":
        openings.append("Do you like paintings by " + artist + "?")

    oindx = random.randint(0, len(openings)-1)

    pword="this painting"
    if artist!="":
        ch=random.randint(0,2)
        if ch==0:
            pword=title
        elif ch==1:
            pword=title+" by "+artist

    ch=random.randint(0, 3)
    if ch==0:
        lastMessage="It was nice sharing about "+pword+"!"
    elif ch==1:
        lastMessage="Hope you found "+pword+" interesting!"
    else:
        lastMessage="Hope you enjoyed knowing more about "+pword+"!"

    overMessage="That's all I had on "+pword+"."

    
    ##START SESSION 
    if artist!="":
        amessage="This is \""+title+"\", a painting by "+artist+"."
    else:
        amessage=title
    aextra=openings[oindx]
 
    extra_resp=""
    prevvmessage=""
    while True:
        print ("\n")
        vmessage = input("ArtQuest: "+amessage.strip()+"\n"+aextra+"\n\nYour response here or exit:")

        if vmessage.lower()=="exit":
            break

        amessage=""
        aextra=""
        sims = model_utils.getSimilarities(vmessage, qembeddings)
            
        ltosrt = []
        for qx, question in enumerate(questions):
            ltosrt.append((question, sims[qx]))
        ltosrt.sort(key=lambda x:x[1], reverse=True)

        for ele in ltosrt:
            (question, simval) = ele
            qc = q2qc[question]
            chosensent=""
            if qc in qc2l:
                for sent in qc2l[qc]:
                    if sent in seen:
                        continue
                    else:
                        chosensent=sent
                        seen[chosensent]=""
                        break
            else:
                for pline in plines:
                    if pline not in seen:
                        chosensent=pline
                        seen[chosensent]=""
                        break


            if chosensent!="":
                amessage = chosensent
                azone=""
                az_typec235=[]
                az_typec14=[]
                az_typenp=[]
                az_typener=[]

                if chosensent in l2az:
                    temp = l2az[chosensent]
                    for ele in temp:
                        (z, t) = ele
                        if t.strip() in ["C2", "C3", "C5"]:
                            az_typec235.append(z)
                        elif t.strip() in ["C1", "C4"]:
                            az_typec14.append(z)
                        elif t.strip()=="NP":
                            az_typenp.append(z)
                        else:
                            az_typener.append(z)
                    
                    if len(az_typec235)!=0:
                        ch = random.randint(0, len(az_typec235)-1)
                        azone = az_typec235[ch]
                    elif len(az_typec14)!=0:
                        ch = random.randint(0, len(az_typec14)-1)
                        azone = az_typec14[ch]
                    elif len(az_typenp)!=0:
                        ch = random.randint(0, len(az_typenp)-1)
                        azone = az_typenp[ch]
                    elif len(az_typener)!=0:
                        ch = random.randint(0, len(az_typener)-1)
                        azone = az_typener[ch]

                aextra = get_engaging_question(amessage, vmessage, azone)
                break ##out of for ltosrt
                
        if amessage=="":
            print ("ArtQuest: " + overMessage)
            break #out of while loop to end session


    print ("ArtQuest: " + lastMessage)
    return

if __name__=="__main__":
    title="Malayan Fruits"
    artist="Georgette Chen"
    psgf="./static/data/sents/gallery/1962_malayan_fruits.txt"
    subsf="./static/data/subsumed/gallery/1962_malayan_fruits.txt"

    getSession(title, artist, psgf, subsf)