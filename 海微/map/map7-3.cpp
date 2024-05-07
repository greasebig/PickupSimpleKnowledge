#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <map>
#include <cmath>
#include <algorithm>
#include <dirent.h>
#include <string>


// Structure to store object annotations
struct Annotation {
    std::string label;
    float center_x;
    float center_y;
    float width;
    float height;
    int matched=0; //1已经匹配过 0未匹配
};

// Structure to store predicted detections
struct Detection {
    std::string label;
    float center_x;
    float center_y;
    float width;
    float height;
    float confidence;
    std::string filenameDet;
    //int tp=0; //1tp 0fp
};



// Function to calculate Intersection over Union (IoU)
float calculateIoU(const Annotation& annotation, const Detection& detection) {



    float x1 = std::max(annotation.center_x - annotation.width / 2, detection.center_x - detection.width / 2);
    float y1 = std::max(annotation.center_y - annotation.height / 2, detection.center_y - detection.height / 2);
    float x2 = std::min(annotation.center_x + annotation.width / 2, detection.center_x + detection.width / 2);
    float y2 = std::min(annotation.center_y + annotation.height / 2, detection.center_y + detection.height / 2);

    if (x1 >= x2 || y1 >= y2)
        return 0.0;

    float intersectionArea = (x2 - x1) * (y2 - y1);
    float annotationArea = annotation.width * annotation.height;
    float detectionArea = detection.width * detection.height;
    float unionArea = annotationArea + detectionArea - intersectionArea;

    return intersectionArea / unionArea;
}



// Function to calculate Average Precision (AP) using VOC 07 11-point method
//模板map映射文件名和预测信息结构体
float calculateAveragePrecision(std::map<std::string, std::vector<Annotation>>& annotations, 
const std::map<std::string, std::vector<Detection>>& detections,
const std::vector<Detection> GroupDetections) {
    
    //const float epsilon = std::numeric_limits<float>::epsilon();
    const float epsilon = 0.000001f;

    //根据单个类别gts 统计单个类别的npos (真实标注框数量)
    int npos =0;
    for (const auto& annotationPair1 : annotations) {
        const std::vector<Annotation>& annotationValues1 = annotationPair1.second;
        std::size_t count = annotationValues1.size();
        npos = npos + count;
    }

    
    std::vector<float> tp;
    std::vector<float> fp;
    
    //遍历所有当前类别检测结果dets 记录tp fp match   最终遍历全部该类别预测结果
    //遍历所有当前类别检测结果dets

    //单个类别detections结构（模板map）--<文件名><det信息>
    //待修改：detections 。 不用修改 annotations
    //在Detection结构体，加文件名filenameDet字段，进行标记查询文件名
    //重构
    //detections结构（模板map）--<文件名><det信息>


    //修改

        

    //置信度排序
    // Sort detections by confidence in descending order
    std::vector<Detection> sortedDetections = GroupDetections;
    std::sort(sortedDetections.begin(), sortedDetections.end(), [](const Detection& a, const Detection& b) {
        return a.confidence > b.confidence;
    });



    // 遍历sortedDetections，检查detection是否存在于annotations中
    // annotations单个类别的所有标注信息，从单个类别所有标注中，找出当前单张图片的检测det的文件名的det的信息

    

    //单个类别的预测dets的匹配统计情况，记录tp fp
    for (size_t i = 0; i < sortedDetections.size(); ++i) {
        const Detection& detection = sortedDetections[i];


        //修改
        const std::string& detectionKey2 = detection.filenameDet; //一个det的 文件名

        auto annotationItr = annotations.find(detectionKey2);  //找相同文件名的真实标注
        if (annotationItr != annotations.end()) {
            std::vector<Annotation>& annotationValues = annotationItr->second;  //该文件名的所有真实标注信息向量


        //修改

            int bestMatchIndex = -1;
            float bestIoU = 0.5;

            //遍历annotationValues的每一个与det进行计算
            for (size_t j = 0; j < annotationValues.size(); ++j) {
                if (annotationValues[j].matched)
                    continue;

                const Annotation& annotation = annotationValues[j];
                float iou = calculateIoU(annotation, detection);

                if (iou > bestIoU) {
                    bestIoU = iou;
                    bestMatchIndex = j;
                }
            }

            if (bestIoU >= 0.5) {
                if (annotationValues[bestMatchIndex].matched != 1) {
                    annotationValues[bestMatchIndex].matched = 1;
                    //sortedDetections[i].tp = 1.0;
                    tp.push_back(1.0);
                    fp.push_back(0.0);
                }
                else {
                    tp.push_back(0.0);
                    fp.push_back(1.0);
                }
            } 
            else {
                tp.push_back(0.0);
                fp.push_back(1.0);
            }

        }
    }





        
    

    //遍历所有当前类别检测结果dets。标记tp
    //标记完当前类别的所有tp fp match










    //缺陷。原版是做全体图片的预测的置信度下降，
    //本算法每次只是单张图片的所有预测的置信度下降，记录的tp可能有问题。

    //不需要统计预测dets的数量
    // Compute precision and recall

    //tp.size()是一个类别下所有图片的检测dets数量
    for (size_t i = 1; i < tp.size(); ++i) {
        tp[i] += tp[i - 1];
        fp[i] += fp[i - 1];
    }
    //tp[i]表示在前i个检测结果中的TP数量，fp[i]表示在前i个检测结果中的FP数量。


    std::vector<float> recall(tp.size()+2, 0.0);
    std::vector<float> precision(tp.size()+2, 0.0);

    // Append sentinel values to beginning and end
    //recall[0] = 0.0;
    //recall[-1] = 1.0;

    //precision[0] = 1.0;
    //precision[-1] = 0.0;

    //tp.size()是一个类别下所有图片的检测dets数量
    //每个det保存有一个召回率和一个精确率
    for (size_t i = 0; i < tp.size()+2; ++i) {
        if(i == 0){
            recall[i] = 0.0;
            precision[i] = 1.0;
            continue;
        }
        if(i == tp.size()+1){
            recall[i] = 1.0;
            precision[i] = 0.0;
            continue;
        }
        recall[i] = tp[i-1] / static_cast<float>(npos);
        precision[i] = tp[i-1] / std::max(tp[i-1] + fp[i-1], epsilon);

        //recall[i] = tp[i] / static_cast<float>(npos);
        //precision[i] = tp[i] / std::max(tp[i] + fp[i], epsilon);
    }

    
    //recall[i]表示在前i个检测结果中的召回率，precision[i]表示在前i个检测结果中的精确率。
    //为了得到精确率-召回率曲线，我们需要对检测结果按照置信度排序，并逐个增加检测结果（从高到低）来计算召回率和精确率。
    //逐个增加预测结果的过程会得到一系列不同的 (召回率, 精确率) 数据点。将这些数据点连线，即可得到精确率-召回率曲线。
    //这个曲线可以直观地展示模型在不同召回率水平下的精确率表现，帮助我们了解模型的性能优势和劣势。
    
    // Compute AP using VOC 07 11-point method
    float ap = 0.0;

    //float gap = 0.001;
    //float length = 1001.0;
    float gap = 0.01;
    float length = 101.0;


    for (float t = 0.0; t <= 1.0; t += gap) {
        int numPoints = 0;
        float maxPrecision = 0.0;

        //然后找出每个召回率点上的最大精确率
        //这是为了确保在不同召回率水平下都获得一个较为准确的精确率值，从而更全面地评估模型的性能。
        for (size_t i = 0; i < recall.size(); ++i) {
            if (recall[i] >= t) {
                numPoints++;
                maxPrecision = std::max(maxPrecision, precision[i]);
            }
        }

        ap += maxPrecision / length;

    }

    std::cout << "finish: " << std::endl;

    return ap;
}


std::map<std::string, std::vector<Annotation>> processDirectorygroundtruth(const std::string& directory) {
    DIR* dir;
    struct dirent* ent;
    std::map<std::string, std::vector<Annotation>> groundtruth;
    if ((dir = opendir(directory.c_str())) != nullptr) {
        
        while ((ent = readdir(dir)) != nullptr) {
            std::string filename(ent->d_name);
            std::vector<Annotation> annotations;
            
            //处理单个文件
            if (filename.length() >= 4 && filename.substr(filename.length() - 4) == ".txt") {
                std::string filepath = directory + "/" + filename;

                std::ifstream file(filepath);
                if (!file.is_open()) {
                    std::cerr << "Failed to open file: " << filename << std::endl;
                    return groundtruth;
                }
                //读取单个文件的每一行
                
                std::string line;
                while (std::getline(file, line)) {
                    Annotation annotation;
                    std::istringstream iss(line);
                    if (!(iss >> annotation.label >> annotation.center_x >> annotation.center_y >> annotation.width >> annotation.height)) {
                        std::cerr << "Error reading line: " << line << std::endl;
                        continue;
                    }
                    annotations.push_back(annotation);
                    

                    //std::cout << "Label: " << label << ", x: " << x << ", y: " << y << ", width: " << width << ", height: " << height << std::endl;
                }
                // Extract the image ID from the file name (assuming the file name format is "image_id.txt")
                
                std::string imageId = filename.substr(0, filename.length() - 4);  // Remove the ".txt" extension

                groundtruth[imageId] = annotations;

                file.close();
                
            }
        }
        closedir(dir);
        return groundtruth; 
    } 
    else {
        std::cerr << "Failed to open directory: " << directory << std::endl;
        return groundtruth;
    }
}

std::map<std::string, std::vector<Detection>> processDirectorydetections(const std::string& directory) {
    DIR* dir;
    struct dirent* ent;
    std::map<std::string, std::vector<Detection>> groundtruth;
    if ((dir = opendir(directory.c_str())) != nullptr) {
        
        while ((ent = readdir(dir)) != nullptr) {
            std::string filename(ent->d_name);
            std::vector<Detection> annotations;
            
            //处理单个文件
            if (filename.length() >= 4 && filename.substr(filename.length() - 4) == ".txt") {
                std::string filepath = directory + "/" + filename;

                std::ifstream file(filepath);
                if (!file.is_open()) {
                    std::cerr << "Failed to open file: " << filename << std::endl;
                    return groundtruth;
                }
                //读取单个文件的每一行
                
                std::string line;
                while (std::getline(file, line)) {
                    Detection annotation;
                    
                    std::istringstream iss(line);
                    if (!(iss >> annotation.label >> annotation.center_x >> annotation.center_y 
                    >> annotation.width >> annotation.height >> annotation.confidence)) {
                        std::cerr << "Error reading line: " << line << std::endl;
                        continue;
                    }


                    //将生成的数据通知处理成yolo格式
                    //float a = annotation.center_x + annotation.width/2.0;
                    //float b = annotation.center_y + annotation.height/2.0;
                    //annotation.center_x = a / 1920.0;
                    //annotation.center_y = b / 1080.0;
                    //annotation.width = annotation.width/1920.0;
                    //annotation.height = annotation.height/1080.0;

                    annotations.push_back(annotation);
                    

                    //std::cout << "Label: " << label << ", x: " << x << ", y: " << y << ", width: " << width << ", height: " << height << std::endl;
                }
                // Extract the image ID from the file name (assuming the file name format is "image_id.txt")
                
                std::string imageId = filename.substr(0, filename.length() - 4);  // Remove the ".txt" extension

                groundtruth[imageId] = annotations;

                file.close();
                
            }
        }
        closedir(dir);
        return groundtruth;
        
    } 
    else {
        std::cerr << "Failed to open directory: " << directory << std::endl;
        return groundtruth;
    }
}



int main() {
    // Read groundtruth and detections from files
    std::map<std::string, std::vector<Annotation>> groundtruth;
    std::map<std::string, std::vector<Detection>> detections;

    // Load groundtruth annotations
    std::string groundtruthFolderPath = "/home/nvidia/Downloads/helmet-test/val_images/remake-image-label4-blank/labelsnew/";
    std::string detectionsFolderPath = "/home/nvidia/luDevelop-trans2wts-cfg/yolov5/runs/detect/exp31/labels/";
    //std::string detectionsFolderPath = "/home/nvidia/4lujunda-firstchange-mychange/newseawaystream626/SeawayStream/pre/";
    
    // Iterate over each groundtruth file
    std::vector<Annotation> annotations;
    groundtruth=processDirectorygroundtruth(groundtruthFolderPath);

    // Load predicted detections
    std::map<std::string, std::vector<Detection>> predictions;
    predictions=processDirectorydetections(detectionsFolderPath);
    

    // Calculate mAP for each class
    std::map<std::string, float> apScores;

    //new change
    //嵌套映射分配不同class  创建class_groundtruth

    std::map<std::string, std::map<std::string, std::vector<Annotation>>> class_groundtruth;
    // 遍历原始映射 groundtruth
    for (const auto& entry : groundtruth) {
        const std::string& imageId = entry.first;
        const std::vector<Annotation>& annotations = entry.second;

        // 遍历当前 imageId 下的 annotations
        for (const Annotation& annotation : annotations) {
            const std::string& label = annotation.label;

            // 检查 class_groundtruth 中是否已经有对应 label 的映射
            auto it = class_groundtruth.find(label);
            if (it != class_groundtruth.end()) {
                // 若已存在，则将当前 imageId 下的 annotations 添加到对应的映射中
                it->second[imageId].push_back(annotation);
            } 
            else {
                // 若不存在，则创建一个新的映射，并添加当前 imageId 下的 annotations
                std::map<std::string, std::vector<Annotation>> newMap;
                newMap[imageId].push_back(annotation);
                class_groundtruth[label] = newMap;
            }
        }
    }

    //创建class_detections
    std::map<std::string, std::map<std::string, std::vector<Detection>>> class_detections;
    // 遍历原始映射 predictions
    for (const auto& entry : predictions) {
        const std::string& imageId = entry.first;
        const std::vector<Detection>& annotations = entry.second;

        // 遍历当前 imageId 下的 annotations
        for (const Detection& annotation : annotations) {
            const std::string& label = annotation.label;

            // 检查 class_detections 中是否已经有对应 label 的映射
            auto it = class_detections.find(label);
            if (it != class_detections.end()) {
                // 若已存在，则将当前 imageId 下的 annotations 添加到对应的映射中
                it->second[imageId].push_back(annotation);
            } else {
                // 若不存在，则创建一个新的映射，并添加当前 imageId 下的 annotations
                std::map<std::string, std::vector<Detection>> newMap;
                newMap[imageId].push_back(annotation);
                class_detections[label] = newMap;
            }
        }
    }



    //new change


    //遍历每一个类别，分别计算AP
    for (auto& classEntry : class_groundtruth) {
        const std::string& className = classEntry.first;
        std::map<std::string, std::vector<Annotation>>& classAnnotations = classEntry.second;
        std::map<std::string, std::vector<Detection>>& classDetections = class_detections[className];


        std::vector<Detection> GroupDetections;
        for (auto& detectionPair : classDetections) {
            const std::string& detectionKey = detectionPair.first; //一个image之下的 文件名

            std::vector<Detection>& detectionValues = detectionPair.second; //该向量指向多个Detection
            //一个image之下的排序
            // Sort detections by confidence in descending order
            std::vector<Detection> sortedDetections = detectionValues;
            std::sort(sortedDetections.begin(), sortedDetections.end(), [](const Detection& a, const Detection& b) {
                return a.confidence > b.confidence;
            });

            for (size_t i = 0; i < sortedDetections.size(); ++i) {
                Detection& detection = sortedDetections[i];
                detection.filenameDet=detectionKey;
                //detectionKey >> detection.filenameDet;

                GroupDetections.push_back(detection);
            }
        }


        float ap = calculateAveragePrecision(classAnnotations, classDetections,GroupDetections);
        apScores[className] = ap;
    }

    // Calculate mean Average Precision (mAP)
    float meanAP = 0.0;

    for (const auto& apEntry : apScores) {
        meanAP += apEntry.second;
    }

    meanAP /= apScores.size();

    // Print class-wise AP and mAP
    for (const auto& apEntry : apScores) {
        std::cout << "Class: " << apEntry.first << ", AP: " << apEntry.second << std::endl;
    }

    std::cout << "mAP: " << meanAP << std::endl;

    return 0;
}
