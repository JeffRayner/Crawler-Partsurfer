# Crawler HP Partsurfer
<tr>
This is a Crawler to extract the list of Part Numbers of all the products used in a specific HP device, through its Part Number or Serial Number. 

The Crawler use thread for every request to optimizate, and create a logger file, where you can see which Part Number not founded, or inform if serial number was used

Save in a Excel file.

<br>

## How intall
<tr>
First you need install Python 3 and some libraries.
After installed python on your system, run this command's line
<br><br>

- pip install bs4==0.0.1
- pip install pandas==1.4.2
- pip install xlsxwriter==3.0.3
<br>

## How use
<tr>
To call the crawler, you need import the Class PartSurf from crawler.py

The Class need twice arguments :

- 1º it's a text with all partnumbers device, separeted by (,)
- 2º it's a excel file name to export, but default's name is "Result"

Exemple:

| PartNumber Devid | Model Name | Category | PartNumber | Description |
| :---: | :---: | :---: | :---: | :---: | 
| 310587-201 | HPE DL380 G3 | Memory Module | 260741-001 | 64MB SDRAM Small.. | 
