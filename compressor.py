import os
import io
import subprocess
import json

def get_video_info(file_path):
    cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', file_path]
    probe_output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    probe_output = probe_output.decode('utf-8')
    probe = json.loads(probe_output)
    video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
    duration = float(video_stream['duration'])
    bitrate = int(video_stream['bit_rate'])
    width = int(video_stream['width'])
    height = int(video_stream['height'])
    
    return duration, bitrate, width, height

def compress_video(file_path_io, file_path, compressed_file_path, target_size):
    min_audio_bitrate = 32000
    max_audio_bitrate = 256000

    file_path_io = io.BytesIO(file_path_io.read())

    cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', file_path]
    probe_output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    probe_output = probe_output.decode('utf-8')
    probe = json.loads(probe_output)

   # duration = float(probe['format']['duration'])
    duration = float(probe['streams'][0]['duration'])

    audio_bitrate = float(next((s for s in probe['streams'] if s['codec_type'] == 'audio'), None)['bit_rate'])

    target_total_bitrate = (target_size * 1024 * 8) / (1.073741824 * duration)

    if 10 * audio_bitrate > target_total_bitrate:
        audio_bitrate = target_total_bitrate / 10
        if audio_bitrate < min_audio_bitrate < target_total_bitrate:
            audio_bitrate = min_audio_bitrate
        elif audio_bitrate > max_audio_bitrate:
            audio_bitrate = max_audio_bitrate

    video_bitrate = target_total_bitrate - audio_bitrate

    cmd_pass1 = ['ffmpeg', '-y', '-i', file_path, '-c:v', 'h264_nvenc', '-b:v', f'{video_bitrate}k', '-pass', '1', '-f', 'mp4', '/dev/null']
   # subprocess.run(cmd_pass1, input=file_path_io.read(), check=True)
    subprocess.run(cmd_pass1, check=True)

    file_path_io.seek(0)

    cmd_pass2 = ['ffmpeg', '-y', '-i', file_path, '-c:v', 'h264_nvenc', '-b:v', f'{video_bitrate}k', '-pass', '2', '-c:a', 'aac', '-b:a', f'{audio_bitrate}k', compressed_file_path]
   # subprocess.run(cmd_pass2, input=file_path_io.read(), check=True)
    subprocess.run(cmd_pass2, check=True)

    file_path_io.seek(0)
    compressed_duration, compressed_bitrate, compressed_width, compressed_height = get_video_info(file_path)

    return compressed_duration, compressed_bitrate, compressed_width, compressed_height