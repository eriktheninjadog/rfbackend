import socket
import json
import struct


#for testing purposes we will use assitant at all times
def ask_ai(question):
    msg = send_message_to_server("127.0.0.1","ask",question) 
    print(str(msg))
    return msg['data']

def send_message_to_server(ipnumber,command,data):
    message_to_send = json.dumps({"command":command,"data":data})
    SERVER_IP = ipnumber
    SERVER_PORT = 9002

    # Create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the server
    client_socket.connect((SERVER_IP, SERVER_PORT))
    print('Connected to {}:{}'.format(SERVER_IP, SERVER_PORT))
    # Create a JSON message to send to the server
    # Send the JSON message to the server
    message_as_bytes = message_to_send.encode()
    message_length = len(message_as_bytes)
    message_length_as_string = f'{message_length:10}'
    client_socket.sendall(message_length_as_string.encode())
    client_socket.sendall(message_to_send.encode())
    # Receive the response from the server
    received_data = b''  # Start with an empty byte string
    lendata = client_socket.recv(10)
    messagelen = int( lendata.decode() )
    print("message recieved len " + str(messagelen))
    while len(received_data) < messagelen:
            data = client_socket.recv(1024)
            received_data += data
            # Decode the received data
    response = received_data.decode()
    print('Received response:', response)
    # Close the connection
    client_socket.close()
    return json.loads(response)


if __name__ == "__main__":
    #ip = "192.168.0.151"
    ip = "127.0.0.1"
    #send_message_to_server("127.0.0.1","blabla","baad")
    send_message_to_server(ip,"robot","Assistant")
    send_message_to_server(ip,"ask","Translate this to English: 由宮崎駿執導兼編劇，吉卜力工作室所製作，2023年夏天上映的日本動畫電影《蒼鷺與少年》，靈感來自小說家吉野源三郎在1937年發表的同名著書，而動畫電影則是原創劇情。《SWITCH影視文藝特寫》2023 NO.9帶來「吉卜力特集」，從美術製作、劇情設定以及角色象徵寓意等與關鍵人物訪談，全面解析吉卜力動畫作品，首先由將吉卜力工作室的許多奇蹟變為現實的藝術家池澤夏樹開始！" )
    send_message_to_server(ip,"ask","What is 5 + 6" )
