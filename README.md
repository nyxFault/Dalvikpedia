[![Python](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Dalvikpedia** is a lightweight command-line tool that fetches and displays Dalvik opcode information from Paller Gabor's Dalvik opcodes [webpage](http://pallergabor.uw.hu/androidblog/dalvik_opcodes.html).

---

### Prerequisites

- Python 3.6 or higher
- pip (Python package manager)

### Quick Install

```bash
# Clone the repository
git clone https://github.com/nyxFault/Dalvikpedia.git
cd dalvikpedia

# Install dependencies
pip install requests beautifulsoup4
```

Or, if you prefer using a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install requests beautifulsoup4
```
### Usage

```bash
# Get help
chmod +x dalvikpedia.py
./dalvikpedia.py --help

# Search by opcode name
./dalvikpedia.py --name "const/16"
./dalvikpedia.py -n "move-object"

# Search by hex value
./dalvikpedia.py --hex "0A"
./dalvikpedia.py --hex "1F"

# Show additional information
./dalvikpedia.py --name "const/4" --verbose

```




Made with ❤️ for the Android reverse engineering community
