import os
import shutil
import subprocess

sep = "/"
if os.name == "nt":
    sep = "\\"


def path(string):
    if sep == "\\":
        return string.replace("/", "\\")
    return string


def run_command(command, mode="silent"):
    if mode == "debug":
        return os.system(command)
    return os.popen(command).read()


def detect_fps(input_path):
    input_path = path(input_path)
    output = os.popen(f'ffprobe -v error -select_streams v -of default=noprint_wrappers=1:nokey=1 -show_entries stream=r_frame_rate "{input_path}"').read()
    if "/" in output:
        try:
            return int(output.split("/")[0]) // int(output.split("/")[1].strip()), output.strip()
        except:
            pass
    return 30, 30


from pathlib import Path


def set_fps(input_path, output_path, fps):
    input_path = Path(input_path)
    output_path = Path(output_path)
    os.system(f'ffmpeg -i "{input_path}" -filter:v fps={fps} "{output_path}" -loglevel error')

import os
from pathlib import Path
import subprocess

def create_video(video_name, fps, output_dir):
    output_dir = Path(output_dir)
    output_path = output_dir / "output.mp4"
    input_pattern = str(output_dir / "%04d.png")
    
    # Set target video bitrate (in kilobits per second)
    target_bitrate = 8000  # Adjust this value to control the compression level
    
    # Calculate the target video bitrate based on the desired file size
    max_file_size = 100  # Maximum file size in megabytes
    target_bitrate = (max_file_size * 8192) // (fps * 1000)
    
    # Run FFmpeg command
    cmd = [
        'ffmpeg',
        '-framerate', str(fps),
        '-i', input_pattern,
        '-c:v', 'libx264',
        '-b:v', f'{target_bitrate}k',
        '-crf', '23',  # Constant Rate Factor for quality (adjust as needed)
        '-pix_fmt', 'yuv420p',
        '-y', str(output_path),
        '-loglevel', 'error'
    ]
    subprocess.run(cmd)

    print(f"Video saved to {output_path}")

def extract_frames(input_path, output_dir):
    input_path, output_dir = path(input_path), path(output_dir)
    os.system(f'ffmpeg -i "{input_path}" "{output_dir}{sep}%04d.png" -loglevel error')

def verify_audio(video):
    result = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries', 'stream=codec_type', '-of', 'default=noprint_wrappers=1:nokey=1', video], capture_output=True, text=True)
    return result.stdout.strip() == 'audio'

def add_audio(output_dir, target_path, keep_frames, output_file):
    video_name = "output"
    video = video_name
    save_to = output_file if output_file else output_dir + "/swapped-" + video_name + ".mp4"
    save_to_ff, output_dir_ff = path(save_to), path(output_dir)
    os.system(f'ffmpeg -i "{output_dir_ff}{sep}output.mp4" -i "{output_dir_ff}{sep}{video}" -c:v copy -map 0:v:0 -map 1:a:0 -y "{save_to_ff}" -loglevel error')
    if not os.path.isfile(save_to):
        shutil.move(output_dir + "/output.mp4", save_to)
    if not keep_frames:
        shutil.rmtree(output_dir)


def is_img(path):
    return path.lower().endswith(("png", "jpg", "jpeg", "bmp"))


def rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)
