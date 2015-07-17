__author__ = 'Sajith'

import json;
import os;
import sys;
import urllib.request;

fileName = sys.argv[1];
jsonFile = fileName + '.json';
txtFile = fileName + '.txt' ;
with open(jsonFile, 'r') as f:
    data = json.load(f);
    file = open(txtFile, "w");
    for items in data:
        file.write('\n');
        file.write('Package:' + items.get('library'));
        file.write('\n');
        file.write('Version:' + str(items.get('version')));
        file.write('\n');
        file.write('License:' + items.get('license'));
        file.write('\n');
        response = urllib.request.urlopen(items.get('link'));
        file.write(response.read().decode('utf-8'));
        file.write("--------------------------------------------------------------------------------------------\n");
       
