#!/usr/bin/env python3
"""
Dalvik Opcode Explorer - Fetches and displays Dalvik opcode information
Usage: ./dexplain.py --name "const/16"
"""

import argparse
import re
import sys
from typing import Optional, Dict, List
import requests
from bs4 import BeautifulSoup

class DalvikOpcodeExplorer:
    def __init__(self, url: str = "http://pallergabor.uw.hu/androidblog/dalvik_opcodes.html"):
        self.url = url
        self.opcodes: Dict[str, Dict] = {}
        self.fetch_opcodes()
    
    def fetch_opcodes(self) -> None:
        """Fetch and parse the Dalvik opcodes from the webpage"""
        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()
            
            # Parse the HTML table
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table')
            
            if not table:
                print("Error: Could not find opcode table on the page")
                sys.exit(1)
            
            # Parse table rows (skip header row)
            rows = table.find_all('tr')[1:]
            
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 3:
                    opcode_hex = cols[0].get_text().strip()
                    opcode_name = cols[1].get_text().strip()
                    explanation = cols[2].get_text().strip() if len(cols) > 2 else ""
                    example = cols[3].get_text().strip() if len(cols) > 3 else ""
                    
                    # Extract just the base opcode name (without parameters)
                    # e.g., "const/16 vx,lit16" -> "const/16"
                    base_name = opcode_name.split()[0] if opcode_name else ""
                    
                    # Store by base name (case-insensitive)
                    if base_name:
                        name_lower = base_name.lower()
                        self.opcodes[name_lower] = {
                            'hex': opcode_hex,
                            'name': base_name,
                            'full_name': opcode_name,
                            'explanation': explanation,
                            'example': example
                        }
                    
                    # Also store by hex if needed
                    if opcode_hex:
                        self.opcodes[f"hex:{opcode_hex}"] = self.opcodes.get(name_lower, {})
                        
        except requests.RequestException as e:
            print(f"Error fetching opcodes from {self.url}: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Error parsing opcodes: {e}")
            sys.exit(1)
    
    def find_opcode(self, search_term: str) -> Optional[Dict]:
        """Find opcode by exact base name or hex code"""
        search_lower = search_term.lower().strip()
        
        # Check if it's a hex search
        if search_lower.startswith('hex:'):
            hex_key = search_lower
            if hex_key in self.opcodes:
                return self.opcodes[hex_key]
            return None
        
        # Try exact match first (most important for your use case)
        if search_lower in self.opcodes:
            return self.opcodes[search_lower]
        
        # If no exact match, look for partial matches but warn the user
        matches = []
        for name, data in self.opcodes.items():
            if not name.startswith('hex:') and search_lower in name:
                matches.append(data)
        
        if matches:
            print(f"\nNo exact match for '{search_term}'. Did you mean one of these?")
            for match in matches:
                print(f"  - {match['name']}")
            print("\nPlease use the exact opcode name (e.g., 'const/16', not 'const/16 vx,lit16')")
            return None
        
        return None
    
    def display_opcode(self, opcode_data: Dict) -> None:
        """Display opcode information in a formatted way"""
        print("\n" + "="*60)
        print(f"Opcode: {opcode_data['name']} (0x{opcode_data['hex']})")
        if opcode_data.get('full_name') and opcode_data['full_name'] != opcode_data['name']:
            print(f"Full syntax: {opcode_data['full_name']}")
        print("="*60)
        
        if opcode_data['explanation']:
            print(f"\n Explanation:")
            print(f"  {opcode_data['explanation']}")
        else:
            print("\n Explanation: Not available")
        
        if opcode_data['example']:
            print(f"\n Example:")
            # Clean up the example formatting
            example_lines = opcode_data['example'].split('\n')
            for line in example_lines:
                if line.strip():
                    print(f"  {line.strip()}")
        else:
            print(f"\n Example: Not available")
        print()

def main():
    parser = argparse.ArgumentParser(
        description='Dexplorer - Dalvik Opcode Explorer - Look up Dalvik opcode information',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  %(prog)s --name "const/16"        # Search by exact opcode name
  %(prog)s -n "move-object"          # Search with short option
  %(prog)s --hex "0A"                 # Search by hex value
  %(prog)s --name "const" --verbose   # Show additional info

NOTE: Use exact opcode names as they appear in the table:
  ✓ "const/4", "const/16", "move-object", "new-array"
  ✗ "const/4 vx,lit4", "move-object vx,vy"
        """
    )
    
    # Create mutually exclusive group for search methods
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-n', '--name', 
                       help='Search by exact opcode name (e.g., "const/16")')
    group.add_argument('--hex', 
                       help='Search by opcode hex value (e.g., "0A", "1F")')
    
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Show additional information')
    
    args = parser.parse_args()
    
    # Initialize explorer
    explorer = DalvikOpcodeExplorer()
    
    # Determine search term
    if args.name:
        search_term = args.name
    elif args.hex:
        # Normalize hex input
        hex_val = args.hex.lower().replace('0x', '').strip().zfill(2)
        search_term = f"hex:{hex_val}"
    
    # Find and display opcode
    opcode = explorer.find_opcode(search_term)
    
    if opcode:
        explorer.display_opcode(opcode)
        
        if args.verbose:
            print("\n Additional Information:")
            print(f"  Source: {explorer.url}")
            print("  • Vx values denote Dalvik registers")
            print("  • Boolean values: 1 = true, 0 = false")
            print("  • Long/double values use two registers (vx, vx+1)")
            print("  • Examples are in big-endian format")
    else:
        if not args.hex:
            print(f"\n No opcode found matching '{args.name}'")
            print("\n Try these common opcodes:")
            common_opcodes = [
                "const/4", "const/16", "const-string",
                "move-object", "move-result",
                "new-instance", "new-array",
                "goto", "if-eq", "return-void"
            ]
            for op in common_opcodes[:5]:
                print(f"  • {op}")
            print("\nOr use --hex to search by hex value")

if __name__ == "__main__":
    main()