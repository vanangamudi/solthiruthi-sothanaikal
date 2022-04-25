import sys
import utils
import random

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

class TextViewWindow(Gtk.Window):
    def __init__(self, inpath, outpath,):
        Gtk.Window.__init__(self, title="அரிவாள்")
        
        self.inpath = inpath
        self.outpath = outpath

        self.outfile = open(outpath, 'w')
        self.words = open(inpath).read().split()

        self.set_default_size(500, 350)

        self.hbox = Gtk.Box(spacing=6, orientation=Gtk.Orientation.VERTICAL)
        self.add(self.hbox)

        self.create_textview()
        self.create_buttons()

        self.outfile.write(self.header_text())
        
    def __del__(self):
        self.outfile.close()
        
    def create_textview(self):
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_hexpand(True)
        scrolledwindow.set_vexpand(True)
        self.hbox.pack_start(scrolledwindow, True, True, 0)

        self.textview = Gtk.TextView()
        self.textbuffer = self.textview.get_buffer()
        self.textbuffer.set_text(self.build_text())
        scrolledwindow.add(self.textview)

    def create_buttons(self):
        self.button = Gtk.Button.new_with_label("Click Me")
        self.button.connect("clicked", self.on_refresh)
        self.hbox.pack_start(self.button, True, True, 0)

    def on_refresh(self, widget):
        
        text = self.textbuffer.get_text(self.textbuffer.get_start_iter(),
                                        self.textbuffer.get_end_iter(),
                                        True)
        for line in text.splitlines():
            line = line.strip()
            if line:
                self.outfile.write(line + '\n')

        self.textbuffer.delete(self.textbuffer.get_start_iter(),
                                        self.textbuffer.get_end_iter())
        
        self.textbuffer.set_text(self.build_text())

    def sample_words(self, approx_count=10, length=20):
        words = []
        while len(words) < approx_count:
            words += [i for i in random.sample(self.words, approx_count) if len(i) >= length]

        return words

    def build_text(self):
        words = self.sample_words()
        text = '\n'.join([ '\t'.join([i, i]) for i in words])

        return text
    
    def header_text(self):
        return \
'''
#உள்ளீடு: {inpath}
#வெளியீடு: {outpath}
'''.format(inpath = self.inpath,
                   outpath=self.outpath)


        
if __name__ == '__main__':
    
    print(sys.argv)
    inpath, outpath = sys.argv[1:]
    
    win = TextViewWindow(inpath, outpath)
    win.connect("destroy", Gtk.main_quit)
    win.show_all()


    Gtk.main()

