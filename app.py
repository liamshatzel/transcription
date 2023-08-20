from flask import Flask, render_template, request
import stable_whisper
from moviepy import *
from moviepy.editor import *
from datetime import datetime
from dataclasses import dataclass

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/handle_upload", methods=['POST'])
def handle_upload():
    uploaded_file = request.files.get('fileToUpload').read()
    if uploaded_file:
        _transcribe(uploaded_file)
    return render_template("index.html")


def _transcribe(uploaded_file):
    model = stable_whisper.load_model('base')
    result = model.transcribe(uploaded_file)
    lines = result.to_srt_vtt()
    print(lines)
    clean_lines = []
    for line in lines:
        if line != '\n':
            clean_lines.append(line.strip())

    clean_lines = clean_lines[1:]

    total_time = clean_lines[0]
    total_time = total_time.split('-->')

    start_time = datetime.strptime(total_time[0].strip(), '%H:%M:%S.%f')
    end_time = datetime.strptime(total_time[1].strip(), '%H:%M:%S.%f')

    total_time = end_time

    tokens = clean_lines[1].split()

    times = []
    for word in tokens:
        word_stamp = word.split('<')
        cur_word = word_stamp[0]
        timestamp = None
        prev_time = None

        if len(word_stamp) > 1:
            timestamp = word_stamp[1]
            timestamp = timestamp.strip('>')
            timestamp = datetime.strptime(timestamp, '%H:%M:%S.%f')
        else:
            timestamp = end_time

        if len(times) >= 1:
            prev_time = times[len(times) - 1].time
        else:
            prev_time = start_time
        times.append(VidSegment(cur_word, timestamp, prev_time))

    video_clips = []
    for e in times:
        cur_time = float(datetime.strftime(e.time, '%S.%f'))
        prev_time = float(datetime.strftime(e.prev_time, '%S.%f'))
        duration = cur_time - prev_time
        video = VideoFileClip(uploaded_file).subclip(prev_time, cur_time)
        text = (TextClip(e.word, fontsize=70, color='white')
                .set_position('center')
                .set_duration(duration))
        cur_clip = CompositeVideoClip([video, text])
        video_clips.append(cur_clip)

    final = concatenate_videoclips(video_clips)
    final.write_videofile('captioned.mp4')
