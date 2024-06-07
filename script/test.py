import paramiko
import re
import time
import sys

var = {'host': []}
# 设置主机列表
host_list = [
    {'ip': 'ai.tordor.top', 'port': 12854, 'username': 'root', 'password': 'NcdKEQj5likCnv0Y'}
]

ssh = paramiko.SSHClient()
# 设置为接受不在known_hosts 列表的主机可以进行ssh连接
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())


def cpu(ssh):
    stdin, stdout, stderr = ssh.exec_command('cat /proc/stat | grep "cpu "')
    str_out = stdout.read().decode()
    str_err = stderr.read().decode()

    if str_err != "":
        print(str_err)
        return False
    else:
        cpu_time_list = re.findall('\d+', str_out)
        cpu_idle1 = cpu_time_list[3]
        total_cpu_time1 = 0
        for t in cpu_time_list:
            total_cpu_time1 = total_cpu_time1 + int(t)

    time.sleep(2)

    stdin, stdout, stderr = ssh.exec_command('cat /proc/stat | grep "cpu "')
    str_out = stdout.read().decode()
    str_err = stderr.read().decode()
    if str_err != "":
        print(str_err)
        return False
    else:
        cpu_time_list = re.findall('\d+', str_out)
        cpu_idle2 = cpu_time_list[3]
        total_cpu_time2 = 0
        for t in cpu_time_list:
            total_cpu_time2 = total_cpu_time2 + int(t)

    cpu_usage = round(1 - (float(cpu_idle2) - float(cpu_idle1)) / (total_cpu_time2 - total_cpu_time1), 2)
    print('当前CPU使用率为：' + str(cpu_usage))
    return True, cpu_usage


def mem(ssh):
    stdin, stdout, stderr = ssh.exec_command('cat /proc/meminfo')
    str_out = stdout.read().decode()
    str_err = stderr.read().decode()

    if str_err != "":
        print(str_err)
        return False

    str_total = re.search('MemTotal:.*?\n', str_out).group()
    # print(str_total)
    totalmem = re.search('\d+', str_total).group()

    str_free = re.search('MemFree:.*?\n', str_out).group()
    # print(str_free)
    freemem = re.search('\d+', str_free).group()
    use = round(float(freemem) / float(totalmem), 2)
    print('当前内存使用率为：' + str(1 - use))
    return True, use


def disk(ssh):
    stdin, stdout, stderr = ssh.exec_command('df -lm')
    str_out = stdout.read().decode()
    str_err = stderr.read().decode()

    if str_err != "":
        print(str_err)
        return False

    print(str_out)
    return True, str_out.split('\n')


def net(ssh):
    stdin, stdout, stderr = ssh.exec_command('cat /proc/net/dev')
    str_out = stdout.read().decode()
    str_err = stderr.read().decode()

    if str_err != "":
        print(str_err)
        return False

    print(str_out)
    return True, str_out.split('\n')


for host in host_list:
    ssh.connect(hostname=host['ip'], port=host['port'], username=host['username'], password=host['password'])
    print(host['ip'])
    cpu_status, cpu_usage = cpu(ssh)
    mem_status, mem_usage = mem(ssh)
    disk_status, disk_usage = disk(ssh)
    net_status, net_usage = net(ssh)
    data = {
        'cpu_usage': f'{cpu_usage}%',
        'mem_usage': f'{mem_usage}',
        'disk_usage': disk_usage,
        'net_usage': net_usage
    ,}
    var['host'].append(data)

    ssh.close()

print(var)

