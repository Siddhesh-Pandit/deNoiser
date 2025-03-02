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


def find_directory_in_tree(root_dir, target_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if target_dir in dirnames:
            return os.path.join(dirpath, target_dir)
    return None


def find_directory(dir_name):
    """
    Finds a directory with the given name under the current working directory.

    Args:
        dir_name: The name of the directory to find.

    Returns:
        The absolute path to the directory if found, otherwise None.
    """
    for item in os.listdir():
        if os.path.isdir(item) and item == dir_name:
            return os.path.abspath(item)
    return None

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

def read_images_from_folder_and_deNoise(folder_path, output_folder_path, brightness_factor):
    
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)
    
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

                output_file_path = os.path.join(output_folder_path, filenameNew)
                np.clip(gaussian_img+ brightness_factor, 0, 255).astype(np.uint8)

                plt.imsave(output_file_path, gaussian_img, dpi=300)
                print(f"processed gaussian filter image:{output_file_path}")

                median_img=nd.median_filter(img, size=3)
                extension ="_median.jpeg"
                filenameNew = append_extension(os.path.splitext(filename)[0],extension)
                output_file_path = os.path.join(output_folder_path, filenameNew)
                
                np.clip(median_img+ brightness_factor, 0, 255).astype(np.uint8)
                plt.imsave(output_file_path, median_img, dpi=500)
                print(f"processed median filter image:{output_file_path}")


                sigma_est = np.mean(estimate_sigma(img, channel_axis=-1))
                denoise_nl = denoise_nl_means(img, h=1.15 * sigma_est, fast_mode=True, patch_distance=2, patch_size=2, channel_axis=-1)
                np.clip(denoise_nl+ brightness_factor, 0, 255).astype(np.uint8)
                extension ="_nonlocal.jpeg"
                filenameNew = append_extension(os.path.splitext(filename)[0],extension)

                output_file_path = os.path.join(output_folder_path, filenameNew)
                plt.imsave(output_file_path, denoise_nl, dpi=300)
                print(f"processed nonlocal filter image:{output_file_path}")
                

                images.append(img)

                print(f"successfully processed:{img_path}")
            else:
                print(f"Error reading image:{filename}")
    return images


print("looking for config.ini")
#where are we copied?
cwd = os.getcwd()
print(f"current dir:{cwd}")

# find project dir:
directory_name_to_find = "deNoiser"
found_directory = find_directory(directory_name_to_find)

if found_directory:
    print(f"Directory '{directory_name_to_find}' found at: {found_directory}")

    if os.path.exists(found_directory) and os.path.isdir(found_directory):
        
        os.chdir(found_directory)        
        cwd = os.getcwd()
        print(f"current dir:{cwd}")

    else:
        print("deNoiser directory structure incorrect")

else:
    print(f"config.ini for '{directory_name_to_find}' not found under the current working directory.")
    print("Please grant persmission to search system for the deNoiser's config if not done previously")
    root_directory = cwd # Replace with the directory to start searching from
    result = find_directory_in_tree(root_directory, directory_name_to_find)

    if result:
        print(f"Directory '{directory_name_to_find}' found at: {result}")
        os.chdir(result)        
        cwd = os.getcwd()
        print(f"current dir:{cwd}")

    else:
        print(f"Directory '{directory_name_to_find}' not found in '{root_directory}'.")

#we found the dir where config.ini is placed
configFileName = "./config.ini"
if os.path.isfile(configFileName):
    print("found config.ini")
    config = configparser.ConfigParser()

    try:
        config.read(configFileName)
        folder_path = config.get('Paths', 'input_file_path')
        output_folder_path = config.get('Paths', 'output_file_path')
        brightness = config.getint('Brightness','brightness')

        print(f"input file path: {folder_path}")
        print(f"output file path: {output_folder_path}")

        images = read_images_from_folder_and_deNoise(folder_path, output_folder_path, brightness)

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
        print("The source and path files are not within deNoiser directory.")
else:
    print("Error! either config.ini not found or source and path files are not within deNoiser directory ")
