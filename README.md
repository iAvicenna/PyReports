# PyReports
PyReports is a python library that allows typing up pdf reports easily and quickly.
It is done via a context managing. A simple example is 

```
from PyReports import Section, Report, Txt, Img, Plt

report = Report('Test Report')  

with report:

  with Section('Introduction'):  
    Txt('This is a text')  
    Img('./image1.png') 
    
  with Section('Results', has_tex=True):
    Plt('./plotly_graph.html')
    
    with Grid(2,1):
      Img('./image1.png)
      Img('./image2.png)
      
    Txt('''
        One can also put a tex formula using regular latex code

        $\int exp^{-x^2} dx = ?? $
        ''')
    
    
  with Section('Resources'):
    Cde('''
        Here goes some code
        which will be syntax highlighted
        formatted
        ''')
    
report.to_html('my_report.html)
    
 
```
Among other things, it also allows embedding [plotly plots](https://plotly.com/) and [antigenic cartography maps](https://www.antigenic-cartography.org/) to your report. See the [example_report.py](https://github.com/iAvicenna/PyReports/blob/main/test/examples/example_report.py) for a much extended example.
