# Copyright (c) 2025 Adwait Godbole and Siddhesh Pandit
# Licensed under CC BY-NC 4.0 (Attribution-NonCommercial 4.0 International)
# https://creativecommons.org/licenses/by-nc/4.0/
# For commercial use, please contact the authors.

"""Mask editor window for selective denoising."""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import numpy as np
from PIL import Image, ImageDraw, ImageTk
from scipy import ndimage


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
        
        # Zoom state
        self.zoom_level = 1.0
        self.min_zoom = 0.25
        self.max_zoom = 4.0
        
        # Scale image to fit window
        self.canvas_width = 1000
        self.canvas_height = 600
        self.max_width = self.canvas_width
        self.max_height = self.canvas_height
        self.scale_image()
        
        # Create mask (white = denoise, black = skip)
        self.mask = Image.new('L', (self.display_width, self.display_height), 0)
        self.mask_draw = ImageDraw.Draw(self.mask)
        
        # Tool state
        self.current_tool = 'brush'  # 'brush', 'eraser', or 'magic_wand'
        self.brush_size = 20
        self.magic_wand_tolerance = 30  # Color tolerance for magic wand (0-255)
        self.drawing = False
        self.last_x = None
        self.last_y = None
        
        # Undo/Redo state
        self.undo_stack = []
        self.redo_stack = []
        self.max_undo_levels = 20  # Limit to prevent memory issues
        
        self.create_widgets()
        self.save_state()  # Save initial empty state
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
        
        self.magic_wand_btn = ttk.Button(toolbar, text="🪄 Magic Wand", command=self.select_magic_wand, width=15)
        self.magic_wand_btn.pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        # Brush size
        ttk.Label(toolbar, text="Brush Size:").pack(side=tk.LEFT, padx=5)
        self.size_var = tk.IntVar(value=self.brush_size)
        size_spinbox = ttk.Spinbox(toolbar, from_=5, to=100, textvariable=self.size_var, 
                                   width=8, command=self.update_brush_size)
        size_spinbox.pack(side=tk.LEFT, padx=2)
        # Bind to capture manual input changes
        self.size_var.trace_add('write', lambda *args: self.update_brush_size())
        
        # Magic wand tolerance
        ttk.Label(toolbar, text="Tolerance:").pack(side=tk.LEFT, padx=(10, 5))
        self.tolerance_var = tk.IntVar(value=self.magic_wand_tolerance)
        tolerance_spinbox = ttk.Spinbox(toolbar, from_=5, to=100, textvariable=self.tolerance_var, 
                                       width=8, command=self.update_tolerance)
        tolerance_spinbox.pack(side=tk.LEFT, padx=2)
        self.tolerance_var.trace_add('write', lambda *args: self.update_tolerance())
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        # Undo/Redo buttons
        self.undo_btn = ttk.Button(toolbar, text="↶ Undo", command=self.undo, width=10)
        self.undo_btn.pack(side=tk.LEFT, padx=2)
        self.undo_btn.state(['disabled'])
        
        self.redo_btn = ttk.Button(toolbar, text="↷ Redo", command=self.redo, width=10)
        self.redo_btn.pack(side=tk.LEFT, padx=2)
        self.redo_btn.state(['disabled'])
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        # Auto-select button
        ttk.Button(toolbar, text="🎯 Auto-Select Gradients", command=self.auto_select_gradients, width=20).pack(side=tk.LEFT, padx=2)
        
        # Clear button
        ttk.Button(toolbar, text="🗑️ Clear All", command=self.clear_mask, width=12).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        # Done/Cancel buttons
        ttk.Button(toolbar, text="✓ Apply Mask", command=self.apply_mask, width=15).pack(side=tk.RIGHT, padx=2)
        ttk.Button(toolbar, text="✗ Cancel", command=self.cancel, width=12).pack(side=tk.RIGHT, padx=2)
        
        # Canvas frame
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create scrollbars
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL)
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL)
        
        # Canvas with scrollbars
        self.canvas = tk.Canvas(canvas_frame, 
                               width=self.canvas_width,
                               height=self.canvas_height,
                               bg='gray',
                               cursor='crosshair',
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
        
        # Zoom controls
        zoom_frame = ttk.Frame(main_frame)
        zoom_frame.pack(pady=5)
        
        ttk.Button(zoom_frame, text="🔍−", command=self.zoom_out, width=5).pack(side=tk.LEFT, padx=5)
        self.zoom_label = ttk.Label(zoom_frame, text="100%", font=('Arial', 10))
        self.zoom_label.pack(side=tk.LEFT, padx=10)
        ttk.Button(zoom_frame, text="🔍+", command=self.zoom_in, width=5).pack(side=tk.LEFT, padx=5)
        ttk.Button(zoom_frame, text="Reset", command=self.zoom_reset, width=8).pack(side=tk.LEFT, padx=5)
        
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
        self.canvas.bind('<MouseWheel>', self.on_mousewheel)  # Windows/Mac
        self.canvas.bind('<Button-4>', self.on_mousewheel)    # Linux scroll up
        self.canvas.bind('<Button-5>', self.on_mousewheel)    # Linux scroll down
        
        # Bind keyboard shortcuts
        self.window.bind('b', lambda e: self.select_brush())
        self.window.bind('e', lambda e: self.select_eraser())
        self.window.bind('w', lambda e: self.select_magic_wand())
        self.window.bind('c', lambda e: self.clear_mask())
        
        # Undo/Redo shortcuts (Ctrl+Z / Ctrl+Y)
        self.window.bind('<Control-z>', lambda e: self.undo())
        self.window.bind('<Control-y>', lambda e: self.redo())
        # Also support Ctrl+Shift+Z for redo (common alternative)
        self.window.bind('<Control-Shift-Z>', lambda e: self.redo())
    
    def select_brush(self):
        """Select brush tool."""
        self.current_tool = 'brush'
        self.brush_btn.state(['pressed'])
        self.eraser_btn.state(['!pressed'])
        self.magic_wand_btn.state(['!pressed'])
        self.status_label.config(text="Tool: Brush")
        self.canvas.config(cursor='crosshair')
    
    def select_eraser(self):
        """Select eraser tool."""
        self.current_tool = 'eraser'
        self.eraser_btn.state(['pressed'])
        self.brush_btn.state(['!pressed'])
        self.magic_wand_btn.state(['!pressed'])
        self.status_label.config(text="Tool: Eraser")
        self.canvas.config(cursor='circle')
    
    def select_magic_wand(self):
        """Select magic wand tool."""
        self.current_tool = 'magic_wand'
        self.magic_wand_btn.state(['pressed'])
        self.brush_btn.state(['!pressed'])
        self.eraser_btn.state(['!pressed'])
        self.status_label.config(text="Tool: Magic Wand (click to select similar areas)")
        self.canvas.config(cursor='target')
    
    def update_brush_size(self):
        """Update brush size from spinbox."""
        try:
            value = self.size_var.get()
            if value and 5 <= value <= 100:
                self.brush_size = value
        except (tk.TclError, ValueError):
            # Ignore invalid values (e.g., empty string during editing)
            pass
    
    def update_tolerance(self):
        """Update magic wand tolerance from spinbox."""
        try:
            value = self.tolerance_var.get()
            if value and 5 <= value <= 100:
                self.magic_wand_tolerance = value
        except (tk.TclError, ValueError):
            # Ignore invalid values (e.g., empty string during editing)
            pass
    
    def save_state(self):
        """Save current mask state to undo stack."""
        # Convert mask to numpy array and save a copy
        mask_state = np.array(self.mask).copy()
        self.undo_stack.append(mask_state)
        
        # Limit undo stack size
        if len(self.undo_stack) > self.max_undo_levels:
            self.undo_stack.pop(0)
        
        # Clear redo stack when new action is performed
        self.redo_stack.clear()
        
        # Update button states
        self.update_undo_redo_buttons()
    
    def undo(self):
        """Undo last action."""
        if len(self.undo_stack) <= 1:  # Keep at least one state
            return
        
        # Save current state to redo stack
        current_state = np.array(self.mask).copy()
        self.redo_stack.append(current_state)
        
        # Restore previous state
        self.undo_stack.pop()
        previous_state = self.undo_stack[-1]
        
        self.mask = Image.fromarray(previous_state, mode='L')
        self.mask_draw = ImageDraw.Draw(self.mask)
        
        self.update_display()
        self.update_undo_redo_buttons()
        self.status_label.config(text="Undo")
    
    def redo(self):
        """Redo last undone action."""
        if not self.redo_stack:
            return
        
        # Get state from redo stack
        redo_state = self.redo_stack.pop()
        
        # Save current state to undo stack
        current_state = np.array(self.mask).copy()
        self.undo_stack.append(current_state)
        
        # Restore redo state
        self.mask = Image.fromarray(redo_state, mode='L')
        self.mask_draw = ImageDraw.Draw(self.mask)
        
        self.update_display()
        self.update_undo_redo_buttons()
        self.status_label.config(text="Redo")
    
    def update_undo_redo_buttons(self):
        """Update undo/redo button states."""
        # Enable/disable undo button
        if len(self.undo_stack) > 1:
            self.undo_btn.state(['!disabled'])
        else:
            self.undo_btn.state(['disabled'])
        
        # Enable/disable redo button
        if self.redo_stack:
            self.redo_btn.state(['!disabled'])
        else:
            self.redo_btn.state(['disabled'])
    
    def feather_mask(self, mask, feather_radius=3):
        """Apply feathering (soft edges) to a mask.
        
        Args:
            mask: Binary or grayscale mask (numpy array)
            feather_radius: Radius of feathering in pixels
            
        Returns:
            Feathered mask with smooth edges
        """
        from scipy.ndimage import distance_transform_edt, gaussian_filter
        
        # Convert to binary
        binary_mask = (mask > 127).astype(np.uint8)
        
        # Calculate distance from edges
        # For pixels inside the mask, calculate distance to nearest edge
        distance_inside = distance_transform_edt(binary_mask)
        
        # Create smooth falloff at edges
        # Pixels within feather_radius of edge get gradual transparency
        feathered = np.clip(distance_inside / feather_radius, 0, 1)
        
        # Apply slight gaussian blur for even smoother transition
        feathered = gaussian_filter(feathered, sigma=0.5)
        
        # Convert back to 0-255 range
        feathered_mask = (feathered * 255).astype(np.uint8)
        
        return feathered_mask
    
    def magic_wand_select(self, x, y):
        """Select connected region using flood fill based on color similarity."""
        # Check bounds
        if x < 0 or x >= self.display_width or y < 0 or y >= self.display_height:
            return
        
        self.status_label.config(text="Selecting region...")
        self.window.update()
        
        try:
            # Convert image to numpy array
            img_array = np.array(self.display_img)
            
            # Get the seed color
            if len(img_array.shape) == 3:
                seed_color = img_array[y, x].astype(float)
            else:
                seed_color = float(img_array[y, x])
            
            # Create a mask for the flood fill
            h, w = img_array.shape[:2]
            filled = np.zeros((h, w), dtype=bool)
            
            # Flood fill using a queue-based approach
            from collections import deque
            queue = deque([(x, y)])
            filled[y, x] = True
            
            tolerance = self.magic_wand_tolerance
            
            while queue:
                cx, cy = queue.popleft()
                
                # Check 4-connected neighbors
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    nx, ny = cx + dx, cy + dy
                    
                    # Check bounds
                    if nx < 0 or nx >= w or ny < 0 or ny >= h:
                        continue
                    
                    # Skip if already filled
                    if filled[ny, nx]:
                        continue
                    
                    # Check color similarity
                    if len(img_array.shape) == 3:
                        neighbor_color = img_array[ny, nx].astype(float)
                        color_diff = np.sqrt(np.sum((neighbor_color - seed_color) ** 2))
                    else:
                        neighbor_color = float(img_array[ny, nx])
                        color_diff = abs(neighbor_color - seed_color)
                    
                    if color_diff <= tolerance:
                        filled[ny, nx] = True
                        queue.append((nx, ny))
            
            # Convert filled region to mask (255 for selected)
            region_mask = (filled * 255).astype(np.uint8)
            
            # Apply feathering to smooth edges
            region_mask = self.feather_mask(region_mask, feather_radius=3)
            
            # Merge with existing mask
            mask_array = np.array(self.mask)
            merged_mask = np.maximum(mask_array, region_mask)
            
            # Update mask
            self.mask = Image.fromarray(merged_mask, mode='L')
            self.mask_draw = ImageDraw.Draw(self.mask)
            
            # Update display
            self.update_display()
            
            # Show result
            selected_pixels = np.sum(filled)
            total_pixels = filled.size
            percentage = (selected_pixels / total_pixels) * 100
            
            self.status_label.config(text=f"Tool: Magic Wand - Selected {percentage:.1f}% ({selected_pixels:,} pixels)")
            
            # Save state for undo
            self.save_state()
            
        except Exception as e:
            messagebox.showerror("Error", f"Magic wand selection failed:\n{str(e)}")
            self.status_label.config(text="Tool: Magic Wand")
    
    def auto_select_gradients(self):
        """Automatically select areas with high gradients (edges/details)."""
        # Ask user for sensitivity
        sensitivity = simpledialog.askfloat(
            "Auto-Select Gradients",
            "Enter gradient sensitivity (0.1-1.0):\n\n"
            "Lower values = more areas selected\n"
            "Higher values = only strong edges\n\n"
            "Recommended: 0.3-0.5",
            initialvalue=0.4,
            minvalue=0.1,
            maxvalue=1.0
        )
        
        if sensitivity is None:
            return
        
        self.status_label.config(text="Detecting gradients...")
        self.window.update()
        
        try:
            # Convert image to grayscale numpy array
            img_gray = np.array(self.display_img.convert('L')).astype(float)
            
            # Calculate gradients using Sobel filters
            gradient_x = ndimage.sobel(img_gray, axis=1)
            gradient_y = ndimage.sobel(img_gray, axis=0)
            
            # Calculate gradient magnitude
            gradient_magnitude = np.sqrt(gradient_x**2 + gradient_y**2)
            
            # Normalize to 0-1
            if gradient_magnitude.max() > 0:
                gradient_magnitude = gradient_magnitude / gradient_magnitude.max()
            
            # Threshold based on sensitivity
            threshold = sensitivity
            gradient_mask = (gradient_magnitude > threshold).astype(np.uint8) * 255
            
            # Apply morphological operations to clean up the mask
            # Dilate to connect nearby edges
            gradient_mask = ndimage.binary_dilation(gradient_mask, iterations=2).astype(np.uint8) * 255
            
            # Apply feathering for smooth edges
            gradient_mask = self.feather_mask(gradient_mask, feather_radius=4)
            
            # Merge with existing mask (union)
            mask_array = np.array(self.mask)
            merged_mask = np.maximum(mask_array, gradient_mask)
            
            # Update mask
            self.mask = Image.fromarray(merged_mask, mode='L')
            self.mask_draw = ImageDraw.Draw(self.mask)
            
            # Update display
            self.update_display()
            
            # Show result
            selected_pixels = np.sum(merged_mask > 0)
            total_pixels = merged_mask.size
            percentage = (selected_pixels / total_pixels) * 100
            
            messagebox.showinfo(
                "Auto-Select Complete",
                f"Gradient areas detected and added to mask.\n\n"
                f"Selected: {percentage:.1f}% of image\n"
                f"({selected_pixels:,} pixels)"
            )
            
            self.status_label.config(text="Tool: Brush")
            
            # Save state for undo
            self.save_state()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to detect gradients:\n{str(e)}")
            self.status_label.config(text="Tool: Brush")
    
    def clear_mask(self):
        """Clear entire mask."""
        response = messagebox.askyesno("Clear Mask", "Clear entire mask?")
        if response:
            self.mask = Image.new('L', (self.display_width, self.display_height), 0)
            self.mask_draw = ImageDraw.Draw(self.mask)
            self.update_display()
            # Save state for undo
            self.save_state()
    
    def canvas_to_image_coords(self, canvas_x, canvas_y):
        """Convert canvas coordinates to image coordinates accounting for scroll."""
        # Get canvas scroll position
        x_scroll = self.canvas.canvasx(canvas_x)
        y_scroll = self.canvas.canvasy(canvas_y)
        return x_scroll, y_scroll
    
    def on_mouse_down(self, event):
        """Handle mouse button press."""
        x, y = self.canvas_to_image_coords(event.x, event.y)
        
        if self.current_tool == 'magic_wand':
            # Magic wand: flood fill on click
            self.magic_wand_select(int(x), int(y))
        else:
            # Brush/Eraser: start drawing
            self.drawing = True
            self.last_x = x
            self.last_y = y
            self.draw_at(x, y)
    
    def on_mouse_drag(self, event):
        """Handle mouse drag."""
        if self.drawing and self.current_tool != 'magic_wand':
            x, y = self.canvas_to_image_coords(event.x, event.y)
            # Draw line from last position to current
            if self.last_x is not None and self.last_y is not None:
                self.draw_line(self.last_x, self.last_y, x, y)
            self.last_x = x
            self.last_y = y
    
    def on_mouse_up(self, event):
        """Handle mouse button release."""
        self.drawing = False
        self.last_x = None
        self.last_y = None
        self.update_display()
        # Save state after brush/eraser stroke is complete
        if self.current_tool in ['brush', 'eraser']:
            self.save_state()
    
    def draw_soft_brush(self, x, y):
        """Draw a soft-edged brush stroke at position.
        
        Args:
            x, y: Center position of brush
        """
        # Get mask as numpy array
        mask_array = np.array(self.mask).astype(float)
        
        radius = self.brush_size // 2
        feather = max(2, radius // 3)  # Feather is 1/3 of radius
        
        # Create coordinate grids
        y_coords, x_coords = np.ogrid[:self.display_height, :self.display_width]
        
        # Calculate distance from brush center
        distance = np.sqrt((x_coords - x)**2 + (y_coords - y)**2)
        
        # Create soft brush: full opacity at center, fade to zero at edge
        # Inner circle (full opacity)
        inner_radius = max(1, radius - feather)
        
        # Calculate brush opacity based on distance
        brush_opacity = np.zeros_like(distance)
        
        # Full opacity in inner circle
        brush_opacity[distance <= inner_radius] = 1.0
        
        # Smooth falloff in feather zone
        feather_zone = (distance > inner_radius) & (distance <= radius)
        if feather > 0:
            falloff = 1.0 - (distance[feather_zone] - inner_radius) / feather
            brush_opacity[feather_zone] = falloff
        
        if self.current_tool == 'brush':
            # Add to mask (max blend)
            mask_array = np.maximum(mask_array, brush_opacity * 255)
        else:  # eraser
            # Subtract from mask (min blend)
            mask_array = np.minimum(mask_array, (1 - brush_opacity) * 255)
        
        # Convert back to PIL Image
        self.mask = Image.fromarray(mask_array.astype(np.uint8), mode='L')
        self.mask_draw = ImageDraw.Draw(self.mask)
    
    def draw_at(self, x, y):
        """Draw at specific position."""
        # Constrain to canvas bounds
        x = max(0, min(x, self.display_width - 1))
        y = max(0, min(y, self.display_height - 1))
        
        # Draw with soft brush
        self.draw_soft_brush(x, y)
        
        # Update display
        self.update_display()
    
    def draw_line(self, x1, y1, x2, y2):
        """Draw line between two points using soft circular brush."""
        import math
        
        radius = self.brush_size // 2
        
        # Calculate distance between points
        dx = x2 - x1
        dy = y2 - y1
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance == 0:
            return
        
        # Draw soft brush strokes along the line
        # Use smaller steps for smoother lines
        steps = max(int(distance / (radius / 3)), 1)
        
        for i in range(steps + 1):
            t = i / steps if steps > 0 else 0
            x = x1 + dx * t
            y = y1 + dy * t
            
            # Constrain to bounds
            x = max(0, min(x, self.display_width - 1))
            y = max(0, min(y, self.display_height - 1))
            
            # Draw soft brush at this position
            self.draw_soft_brush(x, y)
        
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
        """Apply current zoom level to images and mask."""
        # Calculate new dimensions
        width, height = self.original_img.size
        scale_w = self.max_width / width
        scale_h = self.max_height / height
        base_scale = min(scale_w, scale_h, 1.0)
        
        final_scale = base_scale * self.zoom_level
        
        new_width = int(width * final_scale)
        new_height = int(height * final_scale)
        
        # Store old dimensions for mask scaling
        old_width = self.display_width
        old_height = self.display_height
        
        # Update display dimensions
        self.display_width = new_width
        self.display_height = new_height
        self.scale_factor = final_scale
        
        # Resize display image
        self.display_img = self.original_img.resize(
            (self.display_width, self.display_height),
            Image.Resampling.LANCZOS
        )
        
        # Scale mask to new size
        if old_width > 0 and old_height > 0:
            self.mask = self.mask.resize((new_width, new_height), Image.Resampling.LANCZOS)
        else:
            self.mask = Image.new('L', (new_width, new_height), 0)
        self.mask_draw = ImageDraw.Draw(self.mask)
        
        # Update scroll region
        self.canvas.config(scrollregion=(0, 0, self.display_width, self.display_height))
        
        # Update zoom label
        self.zoom_label.config(text=f"{int(self.zoom_level * 100)}%")
        
        # Update display
        self.update_display()
        
        # Center the view when zooming in
        if self.zoom_level > 1.0:
            self.canvas.xview_moveto(0.25)
            self.canvas.yview_moveto(0.25)
    
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
