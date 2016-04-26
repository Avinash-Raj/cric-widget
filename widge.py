from gi.repository import WebKit, Gtk, Gdk
import signal
import requests
import time

class BackgroundPaneCallbacks:
    pass

class BackgroundPaneWebview(WebKit.WebView):
    def __init__(self, score):
        WebKit.WebView.__init__(self)
        self.set_transparent(False)
        self.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0,0,0,0))
        self.load_html_string('<HTML>'+\
                              '<STYLE type="text/css">'+\
                              'BODY { background: rgba(0,0,0,0);}'+\
                              '</STYLE>'+\
                              '<BODY>'+\
                              '<p style="color:Red">' + score +'</p>'+\
                              ''+\
                              '</BODY>'+\
                              '</HTML>',
                              '')
        print("Webview loaded")

class ParseScore():
    @classmethod
    def get_scores(cls):
        r = requests.get('http://cricapi.com/api/cricket/')
        if r.status_code != 200:
            return None

        match_list = r.json()
        teams_list = ['Delhi Daredevils',
                     'Gujarat Lions',
                      'Kings XI Punjab'
                      'Kolkata Knight Riders',
                      'Mumbai Indians',
                      'Rising Pune Supergiants',
                      'Royal Challengers Bangalore']

        titles = [(i['unique_id'], i['title']) for i in match_list['data']]
        unique_ids = []
        for team in teams_list:
            for title in titles:
                if team in title[1]:
                    unique_ids.append(title[0])

        unique_id = unique_ids[0]
        
        payload = {'unique_id': unique_id}

        out = requests.get('http://cricapi.com/api/cricketScore/', params=payload)
        match_info = out.json()

        return match_info['score']


class BackgroundPaneWin(Gtk.Window):
    def __init__(self, address="127.0.0.1", port=54541):
        Gtk.Window.__init__(self, title="Live cricket Scores")
        self.set_title("MyApp1")
        self.set_size_request(400,200)
        #Set transparency
        screen = self.get_screen()
        rgba = screen.get_rgba_visual()
        self.set_visual(rgba)
        self.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0,0,0,0))

        #parse matchlist and score
        match_description = ParseScore.get_scores()
        self.view = BackgroundPaneWebview(match_description)
        
        if '*' in match_description:
            while True:
                self.view = BackgroundPaneWebview(match_description)
                time.sleep(15)

        #Add all the parts
        
        box = Gtk.Box()
        
        #self.add(box)
        box.pack_start(self.view, True, True, 0)
        self.set_decorated(False)
        self.connect("destroy", lambda q: Gtk.main_quit())
        f = Gtk.Frame()
        f.add(box)
        self.add(f)
        #Configure   

        #Show all the parts
        self.show_all()


        print("Win loaded")

class BackgroundPane:
    def __init__(self, params=False):
        #Add all the parts
        self.root = params['root']
        self.win = BackgroundPaneWin()
        print("Pane loaded")

    def init(self):
        pass

    def add_widget(self, widget):
        pass

class Logger:
    def __init__(self, root):
        self.root = root
        self.log("Logger loaded")

    def log(self, msg, level='console'):
        if level=='console':
            print msg

class Handlers:
    pass

class App:
    def __init__(self, params={}):
        #Get screen geometry
        s = Gdk.Screen.get_default()
        params['w'] = s.get_width()
        params['h'] = s.get_height()

        #Store params
        self.params = params
        self.log = Logger(self).log
        self.handlers = Handlers()
        #Get all components
        bg = BackgroundPane({'root':self,
                                           })
        #Store all components
        self.components = {}
        self.components['bg'] = bg

        #Make sure everything is started

        #Make sure Ctl-C works
        signal.signal(signal.SIGINT, signal.SIG_DFL)

    def run(self):
        Gtk.main()

if __name__ == '__main__':
    print("Loading app...")
    app = App({'w': 380, 'h': 180})
    app.run()
