import os
import json



class EpubFromRtf:
    def __init__(self):
        self.metadata = False
        self.defaults_dir = './Defaults/'
        
    def load_metadata(self, metafile):
        with open(metafile, 'r') as infile:
            self.metadata = json.load(infile)
        print('METADATA:::', self.metadata)
    
    def load_chapters(self):
        files = os.listdir(self.metadata['chapter_dir'])
        chapters = []
        for file in files:
            rtf = load_rtf(self.metadata['chapter_dir'] + file)
            info = {'filename':file, 'rtf':rtf}
            chapters.append(info)
        self.rtf_chapters = chapters
        print('LOADED RTF CHAPTERS:::')

    def html_head(self):
        with open('./Defaults/head.html', 'r') as infile:
            html = infile.read()
            html = html.replace('##TITLE##', self.metadata['title'])
            return html


if __name__ == '__main__':
    book = EpubFromRtf()
    book.load_metadata("V:/Dropbox/Books/Stars and Sand/metadata.json")
    book.load_chapters()
    #metadata = load_metadata("V:/Dropbox/Books/Stars and Sand/metadata.json")
    #print(metadata)
    #html = load_html_head()
    #html = html.replace('##TITLE##', metadata['title'])
    #print(html)
    #chapters = load_chapters(metadata)
    #print(chapters)
    #rtf = load_rtf(test_file)
    #print(rtf)