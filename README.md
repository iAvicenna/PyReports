# PyReports
PyReports is a python library that allows typing up pdf reports easily and quickly.
It is done via a context managing. A simple example is 

```python
from PyReports import Section, Report, Txt, Img, Plt, Cde, Grid

report = Report('Test Report')  

with report:

  with Section('Introduction'):  
    Txt('This is a text')  
    Img('./image1.png') 
    
  with Section('Results', has_tex=True):
    Plt('./plotly_graph.html')
    
    with Grid(2,1):
      Img('./image1.png')
      Img('./image2.png')
      
    Txt('''
        One can also put a latex formula using regular tex code:

        $\int exp^{-x^2} dx = ?? $
        
        Once has_tex is set to True, necessary javascripts will be added to the report`s head.
        ''')
        
    with Section('Results Subsection'):
      Txt('''
          Subsections are created in the same way as sections:
          using the context manager within the main section
          as you used context manager to create section in reports.
          ''')
    
  with Section('Resources'):
    Cde('''
        Here goes some code which will
        be syntax highlighted formatted
        ''')
    
report.to_html('my_report.html)
    
 
```
Among other things, it also allows embedding [plotly plots](https://plotly.com/) and [antigenic cartography maps](https://www.antigenic-cartography.org/) to your report. See the [example_report.py](https://github.com/iAvicenna/PyReports/blob/main/test/examples/example_report.py) for a much extended example 
and [test_report](https://github.com/iAvicenna/PyReports/blob/main/test/test_report.html) for the end result.
