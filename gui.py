"""Simple GUI for Image Denoiser using tkinter."""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
import threading
import logging
from PIL import Image, ImageTk
from config_loader import DenoiserConfig, OutputConfig, FilterConfig, GaussianConfig, MedianConfig, NonLocalMeansConfig, RAWConfig
from processor import ImageProcessor
from metrics import save_metrics_to_csv
from image_io import is_rawpy_available
from tooltip import create_tooltip


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


class BeforeAfterWindow:
    """Interactive before/after comparison window with draggable slider."""
    
    def __init__(self, parent, before_path, after_path, title="Before/After Comparison"):
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry("1000x750")
        
        # Load images
        self.before_img = Image.open(before_path)
        self.after_img = Image.open(after_path)
        
        # Zoom state
        self.zoom_level = 1.0
        self.min_zoom = 0.25
        self.max_zoom = 4.0
        
        # Fixed canvas size
        self.canvas_width = 980
        self.canvas_height = 550
        
        # Scale images to fit canvas while maintaining aspect ratio
        self.max_width = self.canvas_width
        self.max_height = self.canvas_height
        self.scale_images(self.canvas_width, self.canvas_height)
        
        # Create canvas frame with scrollbars
        canvas_frame = ttk.Frame(self.window)
        canvas_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        # Create scrollbars
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL)
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL)
        
        # Create canvas with fixed size
        self.canvas = tk.Canvas(canvas_frame, 
                               width=self.canvas_width, 
                               height=self.canvas_height,
                               bg='black', 
                               highlightthickness=0,
                               xscrollcommand=h_scrollbar.set,
                               yscrollcommand=v_scrollbar.set)
        
        # Configure scrollbars
        h_scrollbar.config(command=self.canvas.xview)
        v_scrollbar.config(command=self.canvas.yview)
        
        # Grid layout for canvas and scrollbars
        self.canvas.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.E, tk.W))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        canvas_frame.rowconfigure(0, weight=1)
        canvas_frame.columnconfigure(0, weight=1)
        
        # Set scroll region
        self.canvas.config(scrollregion=(0, 0, self.display_width, self.display_height))
        
        # Convert to PhotoImage
        self.before_photo = ImageTk.PhotoImage(self.before_scaled)
        self.after_photo = ImageTk.PhotoImage(self.after_scaled)
        
        # Display images
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.before_photo, tags="before")
        self.after_id = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.after_photo, tags="after")
        
        # Create slider line
        self.slider_x = self.display_width // 2
        self.slider_line = self.canvas.create_line(
            self.slider_x, 0, self.slider_x, self.display_height,
            fill='white', width=3, tags="slider"
        )
        
        # Create slider handle
        handle_y = self.display_height // 2
        handle_size = 30
        self.slider_handle = self.canvas.create_oval(
            self.slider_x - handle_size, handle_y - handle_size,
            self.slider_x + handle_size, handle_y + handle_size,
            fill='white', outline='black', width=2, tags="slider"
        )
        
        # Add labels on handle
        self.canvas.create_text(
            self.slider_x, handle_y - 5,
            text="◀", fill='black', font=('Arial', 12, 'bold'), tags="slider"
        )
        self.canvas.create_text(
            self.slider_x, handle_y + 5,
            text="▶", fill='black', font=('Arial', 12, 'bold'), tags="slider"
        )
        
        # Clip the after image
        self.update_clip()
        
        # Zoom controls
        zoom_frame = ttk.Frame(self.window)
        zoom_frame.pack(pady=5)
        
        ttk.Button(zoom_frame, text="🔍−", command=self.zoom_out, width=5).pack(side=tk.LEFT, padx=5)
        self.zoom_label = ttk.Label(zoom_frame, text="100%", font=('Arial', 10))
        self.zoom_label.pack(side=tk.LEFT, padx=10)
        ttk.Button(zoom_frame, text="🔍+", command=self.zoom_in, width=5).pack(side=tk.LEFT, padx=5)
        ttk.Button(zoom_frame, text="Reset", command=self.zoom_reset, width=8).pack(side=tk.LEFT, padx=5)
        
        # Info labels
        info_frame = ttk.Frame(self.window)
        info_frame.pack(pady=5)
        
        ttk.Label(info_frame, text="◀ BEFORE", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=20)
        ttk.Label(info_frame, text="Drag the slider to compare", font=('Arial', 10)).pack(side=tk.LEFT, padx=20)
        ttk.Label(info_frame, text="AFTER ▶", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=20)
        
        # Bind mouse events
        self.canvas.bind('<Button-1>', self.on_click)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_release)
        self.canvas.bind('<MouseWheel>', self.on_mousewheel)  # Windows/Mac
        self.canvas.bind('<Button-4>', self.on_mousewheel)    # Linux scroll up
        self.canvas.bind('<Button-5>', self.on_mousewheel)    # Linux scroll down
        
        self.dragging = False
    
    def scale_images(self, max_width, max_height):
        """Scale images to fit display while maintaining aspect ratio."""
        width, height = self.before_img.size
        
        # Calculate scale factor
        scale_w = max_width / width
        scale_h = max_height / height
        scale = min(scale_w, scale_h, 1.0)  # Don't upscale
        
        self.display_width = int(width * scale)
        self.display_height = int(height * scale)
        
        # Resize images
        self.before_scaled = self.before_img.resize(
            (self.display_width, self.display_height), 
            Image.Resampling.LANCZOS
        )
        self.after_scaled = self.after_img.resize(
            (self.display_width, self.display_height), 
            Image.Resampling.LANCZOS
        )
    
    def update_clip(self):
        """Update the clipping region for the after image."""
        # Create a clipped version of the after image
        clipped = self.after_scaled.crop((0, 0, self.slider_x, self.display_height))
        self.after_photo = ImageTk.PhotoImage(clipped)
        self.canvas.itemconfig(self.after_id, image=self.after_photo)
    
    def zoom_in(self):
        """Zoom in by 25%."""
        new_zoom = min(self.zoom_level * 1.25, self.max_zoom)
        if new_zoom != self.zoom_level:
            self.zoom_level = new_zoom
            self.apply_zoom()
    
    def zoom_out(self):
        """Zoom out by 25%."""
        new_zoom = max(self.zoom_level / 1.25, self.min_zoom)
        if new_zoom != self.zoom_level:
            self.zoom_level = new_zoom
            self.apply_zoom()
    
    def zoom_reset(self):
        """Reset zoom to 100%."""
        if self.zoom_level != 1.0:
            self.zoom_level = 1.0
            self.apply_zoom()
    
    def on_mousewheel(self, event):
        """Handle mouse wheel zoom."""
        # Windows/Mac use event.delta, Linux uses event.num
        if hasattr(event, 'delta'):
            delta = event.delta
        elif event.num == 4:
            delta = 120  # Scroll up
        elif event.num == 5:
            delta = -120  # Scroll down
        else:
            return
        
        if delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()
    
    def apply_zoom(self):
        """Apply current zoom level to images."""
        # Calculate new dimensions
        width, height = self.before_img.size
        scale_w = self.max_width / width
        scale_h = self.max_height / height
        base_scale = min(scale_w, scale_h, 1.0)
        
        final_scale = base_scale * self.zoom_level
        
        new_width = int(width * final_scale)
        new_height = int(height * final_scale)
        
        # Resize images
        self.before_scaled = self.before_img.resize(
            (new_width, new_height), 
            Image.Resampling.LANCZOS
        )
        self.after_scaled = self.after_img.resize(
            (new_width, new_height), 
            Image.Resampling.LANCZOS
        )
        
        # Update display dimensions
        old_width = self.display_width
        self.display_width = new_width
        self.display_height = new_height
        
        # Update scroll region (canvas stays same size, content grows/shrinks)
        self.canvas.config(scrollregion=(0, 0, self.display_width, self.display_height))
        
        # Update images
        self.before_photo = ImageTk.PhotoImage(self.before_scaled)
        self.canvas.itemconfig("before", image=self.before_photo)
        
        # Adjust slider position proportionally
        if old_width > 0:
            self.slider_x = int(self.slider_x * self.display_width / old_width)
        else:
            self.slider_x = self.display_width // 2
        
        # Update slider
        handle_y = self.display_height // 2
        handle_size = 30
        
        self.canvas.coords(self.slider_line, 
                         self.slider_x, 0, self.slider_x, self.display_height)
        self.canvas.coords(self.slider_handle,
                         self.slider_x - handle_size, handle_y - handle_size,
                         self.slider_x + handle_size, handle_y + handle_size)
        
        # Update text positions
        items = self.canvas.find_withtag("slider")
        for item in items:
            if self.canvas.type(item) == "text":
                _, y = self.canvas.coords(item)
                if "◀" in str(self.canvas.itemcget(item, "text")):
                    self.canvas.coords(item, self.slider_x, handle_y - 5)
                else:
                    self.canvas.coords(item, self.slider_x, handle_y + 5)
        
        # Update clipped image
        self.update_clip()
        
        # Update zoom label
        self.zoom_label.config(text=f"{int(self.zoom_level * 100)}%")
        
        # Center the view when zooming in
        if self.zoom_level > 1.0:
            # Center on the slider position
            x_center = self.slider_x / self.display_width
            y_center = 0.5
            self.canvas.xview_moveto(max(0, x_center - 0.5))
            self.canvas.yview_moveto(max(0, y_center - 0.5))
    
    def on_click(self, event):
        """Handle mouse click."""
        # Convert event coordinates to canvas coordinates
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        # Check if click is near slider
        if abs(canvas_x - self.slider_x) < 40:
            self.dragging = True
    
    def on_drag(self, event):
        """Handle mouse drag."""
        if self.dragging:
            # Convert event coordinates to canvas coordinates
            canvas_x = self.canvas.canvasx(event.x)
            
            # Constrain to canvas bounds
            self.slider_x = max(0, min(canvas_x, self.display_width))
            
            # Update slider position
            handle_y = self.display_height // 2
            handle_size = 30
            
            self.canvas.coords(self.slider_line, 
                             self.slider_x, 0, self.slider_x, self.display_height)
            self.canvas.coords(self.slider_handle,
                             self.slider_x - handle_size, handle_y - handle_size,
                             self.slider_x + handle_size, handle_y + handle_size)
            
            # Update text positions
            items = self.canvas.find_withtag("slider")
            for item in items:
                if self.canvas.type(item) == "text":
                    _, y = self.canvas.coords(item)
                    self.canvas.coords(item, self.slider_x, y)
            
            # Update clipping
            self.update_clip()
    
    def on_release(self, event):
        """Handle mouse release."""
        self.dragging = False


class DenoiserGUI:
    """GUI application for image denoising."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Image Denoiser")
        self.root.geometry("800x850")  # Increased height to always show logs
        
        # Set application icon if available
        self.set_app_icon()
        
        # Variables
        self.input_path = tk.StringVar()
        self.input_files = []  # Store selected files
        self.output_path = tk.StringVar()
        self.output_format = tk.StringVar(value="png")
        self.jpeg_quality = tk.IntVar(value=95)
        self.preserve_color = tk.BooleanVar(value=True)
        self.apply_sharpening = tk.BooleanVar(value=False)
        self.sharpen_amount = tk.DoubleVar(value=1.2)
        self.sharpen_radius = tk.DoubleVar(value=1.5)
        self.boost_saturation = tk.BooleanVar(value=False)
        self.saturation_amount = tk.DoubleVar(value=1.3)
        
        # Filter toggles
        self.enable_gaussian = tk.BooleanVar(value=True)
        self.enable_median = tk.BooleanVar(value=True)
        self.enable_nonlocal = tk.BooleanVar(value=True)
        
        # Filter parameters
        self.gaussian_sigma = tk.DoubleVar(value=0.75)
        self.median_size = tk.IntVar(value=3)
        self.nl_h_multiplier = tk.DoubleVar(value=0.85)
        self.nl_fast_mode = tk.BooleanVar(value=True)
        self.nl_patch_size = tk.IntVar(value=3)
        self.nl_patch_distance = tk.IntVar(value=3)
        
        # RAW processing mode
        self.raw_mode = tk.StringVar(value="half")
        
        self.processing = False
        self.last_processed_files = []  # Store paths for comparison
        
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
        input_label = ttk.Label(main_frame, text="Input:")
        input_label.grid(row=row, column=0, sticky=tk.W, pady=5)
        create_tooltip(input_label, "Select images to denoise:\n• Folder: Process all images in a folder\n• Files: Select specific images")
        
        ttk.Entry(main_frame, textvariable=self.input_path, width=50).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Input buttons frame
        input_btn_frame = ttk.Frame(main_frame)
        input_btn_frame.grid(row=row, column=2, padx=(5, 0), pady=5)
        folder_btn = ttk.Button(input_btn_frame, text="Folder", command=self.browse_folder, width=8)
        folder_btn.pack(side=tk.LEFT, padx=2)
        create_tooltip(folder_btn, "Select a folder to process all images inside")
        
        files_btn = ttk.Button(input_btn_frame, text="Files", command=self.browse_files, width=8)
        files_btn.pack(side=tk.LEFT, padx=2)
        create_tooltip(files_btn, "Select one or more specific image files")
        row += 1
        
        # Output folder
        output_label = ttk.Label(main_frame, text="Output Folder:")
        output_label.grid(row=row, column=0, sticky=tk.W, pady=5)
        create_tooltip(output_label, "Where to save denoised images")
        
        ttk.Entry(main_frame, textvariable=self.output_path, width=50).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Button(main_frame, text="Browse...", command=self.browse_output).grid(row=row, column=2, padx=(5, 0), pady=5)
        row += 1
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        row += 1
        
        # Output settings
        output_frame = ttk.LabelFrame(main_frame, text="Output Settings", padding="5")
        output_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        format_label = ttk.Label(output_frame, text="Format:")
        format_label.grid(row=0, column=0, sticky=tk.W, padx=5)
        create_tooltip(format_label, "PNG: Lossless, best quality\nJPEG: Smaller files, some quality loss\nTIFF: Lossless, large files")
        
        format_combo = ttk.Combobox(output_frame, textvariable=self.output_format, 
                                    values=["png", "jpg", "tiff"], state="readonly", width=10)
        format_combo.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        quality_label = ttk.Label(output_frame, text="JPEG Quality:")
        quality_label.grid(row=0, column=2, sticky=tk.W, padx=(20, 5))
        create_tooltip(quality_label, "JPEG quality (1-100)\n90-95: High quality\n80-89: Good quality\n70-79: Medium quality")
        
        ttk.Spinbox(output_frame, from_=1, to=100, textvariable=self.jpeg_quality, width=10).grid(row=0, column=3, sticky=tk.W, padx=5)
        
        color_check = ttk.Checkbutton(output_frame, text="Preserve Color (denoise luminance only)", 
                       variable=self.preserve_color)
        color_check.grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        create_tooltip(color_check, "Recommended: Denoises only brightness,\nkeeping colors vibrant and saturated.\nDisable for grayscale images.")
        
        sharpen_check = ttk.Checkbutton(output_frame, text="Apply Sharpening (recommended with Non-local)", 
                       variable=self.apply_sharpening)
        sharpen_check.grid(row=1, column=2, columnspan=2, sticky=tk.W, padx=5, pady=5)
        create_tooltip(sharpen_check, "Restores structure and detail after denoising.\nWorks best with Non-local Means filter.")
        
        # Sharpening controls
        amount_label = ttk.Label(output_frame, text="Sharpen Amount:")
        amount_label.grid(row=2, column=0, sticky=tk.W, padx=5)
        create_tooltip(amount_label, "Sharpening strength:\n0.5-1.0: Subtle\n1.0-1.5: Moderate (default)\n1.5-2.0: Strong")
        ttk.Spinbox(output_frame, from_=0.0, to=2.0, increment=0.1, textvariable=self.sharpen_amount, width=10).grid(row=2, column=1, sticky=tk.W, padx=5)
        
        radius_label = ttk.Label(output_frame, text="Sharpen Radius:")
        radius_label.grid(row=2, column=2, sticky=tk.W, padx=(20, 5))
        create_tooltip(radius_label, "Sharpening radius:\n0.5-1.0: Fine details\n1.0-2.0: Balanced (default)\n2.0-3.0: Broader")
        ttk.Spinbox(output_frame, from_=0.5, to=3.0, increment=0.1, textvariable=self.sharpen_radius, width=10).grid(row=2, column=3, sticky=tk.W, padx=5)
        
        # Saturation boost
        saturation_check = ttk.Checkbutton(output_frame, text="Boost Saturation (enhance colors)", 
                       variable=self.boost_saturation)
        saturation_check.grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        create_tooltip(saturation_check, "Enhance color vibrancy after processing.\nMakes colors more vivid and saturated.")
        
        saturation_label = ttk.Label(output_frame, text="Saturation Amount:")
        saturation_label.grid(row=3, column=2, sticky=tk.W, padx=(20, 5))
        create_tooltip(saturation_label, "Saturation boost strength:\n1.0: No change\n1.3: Moderate (default)\n1.5-2.0: Strong")
        ttk.Spinbox(output_frame, from_=1.0, to=2.0, increment=0.1, textvariable=self.saturation_amount, width=10).grid(row=3, column=3, sticky=tk.W, padx=5)
        
        row += 1
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        row += 1
        
        # Quick Presets section
        presets_frame = ttk.LabelFrame(main_frame, text="Quick Presets", padding="5")
        presets_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(presets_frame, text="Optimize for:").grid(row=0, column=0, sticky=tk.W, padx=5)
        
        preset_photos = ttk.Button(presets_frame, text="📷 Photos", command=self.preset_photos, width=14)
        preset_photos.grid(row=0, column=1, padx=5)
        create_tooltip(preset_photos, "Best for: Portraits, landscapes, general photos\n• Non-local Means only\n• Color preservation ON\n• Sharpening ON")
        
        preset_docs = ttk.Button(presets_frame, text="📄 Documents", command=self.preset_documents, width=15)
        preset_docs.grid(row=0, column=2, padx=5)
        create_tooltip(preset_docs, "Best for: Scanned documents, text\n• Median filter only\n• Color preservation OFF\n• Sharpening ON")
        
        preset_lowlight = ttk.Button(presets_frame, text="🌙 Low-Light", command=self.preset_lowlight, width=14)
        preset_lowlight.grid(row=0, column=3, padx=5)
        create_tooltip(preset_lowlight, "Best for: Night photos, high ISO\n• Non-local Means (aggressive)\n• Color preservation ON\n• Sharpening ON")
        
        preset_compare = ttk.Button(presets_frame, text="🔍 Compare All", command=self.preset_compare, width=16)
        preset_compare.grid(row=0, column=4, padx=5)
        create_tooltip(preset_compare, "Compare all filters\n• All filters enabled\n• See which works best")
        
        row += 1
        
        # Filters section
        filters_frame = ttk.LabelFrame(main_frame, text="Filters (Tip: Non-local Means gives best results)", padding="5")
        filters_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Gaussian filter
        gaussian_check = ttk.Checkbutton(filters_frame, text="Gaussian Filter", variable=self.enable_gaussian)
        gaussian_check.grid(row=0, column=0, sticky=tk.W, pady=2)
        create_tooltip(gaussian_check, "Fast smoothing filter.\nGood for: Quick processing, backgrounds\nCons: May blur fine details")
        
        gaussian_sigma_label = ttk.Label(filters_frame, text="Sigma:")
        gaussian_sigma_label.grid(row=0, column=1, sticky=tk.W, padx=(20, 5))
        create_tooltip(gaussian_sigma_label, "Blur strength:\n0.5: Light smoothing\n0.75: Moderate (default)\n1.0-2.0: Heavy smoothing")
        ttk.Spinbox(filters_frame, from_=0.1, to=3.0, increment=0.1, textvariable=self.gaussian_sigma, width=10).grid(row=0, column=2, sticky=tk.W)
        ttk.Label(filters_frame, text="Fast, smooth - may blur details", foreground="gray").grid(row=0, column=3, sticky=tk.W, padx=5)
        
        # Median filter
        median_check = ttk.Checkbutton(filters_frame, text="Median Filter", variable=self.enable_median)
        median_check.grid(row=1, column=0, sticky=tk.W, pady=2)
        create_tooltip(median_check, "Removes salt-and-pepper noise.\nGood for: Scanned documents, digital artifacts\nCons: Can lose fine detail")
        
        median_size_label = ttk.Label(filters_frame, text="Size:")
        median_size_label.grid(row=1, column=1, sticky=tk.W, padx=(20, 5))
        create_tooltip(median_size_label, "Filter window size (odd numbers):\n3: Light filtering (default)\n5: Moderate\n7+: Heavy filtering")
        ttk.Spinbox(filters_frame, from_=3, to=11, increment=2, textvariable=self.median_size, width=10).grid(row=1, column=2, sticky=tk.W)
        ttk.Label(filters_frame, text="Good for salt-and-pepper noise", foreground="gray").grid(row=1, column=3, sticky=tk.W, padx=5)
        
        # Non-local means filter
        nonlocal_check = ttk.Checkbutton(filters_frame, text="Non-local Means ⭐", variable=self.enable_nonlocal)
        nonlocal_check.grid(row=2, column=0, sticky=tk.W, pady=2)
        create_tooltip(nonlocal_check, "⭐ RECOMMENDED - Best quality filter!\nPreserves edges, textures, and fine details.\nGood for: All photos, portraits, landscapes\nSlower but worth it!")
        
        nl_h_label = ttk.Label(filters_frame, text="h multiplier:")
        nl_h_label.grid(row=2, column=1, sticky=tk.W, padx=(20, 5))
        create_tooltip(nl_h_label, "Denoising strength:\n0.6-0.8: Preserve detail\n0.85: Balanced (default)\n1.0-1.5: More noise removal")
        ttk.Spinbox(filters_frame, from_=0.5, to=2.0, increment=0.05, textvariable=self.nl_h_multiplier, width=10).grid(row=2, column=2, sticky=tk.W)
        ttk.Label(filters_frame, text="Best quality - preserves edges & detail", foreground="green").grid(row=2, column=3, sticky=tk.W, padx=5)
        
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
            raw_mode_label = ttk.Label(raw_frame, text="Processing Mode:")
            raw_mode_label.grid(row=0, column=0, sticky=tk.W, padx=5)
            create_tooltip(raw_mode_label, "RAW processing mode:\nFull: Best quality, slowest\nHalf: Balanced (recommended)\nPreview: Fastest, lower quality")
            
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
        
        # Action buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=3, pady=10)
        
        self.process_btn = ttk.Button(button_frame, text="Start Processing", command=self.start_processing, width=22)
        self.process_btn.pack(side=tk.LEFT, padx=5)
        
        self.compare_btn = ttk.Button(button_frame, text="🔍 View Comparison", command=self.show_comparison_window, width=25)
        self.compare_btn.pack(side=tk.LEFT, padx=5)
        self.compare_btn.config(state='disabled')  # Disabled until processing completes
        create_tooltip(self.compare_btn, "View before/after comparison of processed images\n(Available after processing)")
        
        row += 1
        
        # Progress section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="5")
        progress_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Current file label
        self.progress_label = ttk.Label(progress_frame, text="Ready to process")
        self.progress_label.pack(fill=tk.X, pady=(0, 5))
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate', length=400)
        self.progress_bar.pack(fill=tk.X)
        
        # Percentage label
        self.progress_percent = ttk.Label(progress_frame, text="0%")
        self.progress_percent.pack(fill=tk.X, pady=(5, 0))
        
        row += 1
        
        # Log output
        log_frame = ttk.LabelFrame(main_frame, text="Processing Log", padding="5")
        log_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        main_frame.rowconfigure(row, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, state='disabled', wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
    
    def set_app_icon(self):
        """Set application icon if available."""
        try:
            # Try to load icon file
            if os.path.exists('icon.ico'):
                self.root.iconbitmap('icon.ico')
            elif os.path.exists('icon.png'):
                # For PNG, convert to PhotoImage (works on all platforms)
                icon_image = tk.PhotoImage(file='icon.png')
                self.root.iconphoto(True, icon_image)
            
            # Windows-specific: Set taskbar icon
            if sys.platform == 'win32':
                try:
                    import ctypes
                    # Tell Windows this is a separate app (not Python)
                    myappid = 'imagedenoiser.gui.1.0'  # Arbitrary string
                    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
                except Exception:
                    pass  # Not critical if this fails
        except Exception as e:
            # Silently fail if icon can't be loaded
            pass
    
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
            preserve_original_format=False,
            preserve_color=self.preserve_color.get(),
            apply_sharpening=self.apply_sharpening.get(),
            sharpen_amount=self.sharpen_amount.get(),
            sharpen_radius=self.sharpen_radius.get(),
            boost_saturation=self.boost_saturation.get(),
            saturation_amount=self.saturation_amount.get()
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
        
        # Reset progress
        self.progress_bar['value'] = 0
        self.progress_percent.config(text="0%")
        self.progress_label.config(text="Starting...")
        
        # Start processing in thread
        thread = threading.Thread(target=self.process_images, daemon=True)
        thread.start()
    
    def preset_photos(self):
        """Apply preset for photos (portraits, landscapes)."""
        self.enable_gaussian.set(False)
        self.enable_median.set(False)
        self.enable_nonlocal.set(True)
        self.nl_h_multiplier.set(0.85)
        self.nl_patch_size.set(3)
        self.nl_patch_distance.set(3)
        self.preserve_color.set(True)
        self.apply_sharpening.set(True)
        self.sharpen_amount.set(1.2)
        self.sharpen_radius.set(1.5)
        self.log_message("Applied preset: Photos (portraits, landscapes)")
    
    def preset_documents(self):
        """Apply preset for scanned documents."""
        self.enable_gaussian.set(False)
        self.enable_median.set(True)
        self.enable_nonlocal.set(False)
        self.median_size.set(3)
        self.preserve_color.set(False)
        self.apply_sharpening.set(True)
        self.sharpen_amount.set(1.5)
        self.sharpen_radius.set(1.0)
        self.log_message("Applied preset: Documents (scanned text)")
    
    def preset_lowlight(self):
        """Apply preset for low-light/high ISO photos."""
        self.enable_gaussian.set(False)
        self.enable_median.set(False)
        self.enable_nonlocal.set(True)
        self.nl_h_multiplier.set(1.2)
        self.nl_patch_size.set(5)
        self.nl_patch_distance.set(5)
        self.preserve_color.set(True)
        self.apply_sharpening.set(True)
        self.sharpen_amount.set(1.5)
        self.sharpen_radius.set(1.5)
        self.log_message("Applied preset: Low-Light (night photos, high ISO)")
    
    def preset_compare(self):
        """Apply preset to compare all filters."""
        self.enable_gaussian.set(True)
        self.enable_median.set(True)
        self.enable_nonlocal.set(True)
        self.gaussian_sigma.set(0.75)
        self.median_size.set(3)
        self.nl_h_multiplier.set(0.85)
        self.nl_patch_size.set(3)
        self.nl_patch_distance.set(3)
        self.preserve_color.set(True)
        self.apply_sharpening.set(False)
        self.log_message("Applied preset: Compare All Filters")
    
    def log_message(self, message):
        """Add a message to the log."""
        self.log_text.configure(state='normal')
        self.log_text.insert(tk.END, f"ℹ {message}\n")
        self.log_text.configure(state='disabled')
        self.log_text.see(tk.END)
    
    def update_progress(self, current, total, filename):
        """Update progress bar and labels."""
        progress = (current / total * 100) if total > 0 else 0
        self.progress_bar['value'] = progress
        self.progress_percent.config(text=f"{progress:.1f}%")
        self.progress_label.config(text=f"Processing: {filename} ({current}/{total})")
    
    def show_comparison_dialog(self, processed_count, csv_file):
        """Show success dialog with option to view comparison."""
        # Check if we should offer comparison (non-Photos preset or Compare All)
        multiple_filters = sum([
            self.enable_gaussian.get(),
            self.enable_median.get(),
            self.enable_nonlocal.get()
        ]) > 1
        
        if multiple_filters and self.last_processed_files:
            response = messagebox.askyesno(
                "Success", 
                f"Successfully processed {processed_count} images!\n\n"
                f"Metrics saved to:\n{csv_file}\n\n"
                "Would you like to view a before/after comparison?"
            )
            if response:
                self.show_comparison_window()
        else:
            messagebox.showinfo(
                "Success", 
                f"Successfully processed {processed_count} images!\n\nMetrics saved to:\n{csv_file}"
            )
    
    def show_comparison_window(self):
        """Open before/after comparison window for first processed image."""
        if not self.last_processed_files:
            messagebox.showinfo("No Images", "Please process some images first before viewing comparison.")
            return
        
        # Use first processed file
        original_path = self.last_processed_files[0]
        
        # Find corresponding output file
        config = self.create_config()
        base_name = os.path.splitext(os.path.basename(original_path))[0]
        
        # Check for different filter outputs
        filter_suffixes = []
        if self.enable_gaussian.get():
            filter_suffixes.append('gaussian')
        if self.enable_median.get():
            filter_suffixes.append('median')
        if self.enable_nonlocal.get():
            filter_suffixes.append('nonlocal')
        
        # If multiple filters, show first one found
        output_path = None
        for suffix in filter_suffixes:
            test_path = os.path.join(
                config.output_path,
                f"{base_name}_{suffix}.{config.output.format}"
            )
            if os.path.exists(test_path):
                output_path = test_path
                break
        
        if output_path and os.path.exists(output_path):
            try:
                BeforeAfterWindow(self.root, original_path, output_path)
            except Exception as e:
                messagebox.showerror("Error", f"Could not open comparison window:\n{str(e)}")
        else:
            messagebox.showwarning("Warning", "Could not find processed image for comparison")
    
    def process_images(self):
        """Process images (runs in separate thread)."""
        logger = logging.getLogger(__name__)
        
        try:
            config = self.create_config()
            
            # Store file list locally to avoid clearing during processing
            files_to_process = self.input_files.copy() if self.input_files else []
            
            if files_to_process:
                logger.info(f"Processing {len(files_to_process)} selected files")
                logger.info(f"Output folder: {config.output_path}")
                
                # Store for comparison
                self.last_processed_files = files_to_process.copy()
                
                # Process selected files directly with progress callback
                processor = ImageProcessor(config)
                processed_count, metrics_list = processor.process_files(
                    files_to_process, 
                    progress_callback=lambda c, t, f: self.root.after(0, self.update_progress, c, t, f)
                )
            else:
                logger.info(f"Input folder: {config.input_path}")
                logger.info(f"Output folder: {config.output_path}")
                
                # Get list of files in folder for comparison
                import glob
                pattern = os.path.join(config.input_path, "*")
                all_files = glob.glob(pattern)
                image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', 
                                  '.nef', '.cr2', '.cr3', '.arw', '.dng', '.raf', '.orf', '.rw2', '.raw'}
                self.last_processed_files = [f for f in all_files 
                                            if os.path.splitext(f.lower())[1] in image_extensions]
                
                # Process entire folder with progress callback
                processor = ImageProcessor(config)
                processed_count, metrics_list = processor.process_batch(
                    progress_callback=lambda c, t, f: self.root.after(0, self.update_progress, c, t, f)
                )
            
            if processed_count > 0:
                csv_file = save_metrics_to_csv(metrics_list, config.output_path)
                logger.info(f"📊 Metrics saved to: {csv_file}")
                logger.info(f"✓ Successfully processed {processed_count} images")
                
                # Update progress to complete
                self.root.after(0, lambda: self.progress_bar.config(value=100))
                self.root.after(0, lambda: self.progress_percent.config(text="100%"))
                self.root.after(0, lambda: self.progress_label.config(text=f"Complete! Processed {processed_count} images"))
                
                # Enable Compare button
                self.root.after(0, lambda: self.compare_btn.config(state='normal'))
                
                # Brief pause to show completion before dialog (1 second)
                import time
                time.sleep(1)
                
                # Show dialog with comparison option
                self.root.after(0, lambda: self.show_comparison_dialog(processed_count, csv_file))
            else:
                logger.warning("No images were processed")
                self.root.after(0, lambda: self.progress_label.config(text="No images processed"))
                self.root.after(0, lambda: messagebox.showwarning(
                    "Warning", 
                    "No images were processed. Check the log for details."
                ))
        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error: {error_msg}")
            self.root.after(0, lambda: self.progress_label.config(text="Error occurred"))
            self.root.after(0, lambda msg=error_msg: messagebox.showerror("Error", f"An error occurred:\n{msg}"))
        
        finally:
            self.processing = False
            # Don't clear input_files - keep selection for successive runs
            self.root.after(0, lambda: self.process_btn.config(state='normal', text="Start Processing"))
    


def main():
    """Main entry point for GUI."""
    root = tk.Tk()
    app = DenoiserGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
