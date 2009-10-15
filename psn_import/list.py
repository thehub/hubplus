import sys

from psn_import.utils import maps, reverse, load_file, list_type

if __name__ == '__main__' :
    type = sys.argv[3]
    print type
    load_file(type,'mhpss_export/%s.pickle' % type)
    list_type(type,['all','uid','username','location'])
    exit()

