import os
import pickle
import random
import copy
from value import getSummonersWarScenesName
from PIL import Image

"""
本脚本的作用是对图片进行特征提取，提取后的特征将用于判断图片所在的场景

1. 以文件夹为一种类别
2. 对所有的图片进行分类
3. 计算出每种类别图的特征值
4. 随机对特征值进行删减
"""

def screencap():
    """
    通过adb截图到本地
    """
    # adb exec-out screencap -p > test.png
    pass
def dealpng(fileList):
    """
    截屏代码
    对比两张图片的特征值
    找同类图的相同点 
    找不同图的不同点
    """
    #img list 
    if(len(fileList)<2):
        print("Error, compare at least two picture.")
        return None
    img_list = [[] for i in range(len(fileList))]
    count = 0
    size = (0,0)
    for filename in fileList:
        #默认RGBA
        img = Image.open(filename).convert('RGB')
        #将图片序列读入一个列表中
        img_list[count] = img.load()
        if(size == (0,0)):
            size =img.size
        else:
            if(size != img.size):
                print("Error, gived picture size not same.")
                return None
        #print(img_list[count][(1,1)])
        img.close()
        count+=1
    #print("读入图片列表完成\n---共%d张图片" % (count))
    #print("---图片大小统一为：",size)
    #print("--------------read end---------------")
    
    feature_data = {}
    skip_px_x = 10 #
    skip_px_y = 10 # 10*10网格化搜索
    for pic_x_i in range(int(size[0]/skip_px_x)):
        for pic_y_i in range(int(size[1]/skip_px_y)):
            #真实化坐标
            pic_x = pic_x_i * skip_px_x
            pic_y = pic_y_i * skip_px_y

            if(img_list[0][pic_x,pic_y] == img_list[1][pic_x,pic_y]):
                feature_data[(pic_x,pic_y)] = img_list[0][pic_x,pic_y]
                #print("在坐标(%d,%d)处完成匹配：" % (pic_x,pic_y),img_list[0][pic_x,pic_y])
                pass

    #print("首次计算中相同特征共有%d个." % len(feature_data))
    for img in img_list[2:]:
        keys = list(feature_data.keys())
        for point in keys:
            if(img[point] != feature_data[point]):
                feature_data.pop(point)
            pass
    #print("最终计算得出的共同特征有%d个" % (len(feature_data.keys())))

    return(feature_data)
def saveValue(filename, value):
    """
    保存变量到文件中
    """
    with open(filename, 'wb') as f:
        pickle.dump(value,f)
    return True
def readValue(filename):
    """
    读文件到变量中
    """
    read_data = None
    with open(filename, 'rb') as f:
        read_data = pickle.load(f)
    return read_data
def getFeature(dirname,save = False):
    pic_dir = os.path.join("png_data", dirname)
    fileList = [ os.path.join(pic_dir ,name) for name in os.listdir(pic_dir) if name[-3:]=="png"]
    #print(fileList)
    feature_data = dealpng(fileList)
    if save:
        saveValue(dirname+".features", feature_data)
    return feature_data
def delFeature(features1, features2):
    """
    删除两组特征中相同的部分
    return will deleted
    """
    deleted = []
    keys1 = list(features1.keys())
    keys2 = list(features2.keys())
    #print("删除之前  die的特征数量%d，win的特征数量%d" % (len(keys1),len(keys2)))
    delnum = 0
    for point in keys1:
        if point in keys2:
            delnum+=1
            if features1[point] == features2[point]:
                deleted.append(point)
                #features1.pop(point)
                #features2.pop(point)
    #print("删除之后  die的特征数量%d，win的特征数量%d" % (len(features1),len(features2)))
    return deleted
def RandomlyDeleteFeatures(features,max_len = 2):
    """
    随机保留特征值到 max_len个
    return 特征字典
    """
    new_features = {}
    keys = list(features.keys())
    key_max_position = len(keys)
    print(key_max_position)
    if(max_len >= key_max_position):
        #如果要保留的特征数大于 当前特征 则全部返回
        return features 
    for i in range(max_len):
        random_position = random.randint(i, key_max_position-1)
        #print("在取第%d个随机数，最大值是%d，取到的随机数是%d，取到的位置是："% (i,key_max_position,random_position))
        #随机抽取特征 然后从前面拿一个替换掉被抽取的  取随机位置+1
        new_features[keys[random_position]] = features[keys[random_position]]
        keys[random_position] = keys[i]
    return new_features
if __name__ == "__main__":
    
    #计算出所有图片的特征 ---同类图片中的相同点---
    features = {}
    scenesList = getSummonersWarScenesName()
    for dirname in scenesList:
        features[dirname] = getFeature(dirname)
        print("%s 的特征值数量为%d个" % (dirname, len(features[dirname])))
    #不同类图片 交叉验证 删除掉无效特征 指重复的部分 ---不同类图片中的相同点---
    
    #delFeature(features['die'],features['win'])
    #exit()
    #i = 1
    """
    换了个蠢得算法 虽然慢 但是简单
    有空再想吧
    """
    """
    no_need_similar_test_list = ["start"]
    #start 和其他很不一样 不需要相似检测
    copy_list = scenesList.copy()
    for name in no_need_similar_test_list:
    similar_test_list = copy_list.remove(name)
    一大堆 还不如重新定义一个
    """
    similar_test_list = ["battle", "battle_no_auto", "win", 'reward', "revival", "die", "restart","confirm_sell"]
    will_deled = {name:[] for name in scenesList} 
    for test_name in similar_test_list:
       for other_name in similar_test_list:
            if(test_name==other_name):
               continue
            delspilt = delFeature(features[test_name],features[other_name])
            will_deled[test_name] += delspilt

    """
    i = 1
    while i < len(scenesList):
       for n in range(len(scenesList)-i):
           print("%d -- %d",(i-1,i+n))
           print([len(scene) for scene in features.values()])
           delspilt = delFeature(features[scenesList[i-1]],features[scenesList[i+n]])
           will_deled[scenesList[i-1]] += delspilt
           will_deled[scenesList[i+n]] += delspilt
       i+=1
    
    """
    for name in scenesList:
        will_deled[name] = {}.fromkeys(will_deled[name]).keys()
        for point in will_deled[name]:
            #print(will_deled[name])
            #print(features[name],name)
            #if(point in )
            features[name].pop(point)    
    
    #最后对剩余的有效特征进行随机筛选 ---随机删除 减少特征体积---
    print("净化后的特征数量:")
    for dirname in scenesList:
        print("%s 的特征值数量为%d个" % (dirname, len(features[dirname])))
        #pic_dir = os.path.join("png_data", dirname)
        rdf = RandomlyDeleteFeatures(features[dirname])
        print("%s在随机删减后的特征：" % (dirname))
        print(rdf)
        saveValue(dirname+".features",rdf)