# ✈️ Flight KML Tools for Google Earth

A collection of lightweight Python utilities for flight enthusiasts, frequent flyers, and pilots to clean flight tracks and generate custom airport pin maps for **Google Earth**.

---

## 📸 Previews

<!-- SCREENSHOT PLACEHOLDER: Add a screenshot of your Google Earth map with flight tracks and airport pins -->
![Google Earth Flight Map Overview](docs/images/google_earth_map_overview.png)
*Example: Clean 3D flight trails and custom airport pins imported into Google Earth.*

---

## 🚀 Included Utilities

### 1. `clean_fr24_kml.py` — Flightradar24 & FlightAware KML Optimizer
Flight tracking services like **Flightradar24** export KML files containing two main folders:
1. **Route**: Thousands of individual point placemarks for every second of altitude/speed telemetry.
2. **Trail**: The smooth 3D continuous flight line path.

Importing multiple raw KML files into Google Earth causes **extreme lag** and triggers map element limits due to tens of thousands of individual points. 

`clean_fr24_kml.py` strips out the redundant `Route` folder while preserving the continuous 3D flight path, metadata, headers, and colors — shrinking file sizes by **up to 95%** and making Google Earth run seamlessly.

### 2. `generate_airport_pins.py` — Custom Airport Pin Generator
Generates styled airport pin placemarks matching FlightAware / Google Earth formatting for any visited airport (IATA or ICAO code).

Each pin includes:
* 📍 **Blue Airport Pushpin Style**
* 🏷️ **Name Format:** `IATA (Full Airport Name)` (e.g. `BNA (Nashville International Airport)`)
* ℹ️ **Interactive Balloon Details:** City, State/Country, and live **FlightAware** activity & info links.
* 🌐 **Automatic Code Lookup:** Resolves ~29,000 global airports automatically using built-in / cached data.
* ⚡ **Interactive Quick Pin:** Run `python3 generate_airport_pins.py` and type `BNA`!
* 📁 **Smart Folder Naming:** Single pins import into Google Earth as the airport name directly (e.g. `BNA (Nashville International Airport)`), avoiding generic wrapper folder clutter.
* 🏷️ **Custom Container Naming (`-n`):** Specify custom folder names when bundling multiple airports.
* 🔍 **Auto-Scan Feature:** Scan a folder of exported flight KML files to automatically detect all visited airports and pin them all at once!

---

## 📦 Requirements & Installation

* **Python 3.7+**
* **Zero external dependencies!** Uses Python's built-in standard library (`urllib`, `xml`, `re`, `argparse`).

Simply clone or download this repository:
```bash
git clone https://github.com/your-username/flight-kml-tools.git
cd flight-kml-tools
chmod +x *.py
```

---

## 📖 Step-by-Step Tutorial: How to Get Your Flight KML Files

<!-- SCREENSHOT PLACEHOLDER: Add a screenshot showing the FR24 KML download button -->
![Flightradar24 KML Download Button](docs/images/fr24_export_tutorial.png)

### Exporting from Flightradar24:
1. Log in to your **Flightradar24** account on the web.
2. Go to **My Flightradar24** or search for any flight in history.
3. Select the flight and click on **Download / Export Data**.
4. Choose **KML** (or **KML Track**).
5. Save the `.kml` file to your computer.

### Exporting from FlightAware:
1. Go to [flightaware.com](https://flightaware.com) and search for your flight.
2. Under the flight track map, click **Google Earth (KML)**.
3. Download the resulting `.kml` file.

---

## 🛠️ Usage Guide

### Using `generate_airport_pins.py`

<!-- SCREENSHOT PLACEHOLDER: Add a screenshot of an airport pin balloon popup in Google Earth -->
![Airport Pin Popup Balloon](docs/images/airport_pin_balloon.png)

#### 1. Quick Interactive Mode (Most Popular):
Simply run the script with no arguments:
```bash
python3 generate_airport_pins.py
```
It will prompt you:
```text
Enter airport code(s) (e.g. BNA or BNA, DFW, LHR): BNA
```
*Creates `BNA_airport_pin.kml` ready to open in Google Earth! When imported into Google Earth, it names the item `BNA (Nashville International Airport)` directly without creating generic container folders.*

#### 2. Single Airport Pin via CLI:
```bash
python3 generate_airport_pins.py BNA
```

#### 3. Multiple Airport Pins:
```bash
python3 generate_airport_pins.py HSV DFW LHR FCO CIA LAS -o Visited_Airports.kml
```

#### 4. Custom Folder Name in Google Earth (`-n` / `--name`):
Prevent duplicate folder wrappers by customizing the container name inside Google Earth:
```bash
python3 generate_airport_pins.py BNA DFW LHR -n "2026 Trip Airports" -o Trip_Airports.kml
```

#### 5. Read Airport Codes from a Text or CSV File:
Create a file named `my_airports.txt` with your airport codes (e.g. `HSV, DFW, LHR, FCO, CIA, LAS`) and run:
```bash
python3 generate_airport_pins.py -f my_airports.txt -o Visited_Airports.kml
```

#### 6. Automatically Scan Flight KML Files:
```bash
python3 generate_airport_pins.py --scan ~/Downloads/*.kml -o Scanned_Visited_Airports.kml
```

---

### Command-Line Arguments Reference (`generate_airport_pins.py`)

| Argument | Description | Example |
| :--- | :--- | :--- |
| `codes` | One or more IATA / ICAO airport codes | `python3 generate_airport_pins.py BNA DFW` |
| `-o`, `--output` | Custom output `.kml` filename | `-o Visited_Airports.kml` |
| `-n`, `--name` | Custom folder/document name in Google Earth | `-n "Summer 2026 Airports"` |
| `-f`, `--file` | Path to text/CSV file containing airport codes | `-f my_airports.txt` |
| `--scan` | Glob pattern of KML flight files to scan | `--scan ~/Downloads/*.kml` |

---

### Using `clean_fr24_kml.py`

#### Clean a single KML file (overwrites in-place by default):
```bash
python3 clean_fr24_kml.py AA1667-410eac2d.kml
```

#### Batch clean all KML files in your Downloads directory:
```bash
python3 clean_fr24_kml.py ~/Downloads/*.kml
```

#### Save to a new file without overwriting the original:
```bash
python3 clean_fr24_kml.py flight.kml --no-inplace
```

#### Specify a custom output name:
```bash
python3 clean_fr24_kml.py flight.kml -o flight_clean.kml
```

---

## 🌍 How to Import into Google Earth

### Google Earth Web (Chrome / Edge / Firefox / Safari):
1. Go to [earth.google.com](https://earth.google.com/web/).
2. Open the left menu and click **Projects**.
3. Click **New Project** ➔ **Import KML file from computer**.
4. Select your cleaned `.kml` flight files and your `BNA_airport_pin.kml`.

### Google Earth Pro (Desktop App):
1. Launch **Google Earth Pro**.
2. Go to **File** ➔ **Open...**
3. Select your `.kml` files.
4. Drag and drop them under **My Places** to permanently save your interactive flight map!

---

## 📁 Repository Structure

```
flight-kml-tools/
│
├── clean_fr24_kml.py          # Flightradar24 / FlightAware KML path optimizer
├── generate_airport_pins.py   # Styled airport pin generator
├── README.md                  # Documentation and tutorial
└── docs/
    └── images/
        ├── google_earth_map_overview.png   # (Add your screenshot here)
        ├── fr24_export_tutorial.png        # (Add your screenshot here)
        └── airport_pin_balloon.png         # (Add your screenshot here)
```

---

## 🤝 Contributing & Feedback

Feel free to open an issue or submit a pull request if you have ideas for extra features (e.g. flight distance calculations, airline logos, or custom pin colors)!

---

## 📄 License

MIT License — free for personal and commercial use.
