import os

import imageio
import sys

import nltk
import youtube_dl
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
from webvtt import WebVTT
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.compositing.concatenate import concatenate

# VERY IMPORTANT
# REQUIRED DOWNLOADS
nltk.download('punkt')
imageio.plugins.ffmpeg.download()


# -----------------------------------------------------------------------------------------------------
#                                         OPTIONS
# -----------------------------------------------------------------------------------------------------
# Videos with automatically generated subtitles
# will not work as they do not contain grammar (Most TED talks have grammar)
# Default Video : "Grit: the power of passion and perseverance | Angela Lee Duckworth"
youtube_url = 'https://www.youtube.com/watch?v=H14bBuluwB8'
summary_name = 'my_summary'
# total sentences wanted in summary
SENTENCES_COUNT = 10
LANGUAGE = 'english'


def get_all_sub_files(directory):
    '''
    imput: directory
    output: file list
    Given the path to a directory returns the subtitle files in that directory (end with .vtt)
    '''
    file_list = []
    for file in os.listdir(directory):
        if file.endswith(".vtt"):
            file_list.append(os.path.join(directory, file))
    return file_list

def get_all_mp4_files(directory):
    '''
    imput: directory
    output: file list
    Given the path to a directory returns the video files in that directory (end with .mp4)
    '''
    file_list = []
    for file in os.listdir(directory):
        if file.endswith(".mp4"):
            file_list.append(os.path.join(directory, file))
    return file_list

def summarizer(sentences):
    '''
    imput: sentences
    output: file list
    Given the path to a directory returns the video files in that directory (end with .mp4)
    '''
    stemmer = Stemmer(LANGUAGE)
    parser = PlaintextParser(text, Tokenizer(LANGUAGE))
    summarizer = Summarizer(stemmer)
    summarizer.stop_words = get_stop_words(LANGUAGE)

    # creates a list of the sentences in the summary
    for sentence in summarizer(parser.document, SENTENCES_COUNT):
        summary_list.append(str(sentence))


def time_stamp_to_seconds(timeStamp):
    '''
    :param timeStamp:
    :return timeStamp in seconds:
    '''
    time_list = timeStamp.split(':')
    return int(time_list[0]) * 3600 + int(time_list[1]) * 60 + float(time_list[2])


directory = sys.path[0]
summary_directory = sys.path[0]+'/summaries'

if not os.path.exists(summary_directory):
    os.makedirs(summary_directory)



sub_file_list = get_all_sub_files(directory)
vid_file_list = get_all_mp4_files(directory)
# removes all previous subtitle and video files
try:
    os.remove(sub_file_list[0])
    os.remove(vid_file_list[0])
except:
    pass


# set up YouTube video download to include subtitles
ydl_opts = {'writesubtitles':True, 'forcefilename': True}# , 'skip_download': True}

# download video
with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    ydl.download([youtube_url])

sub_file_list = get_all_sub_files(directory)
vid_file_list = get_all_mp4_files(directory)
sentence_list = []
start_list = []
end_list = []
summary_list = []
video_clips = []
current_sentence = 0
sentence_start = True
sentence_end = False
text = ''

# goes through every caption in the subtitle file and turns it into a list of sentences with start and end times
for caption in WebVTT().read(sub_file_list[0]):
    # the sentence is over if it ends with . , ? , ! , ." , ?" or !"
    if caption.text[len(caption.text)-1] == '.' or caption.text[len(caption.text)-1] == '?' or caption.text[len(caption.text)-1] == '!' or caption.text[len(caption.text)-2] == '.' or caption.text[len(caption.text)-2] == '?':
        sentence_end = True
    # if the caption lin is both the end and the start of a sentence
    if sentence_start and sentence_end:
        sentence_list.append(caption.text.replace('\n', ' '))
        start_list.append(caption.start)
        end_list.append(caption.end)
        current_sentence += 1
        sentence_start = True
        sentence_end = False
    elif sentence_start:
        start_list.append(caption.start)
        sentence_list.append(caption.text.replace('\n',' '))
        sentence_start = False
    elif sentence_end:
        sentence_list[current_sentence] += ' ' + caption.text.replace('\n',' ')
        end_list.append(caption.end)
        sentence_start = True
        sentence_end= False
        current_sentence += 1
    else:
        sentence_list[current_sentence] += ' ' + caption.text.replace('\n',' ')

    text += caption.text + ' '



# runs text through summarizer
summarizer(text)

# converts mp4 file into video clip for further processing
myclip = VideoFileClip(vid_file_list[0])

# runs through each sentence of summary
for i in range(len(summary_list)-1):
    # determines which sentence number it is
    index = sentence_list.index(summary_list[i])
    # creates a video clip using the start and end time of the the sentence
    video_clips.append(myclip.subclip(time_stamp_to_seconds(start_list[index]), time_stamp_to_seconds(end_list[index])))


# combines all video clips
final_clip = concatenate(video_clips)
# creates mp4 file
final_clip.write_videofile(summary_directory + '/' + summary_name + ".mp4")



