# Image to ICO Converter

A desktop application for converting images to ICO files, built with Python and
Tkinter.

## Features

- Select one or more PNG, JPG, or JPEG images at once.
- Choose a custom output directory for the generated ICO files.
- Preserve the original aspect ratio and center the image on a transparent
  background.
- Generate six sizes in each ICO file: 16, 32, 48, 64, 128, and 256 pixels.
- Read and correct image orientation using EXIF metadata.
- Never overwrite existing files. For example, if `01.ico` already exists, the
  application creates `01 (1).ico`, followed by `01 (2).ico`.
- Run conversions in the background while displaying progress and results.

## Requirements

- Python 3.9 or later
- Windows, macOS, or Linux with Tkinter installed

## Installation and Usage

Creating a virtual environment is recommended:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the required dependency:

```powershell
py -m pip install -r requirements.txt
```

Start the application:

```powershell
py convert_to_ico.py
```

Select the images and output directory, then click **Convert to ICO**.

## Building a Windows EXE

The application can be packaged as a standalone executable with PyInstaller.
See the
[official PyInstaller documentation](https://pyinstaller.org/en/stable/usage.html)
for additional build options.

Install PyInstaller:

```powershell
py -m pip install pyinstaller
```

Run the following command from the project root:

```powershell
pyinstaller --noconfirm --clean --onefile --windowed --name ImageToICO convert_to_ico.py
```

Build options:

- `--onefile`: Package the application as a single executable.
- `--windowed`: Do not open a command-line window when the application starts.
- `--name ImageToICO`: Name the executable `ImageToICO.exe`.
- `--clean`: Clear the PyInstaller cache before building.

The resulting executable will be located at:

```text
dist\ImageToICO.exe
```

The `build` directory and `ImageToICO.spec` file are intermediate build
artifacts. They can be safely deleted when no custom PyInstaller configuration
is required. Running the build command again will recreate them.

To use a custom executable icon, prepare an ICO file and add the `--icon`
option:

```powershell
pyinstaller --noconfirm --clean --onefile --windowed --name ImageToICO --icon app.ico convert_to_ico.py
```

Build and test the executable on the target version of Windows. PyInstaller is
not a cross-compiler, so a Windows executable cannot be built directly on macOS
or Linux.

## Project Structure

```text
convert_to_ico.py  Application entry point
converter_gui.py   Tkinter graphical user interface
ico_converter.py   Image conversion and automatic naming logic
requirements.txt   Runtime dependencies
```

## License

This project is licensed under the [MIT License](LICENSE).
