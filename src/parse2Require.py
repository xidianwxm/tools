# coding=utf-8

import os
import logging
import re
import sys



# python2里面默认编码为ASCII，对于中文脚本需要重新编码，否则解析出错
reload(sys)
sys.setdefaultencoding('utf-8')

# 引用logging日志模块，按照格式记录日志
logging.basicConfig(level = logging.ERROR,format = '%(asctime)s %(pathname)s %(filename)s %(funcName)s %(lineno)s %(levelname)s - %(message)s' )
logger = logging.getLogger(__name__)

class ParsedLog:
    '''
    定义了ParsedLog类
    提供ParsedLog日志属性配置信息
    '''
    #################################
    # 类共享属性声明
    #################################

    # 设置parsed.log中时间位置
    timeSeqPos      =  0
    # 设置parsed.log中时间长度
    timeSeqLength   = 15
    # 设置parsed.log中标记seqId位置
    seqIdPos        = 16
    # 设置parsed.log中标记seqId长度
    seqIdLength     = 10
    # 设置parsed.log中线程号位置
    threadIdPos     = 27
    # 设置parsed.log中线程号长度
    threadIdLength  =  9
    # 设置runlog.log中请求数据位置
    reqDataPos      = 37



    ################################
    # 动态函数实现
    ################################
    def __init__(self, logFileFullPath):
        '''
        功能：初始化ParsedLog类，传入BP日志全路径
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
        self.__logOrderList = []
        # 存储clientTest格式日志的列表
        self.__clientTestList = []
        # 存储kcbpTest格式日志的列表
        self.__kcbpTestList = []
        # 存储json格式日志的列表
        self.__jsonList = []

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
    def clientTestList(self):
        return self.__clientTestList

    @clientTestList.setter
    def clientList(self, value):
        if not isinstance(value, []):
            raise TypeError("%s must be List!" % value)
        self.__clientTestList = value

    @property
    def kcbpTestList(self):
        return self.__kcbpTestList

    @kcbpTestList.setter
    def kcbpList(self, value):
        if not isinstance(value, []):
            raise TypeError("%s must be List!" % value)
        self.__kcbpTestList = value

    @property
    def jsonList(self):
        return self.__jsonList

    @jsonList.setter
    def jsonList(self, value):
        if not isinstance(value, []):
            raise TypeError("%s must be List!" % value)
        self.__jsonList = value







    def read2ThreadLog(self):
        '''
        功能：读取解析ParsedLog日志到文件中
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

        # 计算时间序号在parsed.log日志中的起止位置
        timeSeqPosBegin = self.timeSeqPos
        timeSeqPosEnd = self.timeSeqPos + self.timeSeqLength
        # 计算流水序号在parsed.log日志中的起止位置
        seqIdPosBegin = self.seqIdPos
        seqIdPosEnd = self.seqIdPos  + self.seqIdLength
        # 计算线程号在parsed.log日志中的起止位置
        threadIdPosBegin = self.threadIdPos
        threadIdPosEnd = self.threadIdPos + self.threadIdLength

        clientTestList = []
        kcbpTestList = []
        jsonList = []

        # 读取BP日志内容，过滤出日志级别为99的所有日志进filterLogData列表
        with open(self.__fileFullPath, 'r') as file:
            logData = list(file.readlines())
            logger.debug("logData type: %s",type(logData))

            for index in xrange(len(logData)):
                lineStr = logData[index]
                timeSeq = lineStr[timeSeqPosBegin:timeSeqPosEnd]
                seqId = lineStr[seqIdPosBegin:seqIdPosEnd]
                threadId = lineStr[threadIdPosBegin:threadIdPosEnd]
                reqStr = lineStr[self.reqDataPos:]
                logger.debug("#%s %s %s %s" % (timeSeq, seqId, threadId, reqStr,))
                funcid = ParsedLog.dealReqData(reqStr)
                if funcid != "":
                    clientTestStr = funcid + '\n' + reqStr
                    clientTestList.append(clientTestStr)
                    logger.debug("clientTestStr:%s", clientTestStr)
                    kcbpTestStr = funcid + '!' + reqStr
                    kcbpTestList.append(kcbpTestStr)
                    logger.debug("kcbpTestStr:%s", kcbpTestStr)

        self.__clientTestList = clientTestList
        self.__kcbpTestList = kcbpTestList
        self.__jsonList = jsonList



    def writeLog(self, list, writeFileName):
        '''
        功能：导出List中数据到writeFileName文件
        版本: V1.0
        修改日期: 20190223 08:58
        修改原因:
        修改人: xmwan
        备注: 初始实现
        参数：
        param: list, writeFileName
        ret:   NONE
        '''
        logger.debug("writelog %s...bein...\n" % (writeFileName,))
        with open(writeFileName, 'w') as file:
            file.writelines(list)




    @staticmethod
    def dealReqData(lineStr):
        '''
        功能：处理lineStr中reqData，格式化出功能号funcid:或者g_funcid:
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
        funcidPattern = re.compile(r'(g_)?funcid:(?P<funcid>\d{6}),')
        match = funcidPattern.search(lineStr)
        if match == None:
            logger.info("funcid is None" )
            return ""
        else:
            funcid = match.group('funcid')
            logger.info("funcid is %s" % (funcid,))
            return funcid




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
                if filename[-4:] == ".txt":
                    fileFullPath = os.path.join(dataDir, fileName)
                    ParsedLoger = ParsedLog(fileFullPath)
                    logger.info("fileFullPath:%s" % fileFullPath)
                    ParsedLoger.read2ThreadLog()
                    writeFileName = os.path.splitext(fileFullPath)[0]
                    writeFileName = writeFileName + ".client"
                    logger.info("writeFileName:%s" % writeFileName)
                    ParsedLoger.writeLog(ParsedLoger.clientTestList, writeFileName)
                    writeFileName = os.path.splitext(fileFullPath)[0]
                    writeFileName = writeFileName + ".kcbp"
                    logger.info("writeFileName:%s" % writeFileName)
                    ParsedLoger.writeLog(ParsedLoger.kcbpTestList, writeFileName)

