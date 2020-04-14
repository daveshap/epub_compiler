import re


def strip_rtf(text):
    text = text.replace('\i ','<i>')
    text = text.replace('\i0 ','<ii>')
    pattern = re.compile('\\\\\w+')
    r = pattern.sub('',text)
    r = r.replace('<ii>','</i>')
    return r.strip()


if __name__ == '__main__':
    with open('V:\Dropbox\Books\Stars and Sand\Draft 02\ch01 The Pump.rtf', 'r') as infile:
        content = infile.read()
    content = content.strip()
    lines = content.splitlines()
    html = '<html>\n<body>\n'
    for line in lines:
        if line.startswith('{') or line.startswith('}'):
            continue
        clean = strip_rtf(line)
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
    #print(html)
    with open('test.html', 'w') as outfile:
        outfile.write(html)