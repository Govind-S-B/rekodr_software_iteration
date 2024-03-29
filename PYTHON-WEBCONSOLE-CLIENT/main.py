import requests
import os
import sys

BASE_URL = "http://localhost:8000"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_menu():
    clear_screen()
    print("Voice Database Console")
    print("----------------------")
    print("1. List all audio files")
    print("2. Retrieve audio file")
    print("3. Exit")

def list_audio_files():
    try:
        response = requests.get(f"{BASE_URL}/debug/list")
        response.raise_for_status()
        audio_files = response.json()
        for file in audio_files:
            print(f"ID: {file['id']}, Timestamp: {file['timestamp']}, Path: {file['path']}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

import re

def retrieve_audio_file():
    audio_id = input("Enter audio file ID: ")
    try:
        response = requests.get(f"{BASE_URL}/debug/audio/{audio_id}")
        response.raise_for_status()
        content_disposition = response.headers.get("Content-Disposition")
        if content_disposition:
            file_name = re.findall(r"filename=(.+)", content_disposition)[0]
        else:
            file_name = f"audio_{audio_id}.mp3"  # Fallback file name
        with open(file_name, "wb") as file:
            file.write(response.content)
        print(f"Audio file saved as {file_name}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
    except IndexError:
        print("Error: Unable to extract file name from response headers")

def main():
    while True:
        show_menu()
        choice = input("Enter your choice (1-3): ")
        if choice == "1":
            list_audio_files()
        elif choice == "2":
            retrieve_audio_file()
        elif choice == "3":
            print("Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice. Please try again.")
        input("Press Enter to continue...")

if __name__ == "__main__":
    main()