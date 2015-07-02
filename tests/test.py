# coding:utf8
"""

Author: ilcwd
"""

TIMELINE_TYPE = {
    'picture': ('jpg', 'png', 'gif', 'bmp', 'psd',
                'ttf', 'jpeg', 'tiff', 'raw', 'nef',
                'tif', 'emf', 'wmf'),
    'thumbnail': ('jpg', 'png', 'jpeg'),
    'document': ('csv', 'doc', 'docm', 'docx',
                 'dot', 'dotx', 'dps', 'dpt',
                 'et', 'ett', 'pdf', 'pot',
                 'potx', 'pps', 'ppsx', 'ppt',
                 'pptm', 'pptx', 'rtf', 'txt',
                 'wps', 'wpt', 'xls', 'xlsb',
                 'xlsm', 'xlsx', 'xlt', 'xltx'),
    'media': ('mp3', 'wav', 'amr', 'avi', 'mov',
              'flv', 'ogg', '3gp', 'mpg', 'wma',
              'wmv', 'rmvb', 'rm', 'mpeg', 'mkv',
              'mp4', 'ts', 'aac', 'flac',
              'm4a', 'midi', '3g2', 'asf',
              'f4v', 'm4v', 'm4r', 'mka', ),

    'xlpicture': ('ai', 'bmp', 'cdr', 'cur',
                  'dib', 'dxf', 'emf', 'eps',
                  'exif', 'fpx', 'gif', 'icb',
                  'ico', 'iff', 'img', 'ithmb',
                  'j2c', 'jp2', 'jpc', 'jpeg',
                  'jpf', 'jpg', 'jps', 'jpx',
                  'mac', 'mpo', 'ozj', 'pam',
                  'pbm', 'pcd', 'pcx', 'pdd',
                  'pfm', 'pgm', 'pm', 'png',
                  'pnm', 'pns', 'ppm', 'psb',
                  'psd', 'pxr', 'qtx', 'raw',
                  'rle', 'sct', 'svg', 'tbi',
                  'tdi', 'tga', 'tif', 'tiff',
                  'ufo', 'vda', 'vst', 'vtf',
                  'wmf', 'xpm'),

    'xldocument': ('chm', 'csv', 'dbf', 'dif',
                   'doc', 'docm', 'docx', 'dot',
                   'dotm', 'dotx', 'dps', 'dpt',
                   'eml', 'et', 'ett', 'html',
                   'mht', 'mhtml', 'mmap', 'mmas',
                   'mmat', 'mmp', 'pdf', 'pot',
                   'potx', 'pps', 'ppt', 'pptx',
                   'prn', 'res', 'rtf', 'sylk',
                   'txt', 'wps', 'wpt', 'xhtml',
                   'xls', 'xlsm', 'xlsx', 'xlt',
                   'xmind', 'xml', 'xmmap', 'xmmas',
                   'xmmat', 'xps'),

    'xlaudio': ('aac', 'ac3', 'aif', 'aifc',
                'aiff', 'amr', 'ape', 'asx',
                'au', 'avr', 'bwf', 'caf',
                'cda', 'csvz', 'flac', 'htk',
                'iff', 'm3u', 'm4a', 'mat',
                'mid', 'midi', 'mka', 'mlv',
                'mp+', 'mp1', 'mp2', 'mp3',
                'mpc', 'ogg', 'paf', 'pcm',
                'pls', 'pvf', 'rf64', 'sd2',
                'sds', 'sf', 'snd', 'svx',
                'swa', 'voc', 'vox', 'vqf',
                'w64', 'wav', 'wma', 'wve',
                'xi'),

    'xlvideo': ('3g2', '3gp', 'asf', 'ask',
                'avi', 'c3d', 'dat', 'divx',
                'dvr-ms', 'f4v', 'fla', 'flc',
                'fli', 'flv', 'flx', 'm2p',
                'm2t', 'm2ts', 'm2v', 'm4v',
                'mkv', 'mlv', 'mov', 'mp4',
                'mpe', 'mpeg', 'mpg', 'mpv',
                'mts', 'navi', 'ogm', 'qt',
                'ra', 'ram', 'rm', 'rmvb',
                'swf', 'tp', 'trp', 'ts',
                'uis', 'uisx', 'uvp', 'vcd',
                'vcf', 'vob', 'vsp', 'webm',
                'wmv', 'wmvhd', 'wtv', 'xv',
                'xvid'),

    'xlarchive': ('7z', 'ace', 'arj', 'bz2',
                  'cab', 'gzip', 'jar', 'lzh',
                  'rar', 'uue', 'xz', 'z',
                  'zip'),

    'xunlei': ('td',),
}


def main():
    a = '7z ace arj bz2 cab gzip jar lzh rar uue xz z zip'

    print '(',
    for idx, ext in enumerate(a.split()):
        print "'%s', " % ext,
        if (idx + 1) % 4 == 0:
            print
    print ')'


if __name__ == '__main__':
    main()
