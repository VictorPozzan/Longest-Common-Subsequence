# -*- coding: utf-8 -*-
# This class is responsable to read and conversion data

class Data:

    def __init__(self):
        self.elements = []

    def cleanData(self, path_file): 

        file = open(path_file, 'r')
        lines = file.readlines()
        line_one = lines[0].replace(" ","")
        line_two = lines[1].replace(" ","")
                    
        return line_one, line_two

