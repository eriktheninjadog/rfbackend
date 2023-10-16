import socket
import ssl
import json

from threading import Thread, Lock



def ask_ai(question):
    with open('/var/www/html/api/rfbackend/auth_part.txt') as f:
        lines = f.readlines()
    auth_part = lines[0]
    path = "/chat?stream=true&model=gpt-4"
    hostname = 'api.writingmate.ai'
    flog = open('/var/www/html/api/rfbackend/aisocket.log','wb')
    context = ssl.create_default_context()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    abody = {}
    abody["prompt"] = "Human: " + question + "\n"
    #auth="Bearer   "
    "90b8706b-2738-42e1-ad4d-fbf01b89e23b"
    #auth= "Bearer eyJhbGciOiJIUzI1NiJ9.eyJodHRwczovL2hhc3VyYS5pby9qd3QvY2xhaW1zIjp7IngtaGFzdXJhLXByZW1pdW0iOiJmYWxzZSIsIngtaGFzdXJhLWFsbG93ZWQtcm9sZXMiOlsibWUiLCJ1c2VyIl0sIngtaGFzdXJhLWRlZmF1bHQtcm9sZSI6InVzZXIiLCJ4LWhhc3VyYS11c2VyLWlkIjoiM2Q5N2M0YTAtMTFmYi00OTZjLThhNmQtODA4M2QxZDUyMmQ5IiwieC1oYXN1cmEtdXNlci1pcy1hbm9ueW1vdXMiOiJmYWxzZSJ9LCJzdWIiOiIzZDk3YzRhMC0xMWZiLTQ5NmMtOGE2ZC04MDgzZDFkNTIyZDkiLCJpYXQiOjE2ODg2MjI0ODEsImV4cCI6MTY4ODcwODg4MSwiaXNzIjoiaGFzdXJhLWF1dGgifQ.bWFjOoCkbBtRYWvuoYyfSdK9lqemiaVzZXCLSowUUSI"
    #auth="Bearer eyJhbGciOiJIUzI1NiJ9.eyJodHRwczovL2hhc3VyYS5pby9qd3QvY2xhaW1zIjp7IngtaGFzdXJhLXBsYW4iOiJwcm9feWVhcmx5IiwieC1oYXN1cmEtcHJlbWl1bSI6InRydWUiLCJ4LWhhc3VyYS1hbGxvd2VkLXJvbGVzIjpbIm1lIiwidXNlciJdLCJ4LWhhc3VyYS1kZWZhdWx0LXJvbGUiOiJ1c2VyIiwieC1oYXN1cmEtdXNlci1pZCI6IjNkOTdjNGEwLTExZmItNDk2Yy04YTZkLTgwODNkMWQ1MjJkOSIsIngtaGFzdXJhLXVzZXItaXMtYW5vbnltb3VzIjoiZmFsc2UifSwic3ViIjoiM2Q5N2M0YTAtMTFmYi00OTZjLThhNmQtODA4M2QxZDUyMmQ5IiwiaWF0IjoxNjg4NzIwMTM4LCJleHAiOjE2ODg4MDY1MzgsImlzcyI6Imhhc3VyYS1hdXRoIn0.blnm6MGUmTWtH68biEq_vUjRTzCjgqjMQNMBdjQLs9c"
    #auth="Bearer eyJhbGciOiJIUzI1NiJ9.eyJodHRwczovL2hhc3VyYS5pby9qd3QvY2xhaW1zIjp7IngtaGFzdXJhLXBsYW4iOiJwcm9feWVhcmx5IiwieC1oYXN1cmEtcHJlbWl1bSI6InRydWUiLCJ4LWhhc3VyYS1hbGxvd2VkLXJvbGVzIjpbIm1lIiwidXNlciJdLCJ4LWhhc3VyYS1kZWZhdWx0LXJvbGUiOiJ1c2VyIiwieC1oYXN1cmEtdXNlci1pZCI6IjNkOTdjNGEwLTExZmItNDk2Yy04YTZkLTgwODNkMWQ1MjJkOSIsIngtaGFzdXJhLXVzZXItaXMtYW5vbnltb3VzIjoiZmFsc2UifSwic3ViIjoiM2Q5N2M0YTAtMTFmYi00OTZjLThhNmQtODA4M2QxZDUyMmQ5IiwiaWF0IjoxNjg4OTc3NjQ0LCJleHAiOjE2ODkwNjQwNDQsImlzcyI6Imhhc3VyYS1hdXRoIn0.GkKMYB1ZFzq87DZcNqcxrjKsgA5sGMKKD8QyZAphAbM"
    auth="Bearer " + auth_part
    context = ssl.create_default_context()
    #body = '{"prompt":"Human: tell me a story\\n"}'
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
                        firstgotten = True
                    else:
                        #everything start with the length in hex followed by line and data:
                        #is the data encoded, is it binary?
                        athing = chunk.decode()
                        length = int(athing.split("\n")[0],16)
                        print(str(length))
                        start = athing.find("\n")
                        #print(chunk[start+1:length+2].decode())
                        #print("got package")
                        wholenineyards += chunk[start+1:length+2].decode()

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
            finally:
                ssock.close()
                wholenineyards = wholenineyards.replace("data: [DONE]","")
                wholenineyards = wholenineyards.replace("data:","\n")
                for i in wholenineyards.split("\n"):
                    pop = json.loads(i)
                    print(pop['choices'][0]['delta']['content'])
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

answer = ask_ai("write each noun in this text to a new line:機管局表示，截至目前為止，機場航班運作大致維持正常，部分航班可能受影響。旅客應留意最新的航班情況，有需要時向航空公司查詢。\n另外，於風暴信號生效期間，前往機場的公共交通只維持有限度服務，旅客請預留充足時間前往機場。")
print(answer)