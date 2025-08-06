# 📁 Creation Date File Sorter

[![CI/CD Status](https://github.com/anixdorf/creation-date-file-sorter/actions/workflows/run-tests.yml/badge.svg)](https://github.com/anixdorf/creation-date-file-sorter/actions)
[![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)

> 🗂️ **Automatically organize your files into date-based directory structures using intelligent creation date detection**

A powerful Python utility that analyzes file creation dates from multiple sources and organizes files into a clean `YYYY/MM/` directory structure. Perfect for organizing photo collections, document archives, or any time-sensitive file organization tasks.

## ✨ Features

- 🔍 **Multi-Source Date Detection**: Extracts creation dates from a range of included providers.
- 📅 **Smart Date Parsing**: Utilizes a multi-strategy approach with regex and flexible parsing to support numerous date formats.
- 🔄 **Two-Stage Process**: Generate copy lists first, then execute with full control.
- 🔒 **Duplicate Detection**: High-performance BLAKE2b hashing prevents duplicate files.
- ⚡ **Resume Capability**: Skip already processed files on restart.
- 📊 **Progress Tracking**: Visual progress bars and comprehensive logging.
- 🛡️ **Safe Operations**: Creates directory structure without modifying source files.

## 🏗️ Architecture

```
 Source Files   ───▶  🔍 Date Extraction     ───▶  Organized Files 
                       📋 Copy List & Copy           
 📁 Photos/                                         📁 2025/01/     
 📁 Documents/                                      📁 2026/02/     
 📁 Downloads/                                      📁 2027/01/     

```

### 📦 Core Components

- **🎯 Date Providers**: Multiple strategies for extracting creation dates, executed in order of priority:
  - **Filename Provider**: Parses dates directly from filenames.
  - **Hachoir Provider**: Extracts embedded metadata from a wide range of file types (images, videos, etc.).
  - **Windows Shell Provider**: Reads metadata from file properties on Windows.
- **📋 Copy List Generator**: Creates detailed mapping files for review.
- **📁 File Organizer**: Executes the actual file copying with safety checks.

## 🚀 Quick Start

### Prerequisites

- 🐍 Python 3.6 or higher
- 🪟 Windows OS (for full functionality)
- 📦 Required packages (see installation)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/creation-date-file-sorter.git
   cd creation-date-file-sorter
   ```

2. **Install `uv` (Recommended)**  
   This project uses `uv` for high-performance package management.
   ```bash
   # Install uv on macOS / Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Install uv on Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

3. **Install dependencies**
   ```bash
   # Install production dependencies
   uv pip install -r requirements.txt

   # For development, install development tools as well
   uv pip install -r requirements-dev.txt
   ```

### Basic Usage

#### Step 1: 📋 Generate Copy List
```bash
python create_copy_list.py --source "C:\Photos" --destination "D:\Organized"
```

#### Step 2: 🗂️ Execute File Organization
```bash
python copy_files.py --copy-list copy-list-{hash}.csv
```

## 📖 Detailed Usage

### 🔧 Advanced Options

#### Multiple Source Directories
```bash
python create_copy_list.py --source "C:\Photos" "C:\Documents" "C:\Downloads" --destination "D:\Organized"
```

#### Custom Copy List
```bash
python copy_files.py --copy-list my-custom-list.csv
```

### 📊 Copy List Format
The generated CSV file (`copy-list-{hash}.csv`) acts as a "dry run" plan, detailing every file operation. You can review or even modify this file before running `copy_files.py`.

The file is semicolon-delimited and has the following columns:

| Column          | Description                                                    | Example                                                    |
|-----------------|----------------------------------------------------------------|------------------------------------------------------------|
| `source`        | The full, absolute path to the original source file.           | `C:\Photos\IMG_20260615.jpg`                               |
| `date`          | The creation date and time that was successfully extracted.    | `2026-06-15 00:00:00`                                      |
| `provider`      | The name of the provider that successfully extracted the date. | `WindowsShellFileCreationDateProvider`                     |
| `provider_info` | Extra information from the provider (can be empty).            | `System.Photo.DateTaken`                                   |
| `destination`   | The full, absolute path where the file will be copied.         | `D:\Organized\2026\06\IMG_20260615.jpg`                    |

**Example CSV Content:**
```csv
# COPY LIST C:\Photos -> D:\Organized
source;date;provider;provider_info;destination
C:\Photos\IMG_20260615.jpg;2026-06-15 00:00:00;FilenameFileCreationDateProvider;;D:\Organized\2026\06\IMG_20260615.jpg
C:\Photos\vacation.mov;2027-07-20 10:30:00;HachoirFileCreationDateProvider;;D:\Organized\2027\07\vacation.mov
```

### 🎯 Supported Date Formats
The tool uses a powerful date parser that supports a wide variety of formats found in filenames. The highest-priority formats are matched with specific rules:

| Format                | Example                  |
|-----------------------|--------------------------|
| `YYYY-MM-DD HH:MM:SS` | `2025-06-15 10:30:00`    |
| `YYYYMMDD_HHMMSS`     | `20260615_103000`        |
| `YYYYMMDD`            | `20270615`               |
| `YYYY-MM-DD`          | `2028-06-15`             |
| `YYYY_MM_DD`          | `2025_06_15`             |
| `YYYY.MM.DD`          | `2026.06.15`             |
| `DD.MM.YYYY`          | `15.06.2027`             |

For other variations, the parser uses the flexible `python-dateutil` library to find any valid date strings within the filename.

## 🔍 How It Works

### 1. 📂 Directory Scanning
The tool recursively scans source directories to identify all files for processing.

### 2. 📅 Date Extraction
For each file, the system attempts to find the most reliable creation date by querying a series of "providers" in a specific order. The first provider to return a valid date wins.

The provider priority is:
1.  **Filename Provider**: Applies regex patterns to the filename. This is checked first because a date in the filename (e.g., `2025-01-05_vacation.jpg`) is often the most intentionally correct one.
2.  **Hachoir Provider**: If no date is found in the filename, Hachoir reads the file's internal metadata. This is highly reliable for media files (like JPEG, MP4, etc.) that contain EXIF or other metadata headers.
3.  **Windows Shell Provider**: As a final fallback on Windows, it reads basic date properties from the filesystem, such as "Date Created" or "Date Modified".

### 3. 🗂️ Organization Strategy
Files are organized into a hierarchical structure:
```
Destination/
├── 2025/
│   ├── 01/          # January 2025
│   ├── 02/          # February 2025
│   └── ...
├── 2026/
│   ├── 01/          # January 2026
│   └── ...
```

### 4. 🛡️ Safety Features
- **Duplicate Detection**: BLAKE2b hashing prevents overwriting different files with the same name.
- **Collision Handling**: Automatic renaming with `_dup_N` suffix.
- **Dry Run**: Review copy lists before execution.
- **Comprehensive Logging**: Track all operations and errors.

## ⚙️ Configuration

### 🔧 Logging
Logs are automatically generated with timestamps:
- `create_copy_list_{hash}.log`
- `copy_files.log`

### 🎛️ Customization
You can extend the tool by:
- Adding new date extraction providers.
- Modifying regex patterns for filename parsing.
- Customizing the output directory structure.

## 🐛 Troubleshooting

### Common Issues

#### ❌ "Module not found" errors
```bash
uv pip install -r requirements.txt
```

#### ❌ Windows metadata extraction fails
- Ensure you're running on Windows
- Check file permissions
- Verify `pywin32` installation

#### ❌ No dates found in filenames
- Check supported date formats
- Consider adding custom regex patterns

### 📋 Debug Mode
Enable detailed logging by modifying the logging configuration in `lib/setup_logging.py`.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Code Formatting
This project uses `black` for automated code formatting to ensure a consistent style. Before submitting a pull request, please format your code using `uv`.

Make sure you have installed the development dependencies first.
```bash
# Format all python files in the project
uv run black .
```

### Running Tests
To ensure the reliability and correctness of the date parsing logic, you can run the built-in test suite.

From the root directory of the project, run the following command:
```bash
python -m unittest discover
```
This will automatically discover and run all tests.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with Python
- Uses `tqdm` for progress visualization
- Inspired by the need for better file organization tools

## 📞 Support

If you encounter any issues or have questions:
1. Check the [Issues](../../issues) page
2. Create a new issue with detailed information
3. Include log files and error messages

---

<div align="center">

**⭐ Star this repository if you find it helpful!**

</div>
