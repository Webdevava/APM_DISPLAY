# collector_service.py
import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib
import sqlite3
import json

class CollectorService(dbus.service.Object):
    def __init__(self, bus_name):
        dbus.service.Object.__init__(self, bus_name, '/com/example/CollectorService')
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect('collected_data.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS member_data
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      state INTEGER,
                      gender TEXT,
                      age INTEGER)''')
        conn.commit()
        conn.close()

    @dbus.service.method('com.example.CollectorService', in_signature='a(is)', out_signature='')
    def StoreData(self, data):
        conn = sqlite3.connect('collected_data.db')
        c = conn.cursor()
        
        for member in data:
            state, gender, age = member
            c.execute('INSERT INTO member_data (state, gender, age) VALUES (?, ?, ?)', (state, gender, age))
        
        conn.commit()
        conn.close()
        print("Data stored in collected_data.db")

def main():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    bus_name = dbus.service.BusName('com.example.CollectorService', bus)
    collector_service = CollectorService(bus_name)
    
    loop = GLib.MainLoop()
    print("CollectorService is running.")
    loop.run()

if __name__ == '__main__':
    main()
