import stable_whisper
from moviepy import *
from moviepy.editor import *
from datetime import datetime
from dataclasses import dataclass
import re


# TODO: Text styling arguments (size, position, color)
# TODO: Text animations
# TODO: Editing certain words?? (auto emojis to certain words??)
# TODO: Making a flask endpoint st uploading to a site allows users to edit on a website
# TODO: Dockerize??


@dataclass
class VidSegment:
    sen: str
    start_time: None = None
    end_time: None = None


@dataclass
class WordObj:
    word: str
    start_time: None = None
    end_time: None = None


VIDEO_FILE_NAME = 'test2.mov'
OUTPUT_FILE_NAME = VIDEO_FILE_NAME.split('.')[0] + '_output.mp4'


def main():
    model = stable_whisper.load_model('base')
    result = model.transcribe(VIDEO_FILE_NAME)
    lines = result.to_srt_vtt('', vtt=True).split('\n')

    raw_cleaned_words = []
    raw_segments = []
    segment_list = []

    # Clean lines
    for i, line in enumerate(lines):
        if line == '':
            segment = [lines[i+1], lines[i+2]]
            raw_segments.append(segment)

    # Parse Segments
    p = re.compile('<(\d+:\d+:\d+\.\d+)>([^<]+)')
    for segment in raw_segments:
        first_word = ''
        if segment[1][0] != '<':
            first_word = segment[1].split('<')[0]

        # Parse text
        word = segment[1]
        word_tuples = p.findall(word)
        cleaned_line = ''.join([word_tuple[1] for word_tuple in word_tuples])
        cleaned_line = first_word + cleaned_line

        # Create full text
        raw_cleaned_words.append(segment[1])

        # Parse time
        total_time = segment[0].split('-->')
        start_time = datetime.strptime(total_time[0].strip(), '%H:%M:%S.%f')
        end_time = datetime.strptime(total_time[1].strip(), '%H:%M:%S.%f')

        cur_segment = VidSegment(cleaned_line, start_time, end_time)
        segment_list.append(cur_segment)

    begin_time = datetime.strftime(segment_list[0].start_time, '<%H:%M:%S.%f>')
    end_time = segment_list[len(segment_list) - 1].end_time

    raw_cleaned_words.insert(0, begin_time)
    raw_cleaned_words = ' '.join(raw_cleaned_words)

    wordlist = []
    cleaned_words = p.findall(raw_cleaned_words)
    for i, word_tuple in enumerate(cleaned_words):
        cur_word = ''
        start_time = datetime.strptime(word_tuple[0], '%H:%M:%S.%f')
        if i < len(cleaned_words) - 1:
            cur_word = WordObj(
                word=word_tuple[1], start_time=start_time, end_time=datetime.strptime(cleaned_words[i + 1][0], '%H:%M:%S.%f'))
        else:
            cur_word = WordObj(
                word=word_tuple[1], start_time=start_time, end_time=end_time)
        wordlist.append(cur_word)

    insert_vid_text(wordlist)
    return


def insert_vid_text(wordlist):
    video_clips = []
    full_duration = VideoFileClip(VIDEO_FILE_NAME).duration
    end_time = ''
    for e in wordlist:
        start_time = float(datetime.strftime(e.start_time, '%S.%f'))
        end_time = float(datetime.strftime(e.end_time, '%S.%f'))
        duration = end_time - start_time

        video = VideoFileClip(VIDEO_FILE_NAME).subclip(start_time, end_time)

        text = (TextClip(e.word, fontsize=70, color='white')
                .set_position('center')
                .set_duration(duration))

        cur_clip = CompositeVideoClip([video, text])
        video_clips.append(cur_clip)
    end_clip = VideoFileClip(VIDEO_FILE_NAME).subclip(end_time, full_duration)
    video_clips.append(end_clip)

    final = concatenate_videoclips(video_clips)
    final.write_videofile(OUTPUT_FILE_NAME)


if __name__ == '__main__':
    main()
