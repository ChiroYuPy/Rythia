import os
import csv
import re
import shutil


class OsuParser:
    def __init__(self, file_path):
        self.file_path = file_path

    def extract_hit_objects(self):
        hit_objects_info = []
        hit_objects_started = False

        with open(self.file_path, 'r', encoding='utf-8') as osu_file:
            for line in osu_file:
                line = line.strip()
                if hit_objects_started:
                    if line:
                        parts = line.split(',')
                        time = int(parts[2])
                        hit_object = {'time': time}
                        hit_objects_info.append(hit_object)
                    else:
                        break
                elif line == "[HitObjects]":
                    hit_objects_started = True

        return hit_objects_info

    def write_to_csv(self, output_folder):
        hit_objects = self.extract_hit_objects()

        # Extracting desired file name without extension
        base_file_name = os.path.splitext(os.path.basename(self.file_path))[0]
        # Apply regex to extract desired part of the name
        match = re.match(r'.* - (.*) \((.*)\)\s*\[(.*)\]', base_file_name)
        if match:
            song_name = match.group(1)
            mapper = match.group(2)
            difficulty = match.group(3)
            desired_file_name = f"{song_name} [{difficulty}].csv"
        else:
            desired_file_name = f"{base_file_name}.csv"

        # Remove first 7 characters from folder name
        base_folder_name = os.path.basename(os.path.dirname(self.file_path))[7:]
        # Create output subfolder path
        output_subfolder_path = os.path.join(output_folder, base_folder_name)
        os.makedirs(output_subfolder_path, exist_ok=True)
        output_file_path = os.path.join(str(output_subfolder_path), str(desired_file_name))

        with open(output_file_path, 'w', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=['time'])
            writer.writeheader()
            for obj in hit_objects:
                writer.writerow(obj)

        # Copying audio file
        self.copy_audio_file(output_subfolder_path)

    def copy_audio_file(self, output_folder):
        audio_extensions = ['.mp3', '.ogg']
        for file_name in os.listdir(os.path.dirname(self.file_path)):
            if any(file_name.lower().endswith(ext) for ext in audio_extensions):
                audio_file_path = os.path.join(os.path.dirname(self.file_path), file_name)
                shutil.copy(audio_file_path, output_folder)
                break


# Function to process all .osu files in a folder
def process_osu_files(folder_path, output_folder):
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.osu'):
            file_path = os.path.join(folder_path, file_name)
            parser = OsuParser(file_path)
            parser.write_to_csv(output_folder)


# Example usage:
folder_path = r"C:\Users\Adrian\AppData\Local\osu!\Songs\1823153 Poppin'Party x PastelPalettes x Morfonica - Kizunairo no Ensemble"
output_folder = r"../beatmaps"

process_osu_files(folder_path, output_folder)
