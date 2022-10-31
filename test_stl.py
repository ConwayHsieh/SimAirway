#!/usr/bin/python3
import open3d as o3d

mesh = o3d.io.read_triangle_mesh("./solidpython_example_01.stl")

mesh_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=5, 
		origin=[-2, -2, -2])

o3d.visualization.draw_geometries([mesh, mesh_frame])