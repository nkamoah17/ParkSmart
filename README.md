# ParkSmart
Providing stress-free parking. (finding a slab of free asphalt shouldn’t be gut-wrenching)
This code works by creating a set of regions for parking slots using set_region.py (for each the first frame of a video) and when detectronn.py is run it puts out a dictionary for each frame of the video, with the positions marked in set_regions.py as occupied or not occupied. 


This is a barebones implementation of how ParkSmart works. The plan is to use CloudSQL so the data will be updated regularly and this data will be sent to the mobile phones or navigation systems of drivers in vehicles.


The aim is to make parking easier by sending occupancy information of each parking slot. 
