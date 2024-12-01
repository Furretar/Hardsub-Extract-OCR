# Hardsub-Extract-OCR: Extract hardsubs and OCR with 99% accuracy 
Uses [VideoSubFinder](https://sourceforge.net/projects/videosubfinder/)
and [Google Cloud Vision](https://cloud.google.com/vision) (and paddleocr?) to extract hard subs and OCR them to create an SRT file. Main purpose is for use with MPVacious for quick dictionary lookups and use with subs2srs. All code in the .bat and .py files was written by ChatGPT.

## Links
<a href="https://nyaa.si/user/Furretar" target="_blank">
  <img src="https://github.com/user-attachments/assets/bf0a6f97-e1d4-417e-b887-a323cb2f3390" height="50px" title="Nyaa">
</a>
<a href="https://www.youtube.com/@furretar6484" target="_blank">
  <img src="https://github.com/gauravghongde/social-icons/blob/master/SVG/Color/Youtube.svg" height="50px" title="YouTube">
</a>


Discord: furretar

## Installation
1. Download [this repository](https://github.com/Furretar/Hardsub-Extract-OCR/archive/refs/heads/main.zip) and extract anywhere.
2. Make sure you have [python](https://www.python.org/ftp/python/3.13.0/python-3.13.0-amd64.exe) installed (used version 3.13.0 here)
3. Install [VideoSubFinder](https://sourceforge.net/projects/videosubfinder/files/latest/download) and extract Release_x64 to the main directory.
   1. It's important that the folder name matches `Release_x64` exactly.
```bash
/Hardsub-Extract-OCR-main/
└── /PutVideosInHere/
└── /Release_x64/ <-- here
```

## Usage

1.
- Put the videos you want to extract hardsubs from in the /PutVideosInHere/ folder.
- Run the ExtractHardsubs.bat.
  - You will need to check the RGBImages folder so you can tweak the crop settings. Having a closer crop will reduce noise in the final result and increase processing speed in the extraction and OCR steps. You also may need to close VideoSubFinder using Task Manager (ctrl+shift+esc) before running the .bat again:
<img src="https://github.com/user-attachments/assets/bb9097e9-fbe0-4a19-9f84-63fcc53346aa" alt="image" width="400"/> 

This is where the RGBImages folder is:
```bash
/Hardsub-Extract-OCR-main/
└── /PutVideosInHere/
   ├── /output/
       └──/VideoTitle/
          └──RGBImages
   └── VideoTitle.mp4
└── /Release_x64/
```
Example of too high -be value, crops too much off the bottom
![0_00_16_099__0_00_20_686_0019205760896008612800720](https://github.com/user-attachments/assets/3bb3b78b-d555-45a4-8a53-04f6a2485efa)

This is how you can tweak the crop values in ExtractHardsubs.bat. You can edit the file by right clicking and selecting edit.
<img src="https://github.com/user-attachments/assets/7d7e60f3-8c73-405a-8ba2-b1d052cfe5db" alt="image" width="800"/>
<img src="https://github.com/user-attachments/assets/58e1203e-9f34-4875-a39f-a40d18f73c57" alt="image" width="1000"/>

<img src="https://github.com/user-attachments/assets/34c62809-5861-464d-bbb1-fe4c329714d3" alt="image" width="1000"/>


