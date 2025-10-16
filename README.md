# ARW to Ultra HDR Converter

This is a Python CLI tool to convert Sony ARW raw files to Google's Ultra HDR format.

## Prerequisites

- Python 3.8+
- Git
- CMake
- A C/C++ compiler toolchain (like GCC or Clang)

## Installation

1.  **Clone the repository with submodules:**
    ```bash
    git clone --recurse-submodules https://github.com/your-repo/arw-to-ultrahdr.git
    cd arw-to-ultrahdr
    ```

2.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Build `libultrahdr`:**
    This tool depends on Google's `libultrahdr`. You need to build the `ultrahdr_app` executable.
    ```bash
    mkdir -p libultrahdr/build
    cd libultrahdr/build
    cmake .. -DUHDR_BUILD_DEPS=1
    make
    cd ../..
    ```
    After this step, you should have an executable at `libultrahdr/build/ultrahdr_app`.

## Usage

To convert an ARW file, run the script with the input and output file paths.

```bash
python arw_to_ultrahdr.py [INPUT_ARW_FILE] [OUTPUT_HIF_FILE]
```

**Example:**
```bash
python arw_to_ultrahdr.py DSC07340.ARW my_ultrahdr_image.hif
```

### Options

- `--keep-intermediates`: Use this flag to keep the intermediate SDR (.jpg) and HDR (.tiff, .raw) files that are generated during the conversion process. By default, they are deleted.

**Example with option:**
```bash
python arw_to_ultrahdr.py DSC07340.ARW my_ultrahdr_image.hif --keep-intermediates
```