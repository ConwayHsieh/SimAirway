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
	# test data here

	# bt = bottom teeth

	bt1 = np.array([-1, 1, -1])
	bt2 = np.array([-1,-1, 1])
	bt3 = np.array([1, 1, 1])
	bt4 = bt1*0.8#np.array([-0.5, 0.5, -0.5])
	bt5 = np.array([-0.8, 1, -1.2])

	# tt = top teeth
	tt1 = bt1
	tt2 = bt2
	tt3 = bt3
	tt4 = bt4
	tt5 = bt5
	tt6 = -bt1

	# t = tongue
	t1 = np.array([0, 1, 0])
	t2 = np.array([0, 1, -2])
	t3 = np.array([3, 2, 0])
	t4 = np.array([0, 0, 0])

	# l = larynx
	l1 = np.array([-1, 1, 1])
	l2 = np.array([-1, 1, -1])
	l3 = np.array([1, -1, 1])
	l4 = np.array([-0.5, 0.5 , 1])
	l5 = np.array([0, 0, 1])

	#create_teeth(bt1, bt2, bt3, bt4, bt5, None) # create bottom teeth
	#create_teeth(tt1, tt2, tt3, tt4, tt5, tt6) # create top teeth
	
	#mesh_bottom_teeth = o3d.io.read_triangle_mesh(config.BOTTOM_TEETH_STL)
	#mesh_top_teeth = o3d.io.read_triangle_mesh(config.TOP_TEETH_STL)

	#create_tongue(t1, t2, t3, t4)
	#mesh_tongue = o3d.io.read_triangle_mesh(config.TONGUE_STL)

	create_epiglottis(t1, t2, t3)
	mesh_epiglottis = o3d.io.read_triangle_mesh(config.EPIGLOTTIS_STL)

	create_vc(t1, t4, t3)
	mesh_vc = o3d.io.read_triangle_mesh(config.VC_STL)

	create_larynx(l1, l2, l3, l4, l5)
	mesh_larynx = o3d.io.read_triangle_mesh(config.LARYNX_STL)

	mesh_sphere_origin = o3d.geometry.TriangleMesh.create_sphere(radius=0.2)
	mesh_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=5, 
			origin=[-2, -2, -2])

	#o3d.visualization.draw_geometries([mesh_vc, mesh_larynx, mesh_frame,
	#	mesh_sphere_origin])
	meshlist = [mesh_larynx, mesh_epiglottis, mesh_frame, mesh_sphere_origin]

	for m in meshlist:
		if m == mesh_frame:
			continue
		elif m == mesh_sphere_origin:
			m.paint_uniform_color([1, 0.706, 0])
			continue

		m.compute_vertex_normals()
		m.paint_uniform_color([np.random.random(1)[0], np.random.random(1)[0], np.random.random(1)[0]])

	o3d.visualization.draw_geometries(meshlist)

	return

def create_teeth(p1, p2, p3, p4, p5, p6=None):
	'''
	p1, p2, p3 are center, then 2 edges of front (outer edge) of teeth
	p4 is right behind p1 at center of teeth on inner edge, to calculate depth
	p5 is right below p1 on the outer edge, to calculate height
	p6 only if top teeth; defines roof of mouth object extending from p1->p6
	
	Does NOT return an object
	Instead, saves an STL file in location given in config to be called in main
	'''
	if p6 is None:
		print('Creating bottom teeth object since p6 == None')
		TEETH_STL = config.BOTTOM_TEETH_STL
		TEETH_SCAD = config.BOTTOM_TEETH_SCAD
		isTopTeeth = False
	else:
		print('Creating top teeth object since p6 is given')
		TEETH_STL = config.TOP_TEETH_STL
		TEETH_SCAD = config.TOP_TEETH_SCAD
		isTopTeeth = True

	print(vg.euclidean_distance(p1, p2))
	print(vg.euclidean_distance(p1, p3))
	if vg.euclidean_distance(p1, p2) != vg.euclidean_distance(p1, p3):
		print('Warning: p2 & p3 are not equidistant from p1!')

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
	teeth = (cylinder(r=rad, h=height, center=True, segments=segments) -
			cylinder(r=rad-diff, h=height, center=True, segments=segments))

	# translate so that top of cylinder is flush with xy axis
	teeth = translate([0,0,-height/2])(
		teeth
		)

	# subtract half of teeth to make half circle
	teeth = teeth - translate([0,-rad,-height/2])(cube([rad*3, rad*2, height*2], center=True))

	# scale properly
	teeth = scale([vg.euclidean_distance(np.array([0,0,0]), p3)/rad, 
						  vg.euclidean_distance(np.array([0,0,0]), p1-(p2+p3)/2)/rad, 
						  1])(teeth)

	# Add roof of mouth object if TopTeeth object
	if isTopTeeth:
		roof_height = height/10
		teeth += translate([0,0, -roof_height/2])(
			cube([vg.euclidean_distance(np.array([0,0,0]), p3)*3,
				  vg.euclidean_distance(np.array([0,0,0]), p1-(p2+p3)/2)*2,
				  roof_height], 
				 center=True)
			)
	
	# Break rotation into 2 parts
	# 1
	# Rotate X unit vector to vector between p2, p3, 
	# analagous to edges of flat surface of the co-concentric cylinder objects
	if p1[0] < 0:
		rad = -rad
	x_rotation_matrix = rotation_matrix_from_vectors(
							[rad, 0, 0], p2-p3)
	x_rotation_angles = rotation_matrix_to_angles(x_rotation_matrix)
	print(x_rotation_angles)
	teeth = rotate(x_rotation_angles)(teeth)
	
	# 2
	# Rotate Y unit vector to vector from midway point between p2 & p3, to p1
	original_y_vector = [0, -rad, 0]
	r = Rotation.from_matrix(x_rotation_matrix)
	new_y_vector = r.apply(original_y_vector)

	y_rotation_matrix = rotation_matrix_from_vectors(
							new_y_vector, (p1 - (p2+p3)/2))
	y_rotation_angles = rotation_matrix_to_angles(y_rotation_matrix)
	print(y_rotation_angles)
	teeth = rotate(y_rotation_angles)(teeth)


	# Translate center of cylinders to midway point between p2 & p3
	teeth = translate((p2+p3)/2)(teeth)

	# visulize p1, p2, p3
	'''
	teeth += translate(p1)(sphere(r=0.25))
	teeth += translate(p2)(sphere(r=0.25))
	teeth += translate(p3)(sphere(r=0.25))
	'''

	# render and save to SCAD file
	create_obj(teeth, TEETH_SCAD, TEETH_STL)
	return

def create_tongue(p1, p2, p3, p4):
	'''
	Viewing from above, back to front viewpoint
	p1 is front left top of tongue
	p2 is front right top of tongue
	p3 is back left top of tongue, directly behind p1, to calculate depth/angle
	p4 is directly beneath p1, to calculate height
	
	Does NOT return an object
	Instead, saves an STL file in location given in config to be called in main
	'''
	t_width = vg.euclidean_distance(p1, p2) # distance between left and right of tongue
	t_height = vg.euclidean_distance(p1,p4) # how thick tongue is
	t_depth = vg.euclidean_distance(p1,p3) # how far tongue extends into mouth

	# create tongue based on parameters
	# move p1 to [0,0,0]
	tongue = translate([t_depth/2, -t_height/2, -t_width/2])(cube([t_depth, t_height, t_width], center=True))

	# rotate
	rotation_matrix = rotation_matrix_from_vectors([1,0,0], p3-p1)
	rotation_angles = rotation_matrix_to_angles(rotation_matrix)
	tongue = rotate(rotation_angles)(tongue)

	# translate
	tongue = translate(p1)(tongue)

	# visulize p1, p2, p3, p4
	'''
	tongue += translate(p1)(sphere(r=0.25))
	tongue += translate(p2)(sphere(r=0.25))
	tongue += translate(p3)(sphere(r=0.25))
	'''

	# render and save to SCAD file
	create_obj(tongue, config.TONGUE_SCAD, config.TONGUE_STL)
	return

def create_epiglottis(p1, p2, p3, p4=None):
	'''
	Can use 4 points to, similar to create_tongue.
	If only given 3 points, will instead assume thickness of object

	viewing from above:
	p1 is bottom left top of epiglottis
	p2 is bottom right top of epiglottis
	p3 is top left top of epiglottis, directly above p1, to calculate depth/angle
	p4 is directly behind p1, to calculate thickness (if given)
	
	Does NOT return an object
	Instead, saves an STL file in location given in config to be called in main
	'''
	e_width = vg.euclidean_distance(p1, p2) # distance between left and right of epiglottis
	e_depth = vg.euclidean_distance(p1,p3) # how tall epiglottis is
	if p4 is not None:
		e_height = vg.euclidean_distance(p1,p4) # how thick epiglottis is
	else: #assume thickness
		e_height = max(e_width, e_depth)/50

	# create tongue based on parameters
	# move p1 to [0,0,0]
	epiglottis = translate([e_depth/2, -e_height/2, -e_width/2])(cube([e_depth, e_height, e_width], center=True))

	# rotate
	rotation_matrix = rotation_matrix_from_vectors([1,0,0], p3-p1)
	rotation_angles = rotation_matrix_to_angles(rotation_matrix)
	epiglottis = rotate(rotation_angles)(epiglottis)

	# translate
	epiglottis = translate(p1)(epiglottis)

	# visulize p1, p2, p3, p4
	'''
	epglottis += translate(p1)(sphere(r=0.25))
	epiglottis += translate(p2)(sphere(r=0.25))
	epiglottis += translate(p3)(sphere(r=0.25))
	'''

	# render and save to SCAD file
	create_obj(epiglottis, config.EPIGLOTTIS_SCAD, config.EPIGLOTTIS_STL)
	return

def create_vc(p1, p2, p3):
	'''
	p1, p2, p3: three points to determine triangle shape of triangular prism
	thickness will be automatically assumed

	Does NOT return an object
	Instead, saves an STL file in location given in config to be called in main
	'''
	disp = np.array([0.001, 0.001 ,0.001]) #to handle thickness
	vc = polyhedron(
			points=[p1, p2, p1-disp, p2 - disp, p3-disp, p3], 
            faces=[[0,1,2,3],[5,4,3,2],[0,4,5,1],[0,3,4],[5,2,1]]
            )

	# render and save to SCAD file
	create_obj(vc, config.VC_SCAD, config.VC_STL)
	return

def create_larynx(p1,p2,p3, p4, p5):
	'''
	# trachea points
	p1, p2: define top of cylinder, to calulate diameter of trachea (p1 front, p2 back, looking at opening)
	p3: define bottom of cylinder, to determine height of trachea; directly beneath p1
	# opening points
	p4, p5: define top, bottom of circular opening, to determine diameter; 
		should be on the straight line between p1, p3. ASSUME: perfectly circular opening
	
	Does NOT return an object
	Instead, saves an STL file in location given in config to be called in main
	'''
	# make trachea object (cylinder)
	# assume extremely thin hollow cylinder
	
	# define constants
	segments = 120
	diff = 0.1
	trachea_radius = vg.euclidean_distance(p1, p2)/2
	trachea_height = vg.euclidean_distance(p1, p3)

	# create hollow cylinder
	trachea = (cylinder(r=trachea_radius, h=trachea_height, center=True, segments=segments) -
			cylinder(r=trachea_radius-diff, h=trachea_height, center=True, segments=segments))
	
	# rotate cylinder to vertical
	trachea_rotation_matrix = rotation_matrix_from_vectors([0,0,1], [0,1,0])
	trachea_rotation_angles = rotation_matrix_to_angles(trachea_rotation_matrix)
	trachea = rotate(trachea_rotation_angles)(trachea)
	
	# translate p1 to 0,0,0
	trachea = translate([0, -trachea_height/2, -trachea_radius])(trachea)

	# make opening, using cylinder object to subtract from trachea object
	# TODO
	opening_radius = vg.euclidean_distance(p4,p5)/2
	opening = cylinder(r=opening_radius, h=trachea_radius, center=True, segments=segments)
	dist = vg.euclidean_distance(p1,p4)
	opening = translate([0,-(dist+opening_radius),0])(opening)

	# create the hole
	larynx = trachea - opening

	# rotate larynx object to final angle
	larynx = translate([0,trachea_height,0])(larynx)
	larynx_rotation_matrix = rotation_matrix_from_vectors([0,1,0], p1-p3)
	larynx_rotation_angles = rotation_matrix_to_angles(larynx_rotation_matrix)
	larynx = rotate(larynx_rotation_angles)(larynx)

	# translate larynx object
	# 0,0,0 is currently p3
	larynx = translate(p3)(larynx)

	# render and save to SCAD file
	create_obj(larynx, config.LARYNX_SCAD, config.LARYNX_STL)
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

def create_obj(obj, scad, stl):
	'''
	Call subprocess to use OPENSCAD to convert saved SCAD file into STL file
	'''
	path = scad_render_to_file(obj, scad)
	sh = '''"''' + str(config.OPENSCAD_EXE) + '''"''' + ' ' + str(scad) + ' -o ' + str(stl)
	exit_code = subprocess.call(sh)
	return

if __name__ == "__main__":
	main()