
## Usage

- Currently tested on for OS X only
- Download and Extract deNoiser.zip
- Edit file paths in config.ini to reflect the path for noisy images for input and processed output.
- For each source image, 3 processed denoised images are  produced using gaussian, median and nonlocal filter passes.
- Edit brightness in config.ini to adjust brightness factor
- Navigate to deNoiser/dist/ and click to run denoiserBatch.


### Successful run looks like follows

```
Last login: Sun Mar  2 01:39:14 on ttys000
/../../GitHub/deNoiser/dist/denoiserBatch ; exit;
 % /../../GitHub/deNoiser/dist/denoiserBatch ; exit;
Matplotlib is building the font cache; this may take a moment.
looking for config.ini
current dir:/../<yourDirectory>
config.ini 'deNoiser' not found under the current working directory.
Please grant persmission to search system for the deNoiser's config if not done previously
Directory 'deNoiser' found at: /../../GitHub/deNoiser
current dir:/../../GitHub/deNoiser
found config.ini
input file path: /../../GitHub/deNoiser/source
output file path: /../../GitHub/deNoiser/processed
processing:/../../GitHub/deNoiser/source/D85_8126.jpeg
processed gaussian filter image:/../../GitHub/deNoiser/processed/D85_8126_gaussian.jpeg
processed median filter image:/../../GitHub/deNoiser/processed/D85_8126_median.jpeg
processed nonlocal filter image:/../..h/GitHub/deNoiser/processed/D85_8126_nonlocal.jpeg
successfully processed:/../../GitHub/deNoiser/source/D85_8126.jpeg
Successfully read 1 images.
Exiting

Saving session...
...copying shared history...
...saving history...truncating history files...
...completed.

[Process completed]
```
Left is after denoising; Right is before denoising
![Screenshot 2025-02-28 at 8 53 46 PM](https://github.com/user-attachments/assets/8775aef0-abff-4c8a-a0b3-eee30cd0b2c4)

## Maintainers
- Adwait Godbole
- Siddhesh Pandit
