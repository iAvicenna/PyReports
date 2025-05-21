#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 27 15:21:14 2023

@author: avicenna
"""

import PyReports as pr

report = pr.Report('test')

with report:
  with pr.Section('test'):
    with pr.Tab(['A','B']):
      pr.Txt('A')
      with pr.Grid(1,2):
        pr.Txt('TEST')
        with pr.Tab(['C','D']):
          pr.Txt('C')
          pr.Txt('D')


report.to_html('tab_in_tab.html')
