#!/usr/bin/python
import json
import time
import fsspec
import os
import argparse

def read_config(filename):
    with open(filename, 'r') as f:
        config = json.load(f)
    return {
        'bucket': config['OSS']['bucket'],
        'endpoint': config['OSS']['endpoint'],
        'access_key_id': config['OSS']['access_key_id'],
        'access_key_secret': config['OSS']['access_key_secret']
    }

def print_tree(fs, path, indent=0):
    for item in fs.ls(path):
        item_name = os.path.basename(item)
        print(' ' * indent + '├── ' + item_name)
        
        if fs.isdir(item):
            print_tree(fs, item, indent + 4)

def get_filesystem(fs_type, config):
    if fs_type == 'oss':
        return fsspec.filesystem(
            "s3",
            key=config['access_key_id'],
            secret=config['access_key_secret'],
            client_kwargs={"endpoint_url": config['endpoint']}
        )
    elif fs_type == 'local':
        return fsspec.filesystem('file')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor a directory in a filesystem")
    parser.add_argument("-d", "--directory", required=True, help="Directory to monitor")
    parser.add_argument("-t", "--type", choices=['oss', 'local'], default='local', help="Type of filesystem (default: local)")
   
    args = parser.parse_args()
    directory = args.directory
    fs_type = args.type
    
    config = read_config("config.json") if fs_type == 'oss' else None
    fs = get_filesystem(fs_type, config)
    full_path = f"{config['bucket']}/{directory}" if fs_type == 'oss' else directory
    
    while True:
        print("Listing directory contents:")
        print_tree(fs, full_path)
        time.sleep(2)
