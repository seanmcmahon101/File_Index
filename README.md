# File Search Tool

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Introduction

**File Search Tool** is a lightweight, efficient file indexing and search application for Windows. Inspired by the functionality of 'Everything,' this tool allows users to rapidly search for files on their `C:` drive, view detailed results, and open containing folders directly from the interface. Built with Python 3.12 and Tkinter, it offers a seamless and responsive user experience without relying on external dependencies.

## Features

- **Persistent Indexing:** Indexes files on the `C:` drive and maintains a persistent SQLite database to prevent redundant indexing on each run.
- **Incremental Updates:** Detects and updates only new or modified files, ensuring quick refreshes and minimal processing time.
- **Real-Time Search:** Provides instantaneous search results as you type, leveraging efficient SQL queries.
- **User-Friendly GUI:** Intuitive interface built with Tkinter, featuring a search bar, results list, and status indicators.
- **Open Containing Folder:** Easily navigate to the file's location in Windows Explorer with a double-click.
- **Manual Refresh:** Option to manually trigger a full or incremental reindexing process.
- **Customizable Skips:** Configure directories to exclude from indexing to optimize performance and relevance.

## Installation

### Prerequisites

- **Operating System:** Windows 10 or later
- **Python Version:** Python 3.12

### Steps

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/file-search-tool.git
   cd file-search-tool
   ```

2. **Create a Virtual Environment (Optional but Recommended)**

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install Dependencies**

   The tool primarily uses Python's standard libraries. However, ensure that Tkinter is installed.

   ```bash
   pip install --upgrade pip
   ```

   *Note: Tkinter is included with standard Python installations on Windows. If it's missing, you may need to reinstall Python and ensure that the Tkinter option is selected.*

4. **Run the Application**

   ```bash
   python enhanced_file_search_tool.py
   ```

## Usage

1. **Initial Run:**
   - On the first execution, the tool will start indexing all files on the `C:` drive.
   - Progress updates are displayed in the status bar at the bottom.
   - Depending on the number of files, initial indexing may take several minutes.

2. **Searching for Files:**
   - Enter your search query in the search bar at the top.
   - Results matching the query will appear in real-time below.
   - Each result displays the filename and its full path.

3. **Opening Files:**
   - Double-click on any search result to open the containing folder in Windows Explorer.
   - The specific file will be highlighted for easy access.

4. **Refreshing the Index:**
   - Click the "Refresh Index" button to update the index with any new, modified, or deleted files.
   - A confirmation prompt will appear to prevent accidental refreshes.
   - The status bar will display progress during the refresh process.

## Configuration

### Skipping Directories

To optimize indexing performance and relevance, certain directories can be excluded from the scan. By default, the tool skips:

- `C:\$Recycle.Bin`
- `C:\System Volume Information`

#### How to Modify Skipped Directories:

1. Open the `enhanced_file_search_tool.py` script in a text editor.
2. Locate the `skip_dirs` list within the `index_files` function.
3. Add or remove directory paths as needed. Ensure paths are absolute and properly escaped.

   ```python
   skip_dirs = [
       'C:\\$Recycle.Bin',
       'C:\\System Volume Information',
       # Add more directories to skip here
   ]
   ```

### Changing the Root Directory

If you wish to index a different drive or specific directory:

1. Open the `enhanced_file_search_tool.py` script.
2. Locate the `os.walk('C:\\', topdown=True)` line.
3. Replace `'C:\\'` with your desired root path.

   ```python
   for root, dirs, files in os.walk('D:\\YourDirectory', topdown=True):
       # Rest of the code
   ```

## Contributing

Contributions are welcome! Whether it's reporting bugs, suggesting features, or submitting pull requests, your input is valuable.

### Steps to Contribute

1. **Fork the Repository**

   Click the "Fork" button at the top-right corner of the repository page.

2. **Clone Your Fork**

   ```bash
   git clone https://github.com/yourusername/file-search-tool.git
   cd file-search-tool
   ```

3. **Create a New Branch**

   ```bash
   git checkout -b feature/YourFeatureName
   ```

4. **Make Your Changes**

   Implement your feature or fix.

5. **Commit Your Changes**

   ```bash
   git commit -m "Add feature: YourFeatureName"
   ```

6. **Push to Your Fork**

   ```bash
   git push origin feature/YourFeatureName
   ```

7. **Create a Pull Request**

   Navigate to the original repository and click "Compare & pull request."

## License

This project is licensed under the [MIT License](LICENSE). You are free to use, modify, and distribute this software as per the terms of the license.

## Acknowledgements

- [Tkinter Documentation](https://docs.python.org/3/library/tkinter.html) for providing the GUI framework.
- The inspiration from the [Everything](https://www.voidtools.com/) search tool for its efficient search capabilities.
- The Python community for continuous support and extensive documentation.

---


