# Hardsub-Extract-OCR: Extract hardsubs and OCR with 99% accuracy 
Uses [VideoSubFinder](https://sourceforge.net/projects/videosubfinder/)
and [Google Cloud Vision](https://cloud.google.com/vision) through [Chrome Lens Py](https://github.com/bropines/chrome-lens-py) to extract hardsubs and OCR them to create an SRT file. Main purpose is for use with MPVacious for quick dictionary lookups and use with subs2srs. All code in the .bat and .py files was written by ChatGPT. Archive of files at https://github.com/Furretar/Mandarin-Subtitles-Archive.

# Installation (Windows Only)
1. Download [this repository](https://github.com/Furretar/Hardsub-Extract-OCR/archive/refs/heads/main.zip) and extract anywhere.
2. Make sure you have [python](https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe) installed (used version 3.11.0 here)
3. Install [VideoSubFinder](https://sourceforge.net/projects/videosubfinder/files/latest/download) and extract Release_x64 to the main directory.
   1. It's important that the folder name matches `Release_x64` exactly.
```bash
/Hardsub-Extract-OCR-main/
└── /BatchProcessor/
└── /PutVideosInHere/
└── /Release_x64/ <-- here
```

Then, run `01 InstallRequirements.bat`.


# Usage
## Extraction
- Put the videos you want to extract hardsubs from in the /PutVideosInHere/ folder.
- Run the ExtractHardsubs.bat.
  - You will need to check the RGBImages folder so you can tweak the crop settings. Having a closer crop will reduce noise in the final result and increase processing speed in the extraction and OCR steps. You also may need to close VideoSubFinder using Task Manager (ctrl+shift+esc) before running the .bat again:
<img src="https://github.com/user-attachments/assets/bb9097e9-fbe0-4a19-9f84-63fcc53346aa" alt="image" width="400"/> 

This is where the RGBImages folder is:
```bash
/Hardsub-Extract-OCR-main/
└── /BatchProcessor/
└── /PutVideosInHere/
   ├── /output/
       └──/VideoTitle/
          └──RGBImages
   └── VideoTitle.mp4
└── /Release_x64/
```
Example of too high `-be` value, crops too much off the bottom
![0_00_16_099__0_00_20_686_0019205760896008612800720](https://github.com/user-attachments/assets/3bb3b78b-d555-45a4-8a53-04f6a2485efa)

This is how you can tweak the crop values in ExtractHardsubs.bat. You can edit the file by right clicking and selecting edit.
<img src="https://github.com/user-attachments/assets/7d7e60f3-8c73-405a-8ba2-b1d052cfe5db" alt="image" width="800"/>
<img src="https://github.com/user-attachments/assets/58e1203e-9f34-4875-a39f-a40d18f73c57" alt="image" width="1000"/>
<img src="https://github.com/user-attachments/assets/a5ae0f30-82dc-4c2a-8489-4ed346068b8e" alt="image" width="1000"/>

Once your crop values are tweaked, you can let the program run. It will leave you with the final images in TXTImages. They should look like this:
![0_00_16_099__0_00_20_686_1019205790896007012800720](https://github.com/user-attachments/assets/4fd173ed-2511-45a9-a98b-a96a3da4c99b)

## OCR
The OCR we will be using is called Google Cloud Vision, it's the same one used in Google Lens. In my experience it's the best OCR I've seen and makes very few mistakes. It does pick up some noise though. At the time of writing, it can be accessed for free using [this repository](https://github.com/bropines/chrome-lens-py). It will be automatically installed when you run `01 InstallRequirements.bat`.


## SUP to PNG
- SUP files must not have special/chinese characters in the file name
- originally from: https://github.com/mjuhasz/BDSup2Sub

## SUB to SUP
- originally from: https://www.videohelp.com/software/BDSup2Sub
  
# Links
<a href="https://nyaa.si/user/Furretar" target="_blank">
  <img src="https://github.com/user-attachments/assets/bf0a6f97-e1d4-417e-b887-a323cb2f3390" height="50px" title="Nyaa">
</a>
<a href="https://www.youtube.com/@furretar6484" target="_blank">
  <img src="https://github.com/gauravghongde/social-icons/blob/master/SVG/Color/Youtube.svg" height="50px" title="YouTube">
</a>

Discord: furretar

# Note

If you'd rather use a locally hosted OCR rather than Google Cloud Vision, you should consider using [RapidVideOCR Desktop](https://github.com/SWHL/RapidVideOCRDesktop). It uses PaddleOCR, which has about 95% accuracy in my experience.
You can also convert the TXTImages from the first step into a SUP file directly without OCR using [Images to PGS SUP](https://github.com/dam-cav/img-to-pgs-sup)

