#!/usr/bin/python

# TemplateNamer - script for generating a new Slate UI stand alone project based on a template

import sys
import getopt
import re
import os

validate_name_error = 'The name entered must not include special characters or line separators. ' \
                      'Please choice another name and try again.'

key_replacing_name = 'UnrealSlateAppTemplate'

def is_valid_name(name):
    # Make own character set and pass
    # this as argument in compile method
    regex = re.compile('[@!"#$%^&*()<>?/\\\|}{~:]')

    # Pass the string in search
    # method of regex object.
    if (regex.search(name) is None) and (not name.isspace()):
        return True
    raise Exception(f'[ERROR] The entered name "{name}" must not include special characters or line separators. '
                    f'Please choice another name and try again.')


def is_valid_path(path):
    if not os.path.exists(path):
        return False, 'The specified path does not exist'
    return True, None


def parse_args(argv):
    project_name = ''
    project_path = ''

    help_msg = 'Usage: \tTemplateNamer.py ' \
               '[-n <project_name> | --name="<project_name>"] ' \
               '[-p <project_path> | --path="<project_path>"] ' \
               '[-h | --help]\n'

    try:
        opts, args = getopt.getopt(argv, "hn:p:", ["name=", "path="])
    except getopt.GetoptError:
        print('Bad option(s)\n')
        print(help_msg)
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print(help_msg)
            sys.exit()
        if opt == '-n' or opt == '--name':
            if arg.startswith('"') and arg.endswith('"'):
                arg = arg[1:-1]
            if not is_valid_name(arg):
                raise Exception(f'[ERROR] "{arg}" - {validate_name_error}')
            project_name = arg
        if opt == '-p' or opt == '--path':
            if arg.startswith('"') and arg.endswith('"'):
                arg = arg[1:-1]
            is_valid, error = is_valid_path(arg)
            if not is_valid:
                raise Exception(f'[ERROR] "{arg}" - {error}')
            project_path = arg

    return project_name, project_path


def get_dst_name_by_src_path(path, target_name):
    src_base_name = os.path.basename(path)
    if key_replacing_name in src_base_name:
        src_base_name = src_base_name.replace(key_replacing_name, target_name)
    return src_base_name


def read_src_and_write_dst_file(path, target_path, target_name):
    dst_file_name = get_dst_name_by_src_path(path, target_name)
    dst_path = os.path.join(target_path, dst_file_name)

    with open(path, 'r') as src_file:
        with open(dst_path, 'w') as dst_file:
            src_content = src_file.read()
            dst_content = src_content.replace(key_replacing_name, target_name)
            dst_file.write(dst_content)


def iterate_by_dir_content(dir_path, target_path, target_name):
    dst_dir_name = get_dst_name_by_src_path(dir_path, target_name)
    dst_path = os.path.join(target_path, dst_dir_name)
    if not os.path.exists(dst_path):
        os.mkdir(dst_path)

    for item in os.listdir(dir_path):
        item_path = os.path.join(dir_path, item)
        if os.path.isdir(item_path):
            iterate_by_dir_content(item_path, dst_path, target_name)
        else:
            read_src_and_write_dst_file(item_path, dst_path, target_name)


def create_empty_slate_project(name, path):
    target_root = os.path.join(path, name)
    try:
        os.mkdir(target_root)
    except OSError:
        print("Creation of the directory %s failed" % target_root)
        return False
    else:
        print("Successfully created the directory %s " % target_root)

    # detect the current working directory and print it
    tool_path = os.getcwd()
    template_path = os.path.join(tool_path, "../../")
    print("The template path is \"%s\"" % template_path)

    iterate_by_dir_content(os.path.join(template_path, "Source"), target_root, name)
    read_src_and_write_dst_file(os.path.join(template_path, f'{key_replacing_name}.uproject'), target_root, name)

    return True


def main(argv):
    name, path = parse_args(argv)
    print(f'--- Creating "{name}" to "{path}"...')
    if create_empty_slate_project(name, path):
        print(f'--- Done! ---')
    else:
        print(f'--- Failed. ---')


if __name__ == "__main__":
    main(sys.argv[1:])
