import os
import re
import yaml
import docker

def load_config():
    with open('config.yml') as f:
        return yaml.load(f)

if __name__ == '__main__':

    config = load_config()

    src_registry = config['src_registry']['hostname']
    dst_registry = config['dst_registry']['hostname']
    src_username = None if 'username' not in config['src_registry'] else str(config['src_registry']['username'])
    src_password = None if 'password' not in config['src_registry'] else str(config['src_registry']['password'])
    dst_username = None if 'username' not in config['dst_registry'] else str(config['dst_registry']['username'])
    dst_password = None if 'password' not in config['dst_registry'] else str(config['dst_registry']['password'])

    docker_client = docker.from_env()
    docker_client.login(registry=src_registry, 
                        username=src_username,
                        password=src_password)   
    docker_client.login(registry=dst_registry, 
                        username=dst_username,
                        password=dst_password)                          

    repositories = config['repositories']

    for repository in repositories:
        src_repo_url = src_registry + "/" + repository[0]
        dst_repo_url = dst_registry + "/" + repository[1]
        
        images = docker_client.images.pull(src_repo_url)

        for image in images:
            for tag in image.tags:
                tag_name = tag.split(":")
                image.tag(dst_repo_url,tag_name[1])

                docker_client.images.push(dst_repo_url,tag_name[1])
                # remove destination image
                docker_client.images.remove(dst_repo_url + ":" + tag_name[1])