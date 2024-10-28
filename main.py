# app.py
import requests
import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

# Database initialization
def init_db():
    conn = sqlite3.connect('system_status.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS system_status
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  is_ble_power_adapter_connected BOOLEAN,
                  is_ble_remote_connected BOOLEAN,
                  rtc_battery_percentage INTEGER,
                  meter_battery_percentage INTEGER,
                  is_tv_cable_plugged_in BOOLEAN,
                  is_tv_tamper_detected BOOLEAN)''')
    c.execute('''CREATE TABLE IF NOT EXISTS members
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  age INTEGER,
                  gender TEXT,
                  is_active BOOLEAN)''')
    
    # Insert dummy data into system_status
    c.execute('''INSERT OR IGNORE INTO system_status
                 (id, is_ble_power_adapter_connected, is_ble_remote_connected,
                  rtc_battery_percentage, meter_battery_percentage,
                  is_tv_cable_plugged_in, is_tv_tamper_detected)
                 VALUES (1, 1, 0, 75, 80, 1, 0)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/api/system_status')
def get_system_status():
    conn = sqlite3.connect('system_status.db')
    c = conn.cursor()
    
    # Get current system status
    c.execute('SELECT * FROM system_status WHERE id = 1')
    row = c.fetchone()
    
    if row:
        status = {
            'is_ble_power_adapter_connected': bool(row[1]),
            'is_ble_remote_connected': bool(row[2]),
            'rtc_battery_percentage': row[3],
            'meter_battery_percentage': row[4],
            'is_tv_cable_plugged_in': bool(row[5]),
            'is_tv_tamper_detected': bool(row[6])
        }
        conn.close()
        return jsonify(status)
    else:
        conn.close()
        return jsonify({'error': 'No system status found'}), 404

@app.route('/api/send_data', methods=['POST'])
def send_data_to_collector():
    """
    Endpoint to send system data to a specified collector URL. 
    Expects JSON data with 'collector_url'.
    """
    data = request.json
    collector_url = data.get('collector_url')
    
    if not collector_url:
        return jsonify({'error': 'Collector URL is required'}), 400

    # Fetch the system status from the database
    conn = sqlite3.connect('system_status.db')
    c = conn.cursor()
    c.execute('SELECT * FROM system_status WHERE id = 1')
    row = c.fetchone()
    
    if not row:
        conn.close()
        return jsonify({'error': 'No system status found'}), 404
    
    # Prepare the data payload
    status = {
        'is_ble_power_adapter_connected': bool(row[1]),
        'is_ble_remote_connected': bool(row[2]),
        'rtc_battery_percentage': row[3],
        'meter_battery_percentage': row[4],
        'is_tv_cable_plugged_in': bool(row[5]),
        'is_tv_tamper_detected': bool(row[6])
    }
    
    conn.close()

    # Send data to the collector
    try:
        response = requests.post(collector_url, json=status)
        response.raise_for_status()  # Raise an error for unsuccessful requests
        return jsonify({'status': 'Data sent successfully', 'response': response.json()})
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
