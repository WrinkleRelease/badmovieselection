import xbmc
import xbmcaddon
import xbmcgui
import json
import random

## MARK: Global Information
# Global addon information
ADDON = xbmcaddon.Addon()
ADDON_NAME = ADDON.getAddonInfo('name')  # Gets the name from addon.xml
ADDON_ID = ADDON.getAddonInfo('id')  # Gets the ID from addon.xml

# Sets up our main function to handle the behavior of the plugin
class BadMovieSelection:
    def __init__(self):
        self.addon = ADDON
        self.addon_name = ADDON_NAME
        self.addon_id = ADDON_ID
        
        # Get excluded movies from settings.xml
        self.excluded_movies = self.get_excluded_movies()
        
    #-----------------------
    ## MARK: Excluded Movies
    #-----------------------
    def get_excluded_movies(self):
        excluded = []
        index = 1
        while True:
            setting_id = f'excluded_movie{index}'
            movie = self.addon.getSetting(setting_id)
            if not movie: 
                break
            excluded.append(movie)
            index += 1
        return excluded    
    
    #-------------------
    ## MARK: Movies List
    #-------------------
    def get_movies(self):
        xbmc.log(f"{self.addon_name}: Starting get_movies()", xbmc.LOGDEBUG)

        # JSON-RPC method to get the movies 
        json_request = {
            "jsonrpc": "2.0",
            "method": "VideoLibrary.GetMovies",
            "params": {
                "properties": ["title", "playcount", "tag"],
                "filter": {
                    "and": [
                        {"field": "playcount", "operator": "is", "value": "0"},
                        {"field": "tag", "operator": "contains", "value": "Bad Movies"}
                    ]
                }
            },
            "id": 1
        }
        
        # Execute the JSON-RPC request
        response = xbmc.executeJSONRPC(json.dumps(json_request))
        response = json.loads(response)
        
        # Check if we got any movies back
        if 'result' in response and 'movies' in response['result']:
            movies = response['result']['movies']
            
            # Filter out excluded movies here and produce a new list
            available_movies = [
                movie for movie in movies
                if movie['title'] not in self.excluded_movies
            ]
            xbmc.log(f"{self.addon_name}: Available movies: {available_movies}", xbmc.LOGDEBUG)
            
            # Randomly select up to 10 movies
            # Uses the Python -random- module 
            selected_movies = random.sample(available_movies, min(10, len(available_movies)))
            titles = [movie['title'] for movie in selected_movies]

            xbmc.log(f"{self.addon_name}: Selected titles: {titles}", xbmc.LOGDEBUG)

            return titles
    
        xbmc.log(f"{self.addon_name}: No movies found", xbmc.LOGDEBUG)
        return []  # closes the 'if' statement; gives an empty string if no movies were found

    # ---------------------
    ## MARK: Display Movies
    #----------------------
    # We now have our movie titles in a string. The next step is to display them.
    def display_movies(self, titles):
        if not titles:
            xbmcgui.Dialog().ok(self.addon_name, "No unwatched bad movies found! So sad!")
            return # This exits the function early if there are no titles
       
        # Create wheel window
        wheel_window = MovieWheel()
       
        # Create the wheel with the list of movies
        wheel_window.create_wheel(titles)
        wheel_window.show()
        xbmc.sleep(5000)
        wheel_window.close()
       
def run():
    wheel = BadMovieWheel()
    movies = wheel.get_movies()
    wheel.display_movies(movies)
    
if __name__ == '__main__':
    run()