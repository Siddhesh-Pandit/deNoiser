# Copyright (c) 2025 Adwait Godbole and Siddhesh Pandit
# Licensed under CC BY-NC 4.0 (Attribution-NonCommercial 4.0 International)
# https://creativecommons.org/licenses/by-nc/4.0/
# For commercial use, please contact the authors.

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
        
        # Set up proper window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Variables
        self.input_path = tk.StringVar()
        self.input_files = []  # Store selected files
        self.output_path = tk.StringVar()
        self.output_format = tk.StringVar(value="png")
        
        # Load saved output folder
        self.load_saved_output_folder()
        self.jpeg_quality = tk.IntVar(value=95)
        self.preserve_color = tk.BooleanVar(value=True)
        self.apply_sharpening = tk.BooleanVar(value=False)
        self.sharpen_amount = tk.DoubleVar(value=1.2)
        self.sharpen_radius = tk.DoubleVar(value=1.5)
        self.boost_saturation = tk.BooleanVar(value=False)
        self.saturation_amount = tk.DoubleVar(value=1.3)
        self.boost_brightness = tk.BooleanVar(value=False)
        self.brightness_amount = tk.DoubleVar(value=1.1)
        
        # Filter toggles
        self.enable_gaussian = tk.BooleanVar(value=True)
        self.enable_median = tk.BooleanVar(value=True)
        self.enable_nonlocal = tk.BooleanVar(value=True)
        
        # AI Denoiser
        self.enable_ai = tk.BooleanVar(value=False)
        self.ai_model = tk.StringVar(value='scunet')
        self.ai_device = tk.StringVar(value='auto')
        
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
        self.current_mask = None  # Store mask for selective denoising
        self.mask_cache = {}  # Cache masks per image path
        
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
        
        # Quick Presets section (moved before Output Settings for better workflow)
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
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        row += 1
        
        # Output settings (moved after Presets)
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
        
        # Brightness boost
        brightness_check = ttk.Checkbutton(output_frame, text="Boost Brightness (lighten image)", 
                       variable=self.boost_brightness)
        brightness_check.grid(row=4, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        create_tooltip(brightness_check, "Increase image brightness/luminance.\nUseful if denoising darkens the image.")
        
        brightness_label = ttk.Label(output_frame, text="Brightness Amount:")
        brightness_label.grid(row=4, column=2, sticky=tk.W, padx=(20, 5))
        create_tooltip(brightness_label, "Brightness boost strength:\n1.0: No change\n1.1: Subtle (default)\n1.2-1.5: Strong")
        ttk.Spinbox(output_frame, from_=0.8, to=1.5, increment=0.05, textvariable=self.brightness_amount, width=10).grid(row=4, column=3, sticky=tk.W, padx=5)
        
        # Selective denoising (Edit Mask)
        ttk.Separator(output_frame, orient='horizontal').grid(row=5, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10)
        
        self.edit_mask_btn = ttk.Button(output_frame, text="🎨 Edit Mask (Selective Denoising)", 
                                        command=self.open_mask_editor, width=35)
        self.edit_mask_btn.grid(row=6, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        self.edit_mask_btn.config(state='disabled')
        create_tooltip(self.edit_mask_btn, "Paint areas to denoise.\nOnly masked areas will be processed.\n(Available for single file selection)")
        
        self.mask_status = ttk.Label(output_frame, text="", foreground="green", font=('Arial', 9, 'bold'))
        self.mask_status.grid(row=6, column=2, columnspan=2, sticky=tk.W, padx=5)
        
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
        
        # AI Denoiser section
        ai_frame = ttk.LabelFrame(main_frame, text="AI Denoiser (Optional - Requires PyTorch)", padding="5")
        ai_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ai_check = ttk.Checkbutton(ai_frame, text="Enable AI Denoiser 🤖", 
                                   variable=self.enable_ai,
                                   command=self.on_ai_toggle)
        ai_check.grid(row=0, column=0, sticky=tk.W, pady=2)
        create_tooltip(ai_check, "Use neural network for denoising.\nBetter quality but slower.\nRequires: pip install -r requirements-ai.txt")
        
        ttk.Label(ai_frame, text="Model:").grid(row=0, column=1, sticky=tk.W, padx=(20, 5))
        model_combo = ttk.Combobox(ai_frame, textvariable=self.ai_model,
                                   values=['scunet', 'nafnet'], width=10, state='readonly')
        model_combo.grid(row=0, column=2, sticky=tk.W)
        create_tooltip(model_combo, "SCUNet: Faster, 3MB model\nNAFNet: Better quality, 9MB model")
        
        self.ai_status_label = ttk.Label(ai_frame, text="", foreground="blue")
        self.ai_status_label.grid(row=0, column=3, sticky=tk.W, padx=10)
        
        # Reinstall/Update button
        self.ai_reinstall_btn = ttk.Button(ai_frame, text="⚙️ GPU Setup", 
                                           command=self.show_pytorch_options, width=15)
        self.ai_reinstall_btn.grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        create_tooltip(self.ai_reinstall_btn, "Install or update PyTorch with GPU support.\nUse this to add NVIDIA/AMD GPU support.")
        
        # Check AI availability on startup
        self.check_ai_availability()
        
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
        
        # AI status label (shown during AI processing)
        self.ai_status_label = ttk.Label(progress_frame, text="", foreground="blue", font=('Arial', 9, 'italic'))
        self.ai_status_label.pack(fill=tk.X, pady=(0, 5))
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate', length=400)
        self.progress_bar.pack(fill=tk.X)
        
        # Percentage label
        self.progress_percent = ttk.Label(progress_frame, text="0%")
        self.progress_percent.pack(fill=tk.X, pady=(5, 0))
        
        row += 1
        
        # Log output with button
        log_frame = ttk.LabelFrame(main_frame, text="Processing Log", padding="5")
        log_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        main_frame.rowconfigure(row, weight=1)
        
        # Log controls
        log_controls = ttk.Frame(log_frame)
        log_controls.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(log_controls, text="📋 View in Separate Window", 
                  command=self.show_log_window, width=25).pack(side=tk.LEFT, padx=5)
        ttk.Button(log_controls, text="🗑️ Clear Log", 
                  command=self.clear_log, width=12).pack(side=tk.LEFT, padx=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, state='disabled', wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
    
    def set_app_icon(self):
        """Set application icon if available."""
        # Windows-specific: Set taskbar icon FIRST (before setting window icon)
        if sys.platform == 'win32':
            try:
                import ctypes
                # Tell Windows this is a separate app (not Python)
                myappid = 'imagedenoiser.gui.1.0'  # Arbitrary string
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            except Exception:
                pass  # Not critical if this fails
        
        try:
            # Try to load icon file
            if os.path.exists('icon.ico'):
                self.root.iconbitmap('icon.ico')
            elif os.path.exists('icon.png'):
                # For PNG, convert to PhotoImage (works on all platforms)
                icon_image = tk.PhotoImage(file='icon.png')
                self.root.iconphoto(True, icon_image)
        except Exception as e:
            # Silently fail if icon can't be loaded
            pass
    
    def load_saved_output_folder(self):
        """Load previously used output folder from config."""
        config_file = '.gui_settings.ini'
        if os.path.exists(config_file):
            try:
                import configparser
                config = configparser.ConfigParser()
                config.read(config_file)
                if 'GUI' in config and 'output_folder' in config['GUI']:
                    saved_folder = config['GUI']['output_folder']
                    if os.path.exists(saved_folder):
                        self.output_path.set(saved_folder)
            except Exception:
                pass  # Silently fail if can't load
    
    def save_output_folder(self):
        """Save current output folder to config."""
        config_file = '.gui_settings.ini'
        try:
            import configparser
            config = configparser.ConfigParser()
            
            # Load existing config if it exists
            if os.path.exists(config_file):
                config.read(config_file)
            
            # Ensure GUI section exists
            if 'GUI' not in config:
                config['GUI'] = {}
            
            # Save output folder
            config['GUI']['output_folder'] = self.output_path.get()
            
            # Write to file
            with open(config_file, 'w') as f:
                config.write(f)
        except Exception:
            pass  # Silently fail if can't save
    
    def setup_logging(self):
        """Setup logging to GUI text widget."""
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        
        # Remove existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Add console handler (for debug mode)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(console_handler)
        
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
                # Enable mask editing for single file
                self.edit_mask_btn.config(state='normal')
                # Check if we have a cached mask for this image
                image_path = files[0]
                if image_path in self.mask_cache:
                    self.current_mask = self.mask_cache[image_path]
                    self.mask_status.config(text="✓ Mask loaded from cache")
                else:
                    self.current_mask = None
                    self.mask_status.config(text="")
            else:
                self.input_path.set(f"{len(files)} files selected")
                # Disable mask editing for multiple files
                self.edit_mask_btn.config(state='disabled')
                self.current_mask = None
                self.mask_status.config(text="")
    
    def browse_output(self):
        """Browse for output folder."""
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_path.set(folder)
            self.save_output_folder()  # Save for next time
    
    def open_mask_editor(self):
        """Open mask editor window."""
        if not self.input_files or len(self.input_files) != 1:
            messagebox.showwarning("No File", "Please select a single image file first")
            return
        
        image_path = self.input_files[0]
        
        try:
            from mask_editor import MaskEditorWindow
            # Pass existing mask if available
            initial_mask = self.mask_cache.get(image_path, None)
            MaskEditorWindow(self.root, image_path, callback=self.on_mask_created, initial_mask=initial_mask)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open mask editor:\n{str(e)}")
    
    def on_mask_created(self, mask_array):
        """Callback when mask is created.
        
        Args:
            mask_array: Numpy array of mask (0-1 float)
        """
        self.current_mask = mask_array
        
        # Cache the mask for this image
        if self.input_files and len(self.input_files) == 1:
            image_path = self.input_files[0]
            self.mask_cache[image_path] = mask_array
        
        self.mask_status.config(text="✓ Mask applied")
        self.log_message("Mask created for selective denoising")
    
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
        
        # Check if at least one denoising method is enabled (classical filters OR AI)
        has_classical = self.enable_gaussian.get() or self.enable_median.get() or self.enable_nonlocal.get()
        has_ai = self.enable_ai.get()
        
        if not (has_classical or has_ai):
            messagebox.showerror(
                "Error", 
                "Please enable at least one denoising method:\n\n"
                "• Classical filters (Gaussian/Median/Non-local Means)\n"
                "• AI Denoiser\n\n"
                "Or enable both for comparison."
            )
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
            saturation_amount=self.saturation_amount.get(),
            boost_brightness=self.boost_brightness.get(),
            brightness_amount=self.brightness_amount.get()
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
        
        # AI Denoiser config
        from config_loader import AIDenoiserConfig
        ai_denoiser = AIDenoiserConfig(
            enable_ai=self.enable_ai.get(),
            model_name=self.ai_model.get(),
            device=self.ai_device.get()
        )
        
        return DenoiserConfig(
            input_path=input_path,
            output_path=self.output_path.get(),
            output=output,
            filters=filters,
            gaussian=gaussian,
            median=median,
            nonlocal_means=nonlocal_means,
            raw=raw,
            ai_denoiser=ai_denoiser
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
        
        # Auto-open log window if AI is enabled
        if self.enable_ai.get():
            self.show_log_window()
        
        # Disable buttons during processing
        self.process_btn.config(state='disabled', text="Processing...")
        self.compare_btn.config(state='disabled')
        self.processing = True
        
        # Reset progress
        self.progress_bar['value'] = 0
        self.progress_percent.config(text="0%")
        self.progress_label.config(text="Starting...")
        self.ai_status_label.config(text="")  # Clear AI status
        
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
    
    def check_ai_availability(self):
        """Check if AI dependencies are available."""
        try:
            from ai_denoiser import is_ai_available, get_device
            if is_ai_available():
                device, device_desc = get_device()
                self.ai_status_label.config(
                    text=f"✓ Available ({device_desc})",
                    foreground="green"
                )
            else:
                self.ai_status_label.config(
                    text="⚠ PyTorch not installed",
                    foreground="orange"
                )
                self.enable_ai.set(False)
        except Exception as e:
            self.ai_status_label.config(
                text="⚠ Not available",
                foreground="orange"
            )
            self.enable_ai.set(False)
    
    def show_pytorch_options(self):
        """Show PyTorch installation options dialog."""
        options_window = tk.Toplevel(self.root)
        options_window.title("PyTorch Installation Options")
        options_window.geometry("600x500")
        options_window.transient(self.root)
        options_window.grab_set()
        
        ttk.Label(options_window, text="Select PyTorch Version", 
                 font=('Arial', 14, 'bold')).pack(pady=20)
        
        ttk.Label(options_window, text="Choose the version that matches your hardware:",
                 font=('Arial', 10)).pack(pady=5)
        
        # Options frame
        options_frame = ttk.Frame(options_window)
        options_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
        
        install_choice = tk.StringVar(value='cpu')
        
        # CPU option
        cpu_radio = ttk.Radiobutton(options_frame, text="CPU Only (No GPU)", 
                                    variable=install_choice, value='cpu')
        cpu_radio.grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Label(options_frame, text="• Works on any computer\n• Slower (30-60s per image)\n• ~500MB download",
                 foreground="gray").grid(row=1, column=0, sticky=tk.W, padx=20, pady=2)
        
        # NVIDIA option
        nvidia_radio = ttk.Radiobutton(options_frame, text="NVIDIA GPU (CUDA)", 
                                      variable=install_choice, value='cuda')
        nvidia_radio.grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Label(options_frame, text="• For NVIDIA GeForce/RTX/Quadro GPUs\n• Fast (2-5s per image)\n• ~2GB download",
                 foreground="gray").grid(row=3, column=0, sticky=tk.W, padx=20, pady=2)
        
        # AMD option
        amd_radio = ttk.Radiobutton(options_frame, text="AMD GPU (ROCm) - Linux Only", 
                                   variable=install_choice, value='rocm')
        amd_radio.grid(row=4, column=0, sticky=tk.W, pady=5)
        ttk.Label(options_frame, text="• For AMD Radeon RX 6000/7000 series\n• Fast (3-8s per image)\n• ~2GB download\n• Requires ROCm drivers (Linux only)",
                 foreground="gray").grid(row=5, column=0, sticky=tk.W, padx=20, pady=2)
        
        # Apple Silicon option
        if sys.platform == 'darwin':
            apple_radio = ttk.Radiobutton(options_frame, text="Apple Silicon (M1/M2/M3)", 
                                         variable=install_choice, value='mps')
            apple_radio.grid(row=6, column=0, sticky=tk.W, pady=5)
            ttk.Label(options_frame, text="• For Mac with M1/M2/M3 chips\n• Fast (5-10s per image)\n• ~500MB download",
                     foreground="gray").grid(row=7, column=0, sticky=tk.W, padx=20, pady=2)
        
        # Buttons
        button_frame = ttk.Frame(options_window)
        button_frame.pack(pady=20)
        
        def install_selected():
            choice = install_choice.get()
            options_window.destroy()
            self.install_pytorch_version(choice)
        
        ttk.Button(button_frame, text="Install", command=install_selected, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=options_window.destroy, width=15).pack(side=tk.LEFT, padx=5)
        
        # Info label
        ttk.Label(options_window, text="Note: This will uninstall existing PyTorch and install the selected version.",
                 foreground="orange", font=('Arial', 9)).pack(pady=10)
    
    def install_pytorch_version(self, version):
        """Install specific PyTorch version."""
        import subprocess
        import threading
        
        # Map version to pip command
        commands = {
            'cpu': [sys.executable, "-m", "pip", "install", "-r", "requirements-ai.txt"],
            'cuda': [sys.executable, "-m", "pip", "install", "torch", "torchvision", 
                    "--index-url", "https://download.pytorch.org/whl/cu118"],
            'rocm': [sys.executable, "-m", "pip", "install", "torch", "torchvision",
                    "--index-url", "https://download.pytorch.org/whl/rocm5.7"],
            'mps': [sys.executable, "-m", "pip", "install", "torch", "torchvision"]
        }
        
        version_names = {
            'cpu': 'CPU',
            'cuda': 'NVIDIA CUDA',
            'rocm': 'AMD ROCm',
            'mps': 'Apple Silicon'
        }
        
        def install_thread():
            """Run installation in background thread."""
            try:
                # Create progress window
                progress_window = tk.Toplevel(self.root)
                progress_window.title(f"Installing PyTorch ({version_names[version]})")
                progress_window.geometry("500x250")
                progress_window.transient(self.root)
                progress_window.grab_set()
                
                ttk.Label(progress_window, text=f"Installing PyTorch for {version_names[version]}...", 
                         font=('Arial', 12, 'bold')).pack(pady=20)
                
                status_label = ttk.Label(progress_window, text="Uninstalling old version...")
                status_label.pack(pady=10)
                
                progress = ttk.Progressbar(progress_window, mode='indeterminate', length=400)
                progress.pack(pady=10)
                progress.start()
                
                log_text = scrolledtext.ScrolledText(progress_window, height=6, width=60)
                log_text.pack(pady=10, padx=10)
                
                def update_status(msg):
                    status_label.config(text=msg)
                    log_text.insert(tk.END, f"{msg}\n")
                    log_text.see(tk.END)
                    progress_window.update()
                
                # Uninstall existing PyTorch
                update_status("Uninstalling existing PyTorch...")
                subprocess.run(
                    [sys.executable, "-m", "pip", "uninstall", "-y", "torch", "torchvision"],
                    capture_output=True,
                    timeout=120
                )
                
                # Install new version
                update_status(f"Installing PyTorch ({version_names[version]})...")
                update_status("This may take several minutes...")
                
                result = subprocess.run(
                    commands[version],
                    capture_output=True,
                    text=True,
                    timeout=600
                )
                
                progress.stop()
                
                if result.returncode == 0:
                    update_status("✓ Installation successful!")
                    
                    # Check what was detected
                    try:
                        import importlib
                        import torch
                        importlib.reload(torch)
                        
                        if torch.cuda.is_available():
                            device_name = torch.cuda.get_device_name(0)
                            update_status(f"✓ GPU detected: {device_name}")
                        else:
                            update_status("ℹ Running on CPU")
                    except:
                        pass
                    
                    messagebox.showinfo(
                        "Installation Complete",
                        f"PyTorch ({version_names[version]}) installed successfully!\n\n"
                        "Please restart the application to use the new version.",
                        parent=progress_window
                    )
                else:
                    update_status("✗ Installation failed")
                    log_text.insert(tk.END, f"\nError:\n{result.stderr}\n")
                    messagebox.showerror(
                        "Installation Failed",
                        f"Failed to install PyTorch.\n\n"
                        f"Error: {result.stderr[:200]}",
                        parent=progress_window
                    )
                
                progress_window.grab_release()
                progress_window.destroy()
                
                # Refresh AI status
                self.check_ai_availability()
                
            except subprocess.TimeoutExpired:
                messagebox.showerror(
                    "Installation Timeout",
                    "Installation took too long and was cancelled."
                )
            except Exception as e:
                messagebox.showerror(
                    "Installation Error",
                    f"An error occurred:\n{str(e)}"
                )
        
        # Run in background
        thread = threading.Thread(target=install_thread, daemon=True)
        thread.start()
    
    def install_ai_dependencies(self):
        """Install AI dependencies automatically."""
        import subprocess
        import threading
        
        def install_thread():
            """Run installation in background thread."""
            try:
                # Create a progress window
                progress_window = tk.Toplevel(self.root)
                progress_window.title("Installing AI Dependencies")
                progress_window.geometry("500x200")
                progress_window.transient(self.root)
                progress_window.grab_set()
                
                ttk.Label(progress_window, text="Installing PyTorch for AI Denoising...", 
                         font=('Arial', 12, 'bold')).pack(pady=20)
                
                status_label = ttk.Label(progress_window, text="Starting installation...")
                status_label.pack(pady=10)
                
                progress = ttk.Progressbar(progress_window, mode='indeterminate', length=400)
                progress.pack(pady=10)
                progress.start()
                
                log_text = scrolledtext.ScrolledText(progress_window, height=5, width=60)
                log_text.pack(pady=10, padx=10)
                
                def update_status(msg):
                    status_label.config(text=msg)
                    log_text.insert(tk.END, f"{msg}\n")
                    log_text.see(tk.END)
                    progress_window.update()
                
                update_status("Installing PyTorch (this may take a few minutes)...")
                
                # Install AI dependencies
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-r", "requirements-ai.txt"],
                    capture_output=True,
                    text=True,
                    timeout=600  # 10 minute timeout
                )
                
                progress.stop()
                
                if result.returncode == 0:
                    update_status("✓ Installation successful!")
                    messagebox.showinfo(
                        "Installation Complete",
                        "AI dependencies installed successfully!\n\n"
                        "Please restart the application to use AI denoising.",
                        parent=progress_window
                    )
                else:
                    update_status("✗ Installation failed")
                    log_text.insert(tk.END, f"\nError:\n{result.stderr}\n")
                    messagebox.showerror(
                        "Installation Failed",
                        "Failed to install AI dependencies.\n\n"
                        "Please try manual installation:\n"
                        "  pip install -r requirements-ai.txt",
                        parent=progress_window
                    )
                
                progress_window.grab_release()
                progress_window.destroy()
                
            except subprocess.TimeoutExpired:
                messagebox.showerror(
                    "Installation Timeout",
                    "Installation took too long and was cancelled.\n\n"
                    "Please try manual installation:\n"
                    "  pip install -r requirements-ai.txt"
                )
            except Exception as e:
                messagebox.showerror(
                    "Installation Error",
                    f"An error occurred during installation:\n{str(e)}\n\n"
                    "Please try manual installation:\n"
                    "  pip install -r requirements-ai.txt"
                )
        
        # Run installation in background thread
        thread = threading.Thread(target=install_thread, daemon=True)
        thread.start()
    
    def on_ai_toggle(self):
        """Handle AI denoiser toggle."""
        if self.enable_ai.get():
            try:
                from ai_denoiser import is_ai_available, get_device
                
                if not is_ai_available():
                    # Offer to install AI dependencies
                    response = messagebox.askyesnocancel(
                        "AI Dependencies Missing",
                        "PyTorch is not installed.\n\n"
                        "AI denoising requires PyTorch (~500MB download).\n\n"
                        "Would you like to install it now?\n\n"
                        "Yes: Install automatically (recommended)\n"
                        "No: Show manual installation instructions\n"
                        "Cancel: Disable AI denoising"
                    )
                    
                    if response is True:
                        # Install automatically
                        self.install_ai_dependencies()
                    elif response is False:
                        # Show manual instructions
                        messagebox.showinfo(
                            "Manual Installation",
                            "To install AI dependencies manually:\n\n"
                            "1. Open Command Prompt / Terminal\n"
                            "2. Navigate to the project folder\n"
                            "3. Run: pip install -r requirements-ai.txt\n"
                            "4. Restart the application\n\n"
                            "For GPU support (NVIDIA):\n"
                            "  pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118\n\n"
                            "For Apple Silicon (M1/M2/M3):\n"
                            "  pip install torch torchvision"
                        )
                    
                    self.enable_ai.set(False)
                    return
                
                # Show device info
                device, device_desc = get_device()
                
                # Warn about CPU performance
                if device == 'cpu':
                    response = messagebox.askyesno(
                        "AI Denoising on CPU",
                        "AI denoising will run on CPU (no GPU detected).\n\n"
                        "This will be significantly slower than classical methods.\n"
                        "Processing may take 30-60 seconds per image.\n\n"
                        "Continue with AI denoising?"
                    )
                    if not response:
                        self.enable_ai.set(False)
                        return
                
                self.log_message(f"AI Denoiser enabled: {self.ai_model.get()} on {device_desc}")
                
                # Optionally disable classical filters when AI is enabled
                # Only ask if at least one classical filter is enabled
                if (self.enable_gaussian.get() or self.enable_median.get() or self.enable_nonlocal.get()):
                    response = messagebox.askyesnocancel(
                        "Classical Filters",
                        "AI denoising works best alone, but you can also combine it with classical filters.\n\n"
                        "What would you like to do?\n\n"
                        "• Yes: Disable classical filters (AI only - recommended)\n"
                        "• No: Keep classical filters enabled (AI + Classical)\n"
                        "• Cancel: Keep current settings"
                    )
                    
                    if response is True:
                        # Disable classical filters
                        self.enable_gaussian.set(False)
                        self.enable_median.set(False)
                        self.enable_nonlocal.set(False)
                        self.log_message("Classical filters disabled (AI only mode)")
                    elif response is False:
                        # Keep both enabled
                        self.log_message("AI + Classical filters enabled (hybrid mode)")
                    # If None (Cancel), do nothing
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to initialize AI denoiser:\n{str(e)}")
                self.enable_ai.set(False)
        else:
            self.log_message("AI Denoiser disabled")
    
    def show_log_window(self):
        """Show processing log in a separate window."""
        log_window = tk.Toplevel(self.root)
        log_window.title("Processing Log")
        log_window.geometry("800x600")
        
        # Log text
        log_display = scrolledtext.ScrolledText(log_window, wrap=tk.WORD, font=('Consolas', 9))
        log_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Copy current log content
        current_log = self.log_text.get(1.0, tk.END)
        log_display.insert(1.0, current_log)
        log_display.configure(state='disabled')
        
        # Auto-update log (refresh every second while window is open)
        def update_log():
            if log_window.winfo_exists():
                try:
                    log_display.configure(state='normal')
                    log_display.delete(1.0, tk.END)
                    current_log = self.log_text.get(1.0, tk.END)
                    log_display.insert(1.0, current_log)
                    log_display.configure(state='disabled')
                    log_display.see(tk.END)
                    log_window.after(1000, update_log)
                except:
                    pass
        
        update_log()
        
        # Buttons
        button_frame = ttk.Frame(log_window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="📋 Copy to Clipboard", 
                  command=lambda: self.copy_log_to_clipboard(log_display)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="💾 Save to File", 
                  command=lambda: self.save_log_to_file(log_display)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Close", 
                  command=log_window.destroy).pack(side=tk.RIGHT, padx=5)
    
    def copy_log_to_clipboard(self, log_widget):
        """Copy log content to clipboard."""
        log_content = log_widget.get(1.0, tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(log_content)
        messagebox.showinfo("Copied", "Log copied to clipboard!")
    
    def save_log_to_file(self, log_widget):
        """Save log content to file."""
        from datetime import datetime
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"denoiser_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(log_widget.get(1.0, tk.END))
                messagebox.showinfo("Saved", f"Log saved to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save log:\n{str(e)}")
    
    def clear_log(self):
        """Clear the processing log."""
        if messagebox.askyesno("Clear Log", "Clear all log messages?"):
            self.log_text.configure(state='normal')
            self.log_text.delete(1.0, tk.END)
            self.log_text.configure(state='disabled')
    
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
    
    def update_ai_status(self, status_msg):
        """Update AI processing status label."""
        self.ai_status_label.config(text=status_msg)
        self.root.update_idletasks()  # Force GUI update
    
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
        
        # Debug logging
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Comparison: original_path = {original_path}")
        logger.info(f"Comparison: basename = {os.path.basename(original_path)}")
        logger.info(f"Comparison: base_name = {base_name}")
        
        # Check for different filter outputs (classical and AI)
        filter_suffixes = []
        
        # Add AI suffix if enabled (AI replaces the classical filter)
        if self.enable_ai.get():
            # When AI is enabled, it replaces each enabled filter
            if self.enable_nonlocal.get():
                filter_suffixes.append('nonlocal_ai')
            if self.enable_gaussian.get():
                filter_suffixes.append('gaussian_ai')
            if self.enable_median.get():
                filter_suffixes.append('median_ai')
            # If no classical filters enabled, AI still runs with nonlocal as base
            if not any([self.enable_gaussian.get(), self.enable_median.get(), self.enable_nonlocal.get()]):
                filter_suffixes.append('nonlocal_ai')
            
            # FALLBACK: If AI failed, also check for classical filter outputs
            # (AI falls back to classical filters on error)
            if self.enable_nonlocal.get():
                filter_suffixes.append('nonlocal')
            if self.enable_gaussian.get():
                filter_suffixes.append('gaussian')
            if self.enable_median.get():
                filter_suffixes.append('median')
            # If no classical filters enabled, check nonlocal (AI fallback)
            if not any([self.enable_gaussian.get(), self.enable_median.get(), self.enable_nonlocal.get()]):
                filter_suffixes.append('nonlocal')
            
            # Debug logging
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Comparison: Looking for AI output with suffixes: {filter_suffixes}")
            logger.info(f"Comparison: Filters enabled - Gaussian:{self.enable_gaussian.get()}, Median:{self.enable_median.get()}, Nonlocal:{self.enable_nonlocal.get()}")
        
        # Add classical filter suffixes (only if AI is disabled)
        if not self.enable_ai.get():
            if self.enable_gaussian.get():
                filter_suffixes.append('gaussian')
            if self.enable_median.get():
                filter_suffixes.append('median')
            if self.enable_nonlocal.get():
                filter_suffixes.append('nonlocal')
        
        # If multiple filters, show first one found
        output_path = None
        checked_paths = []
        for suffix in filter_suffixes:
            test_path = os.path.join(
                config.output_path,
                f"{base_name}_{suffix}.{config.output.format}"
            )
            checked_paths.append(f"{base_name}_{suffix}.{config.output.format}")
            if os.path.exists(test_path):
                output_path = test_path
                break
        
        if output_path and os.path.exists(output_path):
            try:
                BeforeAfterWindow(self.root, original_path, output_path)
            except Exception as e:
                messagebox.showerror("Error", f"Could not open comparison window:\n{str(e)}")
        else:
            # Show detailed error with what was checked
            checked_list = "\n".join([f"  • {p}" for p in checked_paths])
            messagebox.showwarning(
                "Warning", 
                f"Could not find processed image for comparison.\n\n"
                f"Looked for:\n{checked_list}\n\n"
                f"In folder:\n{config.output_path}\n\n"
                f"Check the Processing Log for details."
            )
    
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
                
                # Check if mask is available (only for single file)
                mask = None
                if len(files_to_process) == 1 and self.current_mask is not None:
                    mask = self.current_mask
                    logger.info("Using selective denoising mask")
                
                # Process selected files directly with progress callback
                processor = ImageProcessor(config)
                processed_count, metrics_list = processor.process_files(
                    files_to_process, 
                    progress_callback=lambda c, t, f: self.root.after(0, self.update_progress, c, t, f),
                    mask=mask,
                    ai_status_callback=lambda msg: self.root.after(0, self.update_ai_status, msg)
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
                    progress_callback=lambda c, t, f: self.root.after(0, self.update_progress, c, t, f),
                    ai_status_callback=lambda msg: self.root.after(0, self.update_ai_status, msg)
                )
            
            if processed_count > 0:
                csv_file = save_metrics_to_csv(metrics_list, config.output_path)
                logger.info(f"📊 Metrics saved to: {csv_file}")
                logger.info(f"✓ Successfully processed {processed_count} images")
                
                # Update progress to complete
                self.root.after(0, lambda: self.progress_bar.config(value=100))
                self.root.after(0, lambda: self.progress_percent.config(text="100%"))
                self.root.after(0, lambda: self.progress_label.config(text=f"Complete! Processed {processed_count} images"))
                self.root.after(0, lambda: self.ai_status_label.config(text=""))  # Clear AI status
                
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
    
    def on_closing(self):
        """Handle window close event."""
        if self.processing:
            response = messagebox.askyesno(
                "Processing in Progress",
                "Image processing is still running.\n\nAre you sure you want to exit?"
            )
            if not response:
                return
        
        # Destroy the window and exit the application
        self.root.destroy()
        sys.exit(0)


def main():
    """Main entry point for GUI."""
    root = tk.Tk()
    app = DenoiserGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
