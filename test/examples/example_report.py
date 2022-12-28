#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 19 18:14:01 2022

@author: Sina Tureli
"""
import os 
from PyReports import Section, Report, Txt, Img, Grid, Plt, Amp, Cde, Fold, Tab, Qte, Lnk, from_json

dir_path = os.path.dirname(os.path.realpath(__file__))

report = Report('Test Report')
report.pretext(('One can add a pretext to a report, this could include such things as links to a home page etc at the top of the report.<br>'
                '<a href="">My home page </a> <a href="">Group home page </a></pre>'))

with report:
    
    with Section('Introduction'):
        Txt('''
            Welcome to PyReports. In PyReports two main categories are containers and objects. Containers are things that contain objects.
            Objects are images, text, code etc things that you would want to put in your report. Containers could reports, sections, grids,
            folds etc. Both the containers and the objects derive from what is called a _Node giving the report a tree structure
            with well defined parent child relation between its containers and objects. The root of the report tree is the report container
            itself where as its leaves will be the objects (objects cant contain other objects and therefore can not be parents to further
            nodes). As you will see below, Nodes have context managers which allow to type reports easily without having to specify the 
            parent and child relations explicitly. It will be guessed from context. So at the heart of report typing lies the _Context
            object in objects.py from which the _Node derives. Class methods and variables of _Context track the creation of containers 
            and objects and establish the necessary associations between them.
            ''')
            
    with Section('Basics'):
        Txt('''
            With PyReports, the suggested workflow is to use contexts (i.e with statements) to create new containers. With in any context,
            any object that is used directly becomes attached to that container whether it be a section, grid or any other object from containers.py.
            As an example one can write:
            ''')
        Txt('''
            with report('My Report'): # create a report
                with Section('Introduction'): # create a section
                    Txt('Hello world') # put a text in that section
                    
                    with Grid(2,1): # put a grid with 2 cols and 1 row in section
                        Img(path1) # put an Img in the grid
                        Img(path2) # put a second Img in the grid
            ''', formatted=True)
        Txt(
            '''
            One can directly attach a container to a parent via statements such
            as 
            
            Section('Introduction', parent=report)
            
            when needed. By the way there is a better way to display
            code using Cde object:
            
            ''')
            
        Cde('''
            with report('My Report'): # create a report
                with Section('Introduction'): # create a section
                    Txt('Hello world') # put a text in that section
                    
                    with Grid(2,1): # put a grid with 2 cols and 1 row in section
                        Img(path1) # put an Img in the grid
                        Img(path2) # put a second Img in the grid
            ''')
            
            
        Txt('''
            When displaying text, newlines are not taken into account and long
            lines get wrapped (maximum of 100 px or 50% of device width which
            can be changed via the configuration files, see section Styling Almost
            everything). Empty lines do appear as they are though. So to have an
            empty line in your text, you do not needs to insert <br><br> manually.
            It will be done automatically such as the empty line that is 
            right below this sentence.
            
            One can also itemize text by starting the line with -, 1-,2-, 1.,2.
            etc such as:
                
            -item1
            -item2
                
            or
            
                1-item1
                2-item2
                
            Not that indents at the beginning of each line are managed automatically
            relative to the text they are in. 
            
            Codes can be displayed using Cde object which has syntax highlighting
            and is automatically formatted to appear as it is on the editor.
            
            By the way you can print what the report looks like using report.summary. 
            It will show the contets of the report up to the point of printing:
            ''')
        Txt(report.summary(formatting='html'))
        
        Txt('''
            You can put single images using the Img tag. Images are directly
            embedded to the html (unless you turn that off while creating
            the image) so you can share your beatiful reports with your friends
            without having to share the images and such. You can add titles to images
            but more formatting requires using Grids which is explained in the Grid
            Layouts section.
            ''')
            
        Img(f'{dir_path}/image7.png', title='Planescape is awesome')
        

    with Section('Beware there be quotes'):
        
        Txt('''
            When you write formatted text or code, there is some internal machinery
            going on to decide when to have linebreaks and this depends on where
            are the newline characters in text. However not every newline character
            could mean that there should be a newline. For instance you might
            be displaying a code which has a variable equated to a string that has newline in it. 
            Therefore newlines inside quotation marks are disregarded when displaying
            code. This means tracking when a quote has been opened and it has been closed.
            We assume that all strings in code are flanked by double quotes,
            single quotes can be reliably parsed in a similiar way due to 
            python`s triple quote formatted strings where newlines should be considered
            as they are. So consider the following cases, first wrong, second correct:
            ''')
            
        Cde('''
            \'\'\'
            Hello world.py
            I am not a quote and I am not not a quote.
            What am I??
            \'\'\'
            
            string1 = "hello world\n I am here"
            
            string2 = \'\'\'
                        Formatting inside formatting, 
                            what a head ache
                        \'\'\'
                        
            a = 5
            
            '''
            )
            
        Cde('''
            \'\'\'
            Hello world.py
            I am not a quote and I am not not a quote.
            What am I??
            \'\'\'
            
            string1 = 'hello world\n I am here'
            
            string2 = \'\'\'
                        Formatting inside formatting, 
                            what a head ache
                        \'\'\'
                        
            a = 5
            
            '''
            )
                
        

    with Section('Grid Layouts'):
        
        Txt('''
            By using grids within grids, you can achieve any layout your heart
            desires. Consider for instance the following which uses two grids,
            one inside the other. As with single images, you can put a title
            to each grid element and we have done so below to make the layout more clear.
            ''')
            
        with Grid(2,1, ['Part 1 of Grid 1', 'Part 2 of Grid2'], end=''):
            Img(f'{dir_path}/image1.jpeg',scale=1.3)
            
            with Grid(1,3, ['Part 1 of Grid2', 'Part 2 of Grid2', 'Part 3 of Grid2'], end=''):
                Img(f'{dir_path}/image2.jpeg')
                Img(f'{dir_path}/image3.png',scale=0.5)
                Img(f'{dir_path}/image4.png',scale=0.5)
                
        Txt('''
            The code used for this layout is
            ''')
            
        
        Cde('''
            with Grid(2,1, end=''):
                Img(f'{dir_path}/image1.jpeg',scale=1.3)
                
                with Grid(1,3,end=''):
                    Img(f'{dir_path}/image2.jpeg')
                    Img(f'{dir_path}/image3.png',scale=0.5)
                    Img(f'{dir_path}/image4.png',scale=0.5)
                 ''')
                    
    with Section('Other Containers'):

        Txt('''
            Apart from Reports, Sections and Grids, there are two other containers:
            Tabs and Folds. 
            
            Tabs allow you to organize objects into tabs so that you only see
            one of object at a time, the one whose tab is selected. As an example:
            ''')

        with Tab(['Tab1','Tab2','Tab3']):
            Img(f'{dir_path}/image5.jpeg')
            Img(f'{dir_path}/image6.png',scale=0.5)
            Img(f'{dir_path}/image7.png',scale=0.5)
            
            
        Txt('''
            Apart from each item`s individual button, there is also the open all
            button which shows all the items at the same time (fun fact: this
            button is also called the Derek button. Derek hates tabulated views).
            
            The fold allows you to hide content by folding it. It comes automatically
            with the Code object (which is the only object that comes with a
            preexisting parent). But you can put other stuff in folds too,
            even other containers. This is a great way to suprise your friends!
            ''')
            
        with Fold():
            with Grid(2,1, end=''):
                Img(f'{dir_path}/image1.jpeg',scale=1.3)
                
                with Grid(1,3,end=''):
                    Img(f'{dir_path}/image2.jpeg')
                    Img(f'{dir_path}/image3.png',scale=0.5)
                    Img(f'{dir_path}/image4.png',scale=0.5)
                    
        Txt('''
            The code for such a Fold would look like:
            ''')
            
        Cde('''
            with Fold():
                with Grid(2,1, end=''):
                    Img(f'{dir_path}/image1.jpeg',scale=1.3)
                    
                    with Grid(1,3,end=''):
                        Img(f'{dir_path}/image2.jpeg')
                        Img(f'{dir_path}/image3.png',scale=0.5)
                        Img(f'{dir_path}/image4.png',scale=0.5)
            ''')
                    
    with Section('Other Simple Objects'):

        Txt('''
            Up until now, we have seen images, code and text as objects.
            There are however more. Other simple objects are links and quotes:
            ''')

        Qte('What are 10 good quotes?')            
        Lnk('#top','Click here to find out!')

        Txt('''
            Apart from these there are two advanced objects which deserve a 
            section of their own: Antigenic Cartography Maps and Plotly Plots
            ''')
            
    with Section('Advanced Objects'):
        
        Txt('''
            There are two advanced objects which deserve a section of their own.
            
            Pyreports supports adding plotly plots and antigenic cartography
            maps using respectively Plt and Amp (while keeping their full 
            interactivity):
            ''')
            
        Plt(f'{dir_path}/plotlyplot1.html')
        Amp(f'{dir_path}/acmap1.html')
        
        Txt('''
            Note that these do not use iframe, instead extract the relevant data, 
            as well as scripts and add then embed them to the report. So as 
            with images you dont need to share individual plots or maps when
            sharing your lovely reports with your friends.
            
            On the downside, with the addition of such elements, you will also 
            be adding alot of javascripts to your report and it will be diffucult to view it as raw html.
            ''')
            
        

    with Section('Styling Almost Everything'):
        
        Txt('''
            There are several way to style elements of a report. Each object
            and container allow style inputs in their creation. For instance
            consider the following text:
            ''')
            
        Txt('A GORGEOUS TEXT', style='font-size:50px;color:red')
        
        Txt('''
            This was done via the following code:
            ''')
            
        Cde('Txt(\'A GORGEOUS TEXT\', style=\'font-size:50px;color:red\')')
        
        Txt('''
            Note that you can change font-size of a text with the font-size
            input the text object but style input always takes precedence.
            
            Finally another way to style objects globally is to look at the 
            configuration files default.ini and user.ini. During the
            creation of a project, styles in default.ini and user.ini
            are included in the head of the project. default.ini 
            is meant to be the factor settings where as any changes
            you want to do should go to user.ini and will overwrite the 
            respective property in default.ini. 
            ''')
            
    with Section('Latex Support!', has_tex=True):
        Txt('''
            No good scientific report writing program can be without tex support.
            And PyReports is not without one!. Any section which should contain 
            tex formulas can be initialized with has_tex=True input so that
            the report will know to include the respective javascripts when 
            compiling. Then you can write any formula to your heart's content:
            
            $\int exp^{-x^2} dx = ?? $
            
            In order to add latex formulas, just add any latex formula
            inside a text object flanked on both sides by dollar signs as you
            would normally in latex. Note however once latex is included
            in a section, two unrelated dollar signs with in the same text
            in any part of the report can cause issue so make sure to escape
            dollar signs in such cases.
            ''')
    
    with Section('Saving Reports, Using Templates'):
        
        Txt('''
            You can initialize reports via from_template function. If you often
            create reports with similiar initial structure such as always having 
            certain links at the top and fixed section names, creating a template
            could be a good idea. Once a template (say called lab) is created 
            it can be used in creation of a report via
            
            with from_template('lab','a report') as report:

            Templates are created via the create_template function which allows
            a name for the template, pretext for the report and section titles
            as inputs. A created template will automatically be saved in the
            templates folder.
            
            An example code for creating templates is:            
            ''')
            
        Cde('''
            from PyReports import create_template

            pretext = '<pre><a href="">Link To My home page </a> <a href="l">Link to Group home page </a></pre>'
            create_template('example_template',pretext)

            ''')
            
        Txt('''
        And to use the template you can follow:
            ''')
            
        Cde('''
            from PyReports import from_template, Txt, Section

            report = from_template('example_template', 'Template Report Title')

            with report:
                with Section('Section 1'):
                    Txt(\'\'\'
                        This is a template DUH.
                        \'\'\')
            ''')
            
        Txt('''
            A template once created, is simply an empty report with some preleminary
            information that is saved as a json file. This brings us to saving reports.
            Under normal circumstances, once you are done with a report you would save
            it to an html via 
            
            report.to_html('test_report.html')

            On the other hand, you might want to save your file as json so
            that it could be loaded via PyReports in other computers or
            by your colleagues. This is done via 
            
            report.to_json('test_report.json')
            report2 = from_json('test_report.json')
            
            Once done report2 is identical to report and can be edited as
            required.
            ''')
            
    with Section('Sections within Sections'):
        
        Txt('''
            If you want to create a subsection within a subsection
            all you have to do is invoke another Section with context manager
            as such:
            ''')
            
        Cde('''
             with Section('Sections within Sections'):
                 
                 Txt(\'\'\'
                     If you want to create a subsection within a subsection
                     all you have to do is invoke another Section with context manager
                     as such:
                     \'\'\')
                     
                 with Section('Subsection'):
                     Txt(\'\'\'
                         Hello I am a subsection. My border will keep going
                         on until the end of this section.
                         <br><br><br><br><br><br><br><br>

                         \'\'\')
                     with Section('Subsubsection'):
                         Txt('Hello!')
                     
             
             ''')
             
        Txt('To see it in effect we also do it here:')
        
        with Section('Subsection'):
            Txt('''
                Hello I am a subsection. My border will keep going
                on until the end of this section.
                <br><br><br><br><br><br><br><br>
                
                ''')
            with Section('Subsubsection'):
                Txt('Hello!')
    
    with Section('The End'):

        Txt('''
            As we are nearing the end of the report it is probably a good idea
            to see again how the summary looks like:
            ''')        
            
        Txt(report.summary(formatting='html'))
        
        Txt('''
            For debugging purposes you can also print it in detailed format.
            ''')

        Txt(report.summary(detailed=True, formatting='html'))
        
        Txt('''
            As you get more comfortable with report operations you can try
            more advanced maniplations such as removing objects from one
            container and putting them to another as such:
            ''')
        
        Cde('''
            with pr.Report('Test1'):
                with pr.Section('Section1'):
                    with pr.Section('Subsection1') as subsection1:
                        text = pr.Txt('Lorem Ipsum')
            
            with pr.Report('Test2') as report2:
                section2 = pr.Section('Section1', parent=report2)

            text._parent = section2
            ''')
            
        Txt('''
            Get and set attributes are constructed such that if the parent of
            an object is changed, it is no longer linked to the previous 
            parent. If it is a container, then all of its children migrate
            with the container to the new parent`s tree. It is basically an operation
            identical to detaching a node and all its descendants and reattaching
            to another tree.
            ''')


report.to_html('test_report.html')
report.to_json('test_report.json')
report2 = from_json('test_report.json')
assert report.summary(detailed=True)==report2.summary(detailed=True)
