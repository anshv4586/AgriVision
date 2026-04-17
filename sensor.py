import serial
import re
import time
import serial.tools.list_ports

# Global serial object
ser = None
PORT = 'COM10'
BAUD = 9600

def init_serial(baud=9600):
    global ser, BAUD
    BAUD = baud
    if ser:
        try:
            ser.close()
        except:
            pass
    
    try:
        ser = serial.Serial(PORT, BAUD, timeout=2)
        print(f"Serial {PORT} Opened at {BAUD}")
    except Exception as e:
        print(f"Serial Error on {PORT}: {e}")
        ser = None

# Initial attempt
init_serial()

def get_sensor_data():
    global ser
    
    # Try to re-init if closed
    if not ser:
        # Try both common baud rates
        for b in [9600, 115200]:
            print(f"Attempting {PORT} at {b}...")
            init_serial(b)
            if ser: break
        if not ser: return None

    # Read logic
    attempts = 10  # Increased attempts to capture both data and alerts
    data_found = None
    alerts = []

    while attempts > 0:
        attempts -= 1
        try:
            if not ser.is_open:
                ser.open()
                
            line = ser.readline().decode(errors='ignore').strip()
            if not line: continue

            print(f"DEBUG: Read line from {PORT}: '{line}'")

            # 1. Check for alerts
            if "ALERT" in line:
                # Clean up the alert text (remove [!] prefix if present)
                clean_alert = line.replace("[!]", "").strip()
                if clean_alert not in alerts:
                    alerts.append(clean_alert)
                continue

            # 2. Check for numeric data
            numbers = re.findall(r"[-+]?\d*\.\d+|\d+", line)
            
            if len(numbers) >= 4:
                try:
                    # Arduino output: Time, Temp, Humid, Moisture
                    temp = float(numbers[1])
                    humidity = float(numbers[2])
                    moisture = int(numbers[3])

                    # Basic validation to filter out obvious garbage
                    if 0 <= humidity <= 100 and -20 <= temp <= 100:
                        data_found = {
                            "temp": temp,
                            "humidity": humidity,
                            "moisture": moisture
                        }
                        # If we have data, we'll keep checking a few more lines for alerts
                except (ValueError, IndexError):
                    continue
                    
            # If we have both data and some alerts, or we are running out of attempts
            if data_found and len(alerts) > 0:
                break
                
        except Exception as e:
            print(f"Read Error: {e}")
            ser = None # Trigger re-init next time
            break
            
    if data_found:
        temp = data_found["temp"]
        humidity = data_found["humidity"]
        moisture = data_found["moisture"]

        # Generate smart alerts from thresholds — no need for Arduino to send "ALERT"
        alerts = []

        if moisture < 20:
            alerts.append("Moisture critically low (" + str(moisture) + "%) — water your plant immediately!")
        elif moisture < 30:
            alerts.append("Moisture low (" + str(moisture) + "%) — consider watering soon")
        
        if temp > 40:
            alerts.append("Temperature dangerously high (" + str(temp) + "°C) — risk of heat stress")
        elif temp > 35:
            alerts.append("Temperature high (" + str(temp) + "°C) — provide shade or cooling")
        elif temp < 5:
            alerts.append("Temperature too low (" + str(temp) + "°C) — risk of frost damage")

        if humidity > 90:
            alerts.append("Humidity very high (" + str(humidity) + "%) — fungal disease risk elevated")
        elif humidity > 80:
            alerts.append("Humidity high (" + str(humidity) + "%) — improve air circulation")
        elif humidity < 25:
            alerts.append("Humidity too low (" + str(humidity) + "%) — consider misting")

        data_found["alerts"] = alerts
        return data_found
        
    return None
