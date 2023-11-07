# Echelon Video Analyzer

This Python script is designed to analyze video files in a specific directory on your local machine (including its subdirectories). It computes the durations and sizes of all videos present in the directory. Videos are categorized into five categories: Super Short, Short, Medium, Long, and Very Long. Furthermore, a word cloud is generated based on the filenames of the videos.

The script provides a comprehensive output log, displaying the range, the average duration, and the size of videos per category. To improve performance, multithreading is employed.

## Installation

Check if Python is installed on your system:

```bash
python --version
```

Clone this GitHub repository:

```bash
git clone https://github.com/ParkWardRR/Echelon-Video-Analyzer.git
```

If required, install the necessary dependencies using pip:

```bash
pip install -r requirements.txt
```

## Usage

To run the script, navigate to the cloned repository and execute `Echelon-Video-Analyzer.py`, specifying the directory containing your videos:

```bash
python Echelon-Video-Analyzer.py -d /path/to/videos
```

Additional options to adjust the number of threads and top-n-words for the word cloud are available:

```bash
python Echelon-Video-Analyzer.py -d /path/to/videos -t 4 -n 10
```

## Options

- `-d / --directory`: (required) Directory containing video files.
- `-t / --threads`: (optional) Maximum number of threads to be utilized. The default is the number of cores.
- `-n / --topn`: (optional) Number of top words to display in the word cloud. The default is 10. If set to 0, the word cloud will not be generated.

The script allows for video file extensions to be specified by modifying the `VALID_EXTENSIONS` list.

## Contributing

I welcome your contributions!  

## License

Echelon Video Analyzer is a free and open-source software under the [MIT License](LICENSE).
