from tkinter import *
from tkinter.messagebox import *
from tkinter.filedialog import *
from PIL import Image, ImageTk
import time
import socket
import sqlite3
import threading
import wave
import struct,os,win32api
import os.path
from pyaudio import PyAudio,paInt16
global sock,win

 
framerate=8000
NUM_SAMPLES=2000
channels=1
sampwidth=2
TIME=2
def save_wave_file(filename,data):
  wf=wave.open(filename,'wb')
  wf.setnchannels(channels)
  wf.setsampwidth(sampwidth)
  wf.setframerate(framerate)
  wf.writeframes(b"".join(data))
  wf.close()

def SEND(name):
      filemess=str(os.stat(name).st_size)+"@"+name
      filemess=bytes(filemess,encoding='utf8')
      sock.sendall(filemess)
      wf=open(name,'rb')
      while True:
          data=wf.read(1024)
          if not data:
              break
          sock.sendall(data)
      wf.close()

def RECV():
    data=sock.recv(1024)
    filemess=str(data,encoding='utf8')
    size,name=filemess.split('@')
    wf=open(name,'wb')
    filesize=int(size)
    recvd_size = 0

    while not recvd_size == filesize:
        if filesize - recvd_size > 1024:
            rdata = sock.recv(1024)
            recvd_size += len(rdata)
        else:
            rdata = sock.recv(filesize - recvd_size)
            recvd_size = filesize
        wf.write(rdata)
    wf.close()
    return name


class fileC():
    def __init__(self,time,name,who):
        self.name=name
        self.time=time
        self.txt=who.txtMsgList
        self.Rfile()
    def Rfile(self):
        self.txt.config(state=NORMAL)
        self.btn = Button(self.txt, text=os.path.basename(self.name),width = 8)
        self.btn.bind('<Button-1>',self.Fopen)
        self.txt.tag_config('tag6', background='white',foreground='red',
                                justify='left',font=(9,9))
        self.txt.insert(END, self.time+"\n",'tag6')
        self.txt.window_create(END,window=self.btn)
        self.txt.insert(END,"\n")
        self.txt.config(state=DISABLED)

    def Fopen(self,event):
        win32api.ShellExecute(0,'open',self.name,'','',1)


class REC():
    def __init__(self,who):
        self.txt=who.txtMsgList
        self.an=who.name
        self.who=who
        self.c=1
        self.yuyin=Toplevel()
        strMsg = time.strftime("%Y-%m-%d %H:%M:%S",
                                time.localtime())
        self.time=strMsg
        strMsg=strMsg.replace(' ','-')
        self.name=strMsg.replace(':','-')+'.wav'
        self.luzhi=Button(self.yuyin,text="录制",width=8)
        self.luzhi.bind('<Button-1>',self.start)
        self.luzhi.bind('<ButtonRelease-1>',self.stop)
        self.luzhi.pack()

    def start(self,event):
        try:
            os.mkdir(self.who.file)
            os.chdir(self.who.file)
        except:
            os.chdir(self.who.file)
        threading._start_new_thread(self.my_record, ())

    def my_record(self):
        pa=PyAudio()
        stream=pa.open(format = paInt16,channels=1,
        rate=8000,input=True,
        frames_per_buffer=2000)
        my_buf=[]
        while self.c:#控制录音时间
            string_audio_data = stream.read(NUM_SAMPLES)
            my_buf.append(string_audio_data)
            print('.')

        save_wave_file(self.name,my_buf)
        stream.close()

    def stop(self,event):
        self.c=0
        s=askyesno('提示','是否发送？')
        if(s):
            R_yuyin(os.getcwd()+'\\'+self.name,self.time,self.who,'0')
            M=bytes(str(3)+'@'+self.an+'@'+self.time,encoding = "utf8")
            sock.sendall(M)
            filepath=self.name
            SEND(filepath)
            DB(['3',self.an,self.time,os.getcwd()+'\\'+self.name],self.an,'0')
            
        self.yuyin.destroy()
        os.chdir(self.who.now)

class R_yuyin():
    def __init__(self,name,file,who,op):
        self.op=op
        self.an=who.name
        self.name=name
        self.time=file
        self.txt=who.txtMsgList
        self.Ryuyin()
    def Ryuyin(self):
        self.txt.config(state=NORMAL)
        self.btn = Button(self.txt, text='播放',width = 8)
        self.btn.bind('<Button-1>',self.play)
        if(self.op=='1'):
            self.txt.tag_config('tag6', background='white',foreground='red',
                                justify='left',font=(9,9))
            self.txt.insert(END, self.time+"\n",'tag6')
        else:
            self.txt.tag_config('tag5', background='white',foreground='blue',
                                justify='right',font=(9,9))
            self.txt.insert(END, self.time+"\n",'tag5')
            self.txt.insert(END, " ",'tag5')
        self.txt.window_create(END,window=self.btn)
        self.txt.insert(END,"\n")
        self.txt.config(state=DISABLED)
        

    def play(self,event):
        wf=wave.open(self.name,'rb')
        p=PyAudio()
        stream=p.open(format=p.get_format_from_width(wf.getsampwidth()),channels=
                    wf.getnchannels(),rate=wf.getframerate(),output=True)
        while True:
          data=wf.readframes(1024)
          if not data:
            break
          stream.write(data)
        stream.close()
        p.terminate()

def MES(who,time,mes,op):
    who.txtMsgList.config(state=NORMAL)
    if(op=='0'):
        who.txtMsgList.tag_config('tag1', background='white',foreground='blue',
                                justify='right',font=(9,9))
        who.txtMsgList.insert(END, time,'tag1')
        
        who.txtMsgList.tag_config('tag2',justify='right',font=(12,12))
        who.txtMsgList.insert(END, mes,'tag2')
    else:
        who.txtMsgList.tag_config('tag3', background='white',
                                            foreground='red',justify='left',font=(9,9))
        who.txtMsgList.insert(END, time,'tag3')
        who.txtMsgList.tag_config('tag4',justify='left',font=(12,12))
        who.txtMsgList.insert(END,mes,'tag4')

    who.txtMsgList.config(state=DISABLED)
        
    
    
    
    
class LoginPage(Frame):
    def __init__(self):
        super().__init__(width = 300,height = 280)
        self.grid_propagate(0)
        self.username = StringVar()
        self.password = StringVar()
        self.pack()
        self.createForm()

 
    def createForm(self):
        Label(self).grid(row=0,column=1,pady=20)
        Label(self).grid(row=1,column=0,padx=25)
        Label(self, text = '账户: ').grid(row=1, column=2,pady=10)
        Entry(self, textvariable=self.username).grid(row=1, column=3,)
        Label(self, text = '密码: ').grid(row=2, column=2,stick=E, pady=10)
        Entry(self, textvariable=self.password, show='*').grid(row=2, column=3)
        Button(self, text='登录', command=self.loginCheck).grid(row=3, column=2,pady=10)
        Button(self, text='退出', command=self.quit).grid(row=3, column=3,sticky=E)

 
    def loginCheck(self):
        if(len(self.username.get())==0 or len(self.password.get())==0):
            showinfo(title='错误', message='请同时输入账号和密码！')
        else:
            global sock
            sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            name = self.username.get()
            secret = self.password.get()
            try:
                sock.connect(('127.0.0.1',1060))
            except:
                showinfo(title='错误', message='无法连接服务器')

            text = name+"@"+secret
            message=bytes(text, encoding = "utf8")
            sock.sendall(message)
            data = sock.recv(1024)
            data=str(data, encoding = "utf8")
            if(data=="OK"):
                self.destroy()
                HomePage()
            else:
                showinfo(title='错误', message='账号或密码错误！')
                sock.close()
                del sock
    def quit(self):
          root.destroy()

def DB(data,w,i):
    mes=sqlite3.connect(w+'.db')
    m=mes.cursor()
    data=data+[i]
    try:
        m.execute('''CREATE TABLE message(num text,oth text,time text,mess text,op text)''')
        m.execute('''INSERT INTO message VALUES(?,?,?,?,?)''',data)
    except:
        m.execute('''INSERT INTO message VALUES(?,?,?,?,?)''',data)
    mes.commit()
    mes.close()

def Emot(who,time,IM,op):
    who.n[time]=PhotoImage(file=IM)
    who.txtMsgList.config(state=NORMAL)
    if(op=='0'):
        who.txtMsgList.tag_config('tag5', background='white',foreground='blue',
                                  justify='right',font=(9,9))
        who.txtMsgList.insert(END, time,'tag5')
        who.txtMsgList.insert(END, " ",'tag5')
    else:
        who.txtMsgList.tag_config('tag6', background='white',foreground='red',
                                  justify='left',font=(9,9))
        who.txtMsgList.insert(END, time,'tag6')
    who.txtMsgList.image_create(END,image=who.n[time])
    who.txtMsgList.insert(END, "\n",)
    who.txtMsgList.config(state=DISABLED)
class Person():
    
    def __init__(self,name):
        self.name=name
        self.p = Toplevel()
        self.now=os.getcwd()
        self.file=self.now+'\\'+name
        self.p.title('与'+name+'聊天中')
        self.p.protocol(name='WM_DELETE_WINDOW',func=self.shutdown)
        self.bqb={}
        self.n={}
       
        self.frmLT = Frame(self.p,width=500, height=320, bg='white')
        self.frmLC = Frame(self.p,width=500, height=150, bg='white')
        self.frmLB = Frame(self.p,width=500, height=30)
        self.frmRT = Frame(self.p,width=200, height=500)
        self.frmCH = Frame(self.p,width=500, height=30)
       
        self.txtMsgList=Text(self.frmLT)
        self.txtMsgList.config(state=DISABLED)
        self.txtMsg = Text(self.frmLC)


        self.btnSend = Button(self.frmLB, text='发 送', width = 8, command=self.sendMsg)
        self.btnYuyin = Button(self.frmCH, text='语 音', width = 8, command=self.yuyin)
        self.btnemo = Button(self.frmCH, text='表情包', width = 8, command=self.Emo)
        self.btnWenjian = Button(self.frmCH, text='文 件', width = 8, command=self.WenJian)
        self.btnCancel = Button(self.frmLB, text='取消', width = 8, command=self.cancelMsg)

        imgInfo = PhotoImage(file = "python.gif")
        self.lblImage = Label(self.frmRT, image = imgInfo)
        self.lblImage.image = imgInfo

        #窗口布局columnspan选项可以指定控件跨越多列显示
        #而rowspan选项同样可以指定控件跨越多行显示
        self.frmLT.grid(row=0, column=0,columnspan=2, padx=1, pady=3)
        self.frmLC.grid(row=2, column=0, columnspan=2,padx=1, pady=3)
        self.frmLB.grid(row=3, column=0,columnspan=2)
        self.frmCH.grid(row=1, column=0,columnspan=2)
        self.frmRT.grid(row=0, column=2, columnspan=2,rowspan=3, padx=2, pady=3)
        #固定大小
        self.frmLT.grid_propagate(0)
        self.frmLC.grid_propagate(0)
        self.frmLB.grid_propagate(0)
        self.frmRT.grid_propagate(0)
        self.frmCH.grid_propagate(0)
        #按钮和图片
        self.btnSend.grid(row=3,column=0)
        self.btnYuyin.grid(row=1,column=0)
        self.btnWenjian.grid(row=1,column=2)
        self.btnemo.grid(row=1,column=3)
        self.btnCancel.grid(row=3,column=1)
        self.txtMsgList.pack(side =LEFT)
        self.txtMsg.grid()

        self.lblImage.grid()
        self.oldmess()
    def Emo(self):
        def Ename(event):
            strtime = time.strftime("%Y-%m-%d %H:%M:%S",
                                time.localtime())+"\n"
            bbb=txtMsgEm.image_cget(CURRENT,option='name')
            photo=os.getcwd()+'\\'+'em'+'\\'+bbb
            Emot(self,strtime,photo,'0')
            M=bytes(str(5)+'@'+self.name+'@'+strtime,encoding = "utf8")
            sock.sendall(M)
            SEND(photo)
            try:
                os.mkdir(self.file)
                os.chdir(self.file)
            except:
                os.chdir(self.file)
            DB(['5',self.name,strtime,photo],self.name,'0')
            os.chdir(self.now)
            
            
            
        em=Toplevel()
        em.title('表情包')
        frmem = Frame(em,width=800, height=500, bg='white')
        txtMsgEm=Text(frmem)
        txtMsgEm.bind('<Button-1>',Ename)
        for list in os.listdir(os.getcwd()+'\\'+'em'):
            self.bqb[list]=PhotoImage(file=os.getcwd()+'\\'+'em'+'\\'+list)
            txtMsgEm.image_create(END,image=self.bqb[list],name=list)
        txtMsgEm.config(state=DISABLED)
        frmem.grid(row=0, column=0,columnspan=2, padx=1, pady=3)
        frmem.grid_propagate(0)
        txtMsgEm.pack()
    def oldmess(self):
        try:
            os.chdir(self.file)
            mes=sqlite3.connect(self.name+'.db')
            m=mes.cursor()
            m.execute('''SELECT * FROM message''')
            r=m.fetchall()
            for mess in r:
                d=int(mess[0])
                if(d==2):
                    MES(self,mess[2],mess[3],mess[4])
                elif(d==3):
                    R_yuyin(mess[3],mess[2],self,mess[4])

                elif(d==4):
                    fileC(mess[2],mess[3],self)
                elif(d==5):
                    Emot(self,mess[2],mess[3],mess[4])
                
                else:
                    print("wrong")
            mes.close()
            os.chdir(self.now)
        except:
            os.chdir(self.now)
        
        

    def doit(self):
        strMsg = time.strftime("%Y-%m-%d %H:%M:%S",
                                time.localtime())+"\n"
        MES(self,strMsg,self.txtMsg.get('0.0', END),'0')
        text=str(2)+"@"+self.name+"@"+strMsg+"@"+self.txtMsg.get('0.0', END)


        data=text.split("@",maxsplit=3)
        try:
            os.mkdir(self.file)
            os.chdir(self.file)
        except:
            os.chdir(self.file)
        DB(data,self.name,'0')
        os.chdir(self.now)


        message=bytes(text, encoding = "utf8")
        sock.sendall(message)
        self.txtMsg.delete('0.0', END)#删除中间刚输入的内容

    def sendMsg(self):#发送消息
        if(len(self.txtMsg.get('0.0', END))>1):
            self.doit()

    def cancelMsg(self):#取消消息
        self.txtMsg.delete('0.0', END)

    def shutdown(self):
        del win[self.name]
        self.p.destroy()
        del self


    def yuyin(self):
        showinfo(title='提示', message='按下录制，释放停止')
        r=REC(self)

    def WenJian(self):
        file=askopenfilename()
        strMsg = time.strftime("%Y-%m-%d %H:%M:%S",
                                time.localtime())
        text=str(4)+"@"+self.name+'@'+strMsg
        message=bytes(text, encoding = "utf8")
        sock.sendall(message)
        SEND(file)
        self.txtMsgList.config(state=NORMAL)
        self.txtMsgList.tag_config('tag7', background='white',foreground='red',
                                justify='center',font=(8,8))
        self.txtMsgList.insert(END, "文件发送成功\n",'tag7')
        self.txtMsgList.config(state=DISABLED)
def DATA(da):
    data=da.split("@",maxsplit=3)
    d=int(data[0])
    
    if(d==0):
        logout(1)

    u_id=data[1]
    file=os.getcwd()
    try:
        os.mkdir(file+'\\'+u_id)
        os.chdir(file+'\\'+u_id)
    except:
        os.chdir(file+'\\'+u_id)
    if(d==3 or d==4 or d==5):
        name=RECV()
        name=os.getcwd()+'\\'+name
        data=data+[name]
    try:
        win[u_id]
        if(d==2):
            MES(win[u_id],data[2],data[3],'1')
            
        elif(d==3):
            b=R_yuyin(name,data[2],win[u_id],'1')

        elif(d==4):
            f=fileC(data[2],name,win[u_id])
        elif(d==5):
            Emot(win[u_id],data[2],name,'1')
        else:
            print("错误")
    except:
        print(u_id+'发来消息')
    DB(data,u_id,'1')
    os.chdir(file)
    

def HomePage():

    def recvMsg():
        while True:
            try:
                data= sock.recv(1024)
            except:
                break
            else:
                data=str(data, encoding = "utf8")
                DATA(data)

    def Try(event):
        who=List.get(List.curselection())
        try:
            P=win[who]
            P.p.deiconify()
        except:
            P=Person(who)
            win[who]=P

    def friend():
        List.delete(0, END)
        friends("client")
    def group():
        List.delete(0, END)
        friends("Cgroup")

    def friends(which):
        conn=sqlite3.connect('IdPw.db')
        c=conn.cursor()
    
        c.execute('''SELECT ID FROM %s'''%which)
        r=c.fetchall()
        List.bind('<Double-Button-1>',Try)
        for i in r:
            List.insert(END,str(i[0]))

    root.protocol(name='WM_DELETE_WINDOW',func=offline)
    frmHA = Frame(width=70, height=500)
    frmHB = Frame(width=270, height=500, bg='white')
    scrollbar = Scrollbar(frmHB,width=1)
    scrollbar.pack( side = RIGHT, fill = Y )
    List = Listbox(frmHB,width=30, height=28, yscrollcommand = scrollbar.set)
    btnGroup = Button(frmHA, text='群 组', width = 8, command=group)
    btnHaoyou = Button(frmHA, text='好 友', width = 8, command=friend)
    frmHA.grid(row=0, column=0,columnspan=1, padx=1, pady=3)
    frmHB.grid(row=0, column=1, columnspan=1,padx=1, pady=3)
    frmHA.grid_propagate(0)
    frmHB.grid_propagate(0)
    List.pack(side =LEFT)
    btnHaoyou.grid(row=1,column=0)
    btnGroup.grid(row=2,column=0)
    friends("client")
    
    t=threading.Thread(target=recvMsg,args=())
    t.start()
    
def friends(which):
    conn=sqlite3.connect('IdPw.db')
    c=conn.cursor()
    
    c.execute('''SELECT ID FROM %s'''%which)
    r=c.fetchall()
    List.bind('<Double-Button-1>',Try)
    for i in r:
        List.insert(END,str(i[0]))
    frmHA.grid(row=0, column=0,columnspan=1, padx=1, pady=3)
    frmHB.grid(row=0, column=1, columnspan=1,padx=1, pady=3)
    frmHA.grid_propagate(0)
    frmHB.grid_propagate(0)
    List.pack(side =LEFT)
    t=threading.Thread(target=recvMsg,args=())
    t.start()

  
def logout(a):
    da=str(a)
    da=bytes(da,encoding='utf8')
    sock.sendall(da)
    sock.close()
    root.destroy()
    

def offline():
    t=askyesno('下线提示','确定下线？')
    if(t):
        logout(0)
    
root = Tk()
root.title('聊天程序')
global win
win={}

LoginPage()

root.mainloop()
