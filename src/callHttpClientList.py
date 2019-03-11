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
    shell=False不可执行，会报错，需要Popen([dir,])
    '''
    #p = subprocess.Popen("dir", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    '''
    p = subprocess.Popen(cmdList, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        shell=True可以执行，
    shell=False不可执行，会报错
    '''
    '''
    logger.debug("retCode: %d" % (retCode, ))
    if 0 == retCode:
        logger.debug("子进程返回成功: %d" % (retCode,))
    else:
        logger.debug("子进程返回失败: %d" % (retCode,))

    (stdoutData, stderrData) = p.communicate()
    logger.debug("stdoutData: %s" % (stdoutData.decode('gbk').encode('utf-8'),))
    logger.debug("stderrData: %s" % (stderrData.decode('gbk').encode('utf-8'),))
    #print stdoutData.decode('gbk').encode('utf-8')
    '''

    #返回3条信息
    #shellStr = r'E:/clienttest/clienttest.exe 10.187.114.76 811002 g_serverid:1,g_operid:3113703,g_operpwd:k$sdn6}Q,g_operway:4,g_funcid:811002,g_stationaddr:FA163E4910AA,custid:1300016,fundid:-1,orgid:3113,status:'
    #返回1条信息
    #shellStr = r'E:/clienttest/clienttest.exe 10.187.114.76 410512 funcid:410512,custid:1006527,custorgid:2102,trdpwd:+0K8mU%),netaddr:13840580040,orgid:2102,operway:M,ext:0,terminalinfo:MI;UUID:8FF3BD5E-BC5F-4346-A170-32DD9BE056F5;MPN:13840580040;@GTJA|V8.22.0,fundid:10889,market:,secuid:,stkcode:,ordersno:,bankcode:6004,qryflag:0,count:5000,poststr:,'
    #返回0条信息
    shellStr = r'E:/clienttest/clienttest.exe 10.187.114.76 410530 funcid:410530,custid:2380907,custorgid:4211,trdpwd:+0K8mU%),netaddr:15071760818,operway:M,ext:0,orgid:4211,fundid:2414301,moneytype:0,terminalinfo:MI;UUID:F18AA9B1-E053-4F32-8820-5B0F851CCA4A;MPN:15071760818;@40GTJA|V8.22.0'
    #shellStr = "dir"
    cmdList = shlex.split(shellStr)
    p = subprocess.Popen(cmdList, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #retCode == 0 成功
    #retCode = p.wait()
    # dir无法正常调用communicate
    #p.communicate(r'D:\\')
    while p.poll() is None:
        line = p.stdout.readline()
        line = line.strip()
        if line:
            print "%s" % (line.decode('gbk').encode('utf-8'))
            #print('Subprogram output: [{}]'.format(line.decode('gbk').encode('utf-8')))
