###
 # @Author: lujunda
 # @Date: 2023-05-11 14:22:40
 # @LastEditTime: 2023-05-11 15:04:49
 # @FilePath: 
 # @Description: 
 # 构建16路engine
 # Copyright (c) 2023 by ${git_name_email}, All Rights Reserved. 
### 
#!/bin/bash

NUMBER=16
NETWORK_MODE=2
## 0=FP32, 1=INT8, 2=FP16 mode

case $NETWORK_MODE in
    0)
        echo "NETWORK_MODE= 0"
        MODEL_NAME="fp32"
        ;;
    1)
        echo "NETWORK_MODE= 1"
        MODEL_NAME="int8"
        ;;
    2)
        echo "NETWORK_MODE= 2"
        MODEL_NAME="fp16"
        ;;
    *)
        echo "Invalid input"
        ;;
esac

MODEL_NAME="..\/model\/model_b${NUMBER}_gpu0_${MODEL_NAME}.engine"
echo "$MODEL_NAME"

echo "即将构建${NUMBER}路${MODEL_NAME} engine"
mkdir ../myresources/

skip_files=("detection-19-yolov3-ds" "road-mark-yolov3-ds" "road-disaster-yolov3-ds")
file_names=$(ls ../../docker)
echo "$file_names"
for file_name in $file_names
do
    skip_file=false
    for skip_filename in "${skip_files[@]}"; do
        if [[ "$file_name" == "$skip_filename" ]]; then
            skip_file=true
            break
        fi
    done
    
    if [ $skip_file = true ]; then
        echo "$file_name skip"
        continue
    fi

    echo "即将构建 $file_name $NUMBER 路engine"
    rm -rf resources
    cp -r ../../docker/$file_name/resources ./

    
    
    ## 修改model-engine-file
    grep 'model-engine-file=' ./resources/config/config_infer_primary_yoloV3.txt | \
    sed "s/model-engine-file=.*/model-engine-file=$MODEL_NAME/" -i ./resources/config/config_infer_primary_yoloV3.txt
    grep 'model-engine-file=' ./resources/config/mark_infer_primary_yoloV3.txt | \
    sed "s/model-engine-file=.*/model-engine-file=$MODEL_NAME/" -i ./resources/config/mark_infer_primary_yoloV3.txt
    grep 'model-engine-file=' ./resources/config/config_infer_primary_yoloV5.txt | \
    sed "s/model-engine-file=.*/model-engine-file=$MODEL_NAME/" -i ./resources/config/config_infer_primary_yoloV5.txt
    grep 'model-engine-file=' ./resources/config/disaster_infer_primary_yoloV3.txt | \
    sed "s/model-engine-file=.*/model-engine-file=$MODEL_NAME/" -i ./resources/config/disaster_infer_primary_yoloV3.txt
    
    ## 修改network-mode
    grep 'network-mode=' ./resources/config/config_infer_primary_yoloV3.txt | \
    sed "s/network-mode=.*/network-mode=$NETWORK_MODE/" -i ./resources/config/config_infer_primary_yoloV3.txt
    grep 'network-mode=' ./resources/config/mark_infer_primary_yoloV3.txt | \
    sed "s/network-mode=.*/network-mode=$NETWORK_MODE/" -i ./resources/config/mark_infer_primary_yoloV3.txt
    grep 'network-mode=' ./resources/config/config_infer_primary_yoloV3.txt | \
    sed "s/network-mode=.*/network-mode=$NETWORK_MODE/" -i ./resources/config/config_infer_primary_yoloV5.txt
    grep 'network-mode=' ./resources/config/disaster_infer_primary_yoloV3.txt | \
    sed "s/network-mode=.*/network-mode=$NETWORK_MODE/" -i ./resources/config/disaster_infer_primary_yoloV3.txt


    ./run.sh

    mv *.engine ./resources/model/
    mkdir ../myresources/$file_name
    mv ./resources ../myresources/$file_name/
    echo "完成 $file_name $NUMBER 路engine构建"
done
mv ../myresources/* ../../docker/*
rm -rf ../myresources
echo "完成所有镜像${NUMBER}路${MODEL_NAME} engine构建"
