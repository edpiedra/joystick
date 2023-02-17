import socket, cv2, pickle, struct
import adafruit_rfm9x
import board, busio, digitalio, subprocess

class Bluetooth():
    def _create_client(self, server_addr, port):
        print("[INFO] creating bluetooth socket client...")
        
        s = socket.socket(
            socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM
        )
        
        trying = True
        
        while trying:
            try:
                s.connect((server_addr, port))
                trying = False 
            except:
                continue 
            
        print("[INFO] connected to {} on {}...".format(
            server_addr, port
        ))
        
        return s 
    
    def _create_server(self, server_addr, port):
        print("[INFO] creating bluetooth socket server...")
        
        subprocess.call(['sudo', 'hciconfig', 'hci0', 'piscan'])
        
        s = socket.socket(
            socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM
        )
        
        s.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
        )
        
        s.bind((server_addr, port))
        s.listen(10)
        conn, addr = s.accept()
        print("[INFO] connected to {}...".format(addr))
        
        subprocess.call(['sudo', 'hciconfig', 'hci0', 'noscan'])
        
        return conn

    def _receive_frame(self, conn):
        data = b""
        payload_size = struct.calcsize(">L")

        while len(data) < payload_size:
            data += conn.recv(4096)

        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack(">L", packed_msg_size)[0]

        while len(data) < msg_size:
            data += conn.recv(4096)

        frame_data = data[:msg_size]
        data = data[msg_size:]

        frame = pickle.loads(frame_data, fix_imports=True, encoding="bytes")
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

        return frame
        
    def _send_color_frame(self, s, frame):
        _, frame = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        data = pickle.dumps(frame, 0)
        size = len(data)
        s.sendall(struct.pack(">L", size) + data)
        
    def _destroy(self, s):
        s.shutdown(1)
        
class Radio():
    def __init__(self):
        spi = busio.SPI( board.SCK, MOSI=board.MOSI, MISO=board.MISO )
        CS = digitalio.DigitalInOut( board.CE1 )
        RESET = digitalio.DigitalInOut( board.D22 )
        RADIO_FREQ_MHZ = 915.0

        rfm9x = adafruit_rfm9x.RFM9x( spi, CS, RESET, RADIO_FREQ_MHZ, baudrate=1000000 )
        rfm9x.tx_power = 13 #default is 13 can go up to 23dB
        
        self.rfm9x = rfm9x 
        
    def _send_message(self, message):
        self.rfm9x.send(bytes(message, "utf-8"))
        
    def _receive_message(self):
        packet = self.rfm9x.receive()
        return packet
    
class WiFi():
    def _create_client(self, host, port):
        c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        trying = True 

        while trying:
            try: 
                c.connect((host, port))
                trying = False
            except:
                continue 

        print("[INFO] connected to...{} on {}".format(host, port)) 
        
        return c 
    
    def _send_frame(self, vs, frame):
        _, frame = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        data = pickle.dumps(frame, 0)
        size = len(data)
        vs.sendall(struct.pack(">L", size) + data)
    
    def _receive_frame(self, conn):
        data = b""
        payload_size = struct.calcsize(">L")

        while len(data) < payload_size:
            data += conn.recv(4096)

        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack(">L", packed_msg_size)[0]

        while len(data) < msg_size:
            data += conn.recv(4096)

        frame_data = data[:msg_size]
        data = data[msg_size:]

        frame = pickle.loads(frame_data, fix_imports=True, encoding="bytes")
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

        return frame
        
    def _create_server(self, port): 
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        s.bind(("", port)) 
        s.listen(10) 
        conn, addr = s.accept() 
        print("[INFO] connected to...{}".format(addr)) 
        
        return conn
    
    def _send_list(self, vs, lst):
        data = pickle.dumps(lst)
        vs.sendall(data)
        
    def _receive_list(self, conn):
        data = conn.recv(1024)
        lst = pickle.loads(data)
        
        return lst
    
    def _destroy(self, s):
        s.shutdown(1)
        s.close()