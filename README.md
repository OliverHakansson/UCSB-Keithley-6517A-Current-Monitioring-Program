# UCSB Keithley 6517A Current Monitoring Program

A Python-based current monitoring system for the **Keithley 6517A Electrometer**, developed for laboratory current monitoring applications at UCSB. The program continuously measures current values, for nanochannels, and sends email notifications when the experiment is completed.

## Features

* Real-time current monitoring using a Keithley 6517A Electrometer
* Email experiment alert notifications
* Lightweight Python implementation
* Suitable for long-term laboratory monitoring and unattended operation

## Project Structure

```text
UCSB-Keithley-6517A-Current-Monitioring-Program/
│
├── main.py
├── emailingtest.py
│
├── templates/
│   └── index.html
│
├── static/
│   └── style.css
│
├── experimentData.csv
├── experimentGraph.png
│
└── README.md
```

## Requirements

* Python 3.8+
* Keithley 6517A Electrometer
* VISA-compatible instrument connection (GPIB, or USB-GPIB)
* Email account for notifications

Install dependencies:

```bash
pip install pyvisa
```

Additional dependencies may be required depending on your email and instrument configuration.

## How It Works

1. `templates/index.html` takes in the experimental conditions
2. Styling is applied using `static/style.css`.
3. `main.py` communicates with the Keithley 6517A and acquires current measurements.
4. `index.html` displays the current measurements as a graph

## Configuration

Before running the program, configure on the website:

* Experimenter name
* Recipient email addresses
* Experiment name
* Sweepings voltages
* List of Test Voltages
* List of Test Timings
* Email results request

## Running the Program

Start monitoring by running:

```bash
python main.py
```

The application will connect to the Keithley 6517A, begin collecting measurements, and save them on the computer, email them when the experiment is complete and display the graphed results as the experiment goes on

## Email Alerts

Email notifications are generated using an template to provide clear and readable status reports.

Alert emails include:

* Experimental Condintions
* a `.csv` containing the individual data points
* a `.png` containing the graph generated from the data points

## Use Cases

* Long-term laboratory experiments
* Nano-channel Research

## Troubleshooting

### Instrument Not Found

Verify that the Keithley 6517A is connected and shows up on the list of connected instruments with the GPIB value associated with the device:


## Contributing

Contributions, bug reports, and feature requests are welcome.

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Open a pull request

## License

Specify your preferred license:

* MIT License

## Author

**Oliver Håkansson**
Intern at Pennathur Lab University of California, Santa Barbara (UCSB)

## Acknowledgments

* UCSB Pennathur laboratory
* Keithley Instruments
* PyVISA contributors
* Open-source Python community
