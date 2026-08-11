#!/usr/bin/env python3
"""
Airport Pin Generator for Google Earth (generate_airport_pins.py)

Description:
    Generates a Google Earth KML file containing styled airport pin placemarks 
    matching FlightAware/Google Earth styling (IATA/ICAO code, full airport name, 
    city/state/country, coordinates, and live FlightAware activity/info links).

Usage:
    # Quick interactive mode (prompts you to type an airport code like BNA):
    python3 generate_airport_pins.py

    # Single airport pin:
    python3 generate_airport_pins.py BNA

    # Multiple airport pins:
    python3 generate_airport_pins.py BNA DFW LHR FCO

    # Specify custom folder name:
    python3 generate_airport_pins.py BNA DFW -n "My Visited Airports"

    # Read airport codes from a text or CSV file:
    python3 generate_airport_pins.py -f my_airports.txt

    # Scan existing KML flight files to automatically extract visited airports:
    python3 generate_airport_pins.py --scan ~/Downloads/*.kml
"""

import os
import sys
import json
import urllib.request
import argparse
import re

CACHE_FILE = os.path.expanduser("~/.cache/airports_db.json")
DATA_URL = "https://raw.githubusercontent.com/mwgg/Airports/master/airports.json"

def fetch_airport_database():
    """Fetches and caches the global airport dataset (~29,000 airports)."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    print("🌐 Downloading global airport database (one-time fetch)...")
    try:
        req = urllib.request.Request(DATA_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)
        print("✅ Database cached locally.")
        return data
    except Exception as e:
        print(f"⚠️ Warning: Could not download online database ({e}). Using offline lookup mode.")
        return {}

def build_lookup_index(db):
    """Builds fast lookup dicts for IATA and ICAO codes."""
    iata_map = {}
    icao_map = {}

    for k, v in db.items():
        icao = (v.get("icao") or k).strip().upper()
        iata = (v.get("iata") or "").strip().upper()

        if icao:
            icao_map[icao] = v
        if iata and iata != "\\N" and iata != "-":
            iata_map[iata] = v

    return iata_map, icao_map

def find_airport(code, iata_map, icao_map):
    """Finds an airport entry by IATA or ICAO code."""
    code = code.strip().upper()
    if code in iata_map:
        return iata_map[code]
    if code in icao_map:
        return icao_map[code]
    # Try adding 'K' prefix for US 3-letter codes if icao search fails
    if len(code) == 3 and f"K{code}" in icao_map:
        return icao_map[f"K{code}"]
    return None

def get_display_title(airport):
    """Generates IATA (Full Name) display title."""
    iata = (airport.get("iata") or "").strip().upper()
    icao = (airport.get("icao") or "").strip().upper()
    name = airport.get("name", "Airport").strip()
    return f"{iata} ({name})" if iata and iata != "\\N" else f"{icao} ({name})"

def create_placemark_xml(airport):
    """Generates KML Placemark XML string matching exact Google Earth schema."""
    iata = (airport.get("iata") or "").strip().upper()
    icao = (airport.get("icao") or "").strip().upper()
    name = airport.get("name", "Airport").strip()
    city = airport.get("city", "").strip()
    state = airport.get("state", "").strip()
    country = airport.get("country", "").strip()
    lat = airport.get("lat", 0.0)
    lon = airport.get("lon", 0.0)

    flightaware_icao = icao if len(icao) == 4 else (f"K{iata}" if len(iata) == 3 and country == "US" else iata)
    display_title = get_display_title(airport)

    location_parts = []
    if city:
        location_parts.append(city)
    if state and state != city:
        location_parts.append(state)
    elif country and not state:
        location_parts.append(country)
    location_str = ", ".join(location_parts)

    description = (
        f"{name}<br>{location_str}<br><br>"
        f"<a href='http://www.flightaware.com/live/airport/{flightaware_icao}'>"
        f"{iata or icao} airport activity (live)</a><br>"
        f"<a href='http://www.flightaware.com/resources/airport/{flightaware_icao}'>"
        f"{iata or icao} airport information</a>"
    )

    placemark = f"""	<Placemark>
		<name>{display_title}</name>
		<styleUrl>#airport_pin</styleUrl>
		<description><![CDATA[{description}]]></description>
		<Point>
			<coordinates>{lon},{lat},0</coordinates>
		</Point>
	</Placemark>"""
    return placemark

def generate_kml_document(placemarks_xml, doc_name=None):
    """Wraps placemarks into a complete KML document."""
    name_tag = f"\t<name>{doc_name}</name>\n" if doc_name else ""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">
<Document>
{name_tag}\t<Style id="airport_pin">
		<IconStyle>
			<scale>1.1</scale>
			<Icon>
				<href>https://earth.google.com/earth/document/icon?color=1976d2&amp;id=2000&amp;scale=4</href>
			</Icon>
			<hotSpot x="64" y="128" xunits="pixels" yunits="insetPixels"/>
		</IconStyle>
		<LabelStyle>
			<scale>0.9</scale>
		</LabelStyle>
		<BalloonStyle>
			<text><![CDATA[$[description]]]></text>
		</BalloonStyle>
	</Style>
""" + "\n".join(placemarks_xml) + """
</Document>
</kml>
"""

def extract_airport_codes_from_kmls(kml_paths, iata_map, icao_map):
    """Extracts airport codes found in KML filenames or flight metadata."""
    found_codes = set()
    pattern = re.compile(r'\b[A-Z]{3,4}\b')

    for path in kml_paths:
        filename = os.path.basename(path)
        matches = pattern.findall(filename)
        for m in matches:
            if find_airport(m, iata_map, icao_map):
                found_codes.add(m)
                
    return sorted(found_codes)

def process_codes(codes_to_process, output_filename, iata_map, icao_map, custom_doc_name=None):
    """Generates KML for the given set of airport codes."""
    if not codes_to_process:
        print("⚠️ No valid airport codes to process.")
        return False

    print(f"✈️ Processing {len(codes_to_process)} airport code(s)...")

    placemarks_xml = []
    found_airports = []

    for code in sorted(codes_to_process):
        airport = find_airport(code, iata_map, icao_map)
        if airport:
            pm = create_placemark_xml(airport)
            placemarks_xml.append(pm)
            found_airports.append(airport)
            iata = airport.get("iata") or airport.get("icao")
            print(f"  ✅ Added {code} -> {iata} ({airport.get('name')})")
        else:
            print(f"  ⚠️ Airport code not found: {code}")

    if not placemarks_xml:
        print("❌ No matching airports found.")
        return False

    # Smart document naming:
    # If 1 airport pin: Use airport name so Google Earth does not create a generic wrapper folder
    # If multiple airports: Use custom_doc_name or "Airport Pins"
    if custom_doc_name:
        doc_name = custom_doc_name
    elif len(found_airports) == 1:
        doc_name = get_display_title(found_airports[0])
    else:
        doc_name = "Airport Pins"

    kml_content = generate_kml_document(placemarks_xml, doc_name=doc_name)

    output_path = os.path.abspath(os.path.expanduser(output_filename))
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(kml_content)

    print(f"\n🎉 Success! Created {len(found_airports)} airport pin(s) in:\n   📍 {output_path}\n")
    return True

def main():
    parser = argparse.ArgumentParser(
        description="Generate Google Earth airport pin KML files matching FlightAware styling.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("codes", nargs="*", help="Airport IATA or ICAO codes (e.g. BNA HSV DFW LHR)")
    parser.add_argument("-f", "--file", type=str, help="Text/CSV file containing list of airport codes")
    parser.add_argument("-o", "--output", type=str, help="Output KML file path")
    parser.add_argument("-n", "--name", type=str, help="Custom folder/document name inside Google Earth")
    parser.add_argument("--scan", nargs="*", help="Scan KML files to automatically detect visited airports")

    args = parser.parse_args()

    db = fetch_airport_database()
    iata_map, icao_map = build_lookup_index(db)

    # Interactive Mode if run with no args
    if not args.codes and not args.file and not args.scan:
        print("✈️ --- Airport Pin Generator (Interactive Mode) ---")
        try:
            user_input = input("Enter airport code(s) (e.g. BNA or BNA, DFW, LHR): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            sys.exit(0)

        if not user_input:
            print("No input provided. Exiting.")
            sys.exit(0)

        codes = [c.strip().upper() for c in user_input.replace(",", " ").split() if c.strip()]
        
        if args.output:
            out_file = args.output
        elif len(codes) == 1:
            out_file = f"{codes[0]}_airport_pin.kml"
        else:
            out_file = "Airport_Pins.kml"

        process_codes(set(codes), out_file, iata_map, icao_map, custom_doc_name=args.name)
        sys.exit(0)

    # Command line mode
    codes_to_process = set()

    if args.codes:
        for c in args.codes:
            for code in c.replace(",", " ").split():
                codes_to_process.add(code.strip().upper())

    if args.file and os.path.exists(args.file):
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read()
            tokens = re.findall(r'\b[A-Za-z]{3,4}\b', text)
            for t in tokens:
                if find_airport(t, iata_map, icao_map):
                    codes_to_process.add(t.strip().upper())

    if args.scan:
        import glob
        expanded = []
        for p in args.scan:
            expanded.extend(glob.glob(os.path.expanduser(p)))
        scanned_codes = extract_airport_codes_from_kmls(expanded, iata_map, icao_map)
        codes_to_process.update(scanned_codes)

    if args.output:
        output_filename = args.output
    elif len(codes_to_process) == 1:
        single_code = next(iter(codes_to_process))
        output_filename = f"{single_code}_airport_pin.kml"
    else:
        output_filename = "Airport_Pins.kml"

    process_codes(codes_to_process, output_filename, iata_map, icao_map, custom_doc_name=args.name)

if __name__ == "__main__":
    main()
