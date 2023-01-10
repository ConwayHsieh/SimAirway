#!/usr/bin/python3

import numpy as np, copy
import matplotlib.pyplot as plt
import open3d as o3d


r_w = 5.0
r_h = 1.0
r_d = 1.0

mesh_rect_1 = o3d.geometry.TriangleMesh.create_box(width=5.0,
													height=1.0,
													depth=1.0)
mesh_rect_2 = o3d.geometry.TriangleMesh.create_box(width=3.0,
													height=1.0,
													depth=1.0)
#mesh_rect.translate(tuple([0, -r_h/2, -r_d/2]))

mesh_rect = mesh_rect_1
#mesh_rect = mesh_rect_1.crop(mesh_rect_2.get_oriented_bounding_box())

mesh_rect.compute_vertex_normals()


mesh_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=10, 
	origin=[-2, -2, -2])

#o3d.visualization.draw_geometries([mesh_rect, mesh_frame])

mat = o3d.visualization.rendering.MaterialRecord()
mat.base_color = np.array([1, 1, 1, .5])

o3d.visualization.draw({'name':'test', 'geometry': mesh_rect, 'material': mat})