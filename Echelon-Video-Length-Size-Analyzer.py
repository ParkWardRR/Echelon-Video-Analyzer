"""
Video Analyzer Script

This Python script analyzes video files in a given directory (including subdirectories). 
It computes the durations and sizes of each video, categorizes them into 5 categories: Super Short, Short, 
Medium, Long, Very Long videos, and generates a word cloud based on video filenames. 
The script provides output showing the range, average duration, and size per category.
Multithreading is used to speed up the processing.

Usage: python video_analyzer.py -d [directory_path] -t [max_threads] -n [top_n_words]
-d/--directory      [REQUIRED] The directory to scan for video files.
-t/--threads        [OPTIONAL] The maximum number of threads to use (default is the number of cores in the system).
-n/--topn           [OPTIONAL] The number of most frequent words displayed in the word cloud (default is 10, 0 means no word cloud).

You can specify video file extensions to search for by modifying the VALID_EXTENSIONS list.

Example usage: python video_analyzer.py -d /path/to/videos -t 4 -n 10
"""
import os
import argparse
import concurrent.futures
import subprocess
import numpy as np
import json
import datetime
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import time
from sklearn.feature_extraction.text import CountVectorizer
import shutil

VALID_EXTENSIONS = ['.mp4', '.avi', '.mkv', '.mov', '.wmv']

def mediainfo_duration(filename):
    """Returns video duration in seconds using mediainfo."""
    try:
        duration_info = subprocess.check_output(['mediainfo', '--Output=Video;%Duration%', filename], universal_newlines=True).strip()
        duration = int(duration_info) / 1000  # Convert milliseconds to seconds
    except subprocess.CalledProcessError:
        print(f"Error occurred when trying to execute mediainfo for file {filename}. Skipping file.")
        duration = 0

    return duration

def video_info(filename, verbose=False):
    """Returns video duration in seconds and size in GB using mediainfo."""
    try:
        duration = mediainfo_duration(filename)
    except Exception:
        duration = 0

    size = os.path.getsize(filename) / 1e9  # Convert bytes to GB

    return duration, size, os.path.splitext(os.path.basename(filename))[0]

def analyze_videos(directory, max_threads, top_n_words, verbose=False):
    """Analyzes videos in directory using multithreading for speed increase."""
    
    start_time = time.time()
    video_files = []
    dir_count = 0
    no_stream_count = 0  # counter for files with no recognizable video streams
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(tuple(VALID_EXTENSIONS)):
                video_files.append(os.path.join(root, file))
        dir_count += 1
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        video_info_list = list(executor.map(lambda f: video_info(f, verbose), video_files))
    
    # add check for duration and size being zero (= no recognizable video streams)
    video_info_list = [info for info in video_info_list if not (info[0] == 0 and info[1] == 0)]
    no_stream_count = len(video_files) - len(video_info_list)
    
    durations = [info[0] for info in video_info_list]
    sizes = [info[1] for info in video_info_list]
    titles = ' '.join([info[2] for info in video_info_list])
    
    print(f"\nScanned {dir_count} directories and found {len(video_files)} videos.\n")
    print(f"Avg video size: {np.mean(sizes):.2f} GB. Total size: {np.sum(sizes):.2f} GB\n")
    
    categories = ["Super Short", "Short", "Medium", "Long", "Very Long"]
    bounds = np.linspace(min(durations), max(durations), len(categories) + 1)
    
    print('Category    Range               Avg Duration    Number of Videos    Avg Size (GB)')
    print('-'*90)
    for i in range(len(categories)):
        videos_in_category_indices = [index for index, dur in enumerate(durations) if bounds[i] <= dur < bounds[i + 1]]
        avg_duration = np.mean([durations[index] for index in videos_in_category_indices])
        avg_size = np.mean([sizes[index] for index in videos_in_category_indices])
        num_videos = len(videos_in_category_indices)
        
        print(f"{categories[i]:<12} {str(datetime.timedelta(seconds=int(bounds[i])))} - "
              f"{str(datetime.timedelta(seconds=int(bounds[i+1])))}   "
              f"{str(datetime.timedelta(seconds=int(avg_duration)))}   "
              f"{num_videos:<16}  {avg_size:.2f}")
    
    elapsed_time = time.time() - start_time  # in seconds
    print(f"\nElapsed time: {elapsed_time:.2f} seconds.")
    print(f"Speed: {len(video_files)/elapsed_time*60:.2f} videos per minute\n")
    
    if top_n_words > 0:
        wordcloud = WordCloud(width=1000, height=600, random_state=21, max_font_size=110, background_color='white').generate(titles)
        plt.figure(figsize=(15, 10))
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis('off')
        plt.show()
        
        # Create bigrams, filter using regex and only keep human-readable words
        vectorizer = CountVectorizer(ngram_range=(1, 2), token_pattern=r'[a-zA-Z]+').fit([titles])
        counts = vectorizer.transform([titles]).toarray().sum(axis=0)
        counter = {word: counts[idx] for word, idx in vectorizer.vocabulary_.items()}
        
        # Print words formatted in a block of text
        formatted_wordcloud = ''
        word_count = 0
        for word, count in sorted(counter.items(), key=lambda x: x[1], reverse=True)[:top_n_words]:
            if word_count != 0 and word_count % 5 == 0:
                formatted_wordcloud += '\n'
            formatted_wordcloud += f"{word}: {count}, "
            word_count += 1
        print(formatted_wordcloud.rstrip(', '))

    if verbose:
        print(f"\nNumber of videos with no recognizable streams: {no_stream_count}\n")

def main():
    parser = argparse.ArgumentParser(description='Analyze video durations in a directory.')
    parser.add_argument('-d', '--directory', required=True, help='Directory to scan for video files.')
    parser.add_argument('-t', '--threads', type=int, default=os.cpu_count(), help='Maximum number of threads to use.')
    parser.add_argument('-n', '--topn', type=int, default=10, help='Number of top words to display in word cloud.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose mode.')
    args = parser.parse_args()

    analyze_videos(args.directory, args.threads, args.topn, args.verbose)

if __name__ == "__main__":
    main()
