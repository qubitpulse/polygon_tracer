"""
Interactive polygon tracer GUI.
- Load an image
- Click to place vertices; lines connect them automatically
- Close the polygon via button or clicking near the first point
- Export: 2D outline PNG, filled PNG, and extruded STL
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw
import numpy as np
import cv2
import trimesh
import os

POINT_RADIUS = 6
CLOSE_THRESHOLD = 18
EXTRUDE_HEIGHT = 5.0
SCALE_MM = 200.0


class PolygonTracer:
    def __init__(self, root):
        self.root = root
        self.root.title("Polygon Tracer")

        self.points = []
        self.closed = False
        self.img_orig = None
        self.orig_w = 0
        self.orig_h = 0
        self.scale = 1.0
        self._display_size = (400, 400)
        self._tk_img = None
        self._preview_line = None

        # ── toolbar ──
        toolbar = tk.Frame(root)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        tk.Button(toolbar, text="Load Image", command=self.load_image).pack(side=tk.LEFT, padx=4, pady=4)
        tk.Button(toolbar, text="Undo", command=self.undo).pack(side=tk.LEFT, padx=4, pady=4)
        tk.Button(toolbar, text="Close Polygon", command=self.close_polygon).pack(side=tk.LEFT, padx=4, pady=4)
        tk.Button(toolbar, text="Clear All", command=self.clear).pack(side=tk.LEFT, padx=4, pady=4)

        sep = tk.Frame(toolbar, width=2, bd=1, relief=tk.SUNKEN)
        sep.pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=2)

        tk.Button(toolbar, text="Save", command=self.save).pack(side=tk.LEFT, padx=4, pady=4)

        self.status = tk.Label(toolbar, text="Load an image to begin", anchor=tk.W)
        self.status.pack(side=tk.LEFT, padx=10)

        # ── canvas with scrollbar support ──
        self.canvas = tk.Canvas(root, bg="#222", cursor="crosshair")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Motion>", self.on_motion)

    # ── image loading ──

    def load_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.tiff *.webp")])
        if not path:
            return
        self.img_orig = Image.open(path).convert("RGB")
        self.orig_w, self.orig_h = self.img_orig.size
        self.points.clear()
        self.closed = False
        self._preview_line = None

        # force geometry update so winfo returns real sizes
        self.root.update_idletasks()
        self._compute_scale()
        self._redraw()
        self.status.config(text=f"Loaded {os.path.basename(path)} — click to place points")

    def _compute_scale(self):
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        if cw < 10:
            cw = 800
        if ch < 10:
            ch = 600
        self.scale = min(cw / self.orig_w, ch / self.orig_h, 1.0)
        dw = int(self.orig_w * self.scale)
        dh = int(self.orig_h * self.scale)
        self._display_size = (dw, dh)

    # ── drawing ──

    def _redraw(self):
        if self.img_orig is None:
            return

        dw, dh = self._display_size
        disp = self.img_orig.copy().resize((dw, dh), Image.LANCZOS)
        draw = ImageDraw.Draw(disp)

        scaled = [(x * self.scale, y * self.scale) for x, y in self.points]

        # draw lines between consecutive points
        for i in range(len(scaled) - 1):
            draw.line([scaled[i], scaled[i + 1]], fill="red", width=2)
        if self.closed and len(scaled) >= 3:
            draw.line([scaled[-1], scaled[0]], fill="red", width=2)

        # draw vertex dots
        for i, (sx, sy) in enumerate(scaled):
            r = POINT_RADIUS
            color = "lime" if i == 0 and len(scaled) >= 3 and not self.closed else "red"
            draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=color, outline="white")

        # bake to tk image and put on canvas
        self._tk_img = ImageTk.PhotoImage(disp)
        self.canvas.delete("all")
        self._preview_line = None  # was destroyed by delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self._tk_img)

    # ── interaction ──

    def on_click(self, event):
        if self.img_orig is None:
            return
        if self.closed:
            self.status.config(text="Polygon is closed. Undo, Clear, or Save.")
            return

        ox = event.x / self.scale
        oy = event.y / self.scale

        # snap to first point to close?
        if len(self.points) >= 3:
            fx, fy = self.points[0]
            if np.hypot((ox - fx) * self.scale, (oy - fy) * self.scale) < CLOSE_THRESHOLD:
                self.closed = True
                self._redraw()
                self.status.config(text=f"Polygon closed ({len(self.points)} pts). Save when ready.")
                return

        self.points.append((ox, oy))
        self._redraw()
        n = len(self.points)
        if n == 1:
            self.status.config(text="1 point placed. Keep clicking to add more.")
        elif n == 2:
            self.status.config(text="2 points. Keep going, or click near the green dot to close.")
        else:
            self.status.config(text=f"{n} points. Click near the green dot or press Close Polygon.")

    def on_motion(self, event):
        if self.img_orig is None or self.closed or len(self.points) == 0:
            if self._preview_line is not None:
                self.canvas.delete(self._preview_line)
                self._preview_line = None
            return

        lx, ly = self.points[-1]
        sx, sy = lx * self.scale, ly * self.scale

        if self._preview_line is not None:
            self.canvas.coords(self._preview_line, sx, sy, event.x, event.y)
        else:
            self._preview_line = self.canvas.create_line(
                sx, sy, event.x, event.y, fill="yellow", dash=(4, 4), width=1)

    # ── actions ──

    def close_polygon(self):
        if len(self.points) < 3:
            messagebox.showwarning("Too few points", "Need at least 3 points to close.")
            return
        if self.closed:
            return
        self.closed = True
        self._redraw()
        self.status.config(text=f"Polygon closed ({len(self.points)} pts). Save when ready.")

    def undo(self):
        if self.closed:
            self.closed = False
            self._redraw()
            self.status.config(text=f"Reopened. {len(self.points)} points.")
        elif self.points:
            self.points.pop()
            self._redraw()
            self.status.config(text=f"{len(self.points)} points.")
        self._preview_line = None

    def clear(self):
        self.points.clear()
        self.closed = False
        self._preview_line = None
        self._redraw()
        self.status.config(text="Cleared. Click to place points.")

    def save(self):
        if len(self.points) < 3:
            messagebox.showwarning("Not enough points", "Place at least 3 points first.")
            return

        out_dir = filedialog.askdirectory(title="Save outputs to folder")
        if not out_dir:
            return

        pts = np.array(self.points, dtype=np.int32)
        h, w = self.orig_h, self.orig_w
        cv_pts = pts.reshape(-1, 1, 2)

        # 2D edges
        edge_img = np.zeros((h, w), dtype=np.uint8)
        cv2.polylines(edge_img, [cv_pts], isClosed=True, color=255, thickness=2)
        cv2.imwrite(os.path.join(out_dir, "edges_2d.png"), edge_img)

        # 2D filled
        filled_img = np.zeros((h, w), dtype=np.uint8)
        cv2.fillPoly(filled_img, [cv_pts], 255)
        cv2.imwrite(os.path.join(out_dir, "filled_2d.png"), filled_img)

        # STL extrusion
        pts_2d = pts.astype(float).copy()
        pts_2d[:, 1] = h - pts_2d[:, 1]
        bbox = pts_2d.max(axis=0) - pts_2d.min(axis=0)
        sc = SCALE_MM / max(bbox)
        pts_2d = (pts_2d - pts_2d.min(axis=0)) * sc

        n = len(pts_2d)
        bottom = np.column_stack([pts_2d, np.zeros(n)])
        top = np.column_stack([pts_2d, np.full(n, EXTRUDE_HEIGHT)])
        verts = np.vstack([bottom, top])

        faces = []
        for i in range(n):
            j = (i + 1) % n
            faces.append([i, j, j + n])
            faces.append([i, j + n, i + n])

        bot_c, top_c = bottom.mean(axis=0), top.mean(axis=0)
        ci_b, ci_t = len(verts), len(verts) + 1
        verts = np.vstack([verts, [bot_c], [top_c]])
        for i in range(n):
            j = (i + 1) % n
            faces.append([ci_b, j, i])
            faces.append([ci_t, i + n, j + n])

        mesh = trimesh.Trimesh(vertices=verts, faces=np.array(faces))
        mesh.fix_normals()
        mesh.export(os.path.join(out_dir, "case.stl"))

        dims = np.round(mesh.bounds[1] - mesh.bounds[0], 1)
        messagebox.showinfo("Saved", (
            f"edges_2d.png\n"
            f"filled_2d.png\n"
            f"case.stl ({len(mesh.faces)} faces)\n"
            f"Size: {dims[0]} x {dims[1]} x {dims[2]} mm"))
        self.status.config(text=f"Saved to {out_dir}")


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("900x700")
    app = PolygonTracer(root)
    root.mainloop()
