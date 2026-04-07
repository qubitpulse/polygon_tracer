"""
Tests for STL mesh generation and STEP solid export.
Creates convex and concave polygons, runs the triangulation + extrusion,
and checks mesh quality via trimesh + cadquery.
"""

import numpy as np
import cv2
import trimesh
from scipy.spatial import Delaunay
import cadquery as cq
import tempfile
import os
import pytest

EXTRUDE_HEIGHT = 5.0
SCALE_MM = 200.0


def scale_pts(pts_raw, img_h):
    pts_2d = pts_raw.astype(float).copy()
    pts_2d[:, 1] = img_h - pts_2d[:, 1]
    bbox = pts_2d.max(axis=0) - pts_2d.min(axis=0)
    sc = SCALE_MM / max(bbox)
    pts_2d = (pts_2d - pts_2d.min(axis=0)) * sc
    return pts_2d


def build_mesh(pts_2d):
    """Reproduce the STL generation from polygon_tracer.save()."""
    n = len(pts_2d)

    tri = Delaunay(pts_2d)
    cap_faces = []
    poly_contour = pts_2d.reshape(-1, 1, 2).astype(np.float32)
    for simplex in tri.simplices:
        centroid = pts_2d[simplex].mean(axis=0)
        if cv2.pointPolygonTest(poly_contour, centroid.tolist(), False) >= 0:
            cap_faces.append(simplex)
    cap_faces = np.array(cap_faces)

    bottom = np.column_stack([pts_2d, np.zeros(n)])
    top = np.column_stack([pts_2d, np.full(n, EXTRUDE_HEIGHT)])
    verts = np.vstack([bottom, top])

    faces = []
    for i in range(n):
        j = (i + 1) % n
        faces.append([i, j, j + n])
        faces.append([i, j + n, i + n])

    for f in cap_faces:
        faces.append([f[0], f[2], f[1]])

    for f in cap_faces:
        faces.append([f[0] + n, f[1] + n, f[2] + n])

    mesh = trimesh.Trimesh(vertices=verts, faces=np.array(faces))
    mesh.fix_normals()
    return mesh


def build_step(pts_2d):
    """Reproduce the STEP generation from polygon_tracer.save()."""
    pts_cq = [tuple(p) for p in pts_2d.tolist()]
    solid = cq.Workplane("XY").polyline(pts_cq).close().extrude(EXTRUDE_HEIGHT)
    return solid


SHAPES = {
    "square": [(100, 100), (300, 100), (300, 300), (100, 300)],
    "triangle": [(250, 50), (400, 400), (100, 400)],
    "l_shape": [
        (100, 100), (300, 100), (300, 250),
        (200, 250), (200, 400), (100, 400),
    ],
    "arrow": [
        (200, 50), (250, 200), (400, 200),
        (280, 300), (320, 450), (200, 370),
        (80, 450), (120, 300), (0, 200), (150, 200),
    ],
    "u_shape": [
        (100, 100), (150, 100), (150, 350),
        (350, 350), (350, 100), (400, 100),
        (400, 400), (100, 400),
    ],
}


@pytest.mark.parametrize("name,pts", SHAPES.items(), ids=SHAPES.keys())
def test_mesh_watertight(name, pts):
    pts_2d = scale_pts(np.array(pts, dtype=np.int32), img_h=500)
    mesh = build_mesh(pts_2d)
    assert mesh.is_watertight
    assert mesh.is_volume
    assert mesh.euler_number == 2


@pytest.mark.parametrize("name,pts", SHAPES.items(), ids=SHAPES.keys())
def test_step_export(name, pts):
    pts_2d = scale_pts(np.array(pts, dtype=np.int32), img_h=500)
    solid = build_step(pts_2d)
    assert solid.val().Volume() > 0

    step_path = os.path.join(tempfile.gettempdir(), f"test_{name}.step")
    cq.exporters.export(solid, step_path)
    assert os.path.getsize(step_path) > 100


@pytest.mark.parametrize("name,pts", SHAPES.items(), ids=SHAPES.keys())
def test_volumes_match(name, pts):
    """STL mesh volume and STEP solid volume should agree."""
    pts_2d = scale_pts(np.array(pts, dtype=np.int32), img_h=500)
    mesh = build_mesh(pts_2d)
    solid = build_step(pts_2d)
    assert abs(mesh.volume - solid.val().Volume()) < 1.0
