# 2018.07.10 14:12:52 CST
#Embedded file name: diff_repo.py
import xml.sax
import os, sys
import getopt
import json

class ManifestHandler(xml.sax.ContentHandler):

    def __init__(self):
        self.current = ''
        self.name = ''
        self.path = ''
        self.own_dict = {}

    def startElement(self, tag, attributes):
        self.current = tag
        name = ''
        path = ''
        if tag == 'project':
            for value in attributes.getNames():
                if value == 'name':
                    name = attributes['name']
                    name = name.replace('Android8/', '')
                    name = name.replace('/', '__')
                if value == 'path':
                    path = attributes['path']

            if len(name) > 0 and len(path) > 0:
                dictObj = {name: path}
                self.own_dict.update(dictObj)

    def copy_all_projs(self):
        json_output = self.own_dict.copy()
        return json_output

    def saveToFile(self, output_file):
        json.dump(self.own_dict, open(output_file, 'w'))


def compare_git_log_in_dir(dir1, dir2):
    print 'hello\n'


def classified_jsons(json1, json2):
    discarded = {}
    same = {}
    added = {}
    discarded = json1.copy()
    added = json2.copy()
    for key in json1:
        if key in added:
            if added[key] == discarded[key]:
                same.update({key: discarded[key]})
                discarded.pop(key)
                added.pop(key)
            else:
                print 'Warning:path1:' + discarded[key] + ', path2: ' + added[key]

    return (discarded, same, added)


def parse_repo(repo_dir):
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    Handler = ManifestHandler()
    parser.setContentHandler(Handler)
    parser.parse(repo_dir + '.repo/manifest.xml')
    json_output = Handler.copy_all_projs()
    return json_output


def get_absolute_path(PWD, relative_path):
    if relative_path[0] != '/':
        return PWD + '/' + relative_path
    else:
        return relative_path

def main(argv):
    PWD = os.getcwd()
    old_repo = ''
    new_repo = ''
    output = ''
    Debug = 0
    GENERAL = 'general_info.txt'
    DETAIL = 'detail_diff.txt'

    try:
        opts, args = getopt.getopt(argv, 'dhi:n:o:')
    except getopt.GetoptError:
        print 'diff_repo.py -i <old repo path> -n <new repo path> -o <output path>.'
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print 'diff_repo.py -i <old repo path> -n <new repo path> -o <output path>'
        elif opt == '-i':
            old_repo = get_absolute_path(PWD, arg)
            if not os.path.exists(old_repo + '.repo/manifest.xml'):
                print 'diff_repo.py -i <old repo path> -n <new repo path> -o <output path>'
                print old_repo + ': is not android repo.'
                sys.exit(3)
        elif opt == '-n':
            new_repo = get_absolute_path(PWD, arg)
            if not os.path.exists(new_repo + '.repo/manifest.xml'):
                print 'diff_repo.py -i <old repo path> -n <new repo path> -o <output path>'
                print new_repo + ': is not android repo.'
                sys.exit(3)
        elif opt == '-o':
            output = get_absolute_path(PWD, arg)
	elif opt == '-d':
	    Debug = 1

    print '============= Param Info ==================='
    print 'old repo path: ' + old_repo
    print 'new repo path: ' + new_repo
    print 'General Diff File: ' + output + '/' + GENERAL
    print 'DETAIL Diff File : ' + output + '/' + DETAIL
    print '============================================\n'
    json_old_repo = parse_repo(old_repo)
    json_new_repo = parse_repo(new_repo)
    if Debug:
        output_old_repo = output + '/old_repo.json'
        output_new_repo = output + '/new_repo.json'
#        json.dump(json_old_repo, open(output_old_repo, 'w'))
#        json.dump(json_new_repo, open(output_new_repo, 'w'))
        old_file = open(output_old_repo, 'w')
	for key in json_old_repo:
	  old_file.write(json_old_repo[key])
	  old_file.write("\n")
	old_file.close()

        new_file = open(output_new_repo, 'w')
	for key in json_new_repo:
	  new_file.write(json_new_repo[key])
	  new_file.write("\n")
	new_file.close()

    discarded, same, added = classified_jsons(json_old_repo, json_new_repo)
    general_str = '======================== General Info =========================\n' \
                + 'Old git amount           : ' + str(len(discarded) + len(same)) \
		+ '\n' + 'New git amount    : ' + str(len(same) + len(added)) + '\n' \
		+ '\n' + 'Discarded amount  : ' + str(len(discarded)) + '\n' \
		+ 'Added amount             : ' + str(len(added)) + '\n' \
		+ 'Continue to used         : ' + str(len(same)) \
		+ '\n' + '\n'

    general_file = output + '/' + GENERAL
    detail_file = output + '/' + DETAIL
    general = open(general_file, 'w')
    general.write(general_str)
    print general_str
    changed_repo_count = 0
    print 'Begin analysis...'
    for key in same:
        shell = PWD + '/compare_git_log.sh'
        arg0 = old_repo + same[key]
        arg1 = new_repo + same[key]
        arg3 = detail_file
        arg4 = same[key]
        os.system(shell + ' ' + arg0 + ' ' + arg1 + ' ' + arg3 + ' ' + arg4)
        with open(detail_file, 'r') as diff_f:
            content = diff_f.read()
            if len(content) > 2:
                general.write('\n\n')
                general.write(same[key])
                general.write('\n\n')
                general.write(content)
                changed_repo_count += 1

    print 'Analyise Done.'
    print '============================================\n'
    print ' Changed repo count: ' + str(changed_repo_count)
    print ' Same repo count: ' + str(len(same) - changed_repo_count)
    general_str = '\nAdded git path: \n'
    for key in added:
        general_str += '    ' + added[key] + '\n'

    general_str += '\nDiscarded git path: \n'
    for key in discarded:
        general_str += '    ' + discarded[key] + '\n'

    general.write(general_str)
    print general_str
    general.close()
    os.remove(detail_file)


if __name__ == '__main__':
    main(sys.argv[1:])
#+++ okay decompyling /home/jcz/diff_repo.pyo 
# decompiled 1 files: 1 okay, 0 failed, 0 verify failed
# 2018.07.10 14:12:52 CST
