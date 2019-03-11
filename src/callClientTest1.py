#coding=utf-8



import sys
import logging
import subprocess
import shlex

# python2里面默认编码为ASCII，对于中文脚本需要重新编码，否则解析出错
reload(sys)
sys.setdefaultencoding('utf-8')

# 引用logging日志模块，按照格式记录日志
logging.basicConfig(level = logging.INFO,format = '%(asctime)s %(pathname)s %(filename)s %(funcName)s %(lineno)s %(levelname)s - %(message)s' )
logger = logging.getLogger(__name__)


if __name__ == '__main__':
    '''
    p = subprocess.Popen("dir", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    shell=True可以执行，
    shell=False不可执行，会报错
    '''
    p = subprocess.Popen("dir", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    '''
    p = subprocess.Popen(cmdList, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        shell=True可以执行，
    shell=False不可执行，会报错
    '''
    # 调用wait后不能执行communicate
    retCode = p.wait()
    logger.debug("retCode: %d" % (retCode, ))
    if 0 == retCode:
        logger.debug("子进程返回成功: %d" % (retCode,))
    else:
        logger.debug("子进程返回失败: %d" % (retCode,))

    (stdoutData, stderrData) = p.communicate(r'D:\\')
    logger.debug("stdoutData: %s" % (stdoutData.decode('gbk').encode('utf-8'),))
    logger.debug("stderrData: %s" % (stderrData.decode('gbk').encode('utf-8'),))
    print "stdoutData: %s" % (stdoutData.decode('gbk').encode('utf-8'),)

