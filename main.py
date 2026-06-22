from flask import Flask, render_template, request, jsonify
from datetime import datetime
from emailingtest import send_experiment_email
import json
import base64

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
        durations = request.form.getlist("durations[]")
        experiment_loops = request.form.get("experiment_loops", "1")
        voltage_sweep = request.form.get("voltageSweepCheckbox") is not None
        email_data = request.form.get("emailCheckBox") is not None
        
        # Filter out empty values
        durations = [d for d in durations if d.strip()]
        
        print("\n--- FORM DATA RECEIVED ---")
        print(f"Name:                    {name}")
        print(f"Email:                   {email}")
        print(f"Experiment:              {experiment_name}")
        print(f"Durations:               {durations}")
        print(f"Experiment Loops:        {experiment_loops}")
        print(f"Voltage Sweep:           {voltage_sweep}")
        print(f"Email Results:           {email_data}")
        print("--------------------------\n")
        
        # Reset experiment data on new submission
        experiment_data["start_time"] = datetime.now()
        experiment_data["data_points"] = []
        
        # Generate theoretical data and save to file
        import random
        data_file_content = f"""Experiment Data Log
===================
Experiment: {experiment_name}
Experimenter: {name}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Data Points:
Time (s)\tConductivity (µS/cm)


"""
        
        # Write data to experiment_data.txt
        with open("experiment_data.txt", "w") as f:
            f.write(data_file_content)
        # for i in range()
        
        print(f"Generated {len(experiment_data['data_points'])} data points")
        
        # Send email if checkbox is checked
        if email_data:
            html_report = f"""
            <html>
              <body>
                <h2 style="color: #1a73e8;">Experiment Report</h2>
                <p><strong>Experimenter:</strong> {name}</p>
                <p><strong>Experiment Name:</strong> {experiment_name}</p>
                <p><strong>Durations:</strong> {', '.join(durations)} s</p>
                <p><strong>Experiment Loops:</strong> {experiment_loops}</p>
                <p><strong>Voltage Sweep:</strong> {'Yes' if voltage_sweep else 'No'}</p>
                <p><strong>Data Points Collected:</strong> {len(experiment_data['data_points'])}</p>
                <hr>
                <p style="font-size: 12px; color: #5f6368;">Sent automatically via Current Monitoring System</p>
              </body>
            </html>
            """
            
            # Create experiment metadata as string for txt attachment
            txt_content = f"""EXPERIMENT REPORT
{'='*80}

Experimenter:        {name}
Email:               {email}
Experiment Name:     {experiment_name}
Date:                {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Durations:           {', '.join(durations)} s
Experiment Loops:    {experiment_loops}
Voltage Sweep:       {'Yes' if voltage_sweep else 'No'}"voltage_sweep": voltage_sweep,
Total Data Points:   {len(experiment_data['data_points'])}

{'='*80}
DATA POINTS (CSV Format)
{'='*80}

Time (s),Conductivity (µS/cm)
"""

            # Add data points in CSV format
            for point in experiment_data['data_points']:
                txt_content += f"{point['time']:.2f},{point['conductivity']:.2f}\n"
            
            # Send email with attachments
            send_experiment_email(
                recipient_email=email,
                html_body=html_report,
                txt_content=txt_content,
                png_attachment_path="experiment_graph.png"
            )
        
        # Return JSON instead of rendering template
        return jsonify({
            "success": True,
            "message": "Experiment started successfully",
            "voltage_sweep": voltage_sweep,
            "email_data": email_data,
            "data_points": experiment_data["data_points"]
        })
        
    return render_template("index.html", data=form_data)

@app.route("/get-experiment-data", methods=["GET"])
def get_experiment_data():
    """Retrieve experiment data from file"""
    try:
        with open("experiment_data.txt", "r") as f:
            content = f.read()
        return jsonify({
            "success": True,
            "data": content,
            "data_points": experiment_data["data_points"]
        })
    except FileNotFoundError:
        return jsonify({
            "success": False,
            "message": "No experiment data file found"
        })

@app.route("/save-chart", methods=["POST"])
def save_chart():
    """Save chart image from base64"""
    data = request.get_json()
    image_data = data.get("image_data")
    
    if image_data:
        try:
            # Remove the data URL prefix
            image_data = image_data.split(",")[1]
            
            # Decode and save
            image_bytes = base64.b64decode(image_data)
            
            with open("experiment_graph.png", "wb") as f:
                f.write(image_bytes)
            
            print("Chart saved as experiment_graph.png")
            return jsonify({"success": True})
        except Exception as e:
            print(f"Error saving chart: {e}")
            return jsonify({"success": False, "error": str(e)})
    
    return jsonify({"success": False})

@app.route("/add-conductivity-point", methods=["POST"])
def add_conductivity_point():
    """Add a conductivity measurement at a specific time"""
    data = request.get_json()
    conductivity = data.get("conductivity")
    
    # Initialize start time if not set
    if experiment_data["start_time"] is None:
        experiment_data["start_time"] = datetime.now()
    
    # Calculate elapsed time in seconds
    current_time = datetime.now()
    elapsed_time = (current_time - experiment_data["start_time"]).total_seconds()
    
    # Add data point
    data_point = {
        "time": elapsed_time,
        "conductivity": float(conductivity),
        "timestamp": current_time.isoformat()
    }
    
    experiment_data["data_points"].append(data_point)
    
    print(f"Conductivity Data Added - Time: {elapsed_time:.2f}s, Conductivity: {conductivity}µS/cm")
    
    return jsonify({
        "success": True,
        "message": "Conductivity measurement added successfully",
        "data": {
            "time": elapsed_time,
            "conductivity": float(conductivity)
        }
    })

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

import pyvisa

# Global variable to track Keithley connection
keithley_connected = False
keithley_device = None

def connect_to_keithley():
    """Connect to Keithley 6517A"""
    global keithley_connected, keithley_device
    
    try:
        # Create a PyVISA resource manager
        rm = pyvisa.ResourceManager()
        
        # List available instruments
        resources = rm.list_resources()
        print(f"Available instruments: {resources}")
        
        # Connect to Keithley 6517A (adjust the address if needed)
        keithley_device = rm.open_resource('GPIB0::27::INSTR')
        
        # Set timeout
        keithley_device.timeout = 5000
        
        # Identify the device
        idn = keithley_device.query("*IDN?")
        print(f"Connected to: {idn}")
        
        keithley_connected = True
        print("Keithley 6517A connected successfully!")
        return True
        
    except Exception as e:
        print(f"Failed to connect to Keithley: {e}")
        keithley_connected = False
        keithley_device = None
        return False

def read_keithley_current():
    """Read current measurement from Keithley 6517A"""
    global keithley_device
    
    if not keithley_connected or keithley_device is None:
        return None
    
    try:
        # Read the current value
        current = keithley_device.query(":MEAS:CURR?")
        return float(current)
    except Exception as e:
        print(f"Error reading from Keithley: {e}")
        return None

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

@app.route("/check-keithley", methods=["GET"])
def check_keithley():
    """Check if Keithley is connected"""
    global keithley_connected
    return jsonify({
        "connected": keithley_connected
    })

if __name__ == "__main__":
    connect_to_keithley()
    app.run(debug=True, port=9084)