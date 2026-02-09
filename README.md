# Hardsub-Extract-OCR: Extract hardsubs and OCR with 99% accuracy 
Uses [VideoSubFinder](https://sourceforge.net/projects/videosubfinder/)
and [Google Cloud Vision](https://cloud.google.com/vision) to extract hardsubs and OCR them to create an SRT file. Main purpose is for use with MPVacious for quick dictionary lookups and use with subs2srs. All code in the .bat and .py files was written by ChatGPT. I used pyinstaller to make the python script an exe, source code is in BatchProcessor.py. Archive of files at https://github.com/Furretar/Mandarin-Subtitles-Archive.

# Installation (Only for Windows)
1. Download [this repository](https://github.com/Furretar/Hardsub-Extract-OCR/archive/refs/heads/main.zip) and extract anywhere.
2. Make sure you have [python](https://www.python.org/ftp/python/3.13.0/python-3.13.0-amd64.exe) installed (used version 3.13.0 here)
3. Install [VideoSubFinder](https://sourceforge.net/projects/videosubfinder/files/latest/download) and extract Release_x64 to the main directory.
   1. It's important that the folder name matches `Release_x64` exactly.
```bash
/Hardsub-Extract-OCR-main/
└── /BatchProcessor/
└── /PutVideosInHere/
└── /Release_x64/ <-- here
```

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
The OCR we will be using is called Google Cloud Vision, it's the same one used in Google Lens. In my experience it makes less than 1 mistake per episode, or 600 sentence. It does pick up some noise though. At the time of writing, Google offers a $300 free trial for 3 months. That's enough to OCR over 300 episodes of anime.

- Make a [Google Cloud account](https://console.cloud.google.com/).
- Create a project.
  - You can just enter random text or "Other" for the details.
- Enable billing, enter payment information.
  - It will not charge you unless you go over the trial amount.
- In `APIs & Services` in your project, go to `Credentials`.
- Click `+ Create Credentials`, then `Service Account`.
- Enter info.
- Inside the Service Account, click Keys.
- Click `ADD KEY`, Create new key, make sure JSON is selected, then click Create.
- Drag this JSON file into the main directory.
- In your project, go to `APIs and Services`.
- `Enabled APIs and Services`.
- `+ Enable APIs and Services`.
- Search for `Cloud Vision`.
- Enable it.
- Make sure it says something like "300 credits remaining" on the project dashboard

Now you can use the Batch Processor.
- Run `01 InstallRequirements.bat`.
- Run `02 BatchProcessor.exe`.
- Select your folder with images.
  - If you're processing multiple videos at once, this will be `output`, check the `Process Multiple Folders` checkbox.
  - If you're processing a single video, this will be `TXTImages`.
- Select the output folder, where the SRT files will be generated.
- Select your JSON file, should be in the main directory. Ex. `example-473422-7e6ba2cacb95.json`.

### Be careful you do not go over the free trial limit, as it will charge your card. Double check your selected folders, how many images they contain, and check the progress of the batch processor frequently.

Once you have your subtitle files, you may want to use subtitle edit to merge lines with the same text. For example, when a scene changes in a show with the same subtitle line on screen, it gets counted as two lines, which can cause problems when using subs2srs.
- To do this, open [subtitle edit](https://github.com/SubtitleEdit/subtitleedit/releases).
- Click on `Tools`
- `Batch Convert`
- Drag in files
- `Merge lines with same text`
- `Overwrite files`
- `Convert`

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

