import os
import zipfile
import shutil
import tempfile
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox
import sys


def print_progress_bar(iteration, total, prefix='', suffix='', length=50, fill='█'):
    """Print a progress bar to the terminal."""
    percent = f"{100 * (iteration / float(total)):.1f}"
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end='\r')
    if iteration == total:
        print()  # Move to a new line when complete


def zip_directory(source_dir, output_zip):
    """Create a ZIP archive of the given directory, including the root folder."""
    parent_folder = os.path.basename(source_dir)  # Get the folder name (e.g., "Clinostat")
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, os.path.dirname(source_dir))  # Include the root folder
                zipf.write(abs_path, rel_path)


def unzip_directory(zip_file, target_dir):
    """Extract a ZIP archive to the target directory with full permissions."""
    with zipfile.ZipFile(zip_file, 'r') as zipf:
        files = zipf.namelist()
        total_files = len(files)
        for i, file in enumerate(files, start=1):
            extracted_path = zipf.extract(file, target_dir)

            # Set full permissions for extracted files and directories
            os.chmod(extracted_path, 0o777)

            print_progress_bar(i, total_files, prefix="Unzipping Progress", suffix="Complete")


def extract_version_from_zip(zip_file):
    """Extract the version number from version.txt in the ZIP file."""
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        version_file_path = None
        for name in zip_ref.namelist():
            if name.endswith("version.txt"):
                version_file_path = name
                break

        if version_file_path:
            with zip_ref.open(version_file_path) as version_file:
                return version_file.read().decode("utf-8").strip()

    return "unknown_version"


def get_backup_zip_path(current_version):
    """Generate a backup ZIP filename with the version and timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"/home/pi/Documents/backups/clinostat_backup_v{current_version}_{timestamp}.zip"


def main():
    app = QApplication([])

    if len(sys.argv) > 1:
        zip_file = sys.argv[1]
    else:
        zip_file, _ = QFileDialog.getOpenFileName(
            None,
            "Select Update File",
            "/media/pi",  # Changed default path
            "ZIP Files (*.zip)"
        )

    if not zip_file:
        QMessageBox.warning(None, "Update Cancelled", "No file selected.")
        return

    # Copy the update file to a temporary location
    temp_zip_file = tempfile.NamedTemporaryFile(delete=False)
    shutil.copy(zip_file, temp_zip_file.name)

    # Define directories
    current_dir = "/home/pi/Documents/clinostat"
    backup_dir = "/home/pi/Documents/backups"
    os.makedirs(backup_dir, exist_ok=True)

    # Extract version from the selected ZIP file
    new_version = extract_version_from_zip(temp_zip_file.name)
    if new_version == "unknown_version":
        QMessageBox.warning(None, "Update Cancelled", "Could not determine the version from the ZIP file.")
        return

    # Generate backup ZIP path
    current_version = "unknown_version"
    version_file_path = os.path.join(current_dir, "version.txt")
    if os.path.exists(version_file_path):
        with open(version_file_path, "r") as version_file:
            current_version = version_file.read().strip()

    backup_zip = get_backup_zip_path(current_version)

    try:
        # Step 1: Ask the user if they want to back up
        backup_decision = QMessageBox.question(
            None,
            "Backup Current Directory?",
            "Do you want to back up the current Clinostat directory before updating?",
            QMessageBox.Yes | QMessageBox.No
        )

        if backup_decision == QMessageBox.Yes and os.path.exists(current_dir):
            print("Backing up current directory...")
            zip_directory(current_dir, backup_zip)
            QMessageBox.information(None, "Backup Created", f"Backup saved at: {backup_zip}")
        else:
            print("Backup skipped by user.")

        # Step 2: Delete the current folder
        if os.path.exists(current_dir):
            print("Deleting old directory...")
            shutil.rmtree(current_dir)

        # Step 3: Extract the new ZIP file
        print("Extracting new update...")
        unzip_directory(temp_zip_file.name, "/home/pi/Documents")
        QMessageBox.information(None, "Update Successful", f"Updated to version {new_version} successfully.")

    except Exception as e:
        QMessageBox.critical(None, "Update Failed", f"An error occurred: {e}")

        # Restore from the backup if available
        if os.path.exists(backup_zip):
            QMessageBox.warning(None, "Restoring Backup", "Restoring the previous version...")
            unzip_directory(backup_zip, current_dir)
            QMessageBox.information(None, "Backup Restored", f"Restored from backup: {backup_zip}")

    finally:
        # Clean up the temporary file
        os.remove(temp_zip_file.name)

if __name__ == "__main__":
    main()
