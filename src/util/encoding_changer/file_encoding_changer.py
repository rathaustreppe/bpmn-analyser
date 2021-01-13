import os

if __name__ == '__main__':
    # Currently there is a bug with the hosted frontend where the *.bpmn files
    # are saved in latin1. But the XML is specified with UTF8.
    # So the parser dies. To truly convert the file to utf8 this thing was written.

    # Please run this tool on every file only once or you get into troubles with
    # encoding.

    # please make a copy of your files before using this thing here :-)

    # Put all file names in this list
    files_to_change = ['2_g.bpmn', '2_h.bpmn', '2_i.bpmn', '2_j.bpmn', '2_j_corrected.bpmn']

    # Specify relative folder from this source file.
    rel_folder_path = r'../../../test/first_field_trial/U2'
    abs_folder_path = os.path.abspath(rel_folder_path)
    file_mask = r'*.bpmn'

    # Your files are encoded in....
    coding1 = "latin1"

    # And you want your files to be encoded in...
    coding2 = "utf8"

    for file in files_to_change:
        filepath = os.path.join(abs_folder_path, file)
        f= open(filepath, 'r', encoding=coding1)
        content= f.read()
        f.close()
        f= open(filepath, 'w', encoding=coding2)
        f.write(content)
        f.close()

        print(f'done {file}')