#!/usr/bin/python3
import os, configparser

class Config:
	config = configparser.ConfigParser()
	config.read(os.path.join(os.getcwd(), './config/config.ini'))

	TOP_TEETH_SCAD = config['OBJ']['TOP_TEETH_SCAD']
	TOP_TEETH_STL = config['OBJ']['TOP_TEETH_STL']
	OPENSCAD_EXE = config['EXE']['OPENSCAD_EXE']

