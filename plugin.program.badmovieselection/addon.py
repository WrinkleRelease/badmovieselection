import xbmc
import xbmcaddon
import xbmcgui
import json
import random
import os

## MARK: Global Information
# Global addon information
ADDON = xbmcaddon.Addon()
ADDON_NAME = ADDON.getAddonInfo('name') 
ADDON_ID = ADDON.getAddonInfo('id') 
ADDON_PATH = ADDON.getAddonInfo('path')

# Sets up our main function to handle the behavior of the plugin
class BadMovieSelection:
    def __init__(self):
        self.addon = ADDON
        self.addon_name = ADDON_NAME
        self.addon_id = ADDON_ID
        self.media_path = os.path.join(ADDON_PATH, 'resources', 'media')
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
        xbmc.log(f"{self.addon_name}: Starting get_movies()", xbmc.LOGINFO)

        # JSON-RPC method to get the movies 
        json_request = {
            "jsonrpc": "2.0",
            "method": "VideoLibrary.GetMovies",
            "params": {
                "properties": ["title"],
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
        xbmc.log(f"{self.addon_name}: Raw JSON Response: {response}", xbmc.LOGINFO)
        response = json.loads(response)
        
        # Check if we got any movies back
        if 'result' in response and 'movies' in response['result']:
            movies = response['result']['movies']
            xbmc.log(f"{self.addon_name}: Found {len(movies)} movies before exclusion", xbmc.LOGINFO)
            
            # Filter out excluded movies here and produce a new list
            available_movies = [
                movie for movie in movies
                if movie['title'] not in self.excluded_movies
            ]
            xbmc.log(f"{self.addon_name}: Found {len(available_movies)} movies after exclusion", xbmc.LOGINFO)
            
            if available_movies:
                return random.choice(available_movies)
        return None
    
    #--------------
    ## MARK: Sounds
    #--------------
    def play_sounds(self, sound_file):
        sound_path = os.path.join(self.media_path, sound_file)
        xbmc.executebuiltin(f'PlayMedia({sound_path}),1')
        
    # def play_movie(self, movie_id):
    #     json_request = {
    #         "jsonrpc": "2.0",
    #         "method": "Player.Open",
    #         "params": {
    #             "item": {
    #                 "movieid": movie_id
    #             }
    #         },
    #         "id": 1
    #     }
    #     xbmc.executeJSONRPC(json.dumps(json_request))

    #---------------
    ## MARK: Display
    #---------------
    def display_result(self):
    
        # Get random movie
        selected_movies = self.get_movies()
        if not selected_movies:
            xbmcgui.Dialog().ok(self.addon_name, "Oh no! No unwatched bad movies found!")
            return

        window = xbmcgui.WindowDialog()
        background = xbmcgui.ControlImage(0, 0, 1920, 1080,
                                          os.path.join(self.media_path, 'background.png'))
        window.addControl(background)
        window.show()

        # Play drum roll and wait
        self.play_sounds('drum_roll02.mp3')
        xbmc.sleep(4700)
        
        # Play fail sound
        fail_sounds = [f for f in os.listdir(self.media_path) if f.startswith('fail_sound')]
        random_fail = random.choice(fail_sounds)
        self.play_sounds(random_fail)
        
        # Show chosen movie
        dialog = xbmcgui.Dialog()
        dialog.ok(self.addon_name, selected_movies['title'])
        xbmc.sleep(4000)
        
        # # Show dialog with movie title and buttons
        # result = xbmcgui.Dialog().yesno(
        #     self.addon_name,
        #     selected_movies['title'],
        #     yeslabel="Play Movie",
        #     nolabel="Cancel"
        # )
        
        # # If user plays movie
        # if result:
        #     self.play_movie(selected_movies['movieid'])
        
def run():
    xbmc.log(f"{ADDON_NAME}: Starting plugin", xbmc.LOGINFO)
    selector = BadMovieSelection()
    selector.display_result()
    
if __name__ == '__main__':
    run()