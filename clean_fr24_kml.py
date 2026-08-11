#!/usr/bin/env python3
"""
Flightradar24 KML Route Stripper (clean_fr24_kml.py)

Description:
    Flightradar24 KML exports contain two main folders:
    1. 'Route': Thousands of individual point Placemarks for every timestamp.
    2. 'Trail': The continuous 3D line string representation of the flight path.

    Importing multiple full KML files into Google Earth frequently hits map 
    element limits and causes severe performance degradation due to the thousands 
    of individual route points.

    This script automatically removes the 'Route' folder from Flightradar24 KML 
    files while preserving the 'Trail' folder, metadata, styles, and headers.

Usage:
    # Clean a single file (overwrites in-place by default):
    python3 clean_fr24_kml.py AA1667-410eac2d.kml

    # Clean all KML files in Downloads folder:
    python3 clean_fr24_kml.py ~/Downloads/*.kml

    # Save output to a new file instead of overwriting:
    python3 clean_fr24_kml.py flight.kml --no-inplace

    # Specify custom output name:
    python3 clean_fr24_kml.py flight.kml -o flight_clean.kml

GitHub Repository: https://github.com/your-username/fr24-kml-cleaner
"""

import sys
import os
import glob
import re
import argparse

def strip_route_folder(kml_content: str) -> tuple[str, bool]:
    """
    Strips the <Folder><name>Route</name>...</Folder> block from KML text.
    Returns (cleaned_content, route_found).
    """
    pattern = re.compile(r'\s*<Folder>\s*<name>Route</name>.*?</Folder>', re.DOTALL)
    if not pattern.search(kml_content):
        return kml_content, False
    
    cleaned_content = pattern.sub('', kml_content)
    return cleaned_content, True

def process_file(filepath: str, inplace: bool = True, output_path: str = None) -> bool:
    """Processes a single KML file."""
    filepath = os.path.abspath(os.path.expanduser(filepath))
    
    if not os.path.exists(filepath):
        print(f"❌ Error: File not found: {filepath}")
        return False
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading {filepath}: {e}")
        return False

    cleaned_content, route_found = strip_route_folder(content)

    if not route_found:
        print(f"ℹ️  No 'Route' folder found in {os.path.basename(filepath)} (already cleaned or unsupported format).")
        return False

    if output_path:
        target_path = os.path.abspath(os.path.expanduser(output_path))
    elif inplace:
        target_path = filepath
    else:
        name, ext = os.path.splitext(filepath)
        target_path = f"{name}_trail_only{ext}"

    try:
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
    except Exception as e:
        print(f"❌ Error writing to {target_path}: {e}")
        return False

    orig_size_kb = len(content) / 1024
    new_size_kb = len(cleaned_content) / 1024
    saved_kb = orig_size_kb - new_size_kb

    print(f"✅ Cleaned: {os.path.basename(filepath)}")
    print(f"   Size: {orig_size_kb:.1f} KB ➡️  {new_size_kb:.1f} KB (Saved {saved_kb:.1f} KB / {((saved_kb/orig_size_kb)*100):.1f}%)")
    print(f"   Output: {target_path}\n")
    return True

def main():
    parser = argparse.ArgumentParser(
        description="Strip the high-density 'Route' point folder from Flightradar24 KML files to optimize Google Earth performance.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        'files', 
        nargs='*', 
        help="One or more KML file paths or glob patterns (e.g. ~/Downloads/*.kml)"
    )
    parser.add_argument(
        '--no-inplace', 
        action='store_true', 
        help="Create a '_trail_only.kml' file instead of overwriting original files"
    )
    parser.add_argument(
        '-o', '--output', 
        type=str, 
        help="Specific output filename (only applies when processing a single file)"
    )

    args = parser.parse_args()

    if not args.files:
        # Default behavior if run in Downloads folder without args: look for .kml files
        print("No files specified. Searching for .kml files in current working directory...")
        kml_files = glob.glob("*.kml")
        if not kml_files:
            parser.print_help()
            sys.exit(1)
        args.files = kml_files

    # Expand glob patterns
    expanded_files = []
    for pattern in args.files:
        matches = glob.glob(os.path.expanduser(pattern))
        if matches:
            expanded_files.extend(matches)
        elif os.path.exists(pattern):
            expanded_files.append(pattern)
        else:
            print(f"⚠️ Warning: Pattern/file not matched: {pattern}")

    if not expanded_files:
        print("No valid KML files found to process.")
        sys.exit(1)

    inplace = not args.no_inplace

    if args.output and len(expanded_files) > 1:
        print("❌ Error: -o / --output can only be used when processing a single file.")
        sys.exit(1)

    print(f"🚀 Processing {len(expanded_files)} file(s)...\n")
    cleaned_count = 0
    for f in expanded_files:
        if process_file(f, inplace=inplace, output_path=args.output if len(expanded_files) == 1 else None):
            cleaned_count += 1

    print(f"🎉 Done! Cleaned {cleaned_count} of {len(expanded_files)} file(s).")

if __name__ == '__main__':
    main()
