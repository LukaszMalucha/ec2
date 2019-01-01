################################################################## App Utilities
import os
import env

from flask_bootstrap import Bootstrap
from flask import Flask, Response, render_template, request, redirect, url_for, session
from flask_restful import Api, Resource

import numpy as np


from ai import grid
from ai import route, best_route

################################################################### APP SETTINGS ##############################################################


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY") 
Bootstrap(app)
api = Api(app)





################################################################### HELPER FUNCTIONS ##############################################################




###################################################################### RESOURCES ##############################################################


class Environment(Resource):
    def post(self):
        
        warning = ""

        start_location = int(request.form['start_location'])
        base_location = int(request.form['base_location'])
        astronauts = int(request.form['astronauts'])
        desert_storm_1 = int(request.form['desert_storm_1'])
        desert_storm_2 = int(request.form['desert_storm_2'])
        desert_storm_3 = int(request.form['desert_storm_3'])
        desert_storm_4 = int(request.form['desert_storm_4'])
        
        desert_storms = [desert_storm_1,desert_storm_2,desert_storm_3,desert_storm_4]
        
        env_dict = {'start_location':start_location,'base_location':base_location,
                    'astronauts':astronauts, 'desert_storms': desert_storms }  
        
        env_list = [start_location, base_location, astronauts, desert_storm_1,desert_storm_2,desert_storm_3,desert_storm_4 ]           


        ## Check if unique
        if len(env_list) > len(set(env_list)):
            return Response(render_template('dashboard.html', warning = "Objects should be placed on distinct tiles"))

        ## Check if there's a distance to prevent stucking
        for i in desert_storms: 
            if abs(i - astronauts) < 2 or abs(i - start_location) <2 or abs(i - start_location) <2:
                return Response(render_template('dashboard.html', warning = "Desert Storms to close to the other objects"))
                
                
      
        
        
        session['env_dict'] = env_dict
        session['desert_storms'] = desert_storms
        
        return Response(render_template('environment.html', env_dict = env_dict, mimetype='text/html'))
        

class Pathfinder(Resource):
    def post(self):
        
        
        env_dict = session.get('env_dict')
        desert_storms = session.get('desert_storms')
        
        reward_grid = grid(8)
        
        starting_location = env_dict['start_location']
        ending_location   = env_dict['base_location']
        collection = env_dict['astronauts']
        desert_storm_1 = desert_storms[0]
        desert_storm_2 = desert_storms[1]
        desert_storm_3 = desert_storms[2]
        desert_storm_4 = desert_storms[3]


        path = best_route(starting_location, collection,
                          desert_storm_1, desert_storm_2,
                          desert_storm_3, desert_storm_4,
                          ending_location, reward_grid)
        
        
        return Response(render_template('route.html', env_dict = env_dict, path = path, mimetype='text/html'))



api.add_resource(Environment, '/environment')
api.add_resource(Pathfinder, '/pathfinder')

########################################################################## VIEWS ######################################################################



############################################################## Home

@app.route('/')
@app.route('/dashboard')
def dashboard():
    
    session.clear()
    return render_template("dashboard.html")
    
 

    
@app.errorhandler(404)
def error404(error):
    return render_template('404.html'), 404
    
@app.errorhandler(500)
def error500(error):
    return render_template('500.html'), 500    
    
    
    
    
################################################################# APP INITIATION #############################################################


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)     