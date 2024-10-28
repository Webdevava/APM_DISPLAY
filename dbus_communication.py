# dbus_communication.py
import dbus

def send_data_to_collector(data):
    try:
        bus = dbus.SystemBus()
        collector_service = bus.get_object('com.example.CollectorService', '/com/example/CollectorService')
        collector_method = collector_service.get_dbus_method('StoreData', 'com.example.CollectorService')
        
        # Send the data over D-Bus
        collector_method(data)
        print("Data sent to CollectorService via D-Bus.")
    except Exception as e:
        print(f"Error sending data via D-Bus: {e}")
