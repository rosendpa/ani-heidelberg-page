import json
from time import sleep
import datetime
from datetime import *
import shutil

try:
    from mal import config
    from mal import Anime
    from mal import AnimeSearch
    config.TIMEOUT = 20  # Import level config
except:
    print("MAL-Api nicht gefunden. Installieren mit 'pip install -U mal-api'")
    exit()


#Hilfsfunktionen

def getAnime(malid):
    maldata = None
    timeout = 1
    while maldata is None:
        try:
            maldata = Anime(malid, timeout=10)
        except Exception as e:
            print(f"Fehler: {e}  Versuche nochmal in {int(timeout)} sec..")
            sleep(timeout)
            timeout=timeout*1.5
    return maldata

def loadjson():
    try:
        with open('archive.json', encoding="utf-8") as f:
            data = json.loads(f.read())
    except:
        with open('archive.json', encoding="utf-8") as f:
            data = json.loads(f.read()[f.read().index("["):])
    try:
        with open('dates.json', encoding="utf-8") as f:
            dates = json.loads(f.read())
    except:
        with open('dates.json', encoding="utf-8") as f:
            dates = json.loads(f.read()[f.read().index("["):])
    if len(data)*len(dates) != 0:
        print("okay. Daten geladen")
        return data, dates

def list_cleanup(data, mal=False):
    clean = []
    clean_w = [] #watchlist at the end or beginning
    for i in range(len(data)):
        old = data[i]
        try:
            if mal: 
                a=1/0 #go to except
            if min([len(str(s)) for s in list(old.values())])==0:
                a=1/0
            tmp = {"index":old["index"], 
                   "malid":old["malid"],
                   "title":old["title"],
                   "titen":old["titen"],
                   "titjp":old["titjp"],
                   "theme":old["theme"],
                   "imurl":old["imurl"],
                   "semes":old["semes"],
                   "progr":old["progr"],
                   "vdate":old["vdate"],
                   "statu":old["statu"]
                   }
        except Exception as es:
            if not mal: 
                print(f"Ungültiger Eintrag (id:{old['malid']}) entdeckt, lade neu von MAL.. ({es})")
            else:
                print("Lade von MAL..")
            
            maldata = getAnime(old["malid"])
                    
            tmp = {"index":old["index"], 
                   "malid":old["malid"],
                   "title":maldata.title,
                   "titen":maldata.title_english,
                   "titjp":maldata.title_japanese,
                   "theme":", ".join(maldata.themes),
                   "imurl":maldata.image_url.replace(".jpg","l.jpg").replace("ll.jpg","l.jpg"), #get large picture
                   "semes":old["semes"],
                   "progr":("00"+old["progr"][:2].replace("/",""))[-2:]+"/"+("00"+str(maldata.episodes).replace("None","??"))[-2:],
                   "vdate":old["vdate"],
                   "statu":old["statu"]
                   }
            #leere Einträge verhindern
            if tmp["titen"] in ["null", None, False, ""]:
                tmp["titen"] = tmp["title"]
            if tmp["theme"] in ["null", None, False, ""]:
                tmp["theme"] = " "
        print("")
        print(f"Eintrag {tmp['index']}:")
        print(tmp['title'])
        print(tmp["titen"])
        print(tmp["titjp"])
        print(tmp["theme"])
        print(tmp["statu"], tmp["progr"])
        print("")
        print("")
        if data[i]["statu"]!="W": 
            clean.append(tmp)
        else:
            clean_w.append(tmp)
    return clean+clean_w

def list_statusupdate(data, flag_needsort=False):

    print("Update-Datum eingeben mit Format: 31.01.2022 >> '3101[2022]' (Punkte und Jahr optional)")
    date = input()

    if len(date)>=4 and len(date)<=6:
        date += str(datetime.now().year)
    if len(date)==8:
        date = date[:2]+"."+date[2:4]+"."+date[4:]

    print("Datum: "+date)
    print("")
    print("STATUS UPDATEN: (Eingabe optional)")
    print("")

    for i in range(len(data)):
        if data[i]["statu"]=="W":
            print("Titel:", data[i]["title"])
            print("Folge:", data[i]["progr"])
            inc = input("increment:  +")
            sta = input("status change (W/F/D):")
            print("")
            if not inc in [None,"null","","0",0,"-0"]:
                try:
                    data[i]["progr"]=("00"+str(int(data[i]["progr"][:2])+int(inc)))[-2:]+data[i]["progr"][2:]
                    data[i]["vdate"]=date
                except:
                    print(f"ERROR: '{data[i]['progr']}' + '{inc}' kein gültiges increment")
                    print("")
            if sta!="":
                if sta in ["W","F","D"]:
                    data[i]["statu"] = sta
                    data[i]["vdate"]=date
                    flag_needsort = True
                else:
                    print(f"ERROR: '{sta}' kein gültiger Status")
                    print("")
            print("")

    print("Programm:") 

    ids = []
    for i in range(len(data)):
        if data[i]["statu"]=="W":
            ids.append(i)

    for i,j in zip(ids,range(len(ids))):
         print(j, "--", data[i]["title"])
    print("Neue Reihenfolge eingeben mit Format '0123': ")
    rf = input()
    if rf != "": #falls neue reihenfolge
        tmp = []
        if sorted(rf) == [str(k) for k in range(len(ids))]:
            for i in rf:
                tmp.append(data[ids[int(i)]])
            for i in range(len(ids)):
                data[sorted(ids)[i]] = tmp[i]
        else:
            print("")
            print("ERROR: Reihenfolge ist ungültig!")

    print("")
    print("FERTIG")
    if flag_needsort:
        print("Sortieren notwendig...")
        sleep(3)
        data = list_cleanup(data, mal = False)
    return data

def list_hinzufuegen(data):
    print("NEUEN ANIME HINZUFÜGEN/ALTEN WIEDERBELEBEN:")
    malid = input("MAL-ID (oder Titel für Suche):")
    maldata = None
    try:
        maldata = Anime(malid)
    except:
        print("")
        print("ID ungültig. Suchergebnisse:")
        try:
            search = AnimeSearch(malid)
            for i in range(min(30,len(search.results))):
                print(f'{(" "+str(i+1))[-2:]} -- {search.results[i].title} ({search.results[i].type})')
            i = input("Position: ")
            malid = search.results[int(i)-1].mal_id
            maldata = Anime(malid, timeout=10)
        except:
            print("")
            print("Suche nicht erfolgreich.")

    if maldata != None:
        print("")
        flag = False
        for i in range(len(data)):
            if data[i]["malid"] == malid:
                flag = True
                index = i
        if flag:
            print(f"Anime schon vorhanden. '{maldata.title}' wird wieder aktiviert.")
            data[i]["statu"] = "W"
        else:
            print(f"ID okay. '{maldata.title}' wird hinzugefügt")
            #semester
            if datetime.now().month in [4,5,6,7,8,9]:
                ts = str(datetime.now().year)[-2:]+"S"
            else:
                if datetime.now().month in [10,11,12]:
                    ts = str(datetime.now().year)[-2:]+"W"
                else:
                    ts = str(datetime.now().year-1)[-2:]+"W"
            #neuer eintrag
            tmp = {"index":str(len(data)+1), 
                   "malid":str(malid),
                   "semes":ts,
                   "vdate":"null",
                   "statu":"W",
                   "progr":"00/??"
                   }            
            data.append(tmp)
        print("")
        print("Bereinigung notwendig...")
        sleep(5)
        data = list_cleanup(data, mal=False)
        print("")
        print("Statusupdate notwendig...")
        sleep(5)
        data = list_statusupdate(data, flag_needsort=True)
    return data

def dates_sort(dates):
    for i in range(len(dates)):
        for j in range(i+1,len(dates)):
            if((datetime.fromisoformat(dates[i]["date"]).timestamp()-datetime.fromisoformat(dates[j]["date"]).timestamp())/(60*60*24) > 0):
                tmp = dates[i].copy()
                dates[i] = dates[j].copy()
                dates[j] = tmp
    return dates    

def dates_next(dates):
    dates = dates_sort(dates)
    i = len(dates)
    while True:
        i+=-1
        if dates[i]["type"]!="S":
            break

    d = datetime.fromisoformat(dates[i]["date"])

    for j in range(1,5):
        tmp_d = d + timedelta(days=7*j)
        print("Datum für Sitzung:", str(tmp_d)[:16])
        ny = input("bestätigen? y/n? ")
        if ny in ["y","Y","j","J","1"]:
            tmp =  dates[i].copy()
            tmp["date"] = tmp_d.isoformat().replace(":00+","+")
            print("okay. Hinzugefügt:", tmp["title"], f"({tmp['type']}) @", str(tmp_d)[:16])
            dates.append(tmp)
        print("")  
    print("") 
    return dates

def dates_new(dates):
    print("(Zeitformat:", dates[-1]["date"].replace("+01:00",")"))
    d = input("Termin eingeben: ")
    d = d + "+01:00"
    try:
        datetime.fromisoformat(d)

        tmp = dates[-1].copy()
        tmp["date"] = d

        tmp["title"] = input("Titel: ")
        tmp["type"] = input("Typ Normal (A/B) oder Event (S): ")
        if not tmp["type"] in ["A","B","S"]:
            a=1/0
        dates.append(tmp)
        print("okay. Hinzugefügt:", tmp["title"], f"({tmp['type']}) @", str(datetime.fromisoformat(tmp["date"]))[:16])
    except:
        print("ERROR: Zeit/Termintyp ungültig")
    print("")
    return dates_sort(dates)

def savejson(data, dates):
    try: #backup
        shutil.copy('archive.json', 'backup/archive'+datetime.now().isoformat()[:19].replace(":","-")+'.json')
    except:
        pass
    #save
    try:
        with open("archive.json", "w", encoding="utf-8") as outfile:
            json.dump(data, outfile, indent = 4)
        with open("dates.json", "w", encoding="utf-8") as outfile:
            json.dump(dates_sort(dates), outfile, indent = 4)
        print("okay. gespeichert")
    except Exception as e:
        print("ERROR beim speichern:", e)


### START
print("START\n\n\n")
data,dates = loadjson()

while True:
    print("\n\n\n")
    print("    MENÜ:\n---------------")
    print("1 - Watchlist Status Update")
    print("2 - Neuen Anime hinzufügen/reaktivieren")
    print("3 - Neue Termine (letzten kopieren)")
    print("4 - Neuer Termin (einzeln)")
    print("")
    print("6 - SPEICHERN UND BEENDEN")
    print("")
    print("    optional:")
    print("9 - Anime-Liste bereinigen/sortieren")
    print("0 - Anime-Liste komplett neu aufbauen (braucht lange)")
    print("")
    cho = input("wählen:")
    if cho in ["1","2","3","4","6","9","0"]:
        cho = int(cho)
        print("\n\n")
        if cho==1:
            data = list_statusupdate(data, flag_needsort=False)
        if cho==2:
            data = list_hinzufuegen(data)
        if cho==3:
            dates = dates_next(dates)
        if cho==4:
            dates = dates_new(dates)
        if cho==6:
            savejson(data, dates)
            break
        if cho==9:
            data = list_cleanup(data, mal=False)
        if cho==0:
            data = list_cleanup(data, mal=True)




        

