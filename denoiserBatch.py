

import numpy as np
import os
import configparser
import matplotlib.pyplot as plt
from skimage import data, img_as_float
from skimage.restoration import denoise_nl_means, estimate_sigma
from skimage.metrics import peak_signal_noise_ratio
from skimage.util import random_noise
from skimage import io
from scipy import ndimage as nd
from skimage.restoration import denoise_nl_means, estimate_sigma


def append_extension(filename, extension):
  """Appends an extension to a filename if it doesn't already have one.

  Args:
      filename: The original filename (without extension).
      extension: The extension to append (e.g., ".txt", ".pdf").

  Returns:
      The filename with the appended extension, or the original filename if 
      it already had an extension.
  """
  if not filename.lower().endswith(extension.lower()):
    return filename + extension
  return filename

def read_images_from_folder_and_deNoise(folder_path):
    images = []
    for filename in os.listdir(folder_path):
        if filename.endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
            img_path = os.path.join(folder_path, filename)
            img = io.imread(img_path)
            print(f"processing:{img_path}")

            if img is not None:

                gaussian_img=nd.gaussian_filter(img, sigma=.75)
                extension ="_gaussian.jpeg"
                filenameNew = append_extension(os.path.splitext(filename)[0],extension)
                plt.imsave(filenameNew, gaussian_img, dpi=300)

                median_img=nd.median_filter(img, size=3)
                extension ="_median.jpeg"
                filenameNew = append_extension(os.path.splitext(filename)[0],extension)
                plt.imsave(filenameNew, median_img, dpi=300)

                sigma_est = np.mean(estimate_sigma(img, channel_axis=-1))
                denoise_nl = denoise_nl_means(img, h=1.15 * sigma_est, fast_mode=True, patch_distance=2, patch_size=2, channel_axis=-1)
                extension ="_nonlocal.jpeg"
                filenameNew = append_extension(os.path.splitext(filename)[0],extension)
                plt.imsave(filenameNew, denoise_nl, dpi=300)

                images.append(img)

                print(f"successfully processed:{img_path}")
            else:
                print(f"Error reading image:{filename}")
    return images


config = configparser.ConfigParser()

try:
    config.read('config.ini')
    folder_path = config.get('Paths', 'file_path')
    print(f"File path: {folder_path}")
    images = read_images_from_folder_and_deNoise(folder_path)

    if images:
        print(f"Successfully read {len(images)} images.")
        print("Exiting")

    else:
        print("No images found or an error occurred.")

except configparser.Error as e:
    print(f"Error reading config file: {e}")
except KeyError:
    print("The 'file_path' key was not found in the 'Paths' section.")
except FileNotFoundError:
    print("The 'config.ini' file was not found.")
