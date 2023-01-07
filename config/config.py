#!/usr/bin/python3
import os, configparser

class Config:
	config = configparser.ConfigParser()
	config.read(os.path.join(os.getcwd(), './config/config.ini'))

	TOP_TEETH_SCAD = config['OBJ']['TOP_TEETH_SCAD']
	TOP_TEETH_STL = config['OBJ']['TOP_TEETH_STL']

	BOTTOM_TEETH_SCAD = config['OBJ']['BOTTOM_TEETH_SCAD']
	BOTTOM_TEETH_STL = config['OBJ']['BOTTOM_TEETH_STL']

	TONGUE_SCAD = config['OBJ']['TONGUE_SCAD']
	TONGUE_STL = config['OBJ']['TONGUE_STL']

	EPIGLOTTIS_SCAD = config['OBJ']['EPIGLOTTIS_SCAD']
	EPIGLOTTIS_STL = config['OBJ']['EPIGLOTTIS_STL']

	OPENSCAD_EXE = config['EXE']['OPENSCAD_EXE']

