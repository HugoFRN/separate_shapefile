import fiona
import os
import argparse
import unicodedata
import yaml
import sys
import tqdm

def clean_string(s):
    # Remove special characters
    s = unicodedata.normalize('NFKD', s)
    s = u"".join([c for c in s if not unicodedata.combining(c)])
    s = str(s.rstrip())
    s = s.replace(' ', '-').replace('/', '').replace('(', '').replace(')', '')
    return s


def main(paths, output_dir, category='SIFRA_KMRS', crop_id_file='', crop_group_file=''):
    '''
    Separate by attribute a shapefile and create shapefile for each value of the attribute.
    i.e : In the Austrian LPIS shapefile, the attribute "SIFRA_KMRS" contain the type of crop in a field. This script
    allow to regroup the same crops in the same shapefile.
    :param paths: Paths the the shapefile to separate (can be a list of path for multiple separation)
    :param output_dir: Output directory : The output file are places there
    :param category: Name of the attribute to use to separate
    :param crop_id_file: Path to the txt file containing the crops id
    :param crop_group_file: Path to the yaml file containing the crops groups
    :return:
    '''
    # Crop group listed by categories:
    if crop_group_file != '':
        try:
            with open(crop_group_file) as f:
                crop_group = yaml.load(f)
            for group in crop_group:
                for i, x in enumerate(crop_group[group]):
                    crop_group[group][i] = clean_string(x)
        except Exception as e:
            print(e)
            sys.exit(0)

    # Link crop id to crop name
    if crop_id_file != '':
        try:
            with open(crop_id_file, 'r') as f:
                lines = f.readlines()
            id = [x.split('-')[0] for x in lines]
            categor = [x.split('-')[1] for x in lines]
        except:
            print(Exception('ERROR : Cannot find file %s' % crop_id_file))
            sys.exit(0)

    for PATH in paths:
        found_cat = []
        try:
            with fiona.open(PATH, 'r') as source:
                for f in tqdm.tqdm(source, total=len(source)):
                    ind = len(found_cat)
                    try:
                        f_cat = f['properties'][category]
                    except:
                        print(Exception('ERROR : Cannot find attribute %s in shapefile' % category))
                        sys.exit(0)
                    f_cat = f_cat.lstrip('0')
                    if crop_id_file != '':
                        for i, num in enumerate(id):
                            if f_cat == num:
                                f_cat = categor[i]
                                break
                    f_cat = clean_string(f_cat)

                    if crop_group_file == '':
                        # Separate each attribute
                        for i, cat in enumerate(found_cat):
                            if cat[0] == f_cat:
                                ind = i
                                break
                        if ind == len(found_cat):
                            found_cat.append(
                                [f_cat,
                                 fiona.open(os.path.join(output_dir, os.path.splitext(os.path.basename(PATH))[-2] +
                                                         '-' + f_cat + '.shp'), 'w', **source.meta)])
                        found_cat[ind][1].write(f)
                    else:
                        # Group by category
                        is_defined = False
                        for group in crop_group:
                            if f_cat in crop_group[group]:
                                is_defined = True
                                for i, cat in enumerate(found_cat):
                                    if group == cat[0]:
                                        ind = i
                                        break
                                if ind == len(found_cat):
                                    found_cat.append([group,
                                                      fiona.open(os.path.join(output_dir,
                                                                              os.path.splitext(os.path.basename(PATH))[
                                                                                  -2] +
                                                                              '-' + group + '.shp'), 'w',
                                                                 **source.meta)])
                                break
                        if is_defined:
                            found_cat[ind][1].write(f)
                        else:
                            print('cannot find %s in any available category' % f_cat)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Separate by attribute a shapefile')
    parser.add_argument('input_file', action='store', help='Input file')
    parser.add_argument('-o', metavar='output_dir', action='store', default='', help='Output directory')
    parser.add_argument('-a', metavar='attribute', action='store', default='SIFRA_KMRS',
                        help='Shapefile attribute to separate with')
    parser.add_argument('-cg', metavar='crop_group_file', action='store', default='',
                        help='Path to the yaml file containing the crops groups')
    parser.add_argument('-f', metavar='crop_id_file', action='store', default='',
                        help='Path to the txt file containing the crops id')
    args = parser.parse_args()
    input_file = [args.input_file]
    output_path = args.o
    category = args.a
    crop_id = args.f
    crop_groups = args.cg

    main(input_file, output_path, category, crop_id, crop_groups)
