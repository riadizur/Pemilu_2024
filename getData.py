import requests as req
import json
import os
import time
import sqlite3
from datetime import datetime

mydb = sqlite3.connect("pemilu2024.db")
def insertData(tableName,fieldName,data):
    mycursor = mydb.cursor()

    sql = "INSERT INTO %s (%s) VALUES (%s)",tableName, fieldName, data
    # mycursor.execute(sql)

    # mydb.commit()
    print(sql)
    # print(mycursor.rowcount, "record inserted.")
# print(mydb)

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
    print(datetime.now(),"\tGET DATA TO URL\t",url)

    payload = {}
    headers = {}
    # if endx == kode[:len(endx)]:
    #     return True
    try:
        resp = req.request("GET", url, headers=headers, data=payload)
        if(resp.json()):
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(datetime.now(),"\tCREATING DIRECTORY\t",directory)
            with open(filex, mode="w", encoding="utf-8") as resp_file:
                resp_file.write(resp.text)
            print(datetime.now(),"\tFILE SAVED\t",filex)
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
                    for name, value in datatable.items():
                        dat = {}
                        # print(name,value)
                        kode = name
                        for ex, val in value.items():
                            dat[ex]=val
                        # print(datetime.now(),"\t",dat)
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
                    print(datetime.now(),"\tDATA\t",dat)
                    field = ""
                    qval = ""
                    n=0
                    table = "vote_presiden"
                    for x,y in dat.items():
                        if(n>0):
                            field = field + ","
                            qval = qval + ","
                        field = field + x
                        qval = qval + "\""+ str(y) + "\""
                        n = n+1
                    sql = "INSERT INTO "+table+" ("+field+") VALUES ("+qval+");"
                    print(datetime.now(),"\t",sql)
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
# python3 -m getData.py
# fromx = 3
# input("Masukkan kode daerah awal:")
# print(fromx)
# getData(fromx="99",xData="wilayah",maxLvl=5)
getData(fromx="99",xData="data",maxLvl=5)