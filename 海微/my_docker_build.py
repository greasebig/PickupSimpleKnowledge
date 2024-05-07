# coding=utf-8
###
 # @Author: lujunda
 # @Date: 2023-07-17 14:22:40
 # @LastEditTime: 2023-07-17 15:04:49
 # @FilePath: /ImgRelease/script/my_docker_build.py
 # @Description: 
 # 构建docker镜像
 # Copyright (c) 2023 by ${git_name_email}, All Rights Reserved. 
### 

import os
import subprocess
import argparse
import shutil
from tqdm import tqdm

VERSION = "0.0.3"

def check_diskspace():
    print("====> 检查磁盘空间")

def check_update():
    opt = input("是否已经把项目代码更新到最新版本?[Y/n] ")
    if opt in ["Y", "y"]:
        print("====> 开始检查")
    else:
        print("====> 请先更新项目代码")
        exit(1)

def check_version():
    print("====> 检查版本号")

def docker_rm():
    print("====> 开始删除镜像\n")
    if os.path.isdir(dockerRmPath):
        file_names = os.listdir(dockerRmPath)
        for file_name in tqdm(file_names):
            image_name = "{}:{}".format(file_name, VERSION)
            print("删除{}".format(image_name))
            if subprocess.call("sudo docker rmi {}".format(image_name), shell=True) != 0:
                print("删除镜像失败,请检查!")
            print("\n")
    else:
        output = subprocess.check_output("sudo docker image ls {}".format(dockerRmPath), shell=True)
        if len(output.splitlines()) == 2:
            subprocess.call("sudo docker rmi {}".format(dockerRmPath), shell=True)

def docker_build(mode):
    all_file_names = os.listdir(dockerPath)
    
    #existing_images = subprocess.check_output("sudo docker images", shell=True).decode().splitlines()
    result = subprocess.check_output("sudo docker images | awk '{print $1\":\"$2}'", shell=True)
    existing_images = result.decode().split('\n')[:-1]
    existing_images = [img.split(':')[0]+':'+img.split(':')[1] for img in existing_images]
    file_names = []
    for file_name in all_file_names:
        image_name = "{}:{}".format(file_name,VERSION)
        if image_name not in existing_images:
            file_names.append(file_name)
    
    print("已有以下 Docker 包:")
    for img in set(all_file_names) - set(file_names):
        print(img, end=', ')
    print("\n")
    print("准备安装以下镜像:")
    print(file_names, "\n")
    
    for file_name in tqdm(file_names):
        image_name = "{}:{}".format(file_name,VERSION)
        print("打包 {}".format(image_name))
        docker_file = "{}/{}".format(dockerPath,file_name)
        if mode==0: #debug版，不加密
            if subprocess.call("sudo docker build --build-arg DOCKER_FILE={} -t {} .".format(docker_file,image_name), shell=True) != 0:
                print("打包失败,请检查!")
                print("\n")
            
            #上传到云
            if push2cloud(file_name) == -1:
                print("本地docker未推送成功，没有找到镜像 {} ，无法上传到云,请检查!".format(image_name))
                print("\n")
                
            
        elif mode==1: #release版，加密
            encrypt(file_name)
            if subprocess.call("sudo docker build -f .dockerignore-release --build-arg DOCKER_FILE={} -t {} .".format(docker_file,image_name), shell=True) != 0:
                print("打包失败,请检查!")
            print("\n")
            
            if push2cloud(file_name) == -1:
                print("本地docker未推送成功，没有找到镜像 {} ，无法上传到云,请检查!".format(image_name))
                print("\n")

def docker_pack(mode):
    check_version()
    docker_build(mode)

def docker_save():
    print("====> 开始保存所有镜像\n")
    file_names = os.listdir(dockerPath)
    #print(file_names)
    for file_name in tqdm(file_names):
        image_name = "{}:{}".format(file_name,VERSION)
        print("保存镜像文件{}".format(image_name))
        if subprocess.call("sudo docker save -o {}.tar {}".format(file_name,image_name), shell=True) != 0:
            print("保存失败,请检查!")
        print("\n")

def few_docker_save(images):
    print("====> 开始保存指定镜像\n")
    print("一共要保存的镜像有{}个".format(len(images)))
    print("具体为: {}".format(images))
    #file_names = os.listdir(dockerPath)
    for file_name in tqdm(images):
        image_name = "{}:{}".format(file_name,VERSION)
        print("保存镜像文件{}".format(image_name))
        if subprocess.call("sudo docker save -o {}.tar {}".format(file_name,image_name), shell=True) != 0:
            print("保存失败,请检查!")
        print("\n")


def few_docker_rm(images):
    print("一共要删除的镜像有{}个".format(len(images)))
    print("具体为: {}".format(images))
    for image_name in tqdm(images):
        if os.path.isdir("{}/{}".format(dockerPath,image_name)):
            print("====> 开始删除镜像 {}:{}\n".format(image_name,VERSION))
            docker_file = "{}/{}".format(dockerPath,image_name)
            if subprocess.call("sudo docker rmi {}:{}".format(image_name,VERSION), shell=True) != 0:
                print("删除镜像 {}:{} 失败,请检查!".format(image_name,VERSION))
            print("\n")
        else:
            output = subprocess.check_output("sudo docker image ls {}".format(dockerRmPath), shell=True)
            if len(output.splitlines()) == 2:
                subprocess.call("sudo docker rmi {}".format(dockerRmPath), shell=True)



def few_docker_build(mode,images):
    
    result = subprocess.check_output("sudo docker images | awk '{print $1\":\"$2}'", shell=True)
    existing_images = result.decode().split('\n')[:-1]
    existing_images = [img.split(':')[0]+':'+img.split(':')[1] for img in existing_images]
    
    print("一共要打包的镜像有{}个".format(len(images)))
    print("具体为: {}".format(images))
    for file_name in tqdm(images):
        image_name = "{}:{}".format(file_name,VERSION)
        if os.path.isdir("{}/{}".format(dockerPath,file_name)):
            
            if image_name in existing_images:
                print("{} 已存在,跳过打包 \n".format(image_name))
                continue
            print("====> 开始打包镜像 {}\n".format(image_name))
            docker_file = "{}/{}".format(dockerPath,file_name)
            #print("docker_file=",docker_file)
            if mode==0: #debug版，不加密
                subprocess.call("cp .dockerignore-debug .dockerignore", shell=True)
                if subprocess.call("sudo docker build --build-arg DOCKER_FILE={} -t {} .".format(docker_file,image_name), shell=True) != 0:
                    print("打包失败,请检查!")
                    print("\n")
                
                if push2cloud(file_name) == -1:
                    print("本地docker未推送成功，没有找到镜像 {} ，无法上传到云,请检查!".format(image_name))
                    print("\n")
                
            elif mode==1: #release版，加密
                encrypt(file_name)
                subprocess.call("cp .dockerignore-release .dockerignore", shell=True)
                if subprocess.call("sudo docker build --build-arg DOCKER_FILE={} -t {} .".format(docker_file,image_name), shell=True) != 0:
                    print("打包失败,请检查!")
                    print("\n")
                
                if push2cloud(file_name) == -1:
                    print("本地docker未推送成功，没有找到镜像 {} ，无法上传到云,请检查!".format(image_name))
                    print("\n")
                
        else:
            print("镜像 {} 不存在,请检查!".format(file_name))
            
def few_docker_pack(mode,images):
    check_version()
    few_docker_build(mode,images)
    

###对单个镜像下所有engine加密，已加密的不再加密    
def encrypt(image):
    print("加密镜像: {}".format(image))
    
    original_modeldir_path = "{}/{}/resources/model".format(dockerPath,image)
    
    for root, dirs, files in os.walk(original_modeldir_path):
        for file in files:
            if file.endswith(".engine"):
                name=file.split('.')[0]
                encrypted_file = name + ".encrypted"
                if encrypted_file not in files:
                    print('{} 尚未加密，加密中...'.format(file))    
                    original_file_path=os.path.join(original_modeldir_path, file)
                    encrypted_file_path = os.path.join(original_modeldir_path, encrypted_file)
                    shutil.copy(original_file_path, encrypted_file_path) 
                    with open(encrypted_file_path, 'ab') as f:
                        f.write(b'seaway')
                    print('Original file {} copied to {} and encrypted'.format(file,encrypted_file))
    
    

###将单个镜像上传到云
def push2cloud(image):
    
    #找 ImageId
    result = subprocess.check_output("sudo docker images | awk '{print $1\":\"$2\";\"$3}'", shell=True)
    existing_images = result.decode().split('\n')[:-1]
    existing_images2=[]
    for a in existing_images:
        existing_images2.append(a.split(';')[0])
        existing_images2.append(a.split(';')[1])  
    
    #匹配名称
    image_name = "{}:{}".format(image,VERSION)
    
    try:
        index = existing_images2.index(image_name)
    except ValueError:
        index = -1 # 未找到元素  
    if index == -1 :
        return -1    
    ImageId=existing_images2[index+1]
    
    print("镜像 {}:{} 正在上传到云...".format(image,VERSION))
    if subprocess.call("sudo docker login --username=cuihao@1951349932148726 --password=Seaway2019 swf-registry.cn-beijing.cr.aliyuncs.com"
                       , shell=True) != 0:
        print("登录阿里云账户失败,请检查!")
        print("\n")
        
    
    if subprocess.call("sudo docker tag {} swf-registry.cn-beijing.cr.aliyuncs.com/store/{}:{}".format(ImageId,image,VERSION)
                       , shell=True) != 0:
        print("docker tag 失败,请检查!")
        print("\n")
    if subprocess.call("sudo docker push swf-registry.cn-beijing.cr.aliyuncs.com/store/{}:{}".format(image,VERSION)
                       , shell=True) != 0:
        print("docker push 失败,请检查!")
        print("\n")
    print("镜像 {}:{} 上传到云成功!".format(image,VERSION))
    print("\n")
    

if __name__ == "__main__":
    
    
        
    #os._exit(0)
    
    parser = argparse.ArgumentParser()
    
    #默认是release版，加 -D 则执行debug版
    parser.add_argument("-R", "--release",action='store_true', help="release版，加密，默认是release版，加 -D 则执行debug版")
    parser.add_argument("-D", "--debug",action='store_true', help="debug版，不加密")
    
    parser.add_argument("-s", "--save_all_docker", action="store_true",help="保存所有镜像")
    parser.add_argument("-p", "--push_all_docker", action="store_true", help="推送所有镜像，默认一起上传到云服务器")
    parser.add_argument("-r", "--rmi_all_docker", action="store_true",help="删除所有镜像")
    
    parser.add_argument("-s1", "--save_specific_docker", nargs="+",help="保存指定镜像")
    parser.add_argument("-p1", "--push_specific_docker", nargs="+", help="新增指定镜像，默认一起上传到云服务器")
    parser.add_argument("-r1", "--rmi_specific_docker", nargs="+", help="删除指定镜像") 
    
    #to do: 
    #1.是否上传到云服务器
    #parser.add_argument("--not2cloud", action="store_true", help="推送镜像时不上传到云服务器")
    #2.修改密码
    #parser.add_argument("--not2cloud", action="store_true", help="推送镜像时不上传到云服务器")

    args = parser.parse_args()

    dockerPath = "docker" 
    dockerRmPath = "docker" 
    
    
    #默认是release版，加 -D 则执行debug版
    if args.debug:   #default: False    
        print('debug版，不加密\n')
        mode=0
        
        if args.save_all_docker:
            docker_save()
        elif args.push_all_docker:
            docker_pack(mode=mode)
        elif args.rmi_all_docker:
            docker_rm()
            
        elif args.save_specific_docker:
            few_docker_save(args.save_specific_docker)
        elif args.push_specific_docker:
            few_docker_pack(mode=mode,images=args.push_specific_docker)
        elif args.rmi_specific_docker:
            few_docker_rm(args.rmi_specific_docker)
        
    else:
        
        mode=1
        
        if args.save_all_docker:
            docker_save()
        elif args.push_all_docker:
            print('release版，加密\n')
            docker_pack(mode=mode)
        elif args.rmi_all_docker:
            docker_rm()
            
        elif args.save_specific_docker:
            few_docker_save(args.save_specific_docker)
        elif args.push_specific_docker:
            print('release版，加密\n')
            few_docker_pack(mode=mode,images=args.push_specific_docker)
        elif args.rmi_specific_docker:
            few_docker_rm(args.rmi_specific_docker)
            
        

    """
        使用说明:
        
        build加密，save成tar包写未加密方法，因为之后不需要转tar包，直接上传到云端
        
        在ImRelease文件夹中执行命令，以检测到Dockerfile以及docker文件夹。
        不需要像上个版本一样输入 docker 作为参数的一部分，可以直接添加、删除指定镜像名。
        
        推送所有镜像:
        python xxx.py -p 
        
        删除指定镜像id:
        python xxx.py -r <镜像id>
        
        保存所有镜像:
        python xxx.py -s 
        
        新增指定镜像:
        python xxx.py -a <镜像1> <镜像2>
        
        删除指定镜像:
        python xxx.py -d <镜像1> <镜像2>
        
        """
