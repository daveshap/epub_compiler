import os
import json
import re
import shutil



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
            if '.rtf' not in file:
                continue
            with open(self.metadata['chapter_dir'] + file, 'r') as infile:
                print('LOADING CHAPTER::: ', file)
                rtf = infile.read()
                info = {'filename':file, 'rtf':rtf}
                chapters.append(info)
        self.rtf_chapters = chapters
        

    def html_head(self):
        with open(self.defaults_dir + 'head.html', 'r') as infile:
            html = infile.read()
            html = html.replace('##TITLE##', self.metadata['title'])
            return html
            
    def strip_rtf(self, text):
        text = text.replace('\i ','<i>')
        text = text.replace('\i0 ','<ii>')
        pattern = re.compile('\\\\\w+')
        r = pattern.sub('',text)
        r = r.replace('<ii>','</i>')
        return r.strip()

    def rtf2html(self, content):
        content = content.strip()
        lines = content.splitlines()
        html = self.html_head()
        for line in lines:
            if line.startswith('{'):
                continue
            if line.startswith('}'):
                break
            clean = self.strip_rtf(line)
            if 'Title:' in line:
                clean = clean.replace('Title:','')
                html += '<h2>%s</h2>\n' % clean.strip()
            elif 'Subtitle:' in line:
                clean = clean.replace('Subtitle:','')
                html += '<h3>%s</h3>\n' % clean.strip()
            elif 'li720' in line:
                clean = clean.replace('<i>','')
                clean = clean.replace('</i>','')
                html += '<blockquote><p><i>%s</i></p></blockquote>\n' % clean
            else:
                html += '<p>%s</p>\n' % clean
        html = html.replace('<p></p>','<br/>')
        html = html.replace('<p>"','<p>&ldquo;')
        html = html.replace('"</p>','&rdquo;</p>')
        html = html.replace('" ','&rdquo; ')
        html = html.replace(' "',' &ldquo;')
        html = html.replace('<p> </p>','')
        html = html.strip()
        return html

    def stage_export(self):
        shutil.rmtree('./Export/', ignore_errors=True)
        os.mkdir('./Export/')
        os.mkdir('./Export/META-INF/')
        os.mkdir('./Export/OEBPS/')
        shutil.copyfile(self.defaults_dir + 'mimetype', './Export/mimetype')
        shutil.copyfile(self.defaults_dir + 'container.xml', './Export/META-INF/container.xml')
        shutil.copyfile(self.defaults_dir + '0.css', './Export/OEBPS/0.css')
        shutil.copyfile(self.defaults_dir + '1.css', './Export/OEBPS/1.css')
        shutil.copyfile(self.defaults_dir + 'pgepub.css', './Export/OEBPS/pgepub.css')
        shutil.copyfile(self.defaults_dir + 'wrap0000.html', './Export/OEBPS/wrap0000.html')
        shutil.copyfile(self.metadata['cover_img'], './Export/OEBPS/cover.jpg')
        
    def export_chapters(self):
        for chapter in self.rtf_chapters:
            print('EXPORTING CHAPTER::: ', chapter['filename'])
            html = self.rtf2html(chapter['rtf'])
            filename = chapter['filename'].replace(' ','_').replace('.rtf','.html')
            with open('./Export/OEBPS/' + filename, 'w') as outfile:
                outfile.write(html)

       

if __name__ == '__main__':
    book = EpubFromRtf()
    book.load_metadata("V:/Dropbox/Books/Stars and Sand/metadata.json")
    book.load_chapters()
    book.stage_export()
    book.export_chapters()
    