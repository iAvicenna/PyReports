#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 12:21:02 2020

@author: avicenna
"""

import os
import sys
import matplotlib.pyplot as plt
import numpy as np
from PyReports import Report, Section, Text, Image, List, Link

module_path = os.path.dirname(os.path.dirname(os.path.abspath( __file__ )))
sys.path.append(module_path)


#create some figures for the report
fig1,ax1 = plt.subplots(1,1)
x_range = np.arange(-5,5,0.1)
ax1.plot(x_range, np.cos(x_range)*np.sin(x_range), color='tab:blue')
plt.close()

fig2,ax2 = plt.subplots(1,1)
ax2.plot(x_range, np.cos(x_range)*np.tan(x_range), linestyle='dashed', color='tab:red')
plt.close()

fig3,ax3 = plt.subplots(1,1)
ax3.plot(x_range, -np.exp(x_range) + np.exp(0), linestyle='dashed', color='tab:brown')
plt.close()

fig4,ax4 = plt.subplots(1,1)
ax4.plot(x_range, x_range + 0.5, color='tab:green')
plt.close()

report = Report(contains_tex=True)
report.add_report_title('PAGE TITLE')

#create a section and add some stuff
section1 = Section(1)
section1.add_section_title('Section 1 (demonstration of adding basic objects)')

#add some text
section1.add_text('Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut ac tempus nunc, vitae gravida nisi. Nam ac nisl tempor, iaculis orci ut, blandit felis. Cras volutpat lacus nec nulla viverra, a luctus velit finibus. Aenean eu ullamcorper nunc. Sed eleifend eu augue ut venenatis. Integer velit nibh, volutpat ut ante sed, varius tincidunt dolor. Nam luctus pulvinar tincidunt. Sed ut elit feugiat, elementum nunc sit amet, ultrices nibh. Maecenas vitae leo vel felis pellentesque dapibus non ut est. Vestibulum sapien mauris, pretium ut lectus vitae, cursus sollicitudin nunc. Etiam consequat hendrerit ultrices. Aliquam sit amet mattis leo, in fringilla augue.')

#add images side by side with captions
captions = ['Caption1', 'Caption2', 'Caption3', 'Caption4']
section1.add_images([fig1,fig2, fig3, fig4],scales=[1]*4, captions=captions)

#add a link
section1.add_link('https://www.lipsum.com/', 'Lipsum generator')

#create a subsection 1.1 and add text and two lists
ssection = Section(1.1, is_subsection=True)
ssection.add_section_title('Sub Section 2 Title')
ssection.add_text('Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse fermentum posuere vestibulum. Quisque nec ante varius, efficitur velit ac, aliquet metus. Duis id magna facilisis, fringilla nisl a, faucibus libero. Donec malesuada finibus justo et iaculis. Praesent pellentesque pulvinar iaculis. Suspendisse interdum viverra nisl eget ultricies. Aenean non odio ut quam ornare ornare. Aliquam feugiat fringilla sollicitudin. Quisque posuere magna ipsum, sed placerat nulla venenatis id. Sed non velit vitae dolor sagittis pharetra.')

#add a list of texts
texts = [Text('Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin nec lacinia dolor.'),
         Text('Morbi augue justo, euismod et ante quis, laoreet congue est. Aliquam erat volutpat.'),
         Text('Praesent pharetra magna vel nunc scelerisque interdum.', font_size=30), Link('https://www.lipsum.com/', 'Lipsum generator')]
ssection.add_list(texts)

texts = [Text('Lorem ipsum dolor sit amet, consectetur adipiscing elit.'),
         Text('Vestibulum auctor eleifend commodo.')
         ]
ssection.add_list(texts, is_ordered=True)


#create new section and add a multitab containing an image, a text and a list
section2 = Section(2)
section2.add_section_title('Section 2 (demonstration of multitabs)')
list1 = List([Text('Lorem ipsum dolor sit amet, consectetur adipiscing elit.'),
              Text('Nullam efficitur mattis laoreet. '),
              Text(' Maecenas cursus ornare massa, nec eleifend arcu posuere sed.', font_size=4)])
tab_contents = [[Image(fig1),Text('Donec venenatis libero a orci pellentesque mattis.')],
                [list1, Text('Nunc arcu est, lacinia vitae justo eget, fringilla fermentum nibh.')]]
section2.add_multitab(0, 2, ['Tab1','Tab2'], tab_contents)

#create new section and add some tex formulas
section3 = Section(3)
section3.add_section_title('Section 3 (demonstration of tex)')
section3.add_text('This is proved by the following formula:')
section3.add_text('{$\int_0^t f(s,z)ds = g(z,t),$}', alignment='center')
section3.add_text('and the following')
section3.add_text('{$\int_0^a g(z,t)dt = h(z,a).$}', alignment='center', font_size=50)



report.add_section(section1) #add section 1
report.add_section(ssection) #add subsection 1.1
report.add_section(section2) #add subsection 2
report.add_section(section3) #add subsection 3
report.write_html('example_report.html')


