#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 27 10:39:21 2023

@author: avicenna
"""
import PyReports as pr
import numpy as np
import pandas as pd

report = pr.Report('test')

table = pd.DataFrame([[10,1],[9,3],[2,1]], columns=['A','B'])

colors = [['#FFFFFF','red'],['blue','green'],['grey','brown']]



with report:
  with pr.Section('test'):
    pr.Tbl(table, cell_colors=colors)

report.to_html('table_test.html')
