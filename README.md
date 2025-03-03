
## Prerequisites

- Ensure you have Python 3+ downloaded.

- Ensure pip installation for numpy, matplotlib, scikit-image, PyWavelets  prior to usage.
- .raw or .nef files can't be used as source at this moment.

- Pending tests for Canon Raw images.

## Usage

- Download deNoiser.py and config.ini to the same location.
- Edit file paths in confi.ini to reflect the path for noisy images for input and processed output.
- save and exit.

### To run the script

``` python3 denoiserBatch.py



python3 denoiserBatch.py

### Successful run looks like follows
% python3 denoiserBatch.py
input file path: /../../Downloads/trial-dnoiser
output file path: /../..//Downloads/deNoised
processing:/../../Downloads/trial-dnoiser/D85_8110_export.jpg
processed gaussian filter image:/../../Downloads/deNoised/D85_8110_export_gaussian.jpeg
processed median filter image:/../../Downloads/deNoised/D85_8110_export_median.jpeg
processed nonlocal filter image:/../../Downloads/deNoised/D85_8110_export_nonlocal.jpeg
successfully processed:/../../Downloads/trial-dnoiser/D85_8110_export.jpg
processing:/../../Downloads/trial-dnoiser/D85_8126.jpeg
processed gaussian filter image:/../../Downloads/deNoised/D85_8126_gaussian.jpeg
processed median filter image:/../../Downloads/deNoised/D85_8126_median.jpeg
processed nonlocal filter image:/../../Downloads/deNoised/D85_8126_nonlocal.jpeg
successfully processed:/../../Downloads/trial-dnoiser/D85_8126.jpeg
Successfully read 2 images.
Exiting
```
Left is after denoising; Right is before denoising
![Screenshot 2025-02-28 at 8 53 46 PM](https://github.com/user-attachments/assets/8775aef0-abff-4c8a-a0b3-eee30cd0b2c4)

## Maintainers
- Adwait Godbole
- Siddhesh Pandit
