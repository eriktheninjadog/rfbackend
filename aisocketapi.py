import socket
import ssl
import json

from threading import Thread, Lock

#lock = Lock()
#lock.acquire()
#lock.release()


def ask_ai(question):
    with open('/var/www/html/api/rfbackend/auth_part.txt') as f:
        lines = f.readlines()
    auth_part = lines[0]
    path = "/chat?stream=true&model=gpt-4"
    hostname = 'api.writingmate.ai'
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
            try:
                ssock.sendall(request.encode())
                total = ""
                while keepgoing:
                    chunk = ssock.recv(4096)
                    if not chunk:
                        break
                    response += chunk
                    #print(chunk.decode())
                    #print("got package")

                    if (chunk.decode().find("data: [DONE]")!=-1):
                        keepgoing = False
                    else:
                        strpackage = chunk.decode()
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
                    # Process the response
                #print(response.decode())
                #text_file = open("sampleresponse.txt", "w")
                #n = text_file.write(total)
                #text_file.close()
            finally:
                # Close the socket connection
                ssock.close()
            return total
    

answer = ask_ai("Explain the grammar and structure of this text: 團隊表示，上蓋可於半小時內開合，令主場館可以全天候開放，不受惡劣天氣影響，組件於來港前亦已進行大量測試。隔音效能亦於來港前測試，確保即使舉行大型音樂活動，亦不會對附近居民造成嘈音問題。")
