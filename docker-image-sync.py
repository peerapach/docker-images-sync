import os
import re
import yaml
import docker

global docker_client

def loadConfig():
    with open('config.yml') as f:
        return yaml.load(f)

def dockerLogin(registry,username,password):
    try:
        docker_client.login(registry=registry, 
                            username=username,
                            password=password) 
    except:
        print("Error login on" + registry)

def dockerPullImage(src_repo_url):
    try:
        images = docker_client.images.pull(src_repo_url)
        return(images)
    except:
        print("Cannot pull image from " + src_repo_url)

def dockerPushImage(dst_repo_url,tag_name):
    try:
        docker_client.images.push(dst_repo_url,tag_name)
    except:
        print("Cannot pull image from " + dst_repo_url)

if __name__ == '__main__':

    config = loadConfig()

    src_registry = config['src_registry']['hostname']
    dst_registry = config['dst_registry']['hostname']
    src_username = None if 'username' not in config['src_registry'] else str(config['src_registry']['username'])
    src_password = None if 'password' not in config['src_registry'] else str(config['src_registry']['password'])
    dst_username = None if 'username' not in config['dst_registry'] else str(config['dst_registry']['username'])
    dst_password = None if 'password' not in config['dst_registry'] else str(config['dst_registry']['password'])

    docker_client = docker.from_env()
    dockerLogin(src_registry,src_username,src_password)
    dockerLogin(dst_registry,dst_username,dst_password)
                          
    repositories = config['repositories']

    for repository in repositories:
        src_repo_url = src_registry + "/" + repository[0]
        dst_repo_url = dst_registry + "/" + repository[1]
        
        images = dockerPullImage(src_repo_url)
        
        for image in images:
            for tag in image.tags:
                tag_name = tag.split(":")
                image.tag(dst_repo_url,tag_name[1])

                dockerPushImage(dst_repo_url,tag_name[1])
                # remove destination image on sync host
                docker_client.images.remove(dst_repo_url + ":" + tag_name[1])