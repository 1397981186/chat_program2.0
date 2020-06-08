import argparse, socket,sys
from datetime import datetime
import sqlite3,time
import threading,os
global client1,client2
import shutil

def SEND(name,sc):
    filemess=str(os.stat(name).st_size)+"@"+name
    filemess=bytes(filemess,encoding='utf8')
    sc.sendall(filemess)
    wf=open(name,'rb')
    while True:
        data=wf.read(1024)
        if not data:
            break
        #message=bytes(data, encoding = "utf8")
        sc.sendall(data)
    wf.close()

def RECV(sc):
    data=sc.recv(1024)
    filemess=str(data,encoding='utf8')
    size,name=filemess.split('@')
    name=os.path.basename(name)
    wf=open(name,'wb')
    filesize=int(size)
    recvd_size = 0

    while not recvd_size == filesize:
        if filesize - recvd_size > 1024:
            rdata = sc.recv(1024)
            recvd_size += len(rdata)
        else:
            rdata = sc.recv(filesize - recvd_size)
            recvd_size = filesize
        wf.write(rdata)
    wf.close()
    return name
        
def PorG(w,da):
    data=da.split("@",maxsplit=3)
    d=int(data[0])
    try:
        int(data[1])
        G=[data[1]]
        data1=data[0]+'@'+w+'@'+data[2]
    except:
        G=['51600','51601','51602']
        data1=data[0]+'@'+data[1]+'@'+data[2]
    try:
        data=data1+'@'+data[3]
    except:
        data=data1
    D=bytes(data, encoding = "utf8")

    return G,D,d

def Unline(who,data):
    file=os.getcwd()
    data=data.split("@",maxsplit=3)
    try:
        os.mkdir(file+'\\'+who)
        os.chdir(file+'\\'+who)
    except:
        os.chdir(file+'\\'+who)
    mes=sqlite3.connect(who+'.db')
    m=mes.cursor()
    try:
        m.execute('''CREATE TABLE message(num text,oth text,time text,mess text)''')
        m.execute('''INSERT INTO message VALUES(?,?,?,?)''',data)
    except:
        m.execute('''INSERT INTO message VALUES(?,?,?,?)''',data)
    mes.commit()
    mes.close()
    os.chdir(file)
        
def DATA(who,da):
    p,data,d=PorG(who,da)
    G=client1[who]
    if(d==2):
        for i in p:
            if i not in who:
                try:
                    F=client1[i]
                    F.sendall(data)
                except:
                    D=str(data, encoding = "utf8")
                    Unline(i,D)
                    

    elif(d==3 or d==4 or d==5):
        name=RECV(G)
        for i in p:
            if i not in who:
                try:
                    F=client1[i]
                    F.sendall(data)
                    SEND(name,F)
                except:
                    D=str(data, encoding = "utf8")+'@'+name
                    Unline(i,D)
                    shutil.copyfile(name,os.getcwd()+'\\'+i+'\\'+name)
        os.remove(name)
                    
    else:
        print("错误")

def handle_c(c_socket):
    while True:
        data=c_socket.recv(1024)
        if not data:
            break
        da=str(data, encoding = "utf8")
        if(da=='0'):
            logout(client2[c_socket])
            break
        if(da=='1'):
            c_socket.close()
            break
        data=DATA(client2[c_socket],da)

def logout(who):
    c=client1[who]
    del client2[c]
    c.close()
    print(who,"下线")
    del client1[who]
    del c
    
    
def oldmes(who):
    file=os.getcwd()
    sc=client1[who]
    try:
        os.chdir(file+'\\'+who)
        mes=sqlite3.connect(who+'.db')
        m=mes.cursor()
        m.execute('''SELECT * FROM message''')
        r=m.fetchall()
        for mess in r:
            d=int(mess[0])
            if(d==2):
                D=bytes(mess[0]+'@'+mess[1]+'@'+mess[2]+'@'+mess[3],
                        encoding = "utf8")
                sc.send(D)
            elif(d==3 or d==4 or d==5):
                D=bytes(mess[0]+'@'+mess[1]+'@'+mess[2],encoding = "utf8")
                sc.sendall(D)
                time.sleep(0.15)
                SEND(mess[3],sc)
                os.remove(mess[3])
                
            else:
                print("wrong")
            time.sleep(0.2)
        m.execute('''DROP TABLE message''')
        mes.commit()
        mes.close()
        c_handler=threading.Thread(target=handle_c,args=(sc,))
        c_handler.start()
        os.chdir(file)
    except:
        os.chdir(file)
        c_handler=threading.Thread(target=handle_c,args=(sc,))
        c_handler.start()
                
        
def server(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.listen(3)
    print('Listening at', sock.getsockname())
    while True:
        sc, sockname = sock.accept()
        data=sc.recv(1024)
        if not data:
            break
        da=str(data, encoding = "utf8")
        data=da.split("@")
        u_id=data[0]
        pw=data[1]
        conn=sqlite3.connect('IdPw.db')
        ID=conn.cursor()
        try:
            ID.execute('''SELECT password FROM checkid WHERE ID='''+u_id)
            r=ID.fetchone()
            if(r[0]==pw):
                text = "OK"
                if u_id in client1:
                    data=str(0)
                    data=bytes(data, encoding = "utf8")
                    client1[u_id].sendall(data)
                    c=client1[u_id]
                    del client2[c]
                    del client1[u_id]
                    del c
                client1[u_id]=sc
                client2[sc]=u_id
                data=bytes(text, encoding = "utf8")
                sc.sendall(data)
                print(u_id,"上线，ip： ",sockname)
                oldmes(u_id)
            else:
                text="WRONG"
                data=bytes(text, encoding = "utf8")
                sc.sendall(data)
                sc.close()
                continue

        except:
            text="WRONG"
            data=bytes(text, encoding = "utf8")
            sc.sendall(data)
            sc.close()
            continue

        

if __name__ == '__main__':
    print(os.getcwd())
    global client1,client2
    client1={}
    client2={}
    server('127.0.0.1',1060)
