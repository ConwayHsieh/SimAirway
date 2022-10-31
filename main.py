#!/usr/bin/python3
import subprocess
from solid import *
from solid.utils import *
import open3d as o3d

from config.config import Config
config = Config()

def main():
	print(config.TOP_TEETH_SCAD)
	d = difference()(
	  cube(size = 10, center = True),
	  sphere(r = 6.5, segments=300)
	)
	path = scad_render_to_file(d, config.TOP_TEETH_SCAD)

	sh = '''"''' + str(config.OPENSCAD_EXE) + '''"''' + ' ' + str(config.TOP_TEETH_SCAD) + ' -o ' + str(config.TOP_TEETH_STL)

	exit_code = subprocess.call(sh)
	print(exit_code)

	mesh = o3d.io.read_triangle_mesh(config.TOP_TEETH_STL)

	mesh_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=5, 
			origin=[-2, -2, -2])

	o3d.visualization.draw_geometries([mesh, mesh_frame])

if __name__ == "__main__":
	main()