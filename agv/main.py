import socket
import time

UDP_IP_MOVE = "192.168.1.100"
UDP_IP = "192.168.1.200"
UDP_PORT = 4000
MESSAGE = bytes([0xFF, 0x88, 0xFF, 0x88])
MESSAGE_STOP = bytes([0xFF, 0xFF, 0xFF, 0xFF])

STOP_FLAG = True


def move():

    global STOP_FLAG
    while STOP_FLAG:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(MESSAGE, (UDP_IP_MOVE, UDP_PORT))

        #time.sleep(1)  # Wait for 1 second before next call


def send_udp_data():

    global STOP_FLAG

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Set timeout for receiving data
    sock.settimeout(1.0)  # 1 second timeout

    try:
        # Send UDP message
        sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

        # Receive UDP response
        #response = b'1314095;1900;2472;2566;'
        response, _ = sock.recvfrom(1024)

        # Decode the bytes response into a string
        response_str = response.decode('utf-8')

        # Split the string into individual values
        values = response_str.split(';')

        # Extracting individual values
        time_value = int(values[0])
        print("Time:", time_value)

        distances = [int(x) for x in values[1:] if x]
        print("Distances:", distances)

        # Check if any distance value is below 500
        if any(distance < 500 for distance in distances):
            print("At least one distance value has fallen below 500.")
            sock.sendto(MESSAGE_STOP, (UDP_IP_MOVE, UDP_PORT))
            STOP_FLAG = False
        else:
            print("All distance values are 500 or above.")

    except socket.timeout:
        print("No response received within the timeout period.")
    finally:
        # Close the socket
        sock.close()

# Call the function every second
while STOP_FLAG:
    send_udp_data()
    #move()