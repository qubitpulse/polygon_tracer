# Polygon Tracer

A tkinter GUI for tracing straight-edged polygon outlines over reference
images and exporting them as 2D PNGs and extruded 3D STL files.

## Quick Start

**Dependencies**: Python 3.10+, plus:

```
pip install pillow numpy opencv-python trimesh
```

**Run**:

```
python polygon_tracer.py
```

## Usage

1. **Load Image** — open any PNG/JPG/BMP/TIFF/WebP as a background reference
2. **Click** on the image to place vertices — red dots appear, connected by red
   lines as you go
3. A yellow dashed preview line follows your cursor from the last point
4. The first point turns **green** once you have 3+ points — click near it to
   close the polygon, or press **Close Polygon**
5. **Undo** removes the last point (or reopens a closed polygon)
6. **Clear All** resets everything
7. **Save** — pick an output folder, generates:
   - `edges_2d.png` — polygon outline on black background (original image resolution)
   - `filled_2d.png` — filled white silhouette
   - `case.stl` — extruded 3D mesh (default: 200mm longest side, 5mm thick)

Extrusion height and scale are configurable at the top of `polygon_tracer.py`
(`EXTRUDE_HEIGHT`, `SCALE_MM`).

---

## What This App Does (2D Feature Coverage)

Cross-referencing against the full set of features needed for a complete 2D
shape drawing application:

### Implemented

| Feature | Status | Notes |
|---|---|---|
| Point placement (click) | Done | Click-to-place on image canvas |
| Straight line segments | Done | Auto-connected between consecutive points |
| Closed polygon | Done | Snap-to-first-point or Close Polygon button |
| Preview line | Done | Yellow dashed line follows cursor |
| Undo | Done | Remove last point or reopen closed polygon |
| Clear | Done | Full reset |
| Image reference layer | Done | Load a background image to trace over |
| 2D edge export (PNG) | Done | Outline on black background |
| 2D filled export (PNG) | Done | Solid white silhouette |
| 3D extrusion (STL) | Done | Flat extrude with top/bottom caps |

### Missing for a Complete 2D Drawing App

Grouped roughly by priority — what matters most for practical shape creation:

#### Curves (High Priority)

The single biggest gap. Without curves, all shapes are faceted polygons.

| Feature | What it adds |
|---|---|
| Cubic Bezier curves | The universal smooth-curve primitive (Photoshop pen tool, SVG, fonts). Two control handles per anchor define curvature |
| Quadratic Bezier | Simpler curves with one control point — good for quick arcs |
| Arc tool | Click center + radius + sweep angle for circular/elliptical arcs |
| Freehand / pencil | Dense polyline from mouse drag, optionally auto-smoothed |
| Corner-to-smooth toggle | Convert a sharp vertex to a Bezier-smoothed one and back |

#### Vertex & Edge Editing (High Priority)

Currently vertices can only be added at the end or removed from the end.

| Feature | What it adds |
|---|---|
| Drag vertex | Click and drag to reposition any placed point |
| Insert vertex on edge | Add a point in the middle of an existing line segment |
| Delete vertex | Remove any vertex (not just the last one) and reconnect neighbors |
| Move edge | Translate a segment while keeping its neighbors connected |

#### Precision & Snapping (Medium Priority)

| Feature | What it adds |
|---|---|
| Snap to grid | Constrain placement to a configurable grid |
| Snap to angle | Lock lines to 15/30/45/90 degree increments (shift-click) |
| Snap to existing point | Merge with a nearby vertex when close enough |
| Coordinate entry | Type exact X,Y for a point instead of clicking |
| Rulers / measurements | Show distances between points, edge lengths |

#### Shape Primitives (Medium Priority)

Pre-built generators that emit the appropriate points/curves automatically:

| Feature | What it adds |
|---|---|
| Rectangle | 4-corner rectangle from drag (optionally with rounded corners) |
| Ellipse / circle | Approximated by 4 cubic Bezier segments, or parametric |
| Regular polygon | N-sided, defined by center + radius |
| Star | Inner + outer radius, N points |

#### Boolean / Path Operations (Medium Priority)

Combining multiple shapes:

| Feature | What it adds |
|---|---|
| Union | Merge two shapes into one outline |
| Subtract | Cut one shape out of another |
| Intersect | Keep only the overlapping region |
| XOR / exclude | Keep everything except the overlap |

#### Transforms (Medium Priority)

| Feature | What it adds |
|---|---|
| Move / translate | Shift entire shape by dx, dy |
| Rotate | Around a chosen pivot point |
| Scale | Uniform or non-uniform resize |
| Mirror / flip | Horizontal or vertical |
| Skew / shear | Slant along one axis |

#### Refinement (Lower Priority)

| Feature | What it adds |
|---|---|
| Offset / inset | Parallel copy of the path at a set distance |
| Fillet / chamfer | Round or bevel individual corners |
| Simplify (Ramer-Douglas-Peucker) | Reduce vertex count while preserving shape |
| Smooth | Fit curves to a jagged polyline |

#### Visual / UX (Lower Priority)

| Feature | What it adds |
|---|---|
| Stroke width control | Variable line thickness |
| Stroke style | Solid, dashed, dotted |
| Fill color / pattern | Visual fill in the editor (not just export) |
| Multiple shapes | More than one polygon on the canvas at once |
| Layers | Organize shapes into stackable layers |
| Zoom & pan | Navigate large images at different scales |
| Keyboard shortcuts | Speed up common actions |
| Undo/redo history | Full history stack, not just single undo |

#### The Minimum to Make Any 2D Shape

Only **4 primitives** are needed to represent any 2D shape:

1. Point placement
2. Straight line segments
3. Cubic Bezier curves
4. Close path

Polygon Tracer has 3 of 4. Adding Bezier curves would make it theoretically
complete — everything else is productivity and convenience.

---

## What Would Be Needed for a Complete 3D Drawing App

Going from 2D to 3D is not just "add a Z axis." The fundamental object changes
from a **closed curve** (1D boundary of a 2D region) to a **closed surface**
(2D boundary of a 3D volume), which brings qualitatively new problems.

### What Polygon Tracer Does in 3D Today

| Feature | Status |
|---|---|
| Flat extrusion | Done — push the 2D polygon into Z by a fixed height |
| Watertight mesh | Done — top/bottom caps + side walls, normals fixed |
| STL export | Done — compatible with slicers and 3D viewers |

This is a single operation: 2D polygon → 3D slab.

### New 3D Concepts (No 2D Equivalent)

These features don't exist in 2D at all — they are unique to working in three
dimensions:

| Feature | What it does |
|---|---|
| **Extrusion (variable)** | Push a 2D profile along a path or with varying height, not just flat |
| **Revolution / lathe** | Spin a 2D profile around an axis to create a solid of revolution (bowls, bottles, chess pieces) |
| **Loft** | Blend smoothly between two or more 2D cross-sections at different Z heights |
| **Sweep** | Move a 2D profile along an arbitrary 3D path (pipes, rails, molding) |
| **Subdivision surfaces** | Iteratively smooth a coarse mesh into organic shapes |
| **Sculpting** | Freeform push/pull/smooth on mesh vertices like digital clay |
| **Normals** | Each face has a direction vector — affects lighting, 3D printing validity, and inside/outside |
| **UV mapping** | Define how 2D textures wrap onto 3D surfaces |
| **Topology management** | Edge loops, face loops, manifold validation, hole detection and repair |

### 2D Features That Get Harder in 3D

| 2D Concept | 3D Equivalent | Why it's harder |
|---|---|---|
| Line segment | **Face** (triangle/quad) | 1D connection → 2D surface patch |
| Bezier curve | **Bezier surface / NURBS** | 1D control points → 2D control point grid |
| Closed path | **Manifold mesh** | Must be watertight — every edge shared by exactly 2 faces |
| Fill (solid color) | **Volume** | Interior is 3D, not a flat region |
| Boolean ops | **CSG (Constructive Solid Geometry)** | 3D intersection math is dramatically more complex |
| Offset / inset | **Shell / wall thickness** | Requires computing offset surfaces with self-intersection handling |
| Point selection | **Vertex/edge/face selection** | Three selection modes instead of one |
| Undo | **Undo with mesh topology** | Mesh operations are expensive to store and reverse |

### The Minimum for Any 3D Shape

Analogous to the 2D minimum of 4 primitives:

1. **Vertices** — points in XYZ space
2. **Triangular faces** — the universal 3D surface primitive (like cubic
   Beziers are for 2D curves)
3. **Manifold closure** — every edge shared by exactly 2 faces (watertight
   solid)

For practical modeling, you also need:

4. **Smooth surfaces** (NURBS or subdivision) — without these, curved objects
   require millions of triangles
5. **Boolean CSG** — combining simple solids into complex ones
6. **Extrusion / revolution / loft** — the bridge from 2D drawings to 3D

### Quantifying the Jump

| | 2D | 3D |
|---|---|---|
| Core primitives | 4 | 3–6 |
| Convenience features | ~25 | ~40+ |
| Data per vertex | 2 floats | 3 floats |
| Connectivity | 1D chain (prev/next) | 2D manifold (half-edge structures) |
| Validation needed | Closed? Self-intersecting? | Manifold? Watertight? Normals consistent? Non-degenerate? |

The feature count only grows ~60%, but the **implementation complexity per
feature** roughly triples due to topology management, surface math, and the
need to maintain valid watertight solids after every operation.

### A Realistic Roadmap from Here

Building toward a complete 3D app from Polygon Tracer's current state:

```
Current state
  [x] Point placement
  [x] Straight lines
  [x] Close polygon
  [x] Flat extrusion → STL

Phase 1 — Complete 2D
  [ ] Bezier curves (pen tool)
  [ ] Drag/insert/delete vertices
  [ ] Shape primitives (rect, ellipse)
  [ ] Zoom & pan

Phase 2 — Richer Extrusion
  [ ] Variable height extrusion
  [ ] Revolution / lathe from 2D profile
  [ ] Loft between multiple 2D cross-sections
  [ ] Sweep along a path

Phase 3 — Direct 3D Editing
  [ ] 3D viewport (OpenGL or similar)
  [ ] Vertex/edge/face selection in 3D
  [ ] Move/rotate/scale in 3D space
  [ ] Boolean CSG operations

Phase 4 — Production 3D
  [ ] NURBS / subdivision surfaces
  [ ] Topology validation & repair
  [ ] Multi-format export (STL, OBJ, STEP, 3MF)
  [ ] Undo/redo with full mesh state
```

Each phase roughly triples the codebase. Phase 1 is a weekend. Phase 2 is a
few weeks. Phase 3 requires an OpenGL integration and is a significant
undertaking. Phase 4 is what separates hobby tools from Blender/Fusion 360.
