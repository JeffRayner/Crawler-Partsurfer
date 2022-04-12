# Crawler HP Partsurfer
<tr>
This is a Crawler to extract the list of Part Numbers of all the products used in a specific HP device, through its Part Number or Serial Number. 

The Crawler use thread for every request to optimizate, and create a logger file, where you can see which Part Number not founded, or inform if serial number was used

Save in a CSV file.

<br>

## How intall
<tr>
First you need install Python 3.9 and a librarie.
<br><br>

- pip install bs4==0.0.1
<br>

## How use
<tr>
To call crawler, you need import the Class PartSurf from crawler.py

Init Class passing a text with all part number's or serial number's device.

Public Methods:

- ### class.find( )
- ### class.save( FileName )

## Output Exemple:

| Model PartNumber | Model Name | Category | PartNumber | Description |
| :---: | :---: | :---: | :---: | :---: | 
| 310587-201 | HPE DL380 G3 | Memory Module | 260741-001 | 64MB SDRAM Small.. | 
