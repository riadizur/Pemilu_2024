import requests as req
import json
import os
import time
import sqlite3
import sys
# import mysql.connector
from datetime import datetime

# mydb = mysql.connector.connect(
#   host="13.214.146.255",
#   user="dev1",
#   password="12345qwerty",
#   database="pemilu2024"
# )
mydb = sqlite3.connect("pemilu2024.db")
# def insertData(tableName,fieldName,data):
#     mycursor = mydb.cursor()

#     sql = "INSERT INTO %s (%s) VALUES (%s)",tableName, fieldName, data
#     # mycursor.execute(sql)

#     # mydb.commit()
#     print(sql)
#     # print(mycursor.rowcount, "record inserted.")
# # print(mydb)

def getData(kode="",fromx="",endx="",xData="", maxLvl = 1,run=True,db=False):
    mainUrl = "https://sirekap-obj-data.kpu.go.id"
    wilayahDir = "/wilayah/pemilu/ppwp"
    dataDir = "/pemilu/hhcw/ppwp"
    dirx=""
    x=""
    arrx = [kode[i:i+2] for i in range(0, len(kode),2)]
    # print(arrx)
    if(len(arrx)>=5):
        arrx[3]=arrx[3]+arrx[4]
        if(len(arrx)>=7):
            arrx[4]=arrx[5]+arrx[6]
            arrx.pop(5)
            arrx.pop(5)
        else:
            arrx.pop(4)
    p=0
    for i in arrx:
        if(i!=""):
            n=x.split("/")
            x=x+"/"+n[len(n)-1]+i
            if p < len(arrx)-1:
                dirx = x
            p=p+1
    if(xData == "wilayah"):
        urlx = wilayahDir
        if(kode==""):
            x="/0"
    elif(xData == "data"):
        urlx = dataDir
    else:
        return 0
    target = x
    directory = os.getcwd() + "/Assets" + urlx + dirx
    filex = os.getcwd() +  "/Assets" + urlx + target +".json"
    url = mainUrl + urlx + target +".json"
    print(datetime.now(),"\tGETTING DATA TO SERVER...",url)

    payload = {}
    headers = {}
    # if endx == kode[:len(endx)]:
    #     return True
    try:
        resp = req.request("GET", url, headers=headers, data=payload)
        if(resp.json()):
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(datetime.now(),"\tCREATING DIRECTORY...",directory)
            with open(filex, mode="w", encoding="utf-8") as resp_file:
                resp_file.write(resp.text)
            print(datetime.now(),"\tFILE SAVED TO DIRECTORY !",filex)
            data = json.loads(resp.text);
            # print(data)
            if(xData == "wilayah"):
                if(fromx!=""):
                    if(len(data[0]["kode"])<=len(fromx)):
                        while data[0]["kode"] != fromx[:len(data[0]["kode"])]:
                            print(datetime.now(),"\tDISMISS\t",data[0],fromx[:len(data[i]["kode"])],data[0]["kode"])
                            data.pop(0)
                for raw in data:
                    # print(raw["id"],raw["kode"],raw["nama"],raw["tingkat"])
                    if(raw["tingkat"]==1):
                        table = "tabel_daftar_provinsi"
                    elif(raw["tingkat"]==2):
                        table = "tabel_daftar_kabupaten"
                    elif(raw["tingkat"]==3):
                        table = "tabel_daftar_kecamatan"
                    elif(raw["tingkat"]==4):
                        table = "tabel_daftar_desa_kelurahan"
                    elif(raw["tingkat"]==5):
                        table = "tabel_daftar_tps"
                    id = raw["id"]
                    kode = raw["kode"]
                    nama = raw["nama"]
                    tingkat = raw["tingkat"]
                    sql = "INSERT INTO "+table+" (id,kode,nama,tingkat) VALUES (\""+str(id)+"\",\""+str(kode)+"\",\""+nama+"\",\""+str(tingkat)+"\");"
                    if(db):
                        print(datetime.now(),"\t",sql)
                        mycursor = mydb.cursor()
                        mycursor.execute(sql)
                        mydb.commit()
                    # if endx == kode[:len(endx)]:
                    #     return True
                    if(tingkat <= maxLvl):
                        # print(raw["kode"],xData)
                        getData(kode=kode,fromx=fromx,endx=endx,xData=xData,maxLvl=maxLvl,db=db)
            elif(xData == "data"):
                ts = data["ts"]
                # print(ts)
                # print(data)
                if(len(kode) <= 10):
                    # print(kode,len(kode))
                    datatable = data["table"]
                    # print(datatable)
                    dat = {}
                    dat["link_data"]=url
                    dat["local_directory"]=filex
                    for name, value in datatable.items():
                        # print(name,value)
                        kode = name
                        dat["kode"]=kode
                        for ex, val in value.items():
                            dat[ex]=val
                        # print(datetime.now(),"\t",dat)
                        field = ""
                        qval = ""
                        table = "vote_presiden_kompilasi_"+str(datetime.now().strftime("%Y%m%d"))
                        for x,y in dat.items():
                            field = field + "`" + x + "`"+","
                            qval = qval + "'"+ str(y) + "'"+","
                        field = field[:-1]
                        qval = qval[:-1]
                        if(db):
                            sql = "INSERT INTO "+table+" ("+field+") VALUES ("+qval+");"
                            print(datetime.now(),"\tINSERT DATA TO TABLE : ",table,sql)
                            mycursor = mydb.cursor()
                            mycursor.execute(sql)
                            mydb.commit()
                        getData(kode=kode,fromx=fromx,endx=endx,xData=xData,maxLvl=maxLvl,db=db)
                else:
                    # print("data")
                    dat = {}
                    data["kode"]=kode
                    data["link_data"]=url
                    data["local_directory"]=filex
                    for item, value in data.items():
                        # print(item,value)
                        if isinstance(value, dict):
                            for x,y in value.items():
                                dat[item+"_"+x]=y
                        elif isinstance(value, list):
                            for i in range(0,len(value)):
                                # print(value[i])
                                dat[item+"_"+str(i)]=value[i]
                        else:
                            # print(item,value)
                            dat[item]=value
                    # print(datetime.now(),"\tDATA\t",dat)
                    field = ""
                    qval = ""
                    table = "vote_presiden_"+str(datetime.now().strftime("%Y%m%d"))
                    for x,y in dat.items():
                        field = field + "`" + x + "`"+","
                        qval = qval + "'"+ str(y) + "'"+","
                    field = field[:-1]
                    qval = qval[:-1]
                    if(db):
                        sql = "INSERT INTO "+table+" ("+field+") VALUES ("+qval+");"
                        print(datetime.now(),"\tINSERT DATA TO TABLE : ",table,sql)
                        mycursor = mydb.cursor()
                        mycursor.execute(sql)
                        mydb.commit()
                    return 0
        else:
            if(run):
                time.sleep(1)
                getData(kode=kode,fromx=fromx,endx=endx,xData=xData,maxLvl=maxLvl,db=db)
    except:
        if(run):
            time.sleep(1)
            getData(kode=kode,fromx=fromx,endx=endx,xData=xData,maxLvl=maxLvl,db=db)
    return True

def createEnvTable_for_data():
    mycursor = mydb.cursor()
    sql = "CREATE TABLE IF NOT EXISTS vote_presiden_"+str(datetime.now().strftime("%Y%m%d"))+" AS SELECT * FROM vote_presiden WHERE 0"
    mycursor.execute(sql)
    mydb.commit()
    sql = "CREATE TABLE IF NOT EXISTS vote_presiden_kompilasi_"+str(datetime.now().strftime("%Y%m%d"))+" AS SELECT * FROM vote_presiden_kompilasi WHERE 0"
    mycursor.execute(sql)
    mydb.commit()
    return 0

def data():
    createEnvTable_for_data()
    return "data"

def wilayah():
    return "wilayah"

def isdb(x=""):
    if(x=="db"):
        createEnvTable_for_data()
        return True
    return False

# nohup python3 -m /Users/riadizur/Library/Mobile Documents/com~apple~CloudDocs/Pemilu 2024/getData_onlocal.py 11
# kode = input("Masukkan kode daerah awal:")

# print(kode)
getData(kode=sys.argv[1],xData=data(),maxLvl=5,db = isdb(sys.argv[2]))
# getData(kode="12",xData="data",maxLvl=5)
# getData(kode="13",xData="data",maxLvl=5)
# getData(kode="14",xData="data",maxLvl=5)
# getData(kode="15",xData="data",maxLvl=5)
# getData(kode="16",xData="data",maxLvl=5)
# getData(kode="17",xData="data",maxLvl=5)
# getData(kode="18",xData="data",maxLvl=5)
# getData(kode="19",xData="data",maxLvl=5)
# getData(kode="21",xData="data",maxLvl=5)
# getData(kode="31",xData="data",maxLvl=5)
# getData(kode="32",xData="data",maxLvl=5)
# getData(kode="33",xData="data",maxLvl=5)
# getData(kode="34",xData="data",maxLvl=5)
# getData(kode="35",xData="data",maxLvl=5)
# getData(kode="36",xData="data",maxLvl=5)
# getData(kode="51",xData="data",maxLvl=5)
# getData(kode="52",xData="data",maxLvl=5)
# getData(kode="53",xData="data",maxLvl=5)
# getData(kode="61",xData="data",maxLvl=5)//
# getData(kode="62",xData="data",maxLvl=5)
# getData(kode="63",xData="data",maxLvl=5)
# getData(kode="64",xData="data",maxLvl=5)
# getData(kode="65",xData="data",maxLvl=5)
# getData(kode="71",xData="data",maxLvl=5)
# getData(kode="72",xData="data",maxLvl=5)
# getData(kode="73",xData="data",maxLvl=5)
# getData(kode="74",xData="data",maxLvl=5)
# getData(kode="75",xData="data",maxLvl=5)
# getData(kode="76",xData="data",maxLvl=5)
# getData(kode="81",xData="data",maxLvl=5)
# getData(kode="82",xData="data",maxLvl=5)
# getData(kode="91",xData="data",maxLvl=5)  
# getData(kode="92",xData="data",maxLvl=5)
# getData(kode="93",xData="data",maxLvl=5)
# getData(kode="94",xData="data",maxLvl=5)
# getData(kode="95",xData="data",maxLvl=5)
# getData(kode="96",xData="data",maxLvl=5)
# getData(kode="99",xData="data",maxLvl=5)
