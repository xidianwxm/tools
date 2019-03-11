#coding:utf-8

import multiprocessing
import logging
import sys
import os
from collections import OrderedDict
import time

from parseBPLog import BPLog


# python2里面默认编码为ASCII，对于中文脚本需要重新编码，否则解析出错
reload(sys)
sys.setdefaultencoding('utf-8')

# 引用logging日志模块，按照格式记录日志
logging.basicConfig(level = logging.INFO,format = '%(asctime)s %(pathname)s %(filename)s %(funcName)s %(lineno)s %(levelname)s - %(message)s' )
logger = logging.getLogger(__name__)




def parseFunc(logFileFullPath):
    '''
    功能：多进程函数；
          构造BPLog实例，处理BP日志
    版本: V1.0
    修改日期: 20190223 08:58
    修改原因:
    修改人: xmwan
    备注: 初始实现
    参数：
    param: fileFullPath
    ret:   None
    '''

    # 初始化BPLog类
    bpLoger = BPLog(logFileFullPath)
    logger.info("fileFullPath:%s" % bpLoger.fileFullPath)
    # 调用BPLog类中日志解析函数
    bpLoger.read2ThreadLog()
    writeFileName = os.path.splitext(bpLoger.fileFullPath)[0]
    writeFileName = writeFileName + ".parsed"
    logger.info("writeFileName:%s" % writeFileName)
    # 调用BPLog类中解析文件生成函数
    bpLoger.writeLog(writeFileName)
    time.sleep(3)

if __name__ == '__main__':
    '''
    需要传递1个文件夹的参数，可以解析该文件夹以及所有子目录下所有*.log的日志
    '''
    if len(sys.argv) != 2:
        print("ParamError: \nExample:\n python cpuTask.py $fileDirFullPath" )
        exit(-1)
    else:
        # 获取解析机器的cpu核数，设置进程池Pool大小
        bpLogList = []
        cpuCount = multiprocessing.cpu_count()
        logger.info("cpucount: %d" % (cpuCount))
        pool = multiprocessing.Pool(processes=cpuCount)
        # 获取所有的子目录
        fileFullDirPath = sys.argv[1]
        logger.info("readFileDirPath:%s" % fileFullDirPath)
        listDir = [dirs[0] for dirs in os.walk(fileFullDirPath)][1:]  # 获取所有的子目录
        listDir.append(fileFullDirPath)
        logger.info("listDir:%s" % listDir)
        for dataDir in listDir:
            logger.info("dataDir:%s" % dataDir)
            # 获取绝对路径
            files = [os.path.join(dataDir, i) for i in os.listdir(dataDir)]  # 获取绝对路径
            logger.info("files:%s" % files)
            # 过滤bp日志文件，加入到解析列表中
            for fileName in files:
                pos, filename = os.path.split(fileName)
                if filename[-4:] == ".log":
                    logFileFullPath = os.path.join(dataDir, fileName)
                    bpLogList.append(logFileFullPath)
        logger.info("bpLogList: %s" % (bpLogList))

        # 根据进程池Pool创建多个子进程任务，调用BPLog解析功能
        for i in range(len(bpLogList)):
            # 维持执行的进程总数为processes，当一个进程执行完毕后会添加新的进程进去
            pool.apply_async(parseFunc, (bpLogList[i],))

        pool.close()
        # 调用join之前，先调用close函数，否则会出错。执行完close后不会有新的进程加入到pool,join函数等待所有子进程结束
        pool.join()
        print "Sub-process(es) done."

