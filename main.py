#!/usr/bin/python3
import vg, subprocess
import numpy as np
from solid import *
from solid.utils import *
from scipy.spatial.transform import Rotation
import open3d as o3d

from config.config import Config
config = Config()

def main():
	# bt = bottom teeth
	'''
	bt1 = np.array([0, 1, 0])
	bt2 = np.array([-1, 0, 0])
	bt3 = np.array([1, 0, 0])
	bt4 = np.array([0, 0.5, 0])
	bt5 = np.array([0, 1, -1])
	'''

	bt1 = np.array([-1, 1, -1])
	bt2 = np.array([-1,-1, 1])
	bt3 = np.array([1, 1, 1])
	bt4 = bt1*0.8#np.array([-0.5, 0.5, -0.5])
	bt5 = np.array([-0.8, 1, -1.2])

	print(vg.euclidean_distance(bt1, bt2))
	print(vg.euclidean_distance(bt1, bt3))

	create_bottom_teeth(bt1, bt2, bt3, bt4, bt5)
	mesh_bottom_teeth = o3d.io.read_triangle_mesh(config.BOTTOM_TEETH_STL)

	mesh_sphere_origin = o3d.geometry.TriangleMesh.create_sphere(radius=0.2)
	mesh_sphere_origin.paint_uniform_color([1, 0.706, 0])
	mesh_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=5, 
			origin=[-2, -2, -2])

	o3d.visualization.draw_geometries([mesh_bottom_teeth, mesh_frame,
		mesh_sphere_origin])


def create_bottom_teeth(p1, p2, p3, p4, p5):
	'''
	p1, p2, p3 are center, then 2 edges of front (outer edge) of teeth
	p4 is right behind p1 at center of teeth on inner edge, to calculate depth
	p5 is right below p1 on the outer edge, to calculate height
	Does not return an object
	Instead, saves an STL file in location given in config to be called in main
	'''
	segments = 120

	# calculate center & radius of outer cylinder
	rad, center = define_circle(p1, p2, p3)
	print(rad)
	print(center)

	# calculate difference in radius between outer and inner cylinders
	diff = vg.euclidean_distance(p1, p4)
	print(diff)

	# calculate height of cylinders
	height = vg.euclidean_distance(p1, p5)
	print(height)


	# starting position of cylinders? - center at 0,0,0; top facing z direction
	bottom_teeth = (cylinder(r=rad, h=height, center=True, segments=segments) -
			cylinder(r=rad-diff, h=height, center=True, segments=segments))

	# translate so that top of cylinder is flush with xy axis
	bottom_teeth = translate([0,0,-height/2])(
		bottom_teeth
		)

	# subtract half of teeth to make half circle
	bottom_teeth = bottom_teeth - translate([0,-rad,-height/2])(cube([rad*3, rad*2, height*2], center=True))

	# scale properly
	bottom_teeth = scale([vg.euclidean_distance(np.array([0,0,0]), p3)/rad, 
						  vg.euclidean_distance(np.array([0,0,0]), p1-(p2+p3)/2)/rad, 
						  1])(bottom_teeth)
	
	# TODO 
	# Break rotation into 2 parts
	print(p2-p3)
	print((p2+p3)/2)

	# 1
	# Rotate X unit vector to vector between p2, p3, 
	# analagous to edges of flat surface of the co-concentric cylinder objects
	if p1[0] < 0:
		rad = -rad
	x_rotation_matrix = rotation_matrix_from_vectors(
							[rad, 0, 0], p2-p3)
	x_rotation_angles = rotation_matrix_to_angles(x_rotation_matrix)
	print(x_rotation_angles)
	bottom_teeth = rotate(x_rotation_angles)(bottom_teeth)
	
	# 2
	# Rotate Y unit vector to vector from midway point between p2 & p3, to p1
	original_y_vector = [0, -rad, 0]
	r = Rotation.from_matrix(x_rotation_matrix)
	new_y_vector = r.apply(original_y_vector)

	y_rotation_matrix = rotation_matrix_from_vectors(
							new_y_vector, (p1 - (p2+p3)/2))
	y_rotation_angles = rotation_matrix_to_angles(y_rotation_matrix)
	print(y_rotation_angles)
	bottom_teeth = rotate(y_rotation_angles)(bottom_teeth)


	# Translate center of cylinders to midway point between p2 & p3
	bottom_teeth = translate((p2+p3)/2)(bottom_teeth)

	bottom_teeth += translate(p1)(sphere(r=0.25))
	bottom_teeth += translate(p2)(sphere(r=0.25))
	bottom_teeth += translate(p3)(sphere(r=0.25))

	# render and save to SCAD file
	path = scad_render_to_file(bottom_teeth, config.BOTTOM_TEETH_SCAD)
	sh = '''"''' + str(config.OPENSCAD_EXE) + '''"''' + ' ' + str(config.BOTTOM_TEETH_SCAD) + ' -o ' + str(config.BOTTOM_TEETH_STL)
	exit_code = subprocess.call(sh)
	return

def define_circle(A, B, C):
	'''
	Given 3 points A, B, C, in 3D space, return radius and center coordinates
	'''
	a = np.linalg.norm(C - B)
	b = np.linalg.norm(C - A)
	c = np.linalg.norm(B - A)
	s = (a + b + c) / 2
	R = a*b*c / 4 / np.sqrt(s * (s - a) * (s - b) * (s - c))
	b1 = a*a * (b*b + c*c - a*a)
	b2 = b*b * (a*a + c*c - b*b)
	b3 = c*c * (a*a + b*b - c*c)
	P = np.column_stack((A, B, C)).dot(np.hstack((b1, b2, b3)))
	P /= b1 + b2 + b3
	return (R, P)

def rotation_matrix_from_vectors(vec1, vec2):
    a, b = (vec1 / np.linalg.norm(vec1)).reshape(3),\
    	(vec2 / np.linalg.norm(vec2)).reshape(3)
    v = np.cross(a, b)
    c = np.dot(a, b)
    s = np.linalg.norm(v)
    kmat = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    rotation_matrix = np.eye(3) + kmat + kmat.dot(kmat) * ((1 - c) / (s ** 2))
    return rotation_matrix

def rotation_matrix_to_angles(rotation_matrix):
	return Rotation.from_matrix(rotation_matrix).as_euler("xyz", degrees=True)

if __name__ == "__main__":
	main()