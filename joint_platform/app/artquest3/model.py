# coding: utf-8

# Author: Sujatha
# Date: 2022-09-14


import os
import sys
import random
import traceback
import app.artquest3.model_utils as model_utils

seed_value = random.randrange(sys.maxsize)
random.seed(seed_value)

def loadAZs(subsf, plines):
    azlines=open(subsf, "r").readlines()
    azones={}
    az2atype={}
    for lx, line in enumerate(azlines):
        lp = line.strip().split("\t")
        azone = lp[0].strip()
        cnts={"C1":0,"C2":0,"C3":0,"C4":0,"C5":0}
        maxc=0
        maxt=""
        for px in range(1, len(lp)):
            atype=lp[px].strip()
            cnts[atype]+=1
            if cnts[atype]>maxc:
                maxc=cnts[atype]
                maxt=atype

        if maxt!="":
            azones[azone]=[]
            az2atype[azone]=maxt


    l2az={}
    l2ner={}
    qc2l={}
    for pline in plines:
        counts={"C1":0, "C2":0, "C3":0, "C4":0, "C5":0}
        temp=[]
        temp2=[]
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
                temp2.append(azone)

            l2az[pline]=temp
            l2ner[pline]=temp2

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
    return l2az, qc2l, l2ner

def get_engaging_question(amessage, vmessage, azone):
    inp_string = "ArtQuest: "+amessage.strip()+" Azone: "+azone.strip()+" Viewer: "+vmessage.strip()
    return model_utils.generate_engaging_question(inp_string)

def get_openning_sentence(title, artist):
    openings = model_utils.opening_cues
    openings.append("Do you like paintings by " + artist + "?")
        
    amessage = f"This is '{title}', a painting by {artist}."
    aextra = openings[random.randint(0, len(openings)-1)].strip()

    return [amessage, aextra]

def get_close_sentence(title, artist):
    pword = "this painting"

    ch = random.randint(0,2)
    if ch == 0:
        pword = title
    elif ch == 1:
        pword = title + " by " + artist
    
    ch = random.randint(0, 3)
    if ch == 0:
        lastMessage = "It was nice sharing about " + pword + "!"
    elif ch == 1:
        lastMessage = "Hope you found " + pword + " interesting!"
    else:
        lastMessage = "Hope you enjoyed knowing more about " + pword + "!"

    overMessage = "That's all I had on "+pword+"."

    return (overMessage, lastMessage)

def getResponse(title, artist, psgf, subsf, seen, seen_questions, vmessage):
    seed_value = random.randrange(sys.maxsize)
    random.seed(seed_value)

    try:
        plines = open (psgf, "r").readlines()
        totl = len(plines)
        q2qc, qembeddings, questions, qc2cues = model_utils.getQuestionEmbeddings2()
        l2az, qc2l, l2ner = loadAZs(subsf, plines)
        
        amessage = ""
        aextra = ""
        sims = model_utils.getSimilarities(vmessage, qembeddings)

        ltosrt = []
        for qx, question in enumerate(questions):
            ltosrt.append((question, sims[qx]))
        ltosrt.sort(key=lambda x:x[1], reverse=True)

        for ele in ltosrt:
            (question, simval) = ele
            qc = q2qc[question]
        #    print ("DEBUG bestmatching q/qc: "+question+" with qtype: "+qc+" "+str(qc in qc2l))
            chosensent=""
            if qc in qc2l:
                qcl = qc2l[qc]
                for ex, ele in enumerate(qcl):
                    if ele not in seen:
                        sent = ele
                        chosensent=sent
                        del qc2l[qc][ex]
                        seen += [chosensent]
                        break

            if chosensent=="":
            #       print ("DEBUG cannot find unseen line for matching qtype, choosing any unseen")
                for px, pline in enumerate(plines):
                    if pline not in seen:
                        chosensent=pline
                        del plines[px]
                        seen += [chosensent]
                        break


            if chosensent!="":
                print ("DEBUG Chosensent: "+chosensent)
                amessage = chosensent
                az_typec235=[]
                az_typec14=[]
                az_typenp=[]
                generic_cues=[]
                azone=""
                if chosensent in l2az:
                    temp = l2az[chosensent]
                    for ele in temp:
                        (z, t) = ele
                        if t.strip()!="NP":
                            for gc in qc2cues[t.strip()]:
                                if gc not in seen_questions:
                                    generic_cues.append(gc)

                        if t.strip() in ["C2", "C3", "C5"]:
                            az_typec235.append(z)
                        elif t.strip() in ["C1", "C4"]:
                            az_typec14.append(z)
                        elif t.strip()=="NP":
                            az_typenp.append(z)
                    
                    if len(az_typec235)!=0:
                        ch = random.randint(0, len(az_typec235)-1)
                        azone = az_typec235[ch]
                    elif len(az_typec14)!=0:
                        ch = random.randint(0, len(az_typec14)-1)
                        azone = az_typec14[ch]
                    elif len(az_typenp)!=0:
                        ch = random.randint(0, len(az_typenp)-1)
                        azone = az_typenp[ch]
                    
                    print ("DEBUG (c235)= "+str(az_typec235))
                    print ("DEBUG (c14)= "+str(az_typec14))
                    print ("DEBUG (np)= "+str(az_typenp))
                    print ("DEBUG Azone for engaging prompt: "+azone)
                    if azone!="":                    
                        aextra = get_engaging_question(amessage, vmessage, azone).strip()

                    if aextra=="" or (aextra!="" and aextra in seen_questions):
                        print ("DEBUG empty azone/question seen before, choosing from generic cues/NER: "+aextra)

                        if chosensent in l2ner:
                            nert = l2ner[chosensent]
                            if len(nert)!=0:
                                ch = random.randint(0, len(nert)-1)
                                azone = nert[ch]
                                aextra = get_engaging_question(amessage, vmessage, azone).strip()
                                if aextra!="" and aextra not in seen_questions:
                                    generic_cues.append(aextra)

                        if len(generic_cues)!=0: #have already removed seen from here, so no need to check
                            ch = random.randint(0, len(generic_cues)-1)
                            aextra = generic_cues[ch]
                            if aextra in seen_questions:
                                aextra=""

                    aextra = aextra.strip()
                    if aextra!="" and aextra not in seen_questions:
                        seen_questions += [aextra]

                if aextra=="":
                    #we don't have azones for this line, so can try asking one of the preset cues
                    #chosen randomly
                    print ("DEBUG no azones known for line, using generic cues ")
                    qtlist=["C2", "C3", "C5"]
                    ch = random.randint(0, len(qtlist)-1)
                    qtype = qtlist[ch]
                    cues = qc2cues[qtype]
                    if len(cues)!=0:
                        ch = random.randint(0, len(cues)-1)
                        aextra = cues[ch].strip()
                        if aextra in seen_questions:
                            aextra=""
                        else:
                            seen_questions += [aextra]

                if aextra=="":
                    print ("DEBUG unseen cues, using generic 2 ")
                    aextra ="Isn't that interesting?"
                    
                break ##out of for ltosrt

        if amessage == "":
            overMessage, lastMessage = get_close_sentence(title, artist)
            return [overMessage, lastMessage, seen, seen_questions]
    except Exception as e:
        traceback.print_exc()

    return [amessage, aextra, seen, seen_questions]


if __name__=="__main__":
    title="Malayan Fruits"
    artist="Georgette Chen"
    psgf="/home/nzsg_nlp_nus/Projects/nus-mu-uoa-nlp-demos/joint_platform/app/artquest3/static/data/sents/gallery/1962_malayan_fruits.txt"
    subsf="/home/nzsg_nlp_nus/Projects/nus-mu-uoa-nlp-demos/joint_platform/app/artquest3/static/data/subsumed/gallery/1962_malayan_fruits.txt"