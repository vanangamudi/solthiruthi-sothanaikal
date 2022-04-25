import sys
import utils
import random
from tkinter import *



class Application:

    def __init__(self, inpath, outpath):

        self.inpath = inpath
        self.outpath = outpath

        self.outfile = open(outpath, 'w')
        self.words = open(inpath).read().split()
        self._build_gui_()

    def __del__(self):
        self.outfile.close()
        
    def _build_gui_(self):
        self.root = Tk() 
        
        self.root.geometry("600x600")
        self.root.minsize(height=560)
        self.root.title("அரிவாள்")
        
        self.scrollbar = Scrollbar(self.root)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.text_box = Text(self.root,  yscrollcommand=self.scrollbar.set)
        self.text_box.pack(fill=BOTH)
        
        self.scrollbar.config(command=self.text_box.yview)
        
        self.refresh_button=Button(self.root,
                                   height=1,
                                   width=10,
                                   text='refresh', 
                                   command=self.on_refresh)
        
        self.refresh_button.pack()

    def mainloop(self):
        self.outfile.write(self.header_text())
        
        self.text_box.delete('1.0', 'end')
        self.text_box.insert('1.0', self.build_text())

        self.root.mainloop()

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
        return '''
#உள்ளீடு: {inpath}
#வெளியீடு: {outpath}
'''.format(inpath = self.inpath,
                   outpath=self.outpath)
        
    def on_refresh(self):
        text = self.text_box.get('1.0', 'end')
        for line in text.splitlines():
            line = line.strip()
            if line:
                self.outfile.write(line + '\n')

        self.text_box.delete('1.0', 'end')
        self.text_box.insert('1.0', self.build_text())


        
if __name__ == '__main__':

    print(sys.argv)
    inpath, outpath = sys.argv[1:]
    
    app = Application(inpath, outpath)
    app.mainloop()

    
