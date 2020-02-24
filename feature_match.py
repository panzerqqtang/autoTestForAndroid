from value import getSummonersWarScenesName
import pickle
import random
import time
from PIL import Image
"""
本脚本的作用是进行特征匹配 找出图片所在的类别
"""
def getpngdata(filename):
    """
    读取图片的数据
    """
    img = Image.open(filename).convert('RGB')
    return img.load()
def getallscenes():
    """
    读取所有特征文件的数据
    """
    scenes_features = {} 
    for name in getSummonersWarScenesName():
        scenes_features[name] = getclassdata(name)
    return scenes_features
def getclassdata(classname):
    """
    读取特征文件的数据
    """
    filename = classname + ".features"
    read_data = None
    with open(filename, 'rb') as f:
        read_data = pickle.load(f)
    return read_data
def feature_match(imageD, classD):
    """
    imageD : png像素数据  
    classD : 判断是否为classname描述的种类
    返回 匹配程度值
    """
    #特征数量
    featuresNumber = len(classD.keys())
    matchedNumber = 0
    for point in classD.keys():
        if imageD[point] == classD[point]:
            matchedNumber += 1
    match_rate = float(matchedNumber)/float(featuresNumber)
    return match_rate
def getpoints(scenes_features):
    """
    从所有的特征中提取出所有要匹配的点
    """
    points = []
    for scenesname in getSummonersWarScenesName():
        for point in scenes_features[scenesname]:
            if not(point in points):
                points.append(point)
    return points
def judgeScene(scenes_features, picdata, match_lowest = 0.6):
    """
        返回最有可能的场景
        都不是将返回None
        match_lowest 匹配程度要求 0~1
    """
    match_name =  ""
    max_match = 0.0
    for scenename in getSummonersWarScenesName():
        match_rate = feature_match(picdata,scenes_features[scenename])
        #print("场景为%s的概率为%f" % (scenename,match_rate))
        if match_rate > max_match:
            match_name = scenename
            max_match = match_rate
    if max_match > match_lowest:
        return match_name
    else:
        return None

if __name__ == "__main__":
    #starttime = time.time()
    #特征数据
    #scenes_features = getallscenes()
    
    #print (getpoints(scenes_features))
    #图片数据
    #picdata = getpngdata("./png_data/test.png")

    #print("读取所有数据特征完毕：\n---用时%f秒" % ((time.time()-starttime)))
    
    #print("通过函数验证的到的结果为：", judgeScene(scenes_features,picdata))
    
    #print("验证所有特征完毕：\n---用时%f秒" % ((time.time()-starttime)))
    pass