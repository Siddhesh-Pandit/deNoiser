"""Simple GUI for Image Denoiser using tkinter."""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
import threading
import logging
from config_loader import DenoiserConfig, OutputConfig, FilterConfig, GaussianConfig, MedianConfig, NonLocalMeansConfig, RAWConfig
from processor import ImageProcessor
from metrics import save_metrics_to_csv
from image_io import is_rawpy_available


class TextHandler(logging.Handler):
    """Custom logging handler that writes to a tkinter Text widget."""
    
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
    
    def emit(self, record):
        msg = self.format(record)
        self.text_widget.configure(state='normal')
        self.text_widget.insert(tk.END, msg + '\n')
        self.text_widget.configure(state='disabled')
        self.text_widget.see(tk.END)


class DenoiserGUI:
    """GUI application for image denoising."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Image Denoiser")
        self.root.geometry("800x700")
        
        # Variables
        self.input_path = tk.StringVar()
        self.input_files = []  # Store selected files
        self.output_path = tk.StringVar()
        self.output_format = tk.StringVar(value="png")
        self.jpeg_quality = tk.IntVar(value=95)
        
        # Filter toggles
        self.enable_gaussian = tk.BooleanVar(value=True)
        self.enable_median = tk.BooleanVar(value=True)
        self.enable_nonlocal = tk.BooleanVar(value=True)
        
        # Filter parameters
        self.gaussian_sigma = tk.DoubleVar(value=0.75)
        self.median_size = tk.IntVar(value=3)
        self.nl_h_multiplier = tk.DoubleVar(value=1.15)
        self.nl_fast_mode = tk.BooleanVar(value=True)
        self.nl_patch_size = tk.IntVar(value=5)
        self.nl_patch_distance = tk.IntVar(value=6)
        
        # RAW processing mode
        self.raw_mode = tk.StringVar(value="half")
        self.nl_fast_mode = tk.BooleanVar(value=True)
        self.nl_patch_size = tk.IntVar(value=5)
        self.nl_patch_distance = tk.IntVar(value=6)
        
        self.processing = False
        
        self.create_widgets()
        self.setup_logging()
    
    def create_widgets(self):
        """Create all GUI widgets."""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Title
        title = ttk.Label(main_frame, text="Image Denoiser", font=('Arial', 16, 'bold'))
        title.grid(row=row, column=0, columnspan=3, pady=(0, 10))
        row += 1
        
        # Input selection
        ttk.Label(main_frame, text="Input:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.input_path, width=50).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Input buttons frame
        input_btn_frame = ttk.Frame(main_frame)
        input_btn_frame.grid(row=row, column=2, padx=(5, 0), pady=5)
        ttk.Button(input_btn_frame, text="Folder", command=self.browse_folder, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(input_btn_frame, text="Files", command=self.browse_files, width=8).pack(side=tk.LEFT, padx=2)
        row += 1
        
        # Output folder
        ttk.Label(main_frame, text="Output Folder:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.output_path, width=50).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Button(main_frame, text="Browse...", command=self.browse_output).grid(row=row, column=2, padx=(5, 0), pady=5)
        row += 1
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        row += 1
        
        # Output settings
        output_frame = ttk.LabelFrame(main_frame, text="Output Settings", padding="5")
        output_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(output_frame, text="Format:").grid(row=0, column=0, sticky=tk.W, padx=5)
        format_combo = ttk.Combobox(output_frame, textvariable=self.output_format, 
                                    values=["png", "jpg", "tiff"], state="readonly", width=10)
        format_combo.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(output_frame, text="JPEG Quality:").grid(row=0, column=2, sticky=tk.W, padx=(20, 5))
        ttk.Spinbox(output_frame, from_=1, to=100, textvariable=self.jpeg_quality, width=10).grid(row=0, column=3, sticky=tk.W, padx=5)
        
        row += 1
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        row += 1
        
        # Filters section
        filters_frame = ttk.LabelFrame(main_frame, text="Filters", padding="5")
        filters_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Gaussian filter
        gaussian_check = ttk.Checkbutton(filters_frame, text="Gaussian Filter", variable=self.enable_gaussian)
        gaussian_check.grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Label(filters_frame, text="Sigma:").grid(row=0, column=1, sticky=tk.W, padx=(20, 5))
        ttk.Spinbox(filters_frame, from_=0.1, to=3.0, increment=0.1, textvariable=self.gaussian_sigma, width=10).grid(row=0, column=2, sticky=tk.W)
        ttk.Label(filters_frame, text="(0.5-2.0 recommended)").grid(row=0, column=3, sticky=tk.W, padx=5)
        
        # Median filter
        median_check = ttk.Checkbutton(filters_frame, text="Median Filter", variable=self.enable_median)
        median_check.grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Label(filters_frame, text="Size:").grid(row=1, column=1, sticky=tk.W, padx=(20, 5))
        ttk.Spinbox(filters_frame, from_=3, to=11, increment=2, textvariable=self.median_size, width=10).grid(row=1, column=2, sticky=tk.W)
        ttk.Label(filters_frame, text="(odd numbers only)").grid(row=1, column=3, sticky=tk.W, padx=5)
        
        # Non-local means filter
        nonlocal_check = ttk.Checkbutton(filters_frame, text="Non-local Means", variable=self.enable_nonlocal)
        nonlocal_check.grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Label(filters_frame, text="h multiplier:").grid(row=2, column=1, sticky=tk.W, padx=(20, 5))
        ttk.Spinbox(filters_frame, from_=0.5, to=2.0, increment=0.05, textvariable=self.nl_h_multiplier, width=10).grid(row=2, column=2, sticky=tk.W)
        ttk.Label(filters_frame, text="(0.8-1.5 recommended)").grid(row=2, column=3, sticky=tk.W, padx=5)
        
        # Non-local means advanced
        ttk.Checkbutton(filters_frame, text="Fast mode", variable=self.nl_fast_mode).grid(row=3, column=0, sticky=tk.W, padx=(20, 0), pady=2)
        ttk.Label(filters_frame, text="Patch size:").grid(row=3, column=1, sticky=tk.W, padx=(20, 5))
        ttk.Spinbox(filters_frame, from_=3, to=9, increment=2, textvariable=self.nl_patch_size, width=10).grid(row=3, column=2, sticky=tk.W)
        ttk.Label(filters_frame, text="Patch distance:").grid(row=4, column=1, sticky=tk.W, padx=(20, 5))
        ttk.Spinbox(filters_frame, from_=3, to=15, increment=2, textvariable=self.nl_patch_distance, width=10).grid(row=4, column=2, sticky=tk.W)
        
        row += 1
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        row += 1
        
        # RAW settings
        raw_available = is_rawpy_available()
        py_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        
        if raw_available:
            raw_title = "RAW Image Settings (Enabled)"
        else:
            raw_title = f"RAW Image Settings (Disabled - Python {py_version})"
        
        raw_frame = ttk.LabelFrame(main_frame, text=raw_title, padding="5")
        raw_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        if raw_available:
            ttk.Label(raw_frame, text="Processing Mode:").grid(row=0, column=0, sticky=tk.W, padx=5)
            raw_combo = ttk.Combobox(raw_frame, textvariable=self.raw_mode, 
                                    values=["full", "half", "preview"], state="readonly", width=15)
            raw_combo.grid(row=0, column=1, sticky=tk.W, padx=5)
            ttk.Label(raw_frame, text="(full=best quality/slow, half=balanced, preview=fast/lower quality)").grid(row=0, column=2, sticky=tk.W, padx=5)
        else:
            if sys.version_info >= (3, 14):
                msg = f"RAW support requires Python 3.8-3.13 (you have {py_version}). RAW files will be skipped."
            else:
                msg = f"Install rawpy for RAW support: pip install rawpy (Python {py_version})"
            ttk.Label(raw_frame, text=msg, foreground="gray").grid(row=0, column=0, columnspan=3, sticky=tk.W, padx=5)
        
        row += 1
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        row += 1
        
        # Process button
        self.process_btn = ttk.Button(main_frame, text="Start Processing", command=self.start_processing)
        self.process_btn.grid(row=row, column=0, columnspan=3, pady=10)
        row += 1
        
        # Log output
        log_frame = ttk.LabelFrame(main_frame, text="Processing Log", padding="5")
        log_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        main_frame.rowconfigure(row, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, state='disabled', wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
    
    def setup_logging(self):
        """Setup logging to GUI text widget."""
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        
        # Remove existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Add GUI handler
        gui_handler = TextHandler(self.log_text)
        gui_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(gui_handler)
    
    def browse_folder(self):
        """Browse for input folder."""
        folder = filedialog.askdirectory(title="Select Input Folder")
        if folder:
            self.input_path.set(folder)
            self.input_files = []  # Clear file selection
    
    def browse_files(self):
        """Browse for individual image files."""
        files = filedialog.askopenfilenames(
            title="Select Image Files",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff *.tif *.nef *.cr2 *.cr3 *.arw *.dng *.raf *.orf *.rw2 *.raw"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("PNG files", "*.png"),
                ("TIFF files", "*.tiff *.tif"),
                ("RAW files", "*.nef *.cr2 *.cr3 *.arw *.dng *.raf *.orf *.rw2 *.raw"),
                ("All files", "*.*")
            ]
        )
        if files:
            self.input_files = list(files)
            if len(files) == 1:
                self.input_path.set(files[0])
            else:
                self.input_path.set(f"{len(files)} files selected")
    
    def browse_output(self):
        """Browse for output folder."""
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_path.set(folder)
    
    def validate_inputs(self):
        """Validate user inputs."""
        if not self.input_path.get():
            messagebox.showerror("Error", "Please select input (folder or files)")
            return False
        
        if not self.output_path.get():
            messagebox.showerror("Error", "Please select an output folder")
            return False
        
        # Validate input exists
        if self.input_files:
            # Check if selected files exist
            for file in self.input_files:
                if not os.path.exists(file):
                    messagebox.showerror("Error", f"File does not exist: {os.path.basename(file)}")
                    return False
        else:
            # Check if folder exists
            if not os.path.exists(self.input_path.get()):
                messagebox.showerror("Error", "Input folder does not exist")
                return False
        
        if not (self.enable_gaussian.get() or self.enable_median.get() or self.enable_nonlocal.get()):
            messagebox.showerror("Error", "Please enable at least one filter")
            return False
        
        return True
    
    def create_config(self):
        """Create configuration from GUI inputs."""
        output = OutputConfig(
            format=self.output_format.get(),
            jpeg_quality=self.jpeg_quality.get(),
            preserve_original_format=False
        )
        
        filters = FilterConfig(
            enable_gaussian=self.enable_gaussian.get(),
            enable_median=self.enable_median.get(),
            enable_nonlocal=self.enable_nonlocal.get()
        )
        
        gaussian = GaussianConfig(sigma=self.gaussian_sigma.get())
        median = MedianConfig(size=self.median_size.get())
        
        nonlocal_means = NonLocalMeansConfig(
            h_multiplier=self.nl_h_multiplier.get(),
            fast_mode=self.nl_fast_mode.get(),
            patch_size=self.nl_patch_size.get(),
            patch_distance=self.nl_patch_distance.get()
        )
        
        raw = RAWConfig(
            processing_mode=self.raw_mode.get()
        )
        
        # Use folder path or first file's directory
        if self.input_files:
            input_path = os.path.dirname(self.input_files[0])
        else:
            input_path = self.input_path.get()
        
        return DenoiserConfig(
            input_path=input_path,
            output_path=self.output_path.get(),
            output=output,
            filters=filters,
            gaussian=gaussian,
            median=median,
            nonlocal_means=nonlocal_means,
            raw=raw
        )
    
    def start_processing(self):
        """Start image processing in a separate thread."""
        if self.processing:
            messagebox.showwarning("Warning", "Processing is already in progress")
            return
        
        if not self.validate_inputs():
            return
        
        # Clear log
        self.log_text.configure(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.configure(state='disabled')
        
        # Disable button
        self.process_btn.config(state='disabled', text="Processing...")
        self.processing = True
        
        # Start processing in thread
        thread = threading.Thread(target=self.process_images, daemon=True)
        thread.start()
    
    def process_images(self):
        """Process images (runs in separate thread)."""
        logger = logging.getLogger(__name__)
        
        try:
            config = self.create_config()
            
            if self.input_files:
                logger.info(f"Processing {len(self.input_files)} selected files")
                logger.info(f"Output folder: {config.output_path}")
                
                # Process selected files directly
                processor = ImageProcessor(config)
                processed_count, metrics_list = processor.process_files(self.input_files)
            else:
                logger.info(f"Input folder: {config.input_path}")
                logger.info(f"Output folder: {config.output_path}")
                
                # Process entire folder
                processor = ImageProcessor(config)
                processed_count, metrics_list = processor.process_batch()
            
            if processed_count > 0:
                csv_file = save_metrics_to_csv(metrics_list, config.output_path)
                logger.info(f"📊 Metrics saved to: {csv_file}")
                logger.info(f"✓ Successfully processed {processed_count} images")
                
                self.root.after(0, lambda: messagebox.showinfo(
                    "Success", 
                    f"Successfully processed {processed_count} images!\n\nMetrics saved to:\n{csv_file}"
                ))
            else:
                logger.warning("No images were processed")
                self.root.after(0, lambda: messagebox.showwarning(
                    "Warning", 
                    "No images were processed. Check the log for details."
                ))
        
        except Exception as e:
            logger.error(f"Error: {e}")
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred:\n{str(e)}"))
        
        finally:
            self.processing = False
            self.input_files = []  # Clear file selection
            self.root.after(0, lambda: self.process_btn.config(state='normal', text="Start Processing"))
    


def main():
    """Main entry point for GUI."""
    root = tk.Tk()
    app = DenoiserGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
