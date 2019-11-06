# /usr/local/bin/python
import json
import sys
import subprocess

if len(sys.argv) < 2:
    print "Usage: python ss.py https://ssr.address"
    sys.exit(0)


def parse_querystring(querystring):
    result = {}
    param_list = querystring.split("&")
    for param in param_list:
        pos = param.index("=")
        name = param[0:pos]
        value = param[pos + 1:]
        result[name] = value
    return result


def exec_command(command_str):
    result = subprocess.Popen(command_str, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              shell=True)
    return result.communicate()


content = open(sys.argv[1]).read()
pid = "--pid-file /tmp/ss.pid"
log = "--log-file /tmp/ss.log"
try:
    exec_command("python local.py -d stop {pid}".format(pid=pid))
    shadow_socks_configs = json.loads(content)
    for node in shadow_socks_configs["configs"]:
        if node["server"] == "127.0.0.1":
            continue
        proto_param = node["protocolparam"] if "protocolparam" in node else ""
        confusion_param = node["obfsparam"] if "obfsparam" in node else ""
        command = "python local.py -b 127.0.0.1 -l 1082 -s \"{0}\" -p \"{1}\" -k \"{2}\" -m \"{3}\" -O \"{4}\" -o \"{5}\" -G \"{6}\" -g \"{7}\" {pid} {log} -d start"
        command = command.format(node["server"], node["server_port"], node["password"], node["method"],
                                 node["protocol"], node["obfs"], proto_param, confusion_param, pid=pid, log=log)
        exec_command(command)
        try:
            output, error = exec_command(
                "curl -I -s  -w \"%{time_total}\" --socks5 127.0.0.1:1082 https://google.com --max-time 5")
            output_list = output.split("\r\n")
            if error == "" and len(output_list) > 1:
                print node["remarks"], node["server"], " CURL TimeTotal Seconds: {0} ".format(output_list[-1],
                                                                                              output_list[0])
        except subprocess.CalledProcessError as e:
            pass
        exec_command("python local.py -d stop {pid}".format(pid=pid))
except KeyboardInterrupt as e:
    print "User Exit"
    sys.exit(1)
except Exception as e:
    print e
