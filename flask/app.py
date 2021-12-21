import requests
import folium
import geocoder
import string
import os as os
import pathlib
import zipfile
import json
from functools import wraps, update_wrapper
from datetime import datetime
from pathlib import Path
from utils import download_from_gdrive



from ediblepickle import checkpoint
from flask import Flask, render_template, request, redirect, url_for, send_file, make_response


###############################################
#      Define navbar with logo                #
###############################################



server = Flask(__name__)
#Bootstrap(app)
server.config['TEMPLATES_AUTO_RELOAD'] = True
map_dict = {  'CenCal.html' : ['California Water Districts and Pits',
                                'Top 3 producers',
                                "https://drive.google.com/file/d/1bqhQ0Wuv_iVOmQKJafpXpbx891rzPLgV/view?usp=sharing"],
              'california_venturacounty_4dec2021.html' : ['Ventura County', 
                                'Todd Arbetter',
                                "https://drive.google.com/file/d/1lnylSF11Yz9g1db-INgNeXFuQN0fikQa/view?usp=sharing"],
               'california_kerncounty.html' : ['Kern County',
                                 'Todd Arbetter',
                                 "https://drive.google.com/file/d/16ktPy0Ui9-XulwK5VEEJCRYCYoE3m-3A/view?usp=sharing"]
             }
server.vars = {}

def nocache(view):
  @wraps(view)
  def no_cache(*args, **kwargs):
    response = make_response(view(*args, **kwargs))
    response.headers['Last-Modified'] = datetime.now()
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response
        
  return update_wrapper(no_cache, view)


@server.route('/')
def main():
  return redirect('/index.html')

@server.route('/index.html', methods=['GET'])
def index():
  if request.method == 'GET':
    #return render_template('input.html')
    map_name = f"california_venturacounty_4dec2021.html"
    #map_name = f"CenCal.html"
    
    #have to set map path - used by template
    map_path = os.path.join(server.root_path, 'static/' + map_name)
    
    print(map_path)
    server.vars['map_path'] = map_path
    print(server.vars['map_path'])
    server.vars['Title_line1'] = map_dict[map_name][0]
    server.vars['Title_line2'] = map_dict[map_name][1]

    
    if Path(map_path).exists():
        return render_template('display.html', vars=server.vars)
    else:     
        return redirect('/maperror.html')

    pass

@server.route('/map', methods=['GET'])
# http://localhost:5000/map?map=CenCal.html
# http://localhost:5000/map?map=california_kerncounty.html
# http://localhost:5000/map?map=california_kerncounty.html
#@nocache
def get_map():
  args = request.args
  print (args) # For debugging
  map_name = args['map']
  print(type(map_name))
  map_path = os.path.join(server.root_path, 'static/' + map_name)
  print(map_path)
  server.vars['map_path'] = map_path
  server.vars['Title_line1'] = map_dict[map_name][0]
  server.vars['Title_line2'] = map_dict[map_name][1]
  
  if Path(map_path).exists():
        return render_template('display.html', vars=server.vars)
  else:     
        return redirect('/maperror.html')

  pass


@server.route('/maps/map.html')
@nocache
def show_map():
  map_path = server.vars.get("map_path")
  print("show map")
  print(map_path)
  map_file = Path(map_path)
  if map_file.exists():
    return send_file(map_path)
  else:
    return render_template('error.html', culprit='map file', details="the map file couldn't be loaded")

  pass


@server.route('/get_logo')
def get_logo():
  logo_path = os.path.join(server.root_path, 'static/img/logo.png' )
  print("show logo")
  print(logo_path)
  logo_file = Path(logo_path)
  if logo_file.exists():
    return send_file(logo_path)
  else:
    return render_template('error.html', culprit='logo file', details="the logo file couldn't be loaded")

  pass


@server.route('/error.html')
def error():
  details = "There was some kind of error."
  return render_template('error.html', culprit='logic', details=details)

@server.route('/apierror.html')
def apierror():
  details = "There was an error with one of the API calls you attempted."
  return render_template('error.html', culprit='API', details=details)

@server.route('/maperror.html')
def geoerror():
  details = "Map not found."
  return render_template('error.html', culprit='the Map', details=details)

