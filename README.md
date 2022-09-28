# PyReports
PyReports is a python package that allows typing up pdf reports easily and quickly.

It is done via a context managing. A simple example is 

```
from PyReports import Section, Report, Txt, Img, Plt


report = Report('Test Report')  

with report:

  with Section('Introduction'):  
    Txt('''This is a text''')  
    Img('./image1.png') 
    
  with Section('Results'):
    Plt('./plotly_graph.html')
    
 
```
Among other things, it also allows embedding [plotly plots](https://plotly.com/) and [antigenic cartography maps](https://www.antigenic-cartography.org/).
See the example_report.py for a much extended example.
