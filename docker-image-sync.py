import os
import re
import yaml
import docker

global docker_client

def load_config():
    with open('config.yml') as f:
        return yaml.load(f)

def docker_login(registry,username,password):
    try:
        docker_client.login(registry=registry,
                            username=username,
                            password=password)
    except:
        print("Error login on" + registry)

def docker_pull_image(src_repo_url):
    try:
        images = docker_client.images.pull(src_repo_url)
        return(images)
    except:
        print("Cannot pull image from " + src_repo_url)

def docker_push_image(dst_repo_url,tag_name):
    try:
        docker_client.images.push(dst_repo_url,tag_name)
    except:
        print("Can't pull image from " + dst_repo_url)

if __name__ == '__main__':

    config = load_config()

    src_registry = config['src_registry']['hostname']
    dst_registry = config['dst_registry']['hostname']
    src_username = None if 'username' not in config['src_registry'] else str(config['src_registry']['username'])
    src_password = None if 'password' not in config['src_registry'] else str(config['src_registry']['password'])
    dst_username = None if 'username' not in config['dst_registry'] else str(config['dst_registry']['username'])
    dst_password = None if 'password' not in config['dst_registry'] else str(config['dst_registry']['password'])

    docker_client = docker.from_env()
    docker_login(src_registry,src_username,src_password)
    docker_login(dst_registry,dst_username,dst_password)

    repositories = config['repositories']

    for repository in repositories:
        src_repo_url = src_registry + "/" + repository[0]
        dst_repo_url = dst_registry + "/" + repository[1]

        print("\033[1;31;40mSyncing... \033[0m" + src_repo_url + "  =>  " + dst_repo_url)
        print("\033[1;32;40mPulling ... \033[0m" + src_repo_url)
        images = docker_pull_image(src_repo_url)
        for image in images:
            for tag in image.tags:
               tag_name = tag.split(":")
               if src_repo_url == tag_name[0]:
                  image.tag(dst_repo_url,tag_name[1])

                  print("\033[1;34;40mPushing... \033[0m" + tag + "  => " + dst_repo_url +":"+ tag_name[1])
                  docker_push_image(dst_repo_url,tag_name[1])
                # remove destination image on sync host
                  docker_client.images.remove(dst_repo_url + ":" + tag_name[1])
        print("")
