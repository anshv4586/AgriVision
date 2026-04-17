import serial
import time

PORT = 'COM10'
BAUD = 9600

def test_sensor():
    print(f"Attempting to open {PORT}...")
    try:
        ser = serial.Serial(PORT, BAUD, timeout=3)
        print(f"Successfully opened {PORT}!")
        
        for i in range(5):
            line = ser.readline().decode(errors='ignore').strip()
            print(f"Read {i+1}: '{line}'")
            time.sleep(1)
            
        ser.close()
        print("Closed port.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_sensor()
