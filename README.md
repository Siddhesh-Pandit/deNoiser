
## Prerequisites

- Ensure you have Python 3+ downloaded.

- Ensure pip installation for numpy, matplotlib, scikit-image, PyWavelets  prior to usage.
- .nef or Nikon Exchange Format files can't be used as source at this moment.

- Pending tests for Canon Raw images.

## Usage

- Download deNoiser.py and config.ini to the same location.
- Edit file_path in confi.ini to reflect the path for noisy images.
save and exit.

### To run the script

``` python3 denoiserBatch.py



python3 denoiserBatch.py

### Successful run looks like follows
File path: /Users/siddhesh/Downloads/trial-dnoiser
processing:/Users/siddhesh/Downloads/trial-dnoiser/D85_8110_export.jpg
successfully processed:/Users/siddhesh/Downloads/trial-dnoiser/D85_8110_export.jpg
processing:/Users/siddhesh/Downloads/trial-dnoiser/D85_8126.jpeg
successfully processed:/Users/siddhesh/Downloads/trial-dnoiser/D85_8126.jpeg
Successfully read 2 images.
```

## Maintainers
- Adwait Godbole
- Siddhesh Pandit
