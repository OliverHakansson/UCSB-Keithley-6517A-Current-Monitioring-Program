from flask import Flask, render_template, request, jsonify
from datetime import datetime
from emailingtest import send_experiment_email
import json
import base64
import pyvisa
import threading
import time

app = Flask(__name__)

# Store experiment data in memory (in production, use a database)
experiment_data = {
    "start_time": None,
    "data_points": []
}

@app.route("/", methods=["GET", "POST"])
def home():
    form_data = None

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        experiment_name = request.form.get("experiment_name")
        voltages = request.form.getlist("voltages[]")  # ADD THIS LINE
        durations = request.form.getlist("durations[]")
        experiment_loops = request.form.get("experiment_loops", "1")
        voltage_sweep = request.form.get("voltageSweepCheckbox") is not None
        email_data = request.form.get("emailCheckBox") is not None
        
        # Filter out empty values
        voltages = [v for v in voltages if v.strip()]  # ADD THIS LINE
        durations = [d for d in durations if d.strip()]
        
        print("\n--- FORM DATA RECEIVED ---")
        print(f"Name:                    {name}")
        print(f"Email:                   {email}")
        print(f"Experiment:              {experiment_name}")
        print(f"Voltages:                {voltages}")  # ADD THIS LINE
        print(f"Durations:               {durations}")
        print(f"Experiment Loops:        {experiment_loops}")
        print(f"Voltage Sweep:           {voltage_sweep}")
        print(f"Email Results:           {email_data}")
        print("--------------------------\n")
        
        
        if email_data:
            html_report = f"""
            <html>
              <body>
                <h2 style="color: #1a73e8;">Experiment Report</h2>
                <p><strong>Experimenter:</strong> {name}</p>
                <p><strong>Experiment Name:</strong> {experiment_name}</p>
                <p><strong>Voltages:</strong> {', '.join(voltages)} V</p>
                <p><strong>Durations:</strong> {', '.join(durations)} s</p>
                <p><strong>Experiment Loops:</strong> {experiment_loops}</p>
                <p><strong>Voltage Sweep:</strong> {'Yes' if voltage_sweep else 'No'}</p>
                <p><strong>Data Points Collected:</strong> {len(experiment_data['data_points'])}</p>
                <hr>
                <p style="font-size: 12px; color: #5f6368;">Sent automatically via Current Monitoring System</p>
              </body>
            </html>
            """
            
            txt_content = f"""EXPERIMENT REPORT
{'='*80}

Experimenter:        {name}
Email:               {email}
Experiment Name:     {experiment_name}
Date:                {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Voltages:            {', '.join(voltages)} V
Durations:           {', '.join(durations)} s
Experiment Loops:    {experiment_loops}
Voltage Sweep:       {'Yes' if voltage_sweep else 'No'}
Total Data Points:   {len(experiment_data['data_points'])}

{'='*80}
DATA POINTS (CSV Format)
{'='*80}

Time (s),Conductivity (µS/cm)
"""

            for point in experiment_data['data_points']:
                txt_content += f"{point['time']:.2f},{point['conductivity']:.2f}\n"
            
            send_experiment_email(
                recipient_email=email,
                html_body=html_report,
                txt_content=txt_content,
                png_attachment_path="experiment_graph.png"
            )
        
        return jsonify({
            "success": True,
            "message": "Experiment started successfully",
            "voltages": voltages,
            "durations": durations,
            "voltage_sweep": voltage_sweep,
            "email_data": email_data,
            "data_points": experiment_data["data_points"]
        })
        
    return render_template("index.html", data=form_data)

@app.route("/get-conductivity-data", methods=["GET"])
def get_conductivity_data():
    """Retrieve all conductivity data for the current experiment"""
    return jsonify({
        "success": True,
        "data_points": experiment_data["data_points"],
        "total_points": len(experiment_data["data_points"])
    })

@app.route("/reset-experiment", methods=["POST"])
def reset_experiment():
    """Reset the experiment data"""
    experiment_data["start_time"] = None
    experiment_data["data_points"] = []
    
    return jsonify({
        "success": True,
        "message": "Experiment data reset"
    })


# Global variable to track Keithley connection
keithley_connected = False
keithley_device = None
reconnect_thread = None
stop_reconnect = False

def connect_to_keithley():
    """Connect to Keithley 6517A"""
    global keithley_connected, keithley_device
    
    try:
        # Create a PyVISA resource manager
        rm = pyvisa.ResourceManager()
        
        # List available instruments
        resources = rm.list_resources()
        print(f"Available instruments: {resources}")
        
        if not resources:
            print("No instruments found!")
            keithley_connected = False
            return False
        
        # Connect directly to GPIB1::27::INSTR
        keithley_address = "GPIB1::27::INSTR"
        
        if keithley_address not in resources:
            print(f"Keithley not found at {keithley_address}")
            print(f"Available: {resources}")
            keithley_connected = False
            return False
        
        # Connect to the device
        keithley_device = rm.open_resource(keithley_address)
        keithley_device.timeout = 10000
        keithley_device.clear()
        
        # Identify the device
        idn = keithley_device.query("*IDN?")
        keithley_device.write("*RST")
        keithley_device.write("*CLS")
        keithley_device.write("SOUR:FUNC VOLT")
        keithley_device.write('SENS:FUNC "CURR"')
        # Electrometer-specific setup
        # keithley_device.write("SYST:ZCH ON")
        # keithley_device.write("SYST:ZCOR ON")
        # keithley_device.write("SYST:ZCH OFF")

        keithley_device.write("SENS:CURR:RANG:AUTO ON")
        keithley_device.write("SENS:CURR:NPLC 1")
        

        print(f"Connected to: {idn}")
        
        keithley_connected = True
        print("Keithley connected successfully!")
        return True
        
    except Exception as e:
        print(f"Failed to connect to Keithley: {e}")
        keithley_connected = False
        keithley_device = None
        return False

@app.route('/read_current')
def read_current():
    current = read_keithley_current()

    return jsonify({
        "success": current is not None,
        "current": current
    })

def read_keithley_current():
    global keithley_device
    print("I did a thing please please \n \n \n \n see this happening")

    if not keithley_connected or keithley_connected is None:
        return None
    try:
        keithley_device.write("SOUR:VOLT 0")
        keithley_device.write("OUTP ON")
        keithley_device.write(f"SOUR:VOLT {voltages[0]}")
        current = keithley_device.query("MEAS:CURR?")
        currentOther = keithley_device.query("READ?")
        print(current)
        print(currentOther)
        return float(current)
    except Exception as e:
        print(f"Error reading current from Keithley: {e}")
        return None

def reconnect_loop():
    """Continuously try to reconnect to Keithley every 5 seconds"""
    global keithley_connected, stop_reconnect
    
    while not stop_reconnect:
        if not keithley_connected:
            print("Attempting to reconnect to Keithley...")
            connect_to_keithley()
        time.sleep(5)  # Try every 5 seconds

def start_reconnect_thread():
    """Start the reconnect thread"""
    global reconnect_thread, stop_reconnect
    stop_reconnect = False
    reconnect_thread = threading.Thread(target=reconnect_loop, daemon=True)
    reconnect_thread.start()
    print("Reconnect thread started")

def stop_reconnect_thread():
    """Stop the reconnect thread"""
    global stop_reconnect
    stop_reconnect = True


@app.route("/check-keithley", methods=["GET"])
def check_keithley():
    """Check if Keithley is connected"""
    global keithley_connected
    return jsonify({
        "connected": keithley_connected
    })

def disconnect_keithley():
    """Disconnect from Keithley 6517A"""
    global keithley_device, keithley_connected
    
    if keithley_device is not None:
        try:
            keithley_device.close()
            keithley_connected = False
            print("Keithley disconnected")
        except Exception as e:
            print(f"Error disconnecting Keithley: {e}")

if __name__ == "__main__":
    connect_to_keithley()
    start_reconnect_thread()  # Start continuous reconnect attempts
    try:
        app.run(debug=True, port=9084)
    finally:
        stop_reconnect_thread()
        disconnect_keithley()