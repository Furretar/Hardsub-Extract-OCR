[English](README.md) | **日本語**

# Hardsub-Extract-OCR：焼き付け字幕を抽出し、99%の精度でOCR
[VideoSubFinder](https://sourceforge.net/projects/videosubfinder/) と、[Chrome Lens Py](https://github.com/bropines/chrome-lens-py) 経由の [Google Cloud Vision](https://cloud.google.com/vision) を使って、動画に焼き付けられた字幕（ハードサブ）を抽出・OCRし、SRTファイルを作成します。主な用途は、MPVacious での素早い辞書引きと、subs2srs での利用です。.bat ファイルと .py ファイルのコードはすべて ChatGPT が書いたものです。作成した字幕のアーカイブは https://github.com/Furretar/Mandarin-Subtitles-Archive にあります。

# インストール（Windows のみ）
1. [このリポジトリ](https://github.com/Furretar/Hardsub-Extract-OCR/archive/refs/heads/main.zip)をダウンロードし、任意の場所に展開します。
2. [Python](https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe) がインストールされていることを確認します（ここではバージョン 3.11.0 を使用しています）。
3. [VideoSubFinder](https://sourceforge.net/projects/videosubfinder/files/latest/download) をダウンロードし、Release_x64 をメインのディレクトリに展開します。
   1. フォルダ名は `Release_x64` と完全に一致している必要があります。
```bash
/Hardsub-Extract-OCR-main/
└── /BatchProcessor/
└── /PutVideosInHere/
└── /Release_x64/ <-- ここ
```

その後、`01 InstallRequirements.bat` を実行します。


# 使い方
## 抽出
- 字幕を抽出したい動画を /PutVideosInHere/ フォルダに入れます。
- ExtractHardsubs.bat を実行します。
  - クロップ（切り抜き）設定を調整するため、RGBImages フォルダを確認する必要があります。字幕に近い範囲で切り抜くほど、最終結果のノイズが減り、抽出と OCR の処理も速くなります。また、.bat を再実行する前に、タスクマネージャー（Ctrl+Shift+Esc）で VideoSubFinder を終了させる必要がある場合があります：
<img src="https://github.com/user-attachments/assets/bb9097e9-fbe0-4a19-9f84-63fcc53346aa" alt="image" width="400"/> 

RGBImages フォルダの場所：
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
`-be` の値が大きすぎて、下側を切り取りすぎている例：
![0_00_16_099__0_00_20_686_0019205760896008612800720](https://github.com/user-attachments/assets/3bb3b78b-d555-45a4-8a53-04f6a2485efa)

ExtractHardsubs.bat のクロップ値は、次のように調整できます。ファイルを右クリックして「編集」を選ぶと編集できます。
<img src="https://github.com/user-attachments/assets/7d7e60f3-8c73-405a-8ba2-b1d052cfe5db" alt="image" width="800"/>
<img src="https://github.com/user-attachments/assets/58e1203e-9f34-4875-a39f-a40d18f73c57" alt="image" width="1000"/>
<img src="https://github.com/user-attachments/assets/a5ae0f30-82dc-4c2a-8489-4ed346068b8e" alt="image" width="1000"/>

クロップ値の調整が終わったら、あとはプログラムを実行させておくだけです。最終的な画像が TXTImages に出力されます。次のような画像になるはずです：
![0_00_16_099__0_00_20_686_1019205790896007012800720](https://github.com/user-attachments/assets/4fd173ed-2511-45a9-a98b-a96a3da4c99b)


続いて `BatchProcessor.py` を実行すると、抽出したスクリーンショットから字幕ファイルが作成されます。このスクリプトは `output` 内のフォルダごとに字幕ファイルを1つ作成します。1つのファイルだけを作成したい場合は、`Process Multiple Folders` のチェックを外し、ファイルパスに `RGBImages` または `TXTImages` フォルダを指定してください。`Process Multiple Folders` にチェックが入っている場合、スクリプトは1ファイルの処理が終わるたびに output フォルダを再スキャンし、新しく追加されたフォルダも処理します。そのため、画像の抽出が OCR より速い場合は、両方のスクリプトを同時に実行できます。生成された TXTImages が読み取りにくい場合は、`Use RGBImages instead of TXTImages` にチェックを入れることもできます。

<img width="843" height="545" alt="image" src="https://github.com/user-attachments/assets/1115e4fa-52d8-4f8b-80e9-1c831f886ce8" />


## OCR
使用する OCR は Google Cloud Vision で、Google レンズと同じものです。私の経験では、これまで見た中で最も優れた OCR で、誤認識はほとんどありません。ただし、ノイズを拾うことはあります。執筆時点では、[こちらのリポジトリ](https://github.com/bropines/chrome-lens-py)を使って無料で利用できます。`01 InstallRequirements.bat` を実行すると自動でインストールされます。


## SUP から PNG へ
- SUP ファイルのファイル名に特殊文字や中国語の文字を含めないでください。
- 元のツール：https://github.com/mjuhasz/BDSup2Sub

## SUB から SUP へ
- 元のツール：https://www.videohelp.com/software/BDSup2Sub
  
# リンク
<a href="https://nyaa.si/user/Furretar" target="_blank">
  <img src="https://github.com/user-attachments/assets/bf0a6f97-e1d4-417e-b887-a323cb2f3390" height="50px" title="Nyaa">
</a>
<a href="https://www.youtube.com/@furretar6484" target="_blank">
  <img src="https://github.com/gauravghongde/social-icons/blob/master/SVG/Color/Youtube.svg" height="50px" title="YouTube">
</a>

Discord: furretar

# 補足

Google Cloud Vision ではなくローカルで動く OCR を使いたい場合は、[RapidVideOCR Desktop](https://github.com/SWHL/RapidVideOCRDesktop) を検討してください。PaddleOCR を使用しており、私の経験では精度はおよそ95%です。
また、最初のステップで得た TXTImages を、OCR を使わずに [Images to PGS SUP](https://github.com/dam-cav/img-to-pgs-sup) で直接 SUP ファイルに変換することもできます。
