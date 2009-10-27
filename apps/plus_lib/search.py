def side_search_args(search_type, search_type_label):
    return {'search_type':search_type, 'search_type_label':search_type_label}

def listing_args(search_url_name, tagged_url_name, tag_string='', search_terms='', multitabbed=False, order='', template_base='site_base.html', search_type_label=""):
    tags = tag_string.split('+')
    try:
        tags.remove('')
    except ValueError:
        pass
    if len(tags) > 1:
        multiple_tags = True
    else:
        multiple_tags = False
    return {'search_url':search_url_name, 'tagged_url':tagged_url_name, 'tag_string':tag_string, 'tag_filter':tags, 'multiple_tags':multiple_tags, 'search_terms':search_terms, 'multitabbed':multitabbed, 'order':order, 'template_base':template_base, 'search_type_label':search_type_label}
