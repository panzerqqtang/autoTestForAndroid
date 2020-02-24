import subprocess
import os
import value
import time
import re
import random
from feature_match import getallscenes, judgeScene, getpoints
from value import eventpoint
#######在运行feature_process之后才能拥有场景特征#######
#1 每隔5秒对屏幕进行截屏
#2 判断当前场景
#3 根据场景进行操作

#战斗开始时间
battle_start_time = 0.0
#单次战斗时间
battle_time = 50.0
#战斗次数
battle_count = 0
#last sence
last_scene = "start"
def adb_shell():
    """
    启动adb shell  **前提** adb 在C:\\Users\\root目录下
    """
    os.chdir(value.getADBPath())
    obj = subprocess.Popen(['adb','shell'], shell = True, stdin=subprocess.PIPE, stdout=subprocess.PIPE ,stderr=subprocess.PIPE)
    obj.stdin.write('adb shell\n'.encode('utf-8'))
    #obj.stdin.write('ls\n'.encode('utf-8'))
    obj.stdin.write('exit\n'.encode('utf-8'))  #重点，一定要执行exit
    info, err = obj.communicate()
    #print(info,err)
    print(info.decode('utf-8')[:-4])
    print(err.decode('utf-8')[:-4])
screencap_thread = None
def screencap():
    """
    捕获一张手机截屏到主目录
    """
    starttime = time.time()
    filename = os.path.join(value.getHomePath(),'screen.png')
    os.chdir(value.getADBPath())
    obj = subprocess.Popen(['adb','exec-out','screencap','-p','>', filename], shell = True, stdin=subprocess.PIPE, stdout=subprocess.PIPE ,stderr=subprocess.PIPE)
    info, err = obj.communicate()
    #print(info.decode('utf-8')[:-4])
    print("截图用时%f秒" % (time.time()-starttime))
    if(len(err)==0):
        return True
    else:
        print(err.decode('utf-8')[:-4])
        return False
    
    #adb exec-out screencap -p > test.png
capable = True
screencap_thread = None

def RGBA_int(colorstr):
    R,G,B,A = colorstr.split(' ')
    R = int(R,16)
    G = int(G,16)
    B = int(B,16)
    #A = int(A,16)
    return R,G,B #,A
def screencap_data():
    # 捕获png数据太耗费时间 这里选择dump数据
    cmd = 'adb shell screencap /mnt/sdcard/0/screen.dump'
    
    obj = subprocess.Popen(cmd, shell = True, stdin=subprocess.PIPE, stdout=subprocess.PIPE ,stderr=subprocess.PIPE)
    #obj.stdin.write('add linux shell code'.encode('utf-8'))
    info, err = obj.communicate()
    #print(info.decode('utf-8'))
    if err:
        print(err.decode('utf-8'))
def getRGB(points):
    """
    直接从手机中dd出来数据
    #1 dump数据
    screencap /mnt/sdcard/0/screen.dump
    #2 根据屏幕的大小来计算颜色值所在的位置 （1920*1200）
    position = 1920*y + x + 3
    #3 dd出数据
    dd if=/mnt/sdcard/0/screen.dump bs=4 count=1 skip=position 2>/dev/null | hd
    """ 
    points_number = len(points)
    #以下都将在手机上运行
    #位置全都转换一下
    os.chdir(value.getADBPath())
    #我的屏幕是1920 * 1080
    #横屏 则 *1920 纵屏则 *1080
    positions = [point[0] + point[1] * 1920 + 3 for point in points]
    #position = 1920*y+x+3
    cmds = [
        #"screencap /mnt/sdcard/0/screen.dump",
        #截屏会堵塞命令  改为单独拿出处理
    ]
    for position in positions:
        cmds.append("dd if=/mnt/sdcard/0/screen.dump bs=4 count=1 skip=" + str(position) + " 2>/dev/null | hd")
    cmds.append("exit")
    pipe = subprocess.Popen("adb shell", shell = True, stdin=subprocess.PIPE, stdout=subprocess.PIPE ,stderr=subprocess.PIPE)
    info, err= pipe.communicate(('\n'.join(cmds) + "\n").encode('gbk'))
    #str_value = info.decode('gbk','ignore')
    str_value = str(info)
    #print(str_value)
    pattern = re.compile(r'\w\w \w\w \w\w FF')
    color_str_list = pattern.findall(str_value)
    if(points_number != len(color_str_list)):
        print("本次查询失败-正在重新查询：",points)
        return getRGB(points)
    #print(color_str_list)
    #print("匹配到的颜色值有%d个。" % (len(color_str_list)))
    colorFeatures = {}
    i = 0
    for colorstr in color_str_list:
        colorFeatures[points[i]] = RGBA_int(colorstr)
        i+=1
    #print("color_list",colorFeatures)
    
    return colorFeatures
def clickPoint(point):
    #随机偏移点击位置  逃避检测
    point = (point[0]+random.randint(-2,2),point[1]+random.randint(-2,2))
    cmd = 'adb shell input tap ' + str(point[0]) + " " + str(point[1])
    
    obj = subprocess.Popen(cmd, shell = True, stdin=subprocess.PIPE, stdout=subprocess.PIPE ,stderr=subprocess.PIPE)
    #obj.stdin.write('add linux shell code'.encode('utf-8'))
    info, err = obj.communicate()
    #print(info.decode('utf-8'))
    if err:
        print(err.decode('utf-8'))
def battle_end():
    global battle_time,battle_count
    if battle_start_time==0:
        return
    #每次检测到战斗结束 触发本次事件
    temptime = time.time() - battle_start_time
    print("-------------分割线-------------")
    print("战斗结束, 本次战斗花费了%f秒的时间。" % (temptime) )
    
    #战斗时间取均值
    if battle_count==0:
        #如果等待时间过长  没能收集到单次战斗时间
        if(temptime - battle_time <5):
            battle_time /= 2 
        else:
            battle_time = temptime
    else:
        battle_time += (temptime-battle_time - 5)/2
    battle_count += 1
    print("将执行第%d次战斗------下次战斗预计所需%f秒，将等待%d秒后检测。" % (battle_count,battle_time,battle_time-5))
def battle_start():
    global battle_start_time,battle_time
    battle_start_time = time.time()
    time.sleep(int(battle_time))
def runActivate(scene, clicklist):
    #global battle_start_time, battle_time
    global last_scene
    
    if scene == None:
        return
    if scene == "battle":
        #print(last_scene)
        if last_scene =="win" or last_scene == "restart" or last_scene == "start":
            battle_start()
    if scene == "start":
        #一次战斗开始
        clickPoint(clicklist["start"])
        #将进行等待战斗白热化
        #battle_start()
    if scene == "battle_no_auto":
        clickPoint(clicklist["auto"])
        battle_start()
    if scene == "restart":
        #战斗开始
        clickPoint(clicklist["restart"])
        #battle_start()
    if scene == "revival":
        clickPoint(clicklist['notrevival'])
    if scene == "reward_3_white":
        clickPoint(clicklist['sell'])
    if scene == "win":
        #2.0 基本只要这里更改了 检测到胜利则脚本一条龙操作 
        #战斗结束时，统计结束的时间
        battle_end()
        clickPoint((1600,570))
        time.sleep(1)
        clickPoint((1600,570))
        time.sleep(2.5)
        clickPoint(clicklist['close'])
        time.sleep(1)
        clickPoint(clicklist["restart"])
        time.sleep(1.5)
        clickPoint(clicklist["start"])
        #加载时间 加载界面
        time.sleep(10)
    if scene == "reward":
        clickPoint(clicklist['close'])
        #clickPoint(clicklist['sell'])
    if scene == "confirm_sell":
        clickPoint(clicklist['confirm_sell'])
    if scene == "die":
        #只统计时间 基本不占用时间
        battle_end()
        clickPoint((1600,570))
    if scene == "energy":
        clickPoint(clicklist["shop"]) 
        time.sleep(1.5)
        clickPoint(clicklist["energy"]) 
        time.sleep(1.5)
        clickPoint(clicklist["shop_ok"]) 
        time.sleep(1.5)
        clickPoint(clicklist["shop_ok_ok"]) 
        time.sleep(1.5)
        clickPoint(clicklist["shop_close"]) 
        
    #最后 保存上次操作的位置  None 将被忽略
    last_scene = scene
    
if __name__ == "__main__":    
    """
    测试部分
    """
    
    
    #1 获取固定的信息
    #获取点击位置列表
    clicklist = eventpoint()
    #获取特征
    scenes_features = getallscenes()
    #判断当前场景
    
    
    #2 获取点位
    points = getpoints(scenes_features)
    print("共有%d个点需要匹配。" % (len(points)))
    print("获取点位成功")
    
    
    
    battle_time = 15.0
    #战斗是否等待  检测到开始后 开始计数
    
    #刷多少次图次数
    run_number = 40
    while battle_count < run_number :
        # 计算单次循环所需时间
        #start_time = time.time()
        #print("当前执行位置：%d次" % (i))
        #3 获取所有需要的的颜色值
        screencap_data()
        scenes_img = {}
        for i in range(int(len(points)/10)+1):
            low = i*10
            high = (i+1)*10
            if(high > len(points)):
                high = len(points)
            if(low == high):
                break
            scenes_split = getRGB(points[low:high])
            scenes_img = {**scenes_img,**scenes_split}
        
        #scenes_img = getRGB(points)
        #print(scenes_img)
        print("获取所需要的颜色值成功")
        #4 匹配判断
        scene = judgeScene(scenes_features, scenes_img)
        print("当前场景被识别为：" , scene )

        #5 根据场景执行操作
        runActivate(scene, clicklist)
        print("执行场景成功")
        
        #6 统计单次操作时间
        #cost_time = time.time() - start_time
        
        #print("单次循环执行过程花费%f秒" % cost_time)
        
        #7 等待
        time.sleep(5)