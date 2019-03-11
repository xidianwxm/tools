# coding=utf-8


import os
import logging
from collections import OrderedDict
import re
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


#logging.basicConfig(level = logging.DEBUG,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#logger = logging.getLogger(__name__)

logging.basicConfig(level = logging.INFO,format = '%(asctime)s %(pathname)s %(filename)s %(funcName)s %(lineno)s %(levelname)s - %(message)s' )
logger = logging.getLogger(__name__)

#logger = logging.getLogger()
#logger.setLevel(logging.DEBUG)

#rht = logging.handlers.TimedRotatingFileHandler("app.log", 'D')
#fmt = logging.Formatter("%(asctime)s %(pathname)s %(filename)s %(funcName)s %(lineno)s \
#      %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S")
#rht.setFormatter(fmt)
#logger.addHandler(rht)

reqLogLevel = "99"
# runlog.log中标记请求日志的列数
logLevelPos = 46
# runlog.log中标记请求日志级别
logLevelLength = 2

timeSeqPos = 1
timeSeqLength = 15

seqIdPos = 18
seqIdLength = 12

threadIdPos = 32
threadIdLength = 9

reqDataPos = 50




logOrderdict = []
threadOrderddict = OrderedDict()

def judgeQuote(str):
    if "'" in str:
        return False
    else:
        return True


def msgidFilter(str):
    if "msgid" in str:
        return False
    else:
        return True


def MsgIdFilter(str):
    if "MsgId:" in str:
        return False
    else:
        return True


def gzdmFilter(str):
    if "gzdm:" in str:
        return False
    else:
        return True

def xmlFilter(str):
    if "?xml" in str:
        return False
    else:
        return True


def printList(str):
    '''

    ret:
    '''
    logger.debug("%s" % str,)

def read2ThreadLog(fileFullPath):
    '''
    功能：读取原生kcbp日志到不同线程日志文件中
    参数：
    param：fileFullPath
    ret:none
    '''
    logger.debug("Func fileFullPath:%s" % fileFullPath, )

    logLevelPosBeg = logLevelPos
    logLevelPosEnd = logLevelPos + logLevelLength

    seqIdPosBegin = seqIdPos
    seqIdPosEnd = seqIdPos  + seqIdLength

    timeSeqPosBegin = timeSeqPos
    timeSeqPosEnd = timeSeqPos + timeSeqLength

    threadIdPosBegin = threadIdPos
    threadIdPosEnd = threadIdPos + threadIdLength

    with open(fileFullPath, 'r') as file:
        logData = file.readlines()
        logger.debug("logData type: %s",type(logData))
        filterLogData = list(filter(lambda x: x[logLevelPosBeg:logLevelPosEnd]  == reqLogLevel, logData))
        logger.debug("filterLogData type: %s", type(filterLogData))
        logger.debug("filterLogData content: %s", map(printList,filterLogData))

    reqData = u""
    count = 0
    for lineStr in filterLogData:
        timeSeq = lineStr[timeSeqPosBegin:timeSeqPosEnd].strip()
        seqId = lineStr[seqIdPosBegin:seqIdPosEnd].strip().replace('-', '')
        threadId = lineStr[threadIdPosBegin:threadIdPosEnd].strip().replace(' ', '_').replace('-', '_')
        count = count + 1
        try:
            reqData = lineStr[reqDataPos:].replace('\n', '').decode('gb2312').encode('utf-8')
            # logger.info("%s, %s, %s, %s", timeSeq, seqId, threadId, reqData)
        except:
            print "error!, count:%d" % (count, )


        if threadId not in threadOrderddict.keys():
            t3OD = OrderedDict()
            t2OD = OrderedDict()
            t3OD[timeSeq] = reqData
            t2OD[seqId] = t3OD
            threadOrderddict[threadId] = t2OD
        else:
            if seqId not in threadOrderddict[threadId].keys():
                #threadInnerDict = threadOrderddict[threadId]
                #t3OD = OrderedDict()
                t3OD = OrderedDict()
                t3OD[timeSeq] = reqData
                threadOrderddict[threadId][seqId] = t3OD
                #threadOrderddict[threadId][seqId] = threadOrderddict[threadId][seqId][timeSeq] + reqData
            else:
                if timeSeq not in threadOrderddict[threadId][seqId].keys():
                    threadOrderddict[threadId][seqId][timeSeq] = reqData
                else:
                    tmpStr = threadOrderddict[threadId][seqId][timeSeq]
                    threadOrderddict[threadId][seqId][timeSeq] = tmpStr + reqData
                    logger.debug("%s, %s, %s, %s", timeSeq, seqId, threadId, threadOrderddict[threadId][seqId][timeSeq])

    logger.debug("\n------------threadOrderddict:\n%s\n", threadOrderddict)

def writeLog(writeFileName, threadOrderddict):
    '''
    :return:
    '''
    logger.debug("writelog...bein...\n")

    with open(writeFileName, 'w') as file:
        for threadId in threadOrderddict.keys():
            logger.debug("threadId:%s\n", threadId)
            seqInnerDict = threadOrderddict[threadId]
            for seqId in seqInnerDict.keys():
                timeSeqInnerDict = seqInnerDict[seqId]
                for timeSeq in timeSeqInnerDict.keys():
                    logger.debug("%s, %s, %s, %s\n" % (timeSeq, seqId, threadId, timeSeqInnerDict[timeSeq]))
                    tmpStr = dealReqData(timeSeqInnerDict[timeSeq])
                    logger.debug("dealReqData: %s\n" % (tmpStr,))
                    timeSeqInnerDict[timeSeq] = tmpStr
                    #logger.info("%s, %s, %s, %s\n" % (timeSeq, seqId, threadId, timeSeqInnerDict[timeSeq].decode('gbk')))
                    if "'" not in timeSeqInnerDict[timeSeq] and \
                        "MsgId:" not in timeSeqInnerDict[timeSeq] and \
                        "gzdm:" not in timeSeqInnerDict[timeSeq] and \
                        "?xml" not in timeSeqInnerDict[timeSeq] :
                        #print "%s %s %s %s\n" % (timeSeq, seqId, threadId,timeSeqInnerDict[timeSeq])
                        file.write("%s %s %s %s\n" % (timeSeq, seqId, threadId,timeSeqInnerDict[timeSeq].decode('utf-8').encode('gb2312')))

def dealReqData(lineStr):
    #切除请求报文前Req字符串
    #sed  "s/Req:.\{0,209\}\?_CA=2..\(&_ENDIAN=.\)\?&//g" 1.txt
    cutHeadPattern = re.compile(r'Req:.{0,209}?_CA=2..(&_ENDIAN=.)?&')
    retStr = cutHeadPattern.sub("", lineStr)

    cutsepPattern1 = re.compile(r'&')
    retStr = cutsepPattern1.sub(",", retStr)

    cutsepPattern2 = re.compile(r'=')
    retStr = cutsepPattern2.sub(":", retStr)

    #替换秘钥
    #sed "s/trdpwd:.\{6,20\}\?,/trdpwd:+0K8mU%),/g"
    #sed "s/g_operpwd:.\{6,35\}\?,/g_operpwd:k$sdn6}Q,/g"
    #sed "s/g_operid:8888,g_operpwd:k$sdn6}Q,/g_operid:8888,g_operpwd:DB8C15E5B8806B3BBD9AB9C444021DAC,/g"
    cuttrdpwdPattern = re.compile(r'trdpwd:.{6,20}?,')
    retStr = cuttrdpwdPattern.sub("trdpwd:+0K8mU%),", retStr)

    #cuttrdpwdPattern1 = re.compile(r'trdpwd:.{6,20}?$')
    #retStr = cuttrdpwdPattern1.sub("trdpwd:+0K8mU%),$", retStr)

    cutg_operpwdPattern = re.compile(r'g_operpwd:.{6,35}?,')
    retStr = cutg_operpwdPattern.sub("g_operpwd:k$sdn6}Q,", retStr)

    cutg_operid8888Pattern = re.compile(r'g_operid:8888,g_operpwd:k$sdn6}Q,')
    retStr = cutg_operid8888Pattern.sub("g_operid:8888,g_operpwd:DB8C15E5B8806B3BBD9AB9C444021DAC,", retStr)

    namePattern = re.compile(r',name:.{1,4}?,')
    retStr = namePattern.sub(",name:测试姓名,", retStr)

    fullNamePattern = re.compile(r',fullname:.{1,4}?,')
    retStr = fullNamePattern.sub(",fullname:测试姓名,", retStr)

    fullNamePattern = re.compile(r',fullname:.{1,4}?,')
    retStr = fullNamePattern.sub(",fullname:测试姓名,", retStr)

    addrPattern = re.compile(r',addr:.{1,64}?,')
    retStr = fullNamePattern.sub(",addr:快递地址laianlu685,", retStr)

    return retStr


if __name__ == '__main__':
    fileName = 'runlog0.log'
    dirName = r'E:\prod\1224'
    #fileFullPath = dirName + fileName

    if len(sys.argv) != 2:
        print("ParamError: \nExample:\n python readThreadLog.py $fileDirFullPath" )
        exit(-1)
    else:
        #fileFullPath = os.path.join(dirName, fileName)
        fileFullDirPath = sys.argv[1]
        logger.info("readFileDirPath:%s" % fileFullDirPath)
        listDir = [dirs[0] for dirs in os.walk(fileFullDirPath)][1:]  # 获取所有的子目录
        if len(listDir) == 0:
            listDir.append(fileFullDirPath)
        logger.info("listDir:%s" % listDir)
        for dataDir in listDir:
            logger.info("dataDir:%s" % dataDir)
            files = [os.path.join(dataDir, i) for i in os.listdir(dataDir)]  # 获取绝对路径
            logger.info("files:%s" % files)
            for fileName in files:
                pos, filename = os.path.split(fileName)
                if filename[-4:] == ".log":
                    fileFullPath = os.path.join(dataDir, fileName)
                    logger.info("fileFullPath:%s" % fileFullPath)
                    read2ThreadLog(fileFullPath)
                    writeFileName = os.path.splitext(fileFullPath)[0]
                    writeFileName = writeFileName + ".parsed"
                    logger.info("writeFileName:%s" % writeFileName)
                    writeLog(writeFileName, threadOrderddict)

