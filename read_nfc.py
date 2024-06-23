import board
import busio
from adafruit_pn532.i2c import PN532_I2C
from azure.iot.device import IoTHubDeviceClient, Message

# Azure IoT Hub connection string
CONNECTION_STRING = "YOUR_DEVICE_CONNECTION_STRING"

# Initialize I2C bus
i2c = busio.I2C(board.SCL, board.SDA)
pn532 = PN532_I2C(i2c, debug=False)

# Begin communication with PN532
pn532.SAM_configuration()

# Create an IoT Hub client
client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)

print('Waiting for NFC card...')
card_found = False  # Flag to track if a card has been found

try:
    while True:
        # Check if a card is available to read
        uid = pn532.read_passive_target(timeout=0.5)

        if uid is not None and not card_found:
            # Found a card, print UID as continuous hexadecimal string
            uid_str = ''.join([format(i, '02X') for i in uid])
            print('Found card with UID:', uid_str)
            
            # Create a message to send to Azure IoT Hub
            message = Message(uid_str)
            # Send the message
            client.send_message(message)
            print("Message successfully sent to IoT Hub")
            
            card_found = True  # Set flag to True to indicate card has been found

        elif uid is None and card_found:
            card_found = False  # Reset flag if no card is detected

except KeyboardInterrupt:
    print("\nProgram stopped by user.")
except Exception as e:
    print("Error:", e)
finally:
    client.shutdown()