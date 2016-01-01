__author__ = 'pmlandwehr'


img_exts = ['jpg', 'jpeg', 'png', 'gif', 'bmp']


def get_filename_for_img(filename, length=50):
        """
        Generate 50-char long random filename
        :param str filename: the original filename
        :param int length: the length of the filename to generate
        :return str: the new, random filename
        """
        import os
        import random
        from string import ascii_uppercase, digits

        name, ext = os.path.splitext(filename.lower())
        ext = ext.strip('.')
        if ext not in img_exts:
            raise TypeError('{} is not a valid image file extension'.format(ext))

        s = ''.join(random.choice(ascii_uppercase + digits) for _ in xrange(length))
        return '{name}.{ext}'.format(name=s, ext=ext)


def parse_google_query(html):
    """
    Parses the HTML returned by the Google reverse image search
    :param str html: Raw html
    :return dict:
        {'query': `Google's best guess for a query`,
         'results': [link1, link2, link3...]
         }
    """
    from bs4 import BeautifulSoup
    import codecs

    # Debug line
    with codecs.open('the_soup.html', 'w', 'utf8') as outfile:
        outfile.write(html)

    query_str = ''
    bs = BeautifulSoup(html, 'lxml')

    text = bs.find('a', {'class': 'qb-b'})
    if text is not None:
        query_str = text.find(text=True)

    result_divs = bs.body.find_all('div', {'class': 'rg_di rg_el ivg-i'})

    matches = []
    for r_d in result_divs:
        match = {}
        img_href_data = r_d.a['href'].split('?')[1].split('&')
        for entry in img_href_data:
            key, val = entry.split('=')
            match[key] = val
        match['caption'] = {}
        match['caption']['res'], match['caption']['domain'] = \
            r_d.find('span', {'class': 'rg_ilmn'}).text.strip().split(' - ')

        match['rg_meta'] = eval(r_d.find('div', {'class': 'rg_meta'}).text)

        for key in match['rg_meta']:
            if isinstance(match['rg_meta'][key], unicode):
                match['rg_meta'][key] = match['rg_meta'][key].encode('utf8')
                try:
                    print(match['rg_meta'][key])
                except:
                    match['rg_meta'][key] = ''

        matches.append(match)

    # Brittle code for getting image thumbnails.
    # script_tags = bs.find_all('script')
    # thumb_list = eval(script_tags[7].text.split('\n;var ')[0][len('(function(){var data='):])[0]
    # thumb_dict = {}
    # for id, thumb in thumb_list:
    #     thumb_dict[id] = thumb
    #
    # for match in matches:
    #     if 'tbnid' in match and match['tbnid'] in thumb_dict:
    #         match['thumbnail'] = thumb_dict[match['tbnid']]
    #     elif 'id' in match['rg_meta'] and match['rg_meta']['id'] in thumb_dict:
    #         match['thumbnail'] = thumb_dict[match['rg_meta']['id']]

    print('len(matches) = {}'.format(len(matches)))
    return {'query': str(query_str), 'results': matches}
