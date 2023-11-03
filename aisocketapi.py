import socket
import ssl
import json
from threading import Thread, Lock
import time
import hashlib
import os



def ask_ai(question):
    result = hashlib.md5(question.encode('utf-8'))
    cachefilename = '/var/www/html/api/rfbackend/storage/aisocketcache'+result.hexdigest()
    if os.path.exists(cachefilename):
        f = open(cachefilename,'r')
        result = f.read()
        f.close()
        return result

    with open('/var/www/html/api/rfbackend/auth_part.txt') as f:
        lines = f.readlines()
    auth_part = lines[0]
    path = "/chat?stream=true&model=gpt-4"
    hostname = 'api.writingmate.ai'
    flog = open('/var/www/html/api/rfbackend/aisocket-'+str(int(time.time()))+'.log','wb')
    context = ssl.create_default_context()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    abody = {}
    abody["prompt"] = "Human: " + question + "\n"
    auth="Bearer " + auth_part
    context = ssl.create_default_context()
    body = json.dumps(abody)
    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            print(ssock.version())
            ssock.connect((hostname, 443))
            #print(ssock)
            request = f"POST {path} HTTP/1.1\r\n" \
                    f"Host: {hostname} \r\n" \
                    f"Authorization: {auth} \r\n" \
                    f":Method: POST \r\n" \
                    f":Path: {path} \r\n" \
                    f":Scheme: https \r\n" \
                    f":Accept:*/*\r\n" \
                    f"Content-Type: application/json \r\n" \
                    f"Sec-Fetch-Mode: cors \r\n" \
                    f"Sec-Fetch-Site: cross-site \r\n" \
                    f"User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36\r\n" \
                    f"Content-Length: {len(body)}\r\n\r\n" \
                    f"{body}"
            #print(request)
            response = b""
            keepgoing = True
            firstgotten = False
            wholenineyards = ""
            try:
                ssock.sendall(request.encode())
                total = ""
                while keepgoing:
                    chunk = ssock.recv(4096*2)
                    flog.write(chunk)
                    flog.flush()
                    if not chunk:
                        break
                    response += chunk
                    if not firstgotten:
                        print("first chunk")
                        firstgotten = True
                        athing = chunk.decode()
                        parts = athing.split("\r\n\r\n")
                        if (len(parts)>1 and len(parts[1])>20):
                            chunkstart = athing.find("\r\n\r\n")
                            athing = parts[1]
                            length = int(athing.split("\r\n")[0],16)
                            start = athing.find("\r\n")
                            wholenineyards += chunk[chunkstart+6+start:chunkstart+start+6+length].decode()
                            print(wholenineyards)
                    else:
                        #everything start with the length in hex followed by line and data:
                        #is the data encoded, is it binary?
                        athing = chunk.decode()
                        try:
                            length = int(athing.split("\n")[0],16)
                            if (length == 0):
                               keepgoing = False
                               return None 
                            print(str(length))
                            start = athing.find("\r\n")
                        #print(chunk[start+1:length+2].decode())
                        #print("got package")
                            #print(chunk[start+2:start+2+length].decode().strip())
                            wholenineyards += chunk[start+2:start+2+length].decode().strip()
                        except:
                            print("Something went wrong trying to parse int -->" + athing + "<--")
                    if (chunk.decode().find("data: [DONE]")!=-1):
                        keepgoing = False
                    else:
                        strpackage = chunk.decode()
                        """
                        print('package ' + strpackage)
                        startidx = strpackage.find("data: ")
                        startidx += len("data: ")
                        endidx = strpackage.    find("}\n")+2
                        #print(strpackage[startidx:endidx])
                        try:
                            jp = json.loads(strpackage[startidx:endidx])
                        except:
                            print("Error in parsing package " + strpackage[startidx:endidx])
                            jp = {}

                        if ("choices" in jp):
                            if (len(jp["choices"])> 0):
                                if ("delta" in jp["choices"][0]):
                                    if ("content" in jp["choices"][0]["delta"]):                                    
                                        total = total + str(jp["choices"][0]["delta"]["content"])
                    """
            except Exception as e:
                print(str(e))
                exit(-1)
            finally:
                ssock.close()
                total = ""
                f = open("/var/www/html/api/rfbackend/storage/wholenineyards.txt","w")
                f.write(wholenineyards)
                f.close()
                wholenineyards = wholenineyards.replace("data: [DONE]","")
                wholenineyards = wholenineyards.replace("data:","\n")
                for i in wholenineyards.split("\n"):
                    if (len(i.strip()) > 0):
                        #print("###" + i)
                        try:
                            pop = json.loads(i)
                            if ( 'content' in pop['choices'][0]['delta'].keys() ):
                                total += pop['choices'][0]['delta']['content']
                        except:
                            print("Could not json -->" + i + "<--")
                f = open(cachefilename,'w',encoding='utf-8')
                f.write(total)
                f.close()
                return total

def write_ai_to_file(question,filename):
    path = "https://api.secretary.chat/chatmessages/streaming"
    hostname = 'api.secretary.chat'
    context = ssl.create_default_context()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    abody = {"message" : question}
    f = open(filename,'wb')
    context = ssl.create_default_context()
    body = json.dumps(abody)
    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            ssock.connect((hostname, 443))
            request = f"POST {path} HTTP/1.1\r\n" \
                    f"Host: {hostname} \r\n" \
                    f"Accept: text/event-stream \r\n" \
                    f"Connection: Keep-Alive \r\n" \
                    f"Content-Type: application/json; charset=UTF-8 \r\n" \
                    f"X-USER-UUID: 713285aa-a985-4b84-a473-d5bdee9b75ef \r\n" \
                    f"X-USER-VERSION:10309\r\n" \
                    f"Content-Type: application/json \r\n" \
                    f"Sec-Fetch-Mode: cors \r\n" \
                    f"Sec-Fetch-Site: cross-site \r\n" \
                    f"User-Agent: Dalvik/2.1.0 (Linux; U; Android 11; Redmi Note 8 Pro Build/RP1A.200720.011)\r\n" \
                    f"Content-Length: {len(body)}\r\n\r\n" \
                    f"{body}"
            print(request)
            response = b""
            keepgoing = True
            state = 1
            try:
                ssock.sendall(request.encode())
                total = ""
                while keepgoing:
                    chunk = ssock.recv(4096*2)
                    f.write(chunk)
                    f.flush()
                    if not chunk:
                        break                    
            finally:
                ssock.close()

def parse_ai_file(filename):
    f = open(filename,'r',encoding='utf-8')
    lines = f.readlines()
    f.close()
    idx = 0
    while (idx < len(lines)):
        idx+=1
    return None

def ask_ai_again(question):
    write_ai_to_file(question,"doctor.txt")
    parse_ai_file("doctor.txt")
    return None       

if __name__ == "__main__":
#    answer = ask_ai("translate into Swedish:機管局表示，截至目前為止，機場航班運作大致維持正常，部分航班可能受影響。旅客應留意最新的航班情況，有需要時向航空公司查詢。\n另外，於風暴信號生效期間，前往機場的公共交通只維持有限度服務，旅客請預留充足時間前往機場。")
    write_ai_to_file("translate into Swedish:機管局表示，截至目前為止，機場航班運作大致維持正常，部分航班可能受影響。旅客應留意最新的航班情況，有需要時向航空公司查詢。\n另外，於風暴信號生效期間，前往機場的公共交通只維持有限度服務，旅客請預留充足時間前往機場。","testai.txt")
    print(answer)