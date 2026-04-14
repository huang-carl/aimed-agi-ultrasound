# Installation Instructions for Aimed AGI Ultrasound

## System Requirements
- **Operating System**: Windows 10/11, macOS 10.15 or higher, or Linux (Ubuntu 20.04 or higher)
- **Processor**: 64-bit processor, 2.0 GHz or faster
- **RAM**: Minimum 8 GB, Recommended 16 GB or more
- **Disk Space**: At least 500 MB free

## Dependencies
- **Python**: Version 3.7 or later
- **Pip**: Python package manager (usually included with Python)
- **Git**: Version control tool to clone the repository
- [Optional] Virtual Environment: For isolating project dependencies (recommended)

## Step-by-Step Installation Guide

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/huang-carl/aimed-agi-ultrasound.git
   cd aimed-agi-ultrasound
   ```

2. **Set Up a Virtual Environment (Optional but Recommended)**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configuration**:
   - Copy the example configuration file:
   ```bash
   cp config.example.json config.json
   ```
   - Edit `config.json` to suit your setup.

5. **Run the Application**:
   ```bash
   python main.py
   ```

## Troubleshooting
- **Command Not Found Error**: Ensure that Python and Pip are installed and added to your system's PATH.
- **Permission Denied**: If you encounter permission issues, try running the command with `sudo` (on Linux/Mac) or as an Administrator on Windows.
- **Module Not Found Error**: Double-check that you have installed all required dependencies listed in `requirements.txt`.

If issues persist, please check the [issues section](https://github.com/huang-carl/aimed-agi-ultrasound/issues) on GitHub for known issues or to report a new one.

---

*Instructions generated on 2026-04-14 23:25:41 UTC*