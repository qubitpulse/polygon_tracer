# 2D Shape Drawing Features & 3D Translation

A comprehensive breakdown of the tools and primitives needed to construct
arbitrary 2D shapes, and what changes when extending to 3D.

---

## Part 1: The Complete 2D Shape Feature Set

Every 2D shape editor — from Photoshop to Illustrator to CAD tools — is built
from a surprisingly small set of core primitives. Everything else is
convenience built on top.

### 1.1 Point Placement & Selection

| Feature | Description |
|---|---|
| Click-to-place | Drop a vertex at a coordinate (what polygon_tracer does) |
| Snap-to-grid | Constrain placement to a grid |
| Snap-to-point | Snap near existing vertices |
| Snap-to-edge | Snap to the nearest point on an existing line |
| Snap-to-angle | Constrain to 15°/30°/45°/90° increments from previous point |
| Coordinate entry | Type exact X,Y values |
| Point selection | Click to select, shift-click to multi-select |
| Marquee select | Drag a box to select multiple points |
| Select all / none / invert | Bulk selection toggles |

### 1.2 Straight Lines & Polylines

| Feature | Description |
|---|---|
| Line segment | Two-point straight connection |
| Polyline | Chain of connected straight segments (open) |
| Polygon | Closed polyline |
| Constrained line | Hold shift to lock to horizontal/vertical/45° |
| Midpoint insertion | Add a vertex in the middle of an existing edge |

### 1.3 Curves

This is where complexity jumps. Straight lines only need endpoints; curves need
control geometry.

| Feature | Description |
|---|---|
| Quadratic Bézier | 1 control point between 2 anchors — simple smooth curve |
| Cubic Bézier | 2 control points between 2 anchors — the Photoshop pen tool standard |
| Arc (circular) | Defined by center + radius + start/end angle |
| Arc (elliptical) | Same but with separate X/Y radii |
| Spline (B-spline) | Smooth curve passing through/near a series of control points |
| Freehand / pencil | Dense polyline from mouse movement, optionally smoothed |

**Key insight**: cubic Béziers are the universal primitive. PostScript, SVG,
TrueType fonts, and the Photoshop pen tool all use them. Any smooth 2D curve
can be approximated to arbitrary precision with enough cubic Bézier segments.

### 1.4 Shape Primitives

Pre-built shapes that generate the appropriate points/curves automatically:

| Feature | Description |
|---|---|
| Rectangle | 4 corners, optionally with rounded corners (arc or Bézier) |
| Ellipse / circle | Bézier approximation (4 cubic segments) or parametric |
| Regular polygon | N-sided, center + radius |
| Star | Inner + outer radius, N points |
| Line / arrow | Simple two-point with optional arrowhead |

### 1.5 Path Operations (Boolean Geometry)

Combining multiple shapes into new ones:

| Feature | Description |
|---|---|
| Union | Merge two shapes into one |
| Subtract / difference | Cut one shape out of another |
| Intersect | Keep only the overlapping area |
| Exclude (XOR) | Keep everything except the overlap |
| Divide | Split shapes at their intersection boundaries |

### 1.6 Transform

| Feature | Description |
|---|---|
| Move / translate | Shift by dx, dy |
| Rotate | Around a point, by an angle |
| Scale | Uniform or non-uniform |
| Mirror / flip | Horizontal or vertical |
| Skew / shear | Slant along one axis |
| Free transform | Arbitrary affine matrix |

### 1.7 Editing & Refinement

| Feature | Description |
|---|---|
| Move vertex | Drag individual points |
| Move edge | Translate a segment while keeping neighbors connected |
| Delete vertex | Remove and reconnect neighbors |
| Insert vertex | Add a point along an existing edge |
| Convert corner ↔ smooth | Toggle between sharp and Bézier-smoothed vertex |
| Offset / inset | Create a parallel copy of the path at a distance |
| Simplify | Reduce point count while preserving shape (Ramer-Douglas-Peucker) |
| Smooth | Apply curve fitting to jagged polylines |
| Fillet / chamfer | Round or bevel a corner |

### 1.8 Stroke & Fill (Visual, not geometric)

| Feature | Description |
|---|---|
| Stroke width | Line thickness |
| Stroke style | Solid, dashed, dotted |
| Fill | Solid, gradient, pattern, none |
| Opacity | Per-shape transparency |

---

## Part 2: The Minimum Feature Set for Any 2D Shape

You can construct **any** 2D shape with just:

1. **Point placement** — define vertices
2. **Straight line segments** — connect them
3. **Cubic Bézier curves** — handle all smooth/curved sections
4. **Close path** — seal the shape

That's 4 primitives. Everything else is productivity tooling built on top:

- Shape primitives → generate points + curves automatically
- Boolean operations → combine simple shapes into complex ones
- Transforms → reposition without redefining
- Snapping → precision without manual coordinate entry
- Undo/redo → error recovery

The polygon tracer currently implements #1, #2, and #4. Adding #3 (Bézier
curves) would make it capable of representing any 2D shape.

---

## Part 3: Translating to 3D — What Changes

### 3.1 The new dimension isn't just "one more axis"

Going from 2D to 3D isn't a linear increase in complexity. A 2D shape is a
closed curve on a plane. A 3D shape is a closed **surface** in space — and
surfaces are fundamentally harder than curves.

### 3.2 The 3D equivalents

| 2D Concept | 3D Equivalent | Complexity change |
|---|---|---|
| Point (vertex) | Point (vertex) | Same |
| Line segment (edge) | **Face** (triangle/quad) | Lines → surfaces |
| Bézier curve | Bézier **surface** / NURBS | 1D control → 2D control grid |
| Closed path | **Manifold mesh** (watertight) | Must be topologically valid |
| Fill | **Volume** | Interior is 3D, not 2D |
| Boolean ops | **CSG** (Constructive Solid Geometry) | Much harder intersection math |
| Offset / inset | **Shell / thickness** | Requires normal computation |
| Stroke width | N/A (edges have no width) | Concept doesn't transfer |

### 3.3 New features that don't exist in 2D

| Feature | Description |
|---|---|
| Extrusion | Push a 2D profile into the Z axis (what our STL export does) |
| Revolution / lathe | Spin a 2D profile around an axis to make a solid |
| Loft | Blend between two or more 2D cross-sections |
| Sweep | Move a 2D profile along a 3D path |
| Subdivision surface | Iteratively smooth a coarse mesh |
| Sculpting | Freeform push/pull on mesh vertices (like digital clay) |
| Normals | Each face has a direction — affects lighting, printing, validity |
| UV mapping | How 2D textures wrap onto 3D surfaces |
| Topology management | Edge loops, face loops, manifold checks, hole detection |

### 3.4 The minimum feature set for any 3D shape

Analogous to the 2D minimum:

1. **Vertices** — points in 3D space
2. **Faces** — triangles connecting 3 vertices (the universal 3D primitive,
   like cubic Béziers are for 2D curves)
3. **Manifold closure** — every edge shared by exactly 2 faces (watertight)

That's it for **mesh-based** modeling. But practical 3D also needs:

4. **NURBS / subdivision surfaces** — for smooth curved geometry without
   millions of triangles
5. **Boolean CSG** — for combining primitives into complex solids
6. **Extrusion** — the bridge from 2D drawings to 3D objects

### 3.5 Quantifying the jump

| Metric | 2D | 3D |
|---|---|---|
| Core primitives | 4 (point, line, curve, close) | 3-6 (vertex, face, closure + smooth surfaces, CSG, extrude) |
| Convenience features | ~25 (see tables above) | ~40+ (all 2D equivalents + extrude, revolve, loft, sweep, sculpt, normals, UV, topology) |
| Data per vertex | 2 floats (x, y) | 3 floats (x, y, z) |
| Connectivity | 1D chain (prev → next) | 2D manifold (face adjacency, half-edge structures) |
| Validation | Path is closed? Self-intersecting? | Manifold? Watertight? Normals consistent? Non-degenerate faces? |
| Difficulty | Moderate | Substantially harder — topology and surface math are the bottleneck |

### 3.6 Where polygon_tracer sits today

```
2D features:          [x] points  [x] lines  [ ] curves  [x] close
3D features:          [x] extrude (flat)  [ ] everything else
Practical capability: Can make any flat-sided 2D outline into a 3D slab
```

The biggest single upgrade would be **Bézier curves** in 2D (handles rounded
case corners) and **variable-height extrusion or lofting** in 3D (handles
non-flat objects).

---

## Summary

2D shapes are fully described by 4 primitives. 3D adds roughly 60% more core
features on top, but the real complexity increase is in **validation and
topology** — making sure a 3D mesh is a valid, watertight solid rather than a
collection of disconnected triangles. The jump from "draw a polygon" to "model
a solid" is less about feature count and more about the mathematical machinery
underneath.
