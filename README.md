# X9-Fuzzer


## Overview

X9-Fuzzer is a powerful and flexible URL fuzzing tool for bug bounty hunters and security researchers. It enables efficient parameter fuzzing with various strategies to help discover potential vulnerabilities in web applications.

## Features

- **Multiple Fuzzing Strategies**: Support for normal, combine, ignore, and all-in-one fuzzing approaches
- **Flexible Value Handling**: Replace or append values to existing parameters
- **Efficient Processing**: Chunk processing to handle large parameter sets
- **Input Flexibility**: Accept single URLs or lists from files
- **Robust Error Handling**: Comprehensive validation and error reporting
- **Performance Optimized**: Generator-based processing for memory efficiency

## Installation

```bash
# Clone the repository
git clone https://github.com/AliHz1337/x9-fuzzer.git

# Navigate to the directory
cd x9-fuzzer

# Make the script executable
chmod +x main.py
```

## Usage

```
usage: main.py [-h] (-u URL | -l URL_LIST) -gs {all,combine,normal,ignore}
             [-vs {replace,suffix}] (-v VALUES_INLINE [VALUES_INLINE ...] | -vf VALUES_FILE)
             [-p PARAMETERS] [-c CHUNK] [-o [OUTPUT]] [-s]
```

### Arguments

| Argument | Description |
|----------|-------------|
| `-u, --url` | Single URL to fuzz |
| `-l, --url_list` | File containing multiple URLs |
| `-gs, --generate_strategy` | Fuzzing strategy: all, combine, normal, or ignore |
| `-vs, --value_strategy` | Value handling: replace or suffix (required for 'all' and 'combine') |
| `-v, --values_inline` | Specify values directly in command line |
| `-vf, --values_file` | File containing values to use |
| `-p, --parameters` | File with parameters (required for 'ignore', 'normal', and 'all') |
| `-c, --chunk` | Number of parameters per URL (default: 25) |
| `-o, --output` | File to save generated URLs (default: x9-generated-link.txt) |
| `-s, --silent` | Suppress banner display |

## Fuzzing Strategies

### 1. Normal Strategy
Adds specified parameters with values to the URL, regardless of existing parameters.

```bash
python3 main.py -u "https://example.com" -gs normal -v test -p parameters.txt
```

### 2. Combine Strategy
Modifies existing parameters in the URL with the provided values.

```bash
python3 main.py -u "https://example.com?param=value" -gs combine -vs replace -v test
```

### 3. Ignore Strategy
Adds specified parameters only if they don't already exist in the URL.

```bash
python3 main.py -u "https://example.com?param=value" -gs ignore -v test -p parameters.txt
```

### 4. All Strategy
Combines all three strategies above for comprehensive fuzzing.

```bash
python3 main.py -u "https://example.com?param=value" -gs all -vs suffix -v test -p parameters.txt
```

## Examples

### Basic Usage
```bash
# Fuzz a single URL with inline values
python3 main.py -u "https://example.com" -gs normal -v payload1 payload2 -p params.txt

# Fuzz multiple URLs from a file
python3 main.py -l urls.txt -gs combine -vs replace -v xss -o results.txt
```

### Advanced Usage
```bash
# Combine multiple strategies with various payloads
python3 main.py -l urls.txt -gs all -vs suffix -vf payloads.txt -p params.txt -c 50

# Silent mode with output to file
python3 main.py -u "https://example.com" -gs normal -vf payloads.txt -p params.txt -s -o
```

## Pipeline Integration
X9-Fuzzer supports piping outputs to other tools:

```bash
python3 main.py -l urls.txt -gs normal -v xss -p params.txt | httpx -silent | nuclei -t xss.yaml
```

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

If you find X9-Fuzzer useful, please consider giving it a star on GitHub!