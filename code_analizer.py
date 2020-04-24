import os
import re
import argparse

from os import walk
from pprint import pprint


parser = argparse.ArgumentParser(description='Input path')
parser.add_argument('--path', type=str, required=True)

# ignore these files by these rules
ignore_files = [
    r'.pyc$', r'db.sqlite3', r'nginx.conf', r'.dockerignore',
    r'README.md', r'requirements.txt', r'swagger.yaml', r'Dockerfile',
    r'docker-compose.yaml'
]

# init structure of final statistic
stat = {
    lang: {
        'code': 0,
        'comment': 0,
        'blank': 0,
        'files': 0,
        'size': 0
    }
    for lang in ['py', 'html', 'json']
}


def ignore_check(filenames):
    """
    Checking if file needs to be ignored
    """
    f = []
    for filename in filenames:
        ignore = False
        for el in ignore_files:
            ignore = re.findall(el, filename)
            if ignore:
                ignore = True
                break

        if not ignore:
            f.append(filename)
    return f


def get_dir_files(path):
    """
    Get list of all files in input directory
    """
    f = []
    for (dirpath, dirnames, filenames) in walk(path):
        for filename in filenames:
            f.append(os.path.join(dirpath, filename))

    filenames = ignore_check(f)
    return filenames


def analize_line(lang, line, multilines_comment):
    """
    Analize line:
        - singleline comment
        - multiline comment
        - code
        - comment in line of code
    """
    line_added = False

    if line in ['\n', '\r\n'] and not multilines_comment:
        stat[lang]['blank'] += 1
        line_added = True
    elif line in ['\n', '\r\n'] and multilines_comment:
        stat[lang]['comment'] += 1
        line_added = True

    # base rules for determine either line comment or not
    multiline_conditions = {
        'py': {
            'start': (line.strip().startswith('"""') and not line.strip().endswith('"""')) or \
                    (line.strip().startswith('\'\'\'') and not line.strip().endswith('\'\'\'')),
            'end': (not line.strip().startswith('"""') and line.strip().endswith('"""')) or \
                   (not line.strip().startswith('\'\'\'') and line.strip().endswith('\'\'\'')),
            'inline': (line.strip().startswith('"""') and line.strip().endswith('"""')) or \
                      (line.strip().startswith('\'\'\'') and line.strip().endswith('\'\'\'')),
            'singleline': '#'
        },
        'html': {
            'start': (line.strip().startswith('<!--') and not line.strip().endswith('-->')),
            'end': (not line.strip().startswith('<!--') and line.strip().endswith('-->')),
            'inline': (line.strip().startswith('<!--') and line.strip().endswith('-->')),
            'singleline': ''
        },
        'js': {
            'start': (line.strip().startswith('/*') and not line.strip().endswith('*/')),
            'end': (not line.strip().startswith('/*') and line.strip().endswith('*/')),
            'inline': (line.strip().startswith('/*') and line.strip().endswith('*/')),
            'singleline': '//'
        },
    }

    # check multiline comments
    if multiline_conditions[lang]['start']:
        # check if the line is the start of multiline comment
        if not multilines_comment:
            multilines_comment = True
        stat[lang]['comment'] += 1
        line_added = True

    elif multiline_conditions[lang]['end']:
        # check if the line is the end of multiline comment
        if multilines_comment:
            # if not multilines_comment then it just end of multiline string
            stat[lang]['comment'] += 1
            line_added = True
            multilines_comment = False

    elif multiline_conditions[lang]['inline']:
        # check if the line is multiline comment in one line
        stat[lang]['comment'] += 1
        line_added = True

    comment_symbol = multiline_conditions[lang]['singleline']

    # check singleline comments
    if comment_symbol and comment_symbol in line and not multilines_comment:
        if line.strip().startswith(comment_symbol):
            stat[lang]['comment'] += 1
            line_added = True

        elif line.split(comment_symbol)[0].count('"') % 2 \
                or line.split(comment_symbol)[0].count('\'') % 2:
            # check singleline comment in line of code
            stat[lang]['comment'] += 1
            stat[lang]['code'] += 1
            line_added = True

    if not line_added:
        stat[lang]['code'] += 1
        line_added = True

    return multilines_comment, line_added


def get_file_stat(filename):
    """
    Analize file:
        - comments
        - code
        - empty line
    """
    name, extension = os.path.splitext(filename)
    if stat.get(extension.replace('.', '')):
        stat[extension.replace('.', '')]['files'] += 1
        stat[extension.replace('.', '')]['size'] = os.path.getsize(filename)

        multilines_comment = False
        lines = 0

        with open(filename) as f:
            for line in f:
                multilines_comment, line_added = analize_line(
                    extension.replace('.', ''),
                    line,
                    multilines_comment
                )

                if line_added:
                    lines += 1
                else:
                    print('shos pishlo ne tak: ', filename, line)
    else:
        print(f'Analize type "{extension}" currently is not available. File: {filename}')

def main(path):
    filenames = get_dir_files(path)
    for filename in filenames:
        get_file_stat(filename)


if __name__ == '__main__':
    path = '/Users/serhii/Documents/projects/currency_app/currency' #TODO remove

    args = parser.parse_args()
    main(args.path)

    pprint(stat)
