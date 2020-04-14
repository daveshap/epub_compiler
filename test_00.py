import os
import json
import re
import shutil
from pprint import pprint



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
        html = html.replace('<p></p>','<p><div align="center">&mdash; &mdash; &mdash;</div></p>')
        html = html.replace('<p>"','<p>&ldquo;')
        html = html.replace('"</p>','&rdquo;</p>')
        html = html.replace('" ','&rdquo; ')
        html = html.replace(' "',' &ldquo;')
        html = html.replace('<p> </p>','')
        html = html.replace('&ldquo;<i>','<i>&ldquo;')
        html = html.replace('</i>,&rdquo;','&rdquo;,</i>')
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

    def get_h2_title(self, content):
        lines = content.splitlines()
        for line in lines:
            if '<h2>' in line:
                title = line.replace('<h2>','').replace('</h2>','')
                return title

    def get_chap_num(self, filename):
        chunks = filename.split(' ')
        number = int(chunks[0].replace('ch',''))
        return number
        
    def export_chapters(self):
        self.toc = []
        for chapter in self.rtf_chapters:
            html = self.rtf2html(chapter['rtf'])
            chap_name = self.get_h2_title(html)
            chap_num = self.get_chap_num(chapter['filename'])
            filename = chapter['filename'].replace(' ','_').replace('.rtf','.html')
            info = {'filename': filename, 'title': chap_name, 'number': chap_num}
            self.toc.append(info)
            print('EXPORTING CHAPTER::: ', filename, chap_name, chap_num)
            with open('./Export/OEBPS/' + filename, 'w') as outfile:
                outfile.write(html)
        print('TOC:::')
        pprint(self.toc)
        
    def generate_content_opf(self):
        with open(self.defaults_dir + 'content.opf', 'r') as infile:
            content = infile.read()
        metablock =  '    <dc:rights>%s</dc:rights>\n' % self.metadata['rights']
        metablock += '    <dc:creator opf:file-as="%s">%s</dc:creator>\n' % (self.metadata['file-as'], self.metadata['author'])
        metablock += '    <dc:title>%s</dc:title>\n' % self.metadata['title']
        metablock += '    <dc:date opf:event="publication">%s</dc:date>\n' % self.metadata['published']
        metablock += '    <dc:language xsi:type="dcterms:RFC4646">en</dc:language>\n'
        for subject in self.metadata['subjects']:
            metablock += '    <dc:subject>%s</dc:subject>\n' % subject
        metablock += '    <dc:date opf:event="publication">%s</dc:date>' % self.metadata['published']
        content = content.replace('##METADATA##', metablock)
        
        manifestblock = ''
        spineblock = ''
        for chapter in self.toc:
            item = chapter['number'] + 5
            manifestblock += '    <item href="%s" id="item%s" media-type="application/xhtml+xml"/>\n' % (chapter['filename'], item)
            spineblock += '    <itemref idref="item%s" linear="yes"/>\n' % item
        content = content.replace('##MANIFEST##', manifestblock)
        content = content.replace('##SPINE##', spineblock)
        content = content.replace('\n\n','\n')
        
        with open('./Export/OEBPS/content.opf', 'w') as outfile:
            outfile.write(content)
           
        

if __name__ == '__main__':
    book = EpubFromRtf()
    book.load_metadata("V:/Dropbox/Books/Stars and Sand/metadata.json")
    book.load_chapters()
    book.stage_export()
    book.export_chapters()
    book.generate_content_opf()
    