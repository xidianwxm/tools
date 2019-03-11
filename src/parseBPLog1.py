# coding=utf-8

import os
import logging
from collections import OrderedDict
import re
import sys

# python2里面默认编码为ASCII，对于中文脚本需要重新编码，否则解析出错
reload(sys)
sys.setdefaultencoding('utf-8')

# 引用logging日志模块，按照格式记录日志
logging.basicConfig(level = logging.DEBUG,format = '%(asctime)s %(pathname)s %(filename)s %(funcName)s %(lineno)s %(levelname)s - %(message)s' )
logger = logging.getLogger(__name__)

class BPLog:
    '''
    定义了BPLog类
    提供BP日志属性配置信息
    '''
    #################################
    # 类共享属性声明
    #################################
    # 设置请求报文日志级别99
    reqLogLevel = "99"
    # runlog.log中标记请求日志的列数
    logLevelPos = 50
    # runlog.log中标记请求日志级别
    logLevelLength = 2
    # 设置runlog.log中时间位置
    timeSeqPos = 1
    # 设置runlog.log中时间长度
    timeSeqLength = 15
    # 设置runlog.log中序号位置
    seqIdPos = 18
    # 设置runlog.log中序号长度
    seqIdLength = 12
    # 设置runlog.log中线程号位置
    threadIdPos = 32
    # 设置runlog.log中线程号长度
    threadIdLength = 13
    # 设置runlog.log中请求数据位置
    reqDataPos = 54

    ################################
    # 动态函数实现
    ################################
    def __init__(self, logFileFullPath):
        '''
        功能：初始化BPLog类，传入BP日志全路径
        版本: V1.0
        修改日期: 20190223 08:58
        修改原因:
        修改人: xmwan
        备注: 初始实现
        参数：
        param: fileFullPath
        ret:   NONE
        '''
        ###################################
        # 类普通属性
        ###################################
        # BP日志全路径
        self.__fileFullPath = logFileFullPath
        # BP日志解析文件全路径
        self.__writeFileName = ""
        # 未使用
        self.__logOrderdict = []
        # 存储解析BP日志的字典
        self.__threadOrderddict = OrderedDict()

    @property
    def fileFullPath(self):
        return self.__fileFullPath

    @fileFullPath.setter
    def fileFullPath(self, value):
        if not isinstance(value, str):
            raise TypeError("%s must be fullPath!" % value)
        self.__fileFullPath = value

    @property
    def writeFileName(self):
        return self.__writeFileName

    @writeFileName.setter
    def writeFileName(self, value):
        if not isinstance(value, str):
            raise TypeError("%s must be fullPath!" % value)
        self.__writeFileName = value

    @property
    def threadOrderddict(self):
        return self.__threadOrderddict

    @threadOrderddict.setter
    def threadOrderddict(self, value):
        if not isinstance(value, OrderedDict):
            raise TypeError("%s must be OrderedDict!" % value)
        self.__threadOrderddict = value

    def read2ThreadLog(self):
        '''
        功能：读取原生kcbp日志到不同线程日志文件中
        版本: V1.0
        修改日期: 20190223 08:58
        修改原因:
        修改人: xmwan
        备注: 初始实现
        参数：
        param: NONE
        ret:   NONE
        '''
        logger.debug("Func fileFullPath:%s" % self.fileFullPath, )
        # 计算请求日志级别在BP日志中的起止位置
        logLevelPosBeg = self.logLevelPos
        logLevelPosEnd = self.logLevelPos + self.logLevelLength
        # 计算流水序号在BP日志中的起止位置
        seqIdPosBegin = self.seqIdPos
        seqIdPosEnd = self.seqIdPos  + self.seqIdLength
        # 计算时间序号在BP日志中的起止位置
        timeSeqPosBegin = self.timeSeqPos
        timeSeqPosEnd = self.timeSeqPos + self.timeSeqLength
        # 计算线程号在BP日志中的起止位置
        threadIdPosBegin = self.threadIdPos
        threadIdPosEnd = self.threadIdPos + self.threadIdLength

        # 读取BP日志内容，过滤出日志级别为99的所有日志进filterLogData列表
        with open(self.__fileFullPath, 'r') as file:
            logData = file.readlines()
            logger.debug("logData type: %s",type(logData))
            filterLogData = list(filter(lambda x: x[logLevelPosBeg:logLevelPosEnd]  == self.reqLogLevel, logData))
            logger.debug("filterLogData type: %s", type(filterLogData))
            logger.debug("filterLogData count: %d", len(filterLogData))
            #logger.debug("filterLogData content: %s", map(BPLog.printList,filterLogData))

        reqData = u""
        count = 0
        for lineStr in filterLogData:
            # 切割关键位置信息并做格式化替换
            timeSeq = lineStr[timeSeqPosBegin:timeSeqPosEnd].strip()
            seqId = lineStr[seqIdPosBegin:seqIdPosEnd].strip().replace('-', '')
            threadId = lineStr[threadIdPosBegin:threadIdPosEnd].strip().replace(' ', '_').replace('-', '_')
            count = count + 1

            # reqData为gb2312编码，需要从gb2312转unicode再编码为utf-8
            # BP日志记录不全，解析有问题，先用异常捕获的方式输出错误行号，以便继续进行不中断
            try:
                reqData = lineStr[self.reqDataPos:].replace('\n', '').decode('gb2312').encode('utf-8')
                # logger.info("%s, %s, %s, %s", timeSeq, seqId, threadId, reqData)
            except:
                print "error!, count:%d" % (count, )

            # 初始化threadOrderddict3层字典，按照threadId、seqId、timeSeq顺序建立key，每个字典都是OrderDict
            if threadId not in self.threadOrderddict.keys():
                # 新threadId需要初始化后续3层字典
                t3OD = OrderedDict()
                t2OD = OrderedDict()
                t3OD[timeSeq] = reqData
                t2OD[seqId] = t3OD
                self.threadOrderddict[threadId] = t2OD
            else:
                if seqId not in self.threadOrderddict[threadId].keys():
                    #  新seqId需要初始化后续2层字典
                    t3OD = OrderedDict()
                    t3OD[timeSeq] = reqData
                    self.threadOrderddict[threadId][seqId] = t3OD
                else:
                    if timeSeq not in self.threadOrderddict[threadId][seqId].keys():
                        # 新timeSeq需要初始化后续1层字典
                        self.threadOrderddict[threadId][seqId][timeSeq] = reqData
                    else:
                        # 一笔交易的请求报文的后续行内容，按照顺序拼接
                        tmpStr = self.threadOrderddict[threadId][seqId][timeSeq]
                        self.threadOrderddict[threadId][seqId][timeSeq] = tmpStr + reqData
                        logger.debug("%s, %s, %s, %s", timeSeq, seqId, threadId, self.threadOrderddict[threadId][seqId][timeSeq])

        logger.debug("\n------------threadOrderddict:\n%s\n", self.threadOrderddict)

    def writeLog(self, writeFileName):
        '''
        功能：导出threadOrderddict中数据到*.parsed文件
        版本: V1.0
        修改日期: 20190223 08:58
        修改原因:
        修改人: xmwan
        备注: 初始实现
        参数：
        param: writeFileName
        ret:   NONE
        '''
        logger.debug("writelog...bein...\n")

        with open(writeFileName, 'w') as file:
            for threadId in self.threadOrderddict.keys():
                logger.debug("threadId:%s\n", threadId)
                seqInnerDict = self.threadOrderddict[threadId]
                for seqId in seqInnerDict.keys():
                    timeSeqInnerDict = seqInnerDict[seqId]
                    for timeSeq in timeSeqInnerDict.keys():
                        logger.debug("%s, %s, %s, %s\n" % (timeSeq, seqId, threadId, timeSeqInnerDict[timeSeq]))
                        tmpStr = self.dealReqData(timeSeqInnerDict[timeSeq])
                        logger.debug("dealReqData: %s\n" % (tmpStr,))
                        timeSeqInnerDict[timeSeq] = tmpStr
                        #logger.info("%s, %s, %s, %s\n" % (timeSeq, seqId, threadId, timeSeqInnerDict[timeSeq].decode('gbk')))
                        # 导出前判断以下关键词，如果有则不导出
                        # 实现不完整，需要后续用shell脚本进一步过滤功能号黑名单
                        if "'" not in timeSeqInnerDict[timeSeq] and \
                            "MsgId:" not in timeSeqInnerDict[timeSeq] and \
                            "gzdm:" not in timeSeqInnerDict[timeSeq] and \
                            "Call:" not in timeSeqInnerDict[timeSeq] and \
                            "?xml" not in timeSeqInnerDict[timeSeq] :
                            #print "%s %s %s %s\n" % (timeSeq, seqId, threadId,timeSeqInnerDict[timeSeq])
                            file.write("%s %s %s %s\n" % (timeSeq, seqId, threadId,timeSeqInnerDict[timeSeq].decode('utf-8').encode('gb2312')))

    @staticmethod
    def dealReqData(lineStr):
        '''
        功能：处理threadOrderddict中reqData，数据清洗
        版本: V1.0
        修改日期: 20190223 08:58
        修改原因:
        修改人: xmwan
        备注: 初始实现
        参数：
        param: lineStr
        ret:   retStr
        '''
        # 切除请求报文前Req字符串
        # 命令sed  "s/Req:.\{0,209\}\?_CA=2..\(&_ENDIAN=.\)\?&//g" 1.txt
        cutHeadPattern = re.compile(r'Req:.{0,209}?_CA=2..(&_ENDIAN=.)?&')
        retStr = cutHeadPattern.sub("", lineStr)

        cutsepPattern1 = re.compile(r'&')
        retStr = cutsepPattern1.sub(",", retStr)
        cutsepPattern2 = re.compile(r'=')
        retStr = cutsepPattern2.sub(":", retStr)

        # 替换秘钥
        # 替换trdpwd:+0K8mU%) 交易密码:990818
        # sed "s/trdpwd:.\{6,20\}\?,/trdpwd:+0K8mU%),/g"
        cuttrdpwdPattern = re.compile(r'trdpwd:.{6,20}?,')
        retStr = cuttrdpwdPattern.sub("trdpwd:+0K8mU%),", retStr)
        # 替换g_operpwd:k$sdn6}Q 普通柜员密码:1234!qwe
        # sed "s/g_operpwd:.\{6,35\}\?,/g_operpwd:k$sdn6}Q,/g"
        cutg_operpwdPattern = re.compile(r'g_operpwd:.{6,35}?,')
        retStr = cutg_operpwdPattern.sub("g_operpwd:k$sdn6}Q,", retStr)
        # 替换g_operid:8888,g_operpwd:DB8C15E5B8806B3BBD9AB9C444021DAC 超级柜员密码:1234!1234qwer
        # sed "s/g_operid:8888,g_operpwd:k$sdn6}Q,/g_operid:8888,g_operpwd:DB8C15E5B8806B3BBD9AB9C444021DAC,/g"
        cutg_operid8888Pattern = re.compile(r'g_operid:8888,g_operpwd:k$sdn6}Q,')
        retStr = cutg_operid8888Pattern.sub("g_operid:8888,g_operpwd:DB8C15E5B8806B3BBD9AB9C444021DAC,", retStr)

        # 生产敏感数据清洗
        # 替换name
        namePattern = re.compile(r',name:.{1,4}?,')
        retStr = namePattern.sub(",name:测试姓名,", retStr)
        # 替换fullname
        fullNamePattern = re.compile(r',fullname:.{1,4}?,')
        retStr = fullNamePattern.sub(",fullname:测试姓名,", retStr)
        # 转置idNo，需进一步实现
        # 替换addr
        addrPattern = re.compile(r',addr:.{1,64}?,')
        retStr = fullNamePattern.sub(",addr:快递地址laianlu685,", retStr)

        return retStr

    @staticmethod
    def printList(str):
        '''

        ret:
        '''
        logger.debug("%s" % str,)


if __name__ == '__main__':
    '''
    需要传递1个文件夹的参数，可以解析该文件夹以及所有子目录下所有*.log的日志
    '''
    if len(sys.argv) != 2:
        print("ParamError: \nExample:\n python readThreadLog.py $fileDirFullPath" )
        exit(-1)
    else:
        fileFullDirPath = sys.argv[1]
        logger.info("readFileDirPath:%s" % fileFullDirPath)
        # 获取所有的子目录
        listDir = [dirs[0] for dirs in os.walk(fileFullDirPath)][1:]
        listDir.append(fileFullDirPath)
        logger.info("listDir:%s" % listDir)
        for dataDir in listDir:
            logger.info("dataDir:%s" % dataDir)
            # 获取绝对路径
            files = [os.path.join(dataDir, i) for i in os.listdir(dataDir)]
            logger.info("files:%s" % files)
            for fileName in files:
                pos, filename = os.path.split(fileName)
                if filename[-4:] == ".log":
                    fileFullPath = os.path.join(dataDir, fileName)
                    bpLoger = BPLog(fileFullPath)
                    logger.info("fileFullPath:%s" % fileFullPath)
                    bpLoger.read2ThreadLog()
                    writeFileName = os.path.splitext(fileFullPath)[0]
                    writeFileName = writeFileName + ".parsed"
                    logger.info("writeFileName:%s" % writeFileName)
                    bpLoger.writeLog(writeFileName)

