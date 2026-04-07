# Automatic Polygon Detection: Why It Failed & What Would Fix It

## What We Tried

`detect_polygon.py` used OpenCV's Line Segment Detector (LSD) to find straight
lines in the image, then clustered nearby endpoints into shared vertices and
tried to extract the largest closed polygon from the resulting graph.

## Why It Failed

### 1. Signal-to-noise ratio

LSD found **1,246 segments** total. Only ~15-20 of those belong to the drawn
overlay. The rest come from:

- **Notebook ruled lines** — horizontal lines spanning the full image, similar
  length and strength to the overlay segments.
- **Case surface texture** — the matte black plastic has a fine grain that
  produces many short edge responses.
- **Case edge highlights** — the physical edges of the keyboard case create
  strong straight segments that overlap with (but don't exactly match) the drawn
  outline.
- **Shadows and lighting gradients** — the case casts soft shadows that produce
  spurious edge responses along the bottom and right sides.
- **Label text and logos** — the Redragon sticker and regulatory markings add
  dozens of short segments in the center of the case.

### 2. No reliable way to distinguish overlay from scene

The drawn red/orange lines are only ~2-3px wide in the image. LSD treats them
the same as any other edge. Without color filtering (which we avoided to keep
the tool generic), there is no structural property that reliably separates
"drawn overlay" from "real-world edge."

### 3. Graph became too noisy to extract a clean cycle

With 181 segments surviving the length filter, the endpoint clustering produced
195 vertices and a densely connected graph. The degree-based pruning
(iteratively removing degree-1 vertices) was too aggressive — it collapsed the
graph down to a 3-vertex triangle because many real polygon corners had
spurious extra connections from nearby noise segments.

## What Would Be Required for It to Work

### Approach A: Color-aware filtering (partially generic)

If the overlay is a distinct color from the scene, convert to HSV and mask for
high-saturation pixels. This isolates drawn lines (markers, digital overlays)
from the grayscale-ish photo beneath. Then run LSD on only the masked region.

- **Pro**: simple, effective when the overlay has any saturated color.
- **Con**: fails for black/white/gray overlays; not fully color-agnostic.

### Approach B: Paired image differencing

Require two images: the original photo and the annotated version. Subtract them
to isolate only the drawn overlay, then detect lines on the difference image.

- **Pro**: perfectly generic regardless of line color.
- **Con**: requires the user to provide the un-annotated original.

### Approach C: Deep learning line/polygon detection

Use a trained model (e.g., LETR, HAWP, or a fine-tuned instance segmentation
model) that understands "drawn annotation" vs "scene edge" semantically.

- **Pro**: handles arbitrary colors, styles, and noisy backgrounds.
- **Con**: requires a trained model, GPU ideally, and significant setup.

### Approach D: Hybrid — auto-detect + manual correction (recommended)

Run a rough auto-detection pass (LSD + heuristic scoring), propose candidate
polygon vertices in the GUI, and let the user drag/add/delete points to fix
mistakes. This combines the speed of automation with the reliability of human
judgment.

- **Pro**: practical, works for any image, tolerates imperfect detection.
- **Con**: still requires some manual effort.

### Approach E: Structured input

Instead of detecting lines from a photo, require the user to draw the polygon
on a clean background (e.g., white canvas with only the drawn lines). This
eliminates all background noise and makes LSD detection trivial.

- **Pro**: near-perfect detection.
- **Con**: can't work directly from a photo of the object.

## Summary

The core problem is **scene complexity vs. overlay simplicity**. A 15-segment
polygon drawn over a photo containing hundreds of natural edges is a needle in
a haystack without some form of prior knowledge — whether that's color, a
reference image, a learned model, or human guidance.

The GUI tracer (`polygon_tracer.py`) sidesteps this entirely by letting the
user be the detector, which is the most robust solution for arbitrary images.
