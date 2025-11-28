# Copyright (c) 2025 Adwait Godbole and Siddhesh Pandit
# Licensed under CC BY-NC 4.0 (Attribution-NonCommercial 4.0 International)
# https://creativecommons.org/licenses/by-nc/4.0/
# For commercial use, please contact the authors.

"""Mask editor window for selective denoising."""
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from PIL import Image, ImageDraw, ImageTk


class MaskEditorWindow:
    """Interactive mask editor for selective denoising."""
    
    def __init__(self, parent, image_path, callback=None):
        """Initialize mask editor.
        
        Args:
            parent: Parent tkinter window
            image_path: Path to image file
            callback: Function to call with mask when done (receives numpy array)
        """
        self.window = tk.Toplevel(parent)
        self.window.title("Mask Editor - Select Areas to Denoise")
        self.window.geometry("1200x800")
        
        self.callback = callback
        self.image_path = image_path
        
        # Load image
        self.original_img = Image.open(image_path)
        
        # Scale image to fit window
        self.canvas_width = 1000
        self.canvas_height = 600
        self.scale_image()
        
        # Create mask (white = denoise, black = skip)
        self.mask = Image.new('L', (self.display_width, self.display_height), 0)
        self.mask_draw = ImageDraw.Draw(self.mask)
        
        # Tool state
        self.current_tool = 'brush'  # 'brush' or 'eraser'
        self.brush_size = 20
        self.drawing = False
        self.last_x = None
        self.last_y = None
        
        self.create_widgets()
        self.update_display()
    
    def scale_image(self):
        """Scale image to fit canvas."""
        width, height = self.original_img.size
        
        scale_w = self.canvas_width / width
        scale_h = self.canvas_height / height
        scale = min(scale_w, scale_h, 1.0)
        
        self.display_width = int(width * scale)
        self.display_height = int(height * scale)
        self.scale_factor = scale
        
        self.display_img = self.original_img.resize(
            (self.display_width, self.display_height),
            Image.Resampling.LANCZOS
        )
    
    def create_widgets(self):
        """Create UI widgets."""
        # Main container
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Top toolbar
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        # Tool buttons
        ttk.Label(toolbar, text="Tool:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        
        self.brush_btn = ttk.Button(toolbar, text="🖌️ Brush", command=self.select_brush, width=12)
        self.brush_btn.pack(side=tk.LEFT, padx=2)
        self.brush_btn.state(['pressed'])  # Start selected
        
        self.eraser_btn = ttk.Button(toolbar, text="🧹 Eraser", command=self.select_eraser, width=12)
        self.eraser_btn.pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        # Brush size
        ttk.Label(toolbar, text="Brush Size:").pack(side=tk.LEFT, padx=5)
        self.size_var = tk.IntVar(value=self.brush_size)
        size_spinbox = ttk.Spinbox(toolbar, from_=5, to=100, textvariable=self.size_var, 
                                   width=8, command=self.update_brush_size)
        size_spinbox.pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        # Clear button
        ttk.Button(toolbar, text="🗑️ Clear All", command=self.clear_mask, width=12).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        # Done/Cancel buttons
        ttk.Button(toolbar, text="✓ Apply Mask", command=self.apply_mask, width=15).pack(side=tk.RIGHT, padx=2)
        ttk.Button(toolbar, text="✗ Cancel", command=self.cancel, width=12).pack(side=tk.RIGHT, padx=2)
        
        # Canvas frame
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas with scrollbars
        self.canvas = tk.Canvas(canvas_frame, 
                               width=self.canvas_width,
                               height=self.canvas_height,
                               bg='gray',
                               cursor='crosshair')
        self.canvas.pack()
        
        # Info label
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(info_frame, text="💡 Paint areas to denoise (white). Unpainted areas will be skipped.",
                 font=('Arial', 9)).pack(side=tk.LEFT)
        
        self.status_label = ttk.Label(info_frame, text="Tool: Brush", font=('Arial', 9, 'bold'))
        self.status_label.pack(side=tk.RIGHT)
        
        # Bind mouse events
        self.canvas.bind('<Button-1>', self.on_mouse_down)
        self.canvas.bind('<B1-Motion>', self.on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_up)
        
        # Bind keyboard shortcuts
        self.window.bind('b', lambda e: self.select_brush())
        self.window.bind('e', lambda e: self.select_eraser())
        self.window.bind('c', lambda e: self.clear_mask())
    
    def select_brush(self):
        """Select brush tool."""
        self.current_tool = 'brush'
        self.brush_btn.state(['pressed'])
        self.eraser_btn.state(['!pressed'])
        self.status_label.config(text="Tool: Brush")
        self.canvas.config(cursor='crosshair')
    
    def select_eraser(self):
        """Select eraser tool."""
        self.current_tool = 'eraser'
        self.eraser_btn.state(['pressed'])
        self.brush_btn.state(['!pressed'])
        self.status_label.config(text="Tool: Eraser")
        self.canvas.config(cursor='circle')
    
    def update_brush_size(self):
        """Update brush size from spinbox."""
        self.brush_size = self.size_var.get()
    
    def clear_mask(self):
        """Clear entire mask."""
        response = messagebox.askyesno("Clear Mask", "Clear entire mask?")
        if response:
            self.mask = Image.new('L', (self.display_width, self.display_height), 0)
            self.mask_draw = ImageDraw.Draw(self.mask)
            self.update_display()
    
    def on_mouse_down(self, event):
        """Handle mouse button press."""
        self.drawing = True
        self.last_x = event.x
        self.last_y = event.y
        self.draw_at(event.x, event.y)
    
    def on_mouse_drag(self, event):
        """Handle mouse drag."""
        if self.drawing:
            # Draw line from last position to current
            if self.last_x is not None and self.last_y is not None:
                self.draw_line(self.last_x, self.last_y, event.x, event.y)
            self.last_x = event.x
            self.last_y = event.y
    
    def on_mouse_up(self, event):
        """Handle mouse button release."""
        self.drawing = False
        self.last_x = None
        self.last_y = None
        self.update_display()
    
    def draw_at(self, x, y):
        """Draw at specific position."""
        # Constrain to canvas bounds
        x = max(0, min(x, self.display_width))
        y = max(0, min(y, self.display_height))
        
        # Draw circle
        color = 255 if self.current_tool == 'brush' else 0
        radius = self.brush_size // 2
        
        bbox = [x - radius, y - radius, x + radius, y + radius]
        self.mask_draw.ellipse(bbox, fill=color)
        
        # Update display
        self.update_display()
    
    def draw_line(self, x1, y1, x2, y2):
        """Draw line between two points using circular brush."""
        import math
        
        color = 255 if self.current_tool == 'brush' else 0
        radius = self.brush_size // 2
        
        # Calculate distance between points
        dx = x2 - x1
        dy = y2 - y1
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance == 0:
            return
        
        # Draw circles along the line for smooth circular brush
        steps = max(int(distance / (radius / 2)), 1)  # Overlap circles for smooth line
        
        for i in range(steps + 1):
            t = i / steps if steps > 0 else 0
            x = x1 + dx * t
            y = y1 + dy * t
            
            # Draw circle at this position
            bbox = [x - radius, y - radius, x + radius, y + radius]
            self.mask_draw.ellipse(bbox, fill=color)
        
        # Update display
        self.update_display()
    
    def update_display(self):
        """Update canvas display with image and mask overlay."""
        # Create composite image
        display = self.display_img.copy().convert('RGBA')
        
        # Create colored mask overlay (semi-transparent green)
        mask_colored = Image.new('RGBA', (self.display_width, self.display_height), (0, 255, 0, 0))
        mask_pixels = mask_colored.load()
        mask_data = self.mask.load()
        
        for y in range(self.display_height):
            for x in range(self.display_width):
                if mask_data[x, y] > 0:
                    mask_pixels[x, y] = (0, 255, 0, 100)  # Semi-transparent green
        
        # Composite
        display = Image.alpha_composite(display, mask_colored)
        
        # Convert to PhotoImage
        self.photo = ImageTk.PhotoImage(display)
        
        # Update canvas
        self.canvas.delete('all')
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
    
    def apply_mask(self):
        """Apply mask and close window."""
        # Scale mask back to original image size
        original_size = self.original_img.size
        mask_full = self.mask.resize(original_size, Image.Resampling.LANCZOS)
        
        # Convert to numpy array (0-255 -> 0-1)
        mask_array = np.array(mask_full).astype(np.float32) / 255.0
        
        # Check if mask is empty
        if mask_array.max() == 0:
            response = messagebox.askyesno(
                "Empty Mask",
                "Mask is empty. This will skip denoising entirely.\n\nContinue anyway?"
            )
            if not response:
                return
        
        # Call callback with mask
        if self.callback:
            self.callback(mask_array)
        
        self.window.destroy()
    
    def cancel(self):
        """Cancel and close window."""
        self.window.destroy()
