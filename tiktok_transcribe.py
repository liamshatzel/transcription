import stable_whisper
from moviepy import *
from moviepy.editor import *
from datetime import datetime
from dataclasses import dataclass


#TODO: Text styling arguments (size, position, color)
#TODO: Text animations
#TODO: Editing certain words?? (auto emojis to certain words??)
#TODO: Making a flask endpoint st uploading to a site allows users to edit on a website
#TODO: Dockerize??


@dataclass
class VidSegment():
    word: str
    time: None = None
    prev_time: None = None

#model = stable_whisper.load_model('base')
#result = model.transcribe('test.mp4')
#result.to_srt_vtt('audio.vtt')


lines = []
with open('audio.vtt') as f:
    lines = f.readlines()

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
    video = VideoFileClip('test.mp4').subclip(prev_time, cur_time)
    text = (TextClip(e.word, fontsize=70, color='white')
            .set_position('center')
            .set_duration(duration))
    cur_clip = CompositeVideoClip([video, text])
    video_clips.append(cur_clip)

final = concatenate_videoclips(video_clips)
final.write_videofile('captioned.mp4')

