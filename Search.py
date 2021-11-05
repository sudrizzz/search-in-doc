import os
import pypandoc


class Search(object):
    def __init__(self):
        self.extension_list = ['commonmark', 'docbook', 'docx', 'epub', 'haddock', 'html', 'latex', 'markdown',
                               'odt', 'opml', 'org', 'rst', 't2t', 'textile', 'twiki']

    def find_in_dir(self, root_dir, keyword, cache_path):
        root_dir = os.path.abspath(root_dir)
        process_list = self.get_process_files(root_dir)
        data = []
        index = 1
        for filename in process_list:
            cache_file = os.path.join(cache_path, filename[0] + '.txt')
            origin_path = filename[1]
            if filename[0].startswith('~') or os.path.getsize(origin_path) == 0:
                continue
            if not os.path.exists(cache_file):
                print(origin_path)
                output = pypandoc.convert_file(origin_path, 'plain', outputfile=cache_file)
                assert output == ''
            file = open(cache_file, "r", encoding='utf-8')
            for line in file:
                if keyword in line:
                    data.append([index, origin_path, line.strip()])
                    index += 1
            file.close()
        return data

    def get_process_files(self, root_dir):
        cur_dir = os.path.abspath(root_dir)
        file_list = os.listdir(cur_dir)
        process_list = []
        for file in file_list:
            fullfile = cur_dir + "\\" + file
            if os.path.isfile(fullfile):
                filename, file_extension = os.path.splitext(file)
                if file_extension[1:].lower() not in self.extension_list:
                    continue
                process_list.append([filename, fullfile])
            elif os.path.isdir(fullfile):
                dir_extra_list = self.get_process_files(fullfile)
                if len(dir_extra_list) != 0:
                    for x in dir_extra_list:
                        process_list.append(x)
        return process_list
