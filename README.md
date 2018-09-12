## separate_shapefile

Script used to separate a LPIS shapefile into shapefiles of the same crop types for the Perceptive Sentinel project. 

### Requirements:

This python script requires a few libraries listed in _requirements.txt_:
To install them (Using pip):

`pip install -r requirements.txt`

### Usage:

`separate_shapefile -h` 
Print the help.

The script accept differents arguments:
    
    -a attribute : Name of the attribute to look for in the shapefile (SIFRA_KMRS or SNAR_BEZEI for example)
    -f crop_id_file : (OPTIONAL) Path to the txt file containing the crops id (ie: translate the id in the shapefile into the corresponding name)
    -cg crop_group_file : (OPTIONAL) Path to the yaml file defining the differents crops groups. If not given, will separate every crop found
    -o output_dir : Path to the output directory (default to ./)
    input_file: Path to input shapefile
    
#### Example:

The command used for the Austrian shapefile:

`python3 separate_shapefile.py path_to_austria_lpis.shp -a SNAR_BEZEI -cg croup_group.yaml -o output_dir/`

The command used for the Slovenian shapefile:

`python3 separate_shapefile.py path_to_slovenian_lpis.shp -a SIFRA_KMRS -f crop_id.txt -cg croup_group.yaml -o output_dir/`
