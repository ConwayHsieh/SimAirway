#!/usr/bin/python3

import vg
import numpy as np, copy
import matplotlib.pyplot as plt
import open3d as o3d

def main():
	# User IO for initial conditions
	# hard code for now
	
	width = 5
	point_a = np.array([3,-4,0])
	point_b = np.array([1,0,0])
	point_c = np.array([5,5,6])

	draw_struct(point_a, point_b, point_c)


def draw_struct(point_a, point_b, point_c, r_height=1, r_depth=1):
	# draw_struct will redraw the defined structure at given anchor points
	# 
	# Params:
	# point_a = head of cylinder
	# point_b = where cylinder meets rectangle
	# point_c = tail of rectangular prism
	# all points of format np.array([x,y,z])
	# r_depth = how wide rectangular prism will be (into/out of the page)
	# r_height = how tall rectangluar prism will be
	point_a = np.float64(point_a)
	point_b = np.float64(point_b)
	point_c = np.float64(point_c) 
	
	point_a += 0.001
	point_b += 0.001
	point_c += 0.001

	mesh_sphere_origin = o3d.geometry.TriangleMesh.create_sphere(radius=0.2)
	mesh_sphere_a = o3d.geometry.TriangleMesh.create_sphere(radius=0.4).\
		translate(point_a)
	mesh_sphere_b = o3d.geometry.TriangleMesh.create_sphere(radius=0.6).\
		translate(point_b)
	mesh_sphere_c = o3d.geometry.TriangleMesh.create_sphere(radius=0.4).\
		translate(point_c)

	mesh_rect_1_display = make_rect(point_b, point_a, r_height, r_depth)
	mesh_rect_2_display = make_rect(point_b, point_c, r_height, r_depth)

	# display structures
	mesh_rect_1_display.compute_vertex_normals()
	mesh_rect_2_display.compute_vertex_normals()
	mesh_sphere_b.paint_uniform_color([1, 0.706, 0])

	mesh_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=5, 
		origin=[-2, -2, -2])

	o3d.visualization.draw_geometries(\
		[mesh_rect_1_display, mesh_rect_2_display,
			mesh_sphere_a, mesh_sphere_b, mesh_sphere_c, mesh_sphere_origin,
			mesh_frame])
	return

def make_rect(point_1, point_2, r_height, r_depth):
	
	# initialize rectangle
	rect_length = vg.euclidean_distance(point_1, point_2)
	mesh_rect = o3d.geometry.TriangleMesh.create_box(
		depth=r_depth,
		height=r_height,
		width=rect_length) 
	
	mesh_rect_display = copy.deepcopy(mesh_rect)

	# translate center of rectangle to halfway point between 1 & 2
	mesh_rect_display.translate(tuple((point_1 + point_2)/2))

	#calculate rotation matrix for rect
	rotation_matrix =\
		rotation_matrix_from_vectors(np.array([rect_length,0,0]), point_2)
	#print(rotation_matrix)
	
	# if there is a rotation, rotate and translate to fix rotation offset
	if not np.isnan(rotation_matrix).any():
		# rotate based on calculated matrix
		mesh_rect_display.rotate(rotation_matrix) 
	
		# translate to fix rotation offset
		# find if point B is to the left or right of point C
		verts = np.asarray(mesh_rect_display.vertices)
		left_2 = verts[verts[:,0].argsort()][0:4,:].mean(0)
		right_2 = verts[verts[:,0].argsort()][4:,:].mean(0)

		print(verts[verts[:,0].argsort()])
		print(left_2)
		print(right_2)

		if point_1[0] < point_2[0]:
			t = point_1 - left_2
		elif point_1[0] > point_2[0]:
			t = point_1 - right_2
		else: # point_1[0] = point_2[0]
			if point_1[0] > 0:
				t = point_1 - left_2
			elif point_b[0] < 0:
				t = point_1 - right_2
			else: # point_1[0] = point_2[0] == 0
				t = np.array([0,0,0])
		
		print(t)
		mesh_rect_display.translate(tuple(t))
	
	return mesh_rect_display

def calc_rot_angles(p1, p2):
	p1 = np.array(p1)
	p2 = np.array(p2)

	p_diff = p2-p1

	theta_xz = vg.signed_angle(vg.basis.x, p_diff, look=vg.basis.y)
	theta_xy = vg.signed_angle(vg.basis.x, p_diff, look=vg.basis.z)
	
	return [theta_xz, theta_xy]

def rotation_matrix_from_vectors(vec1, vec2):
    a, b = (vec1 / np.linalg.norm(vec1)).reshape(3),\
    	(vec2 / np.linalg.norm(vec2)).reshape(3)
    v = np.cross(a, b)
    c = np.dot(a, b)
    s = np.linalg.norm(v)
    kmat = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    rotation_matrix = np.eye(3) + kmat + kmat.dot(kmat) * ((1 - c) / (s ** 2))
    return rotation_matrix

if __name__ == "__main__":
	main()