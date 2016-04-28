from gi.repository import WebKit, Gtk, Gdk, GObject
import signal
import requests
import time
import re

class BackgroundPaneCallbacks:
    pass


class BackgroundPaneWebview(WebKit.WebView):
    def __init__(self, score, title, commentary):
        WebKit.WebView.__init__(self)
        self.set_transparent(False)
        self.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0,0,0,0))
        score = ParseScore.split_scores(score)
        self.load_html_string(ParseScore.generate_html(score, title, commentary), '')
        print("Webview loaded")
        GObject.timeout_add_seconds(10, self.callback)

    def callback(self):
        score, title, commentary = ParseScore.get_scores()
        score = ParseScore.split_scores(score)
        self.load_html_string(ParseScore.generate_html(score, title, commentary),'')
        return True


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
                    unique_ids.append(title)

        unique_id = unique_ids[0][0]
        #print '\033[92m' + unique_id + '\033[0m'
        payload = {'unique_id': unique_id}

        out = requests.get('http://cricapi.com/api/cricketScore/', params=payload)
        match_info = out.json()
        comment = requests.get('http://cricapi.com/api/cricketCommentary/', params=payload)
        commentary = comment.json()['commentary']
        commentary = re.sub(r'\s*\n\s*', '', commentary)
        list_comm = re.split(r'\.(?!\d)', commentary)
        final_comment = '.'.join(list_comm[:5])

        return match_info['score'], unique_ids[0][1], final_comment



    @classmethod
    def split_scores(cls, score):
        if '*' in score:
            m = re.search(r'^([^()]*)\(([^,]+),\s*([^,]+),\s*([^,]+),\s*([^)]+)', score)
            score = m.group(1)
            overs = m.group(2)
            bat1 = m.group(3)
            bat2 = m.group(4)
            bowl = m.group(5)
            return score, overs, bat1, bat2, bowl
        return score

    @classmethod
    def generate_html(cls, score, title, commentary):
        if type(score) == unicode:
            return '''<HTML>
                              <STYLE type="text/css">
                              BODY { 
                                   background: rgba(0,0,0,0);
                                   background-color:  #009688;
                                   }
                              </STYLE>
                              <BODY>
                              <h2>''' + title + '''</h2>
                              <p style="color:yellow">''' + score +'''</p>
                              ''' + commentary + '''
                               </BODY>
                              </HTML>'''
                              
        else:
            return '''<HTML>
                              <STYLE type="text/css">
                              BODY { background: rgba(0,0,0,0);
                                      background-color:  #009688;
                              }
                              </STYLE>
                              <BODY>
                              <h2>''' + title + '''</h2>
                              <p style="color:Blue">Score: ''' + score[0] + '''</p>
                              <p style="color: #cddc39">overs: ''' + score[1] +'''</p>
                              <p style="color:Orange">''' + score[2] +'''</p>
                              <p style="color:yellow">''' + score[3] +'''</p>
                              <p style="color:Brown">''' + score[4] +'''</p>
                              ''' + commentary + '''
                              </BODY>
                              </HTML>'''


class BackgroundPaneWin(Gtk.Window):
    def __init__(self, address="127.0.0.1", port=54541):
        Gtk.Window.__init__(self, title="Live cricket Scores")
        self.set_title("Live IPL cricket Scores")
        self.set_size_request(400,200)
        #Set transparency
        screen = self.get_screen()
        rgba = screen.get_rgba_visual()
        self.set_visual(rgba)
        self.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0,0,0,0))

        #parse matchlist and score
        score, title, commentary = ParseScore.get_scores()        

        self.view = BackgroundPaneWebview(score, title, commentary)

        #Add all the parts
        
        box = Gtk.Box()
        
        #self.add(box)
        box.pack_start(self.view, True, True, 0)
        self.set_decorated(True)
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
    app = App()
    app.run()
