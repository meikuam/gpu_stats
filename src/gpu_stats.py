import json
import time
# from time import gmtime, strftime
import matplotlib.pyplot as plt
import pandas as pd
from io import StringIO
from openssh_wrapper import SSHConnection
import random
import subprocess


def get_random_hex(min_r=0, max_r=200, min_g=0, max_g=200, min_b=0, max_b=255):
    r = f'{random.randint(min_r, max_r):02x}'
    g = f'{random.randint(min_g, max_g):02x}'
    b = f'{random.randint(min_b, max_b):02x}'
    hex_val = '#' + r + g + b
    return hex_val


def send_message(message):
    subprocess.Popen(['notify-send', message])
    return


def get_current(conn):
    get_temp = 'nvidia-smi --query-gpu=gpu_name,temperature.gpu,utilization.gpu,memory.free,memory.used,memory.total --format=csv,nounits,noheader'
    ret = conn.run(get_temp)
    ret = str(ret)
    return pd.read_csv(StringIO(ret), header=None, names=['name', 'temp', 'utilization', 'free', 'used', 'total'])


class Alarm:

    def __init__(self, name, key, min_val, max_val):
        self.name = name
        self.key = key
        self.min_val = min_val
        self.max_val = max_val

        self.max_alarm = False
        self.min_alarm = False

    def check(self, val):
        if val < self.min_val:  # check minimum
            if not self.min_alarm:
                self.min_alarm = True
                # time_stamp = strftime("%d.%m.%Y %H:%M:%S", gmtime())
                message_text = f"{self.name}: {val} <= {self.min_val}"
                Alarm.alarm(message_text)

        elif val > self.max_val:  # check maximum
            if not self.max_alarm:
                self.max_alarm = True
                # time_stamp = strftime("%d.%m.%Y %H:%M:%S", gmtime())
                message_text = f"{self.name}: {val} >= {self.max_val}"
                Alarm.alarm(message_text)
        else:
            self.max_alarm = False
            self.min_alarm = False

    @staticmethod
    def alarm(message_text):
        send_message(message_text)


class GPUStats:

    def __init__(self, name, step, units=[], alarms=[]):
        self.name = name
        self.step = step
        self.units = units
        self.data = pd.DataFrame()
        self.colors = {}
        self.alarms = alarms

    def add(self, item):
        """item - pd.DataFrame row of data"""

        self.data = self.data.append(item[self.units],  ignore_index=True, sort=False)
        for alarm in self.alarms:
            alarm.check(self.data[alarm.key].tolist()[-1])

        if len(self.data) > self.step:
            self.data = self.data.iloc[1:]

    def plot(self, ax):

        for key, value in self.data.iteritems():
            if key not in self.colors:
                self.colors[key] = get_random_hex()
            value.plot(kind='line', color=self.colors[key], ax=ax, label=self.name + ' ' + key)


if __name__ == "__main__":
    random.seed(42)

    with open('params.json', 'r') as f:
        params = json.load(f)

    print('connect to host')
    conn = SSHConnection(params['host'], login=params['ssh_user'], port=params['ssh_port'])

    gpustats = {}

    print('start monitoring')
    if params['plot_graph']:
        plt.ion()
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_xlim(0, params['steps'])

    while True:
        if params['plot_graph']:
            ax.clear()
            ax.set_xlim(0, params['steps'])
        df = get_current(conn)
        for i, item in df.iterrows():
            name = item['name']
            if i not in gpustats:
                alarms = []
                for key, val in params['alarms'].items():
                    alarms.append(
                        Alarm(str(i) + ' ' + name + ' ' + key, key=key, min_val=min(val), max_val=max(val))
                    )
                gpustats[i] = GPUStats(f"{i} {name}", params['steps'], units=params['units'], alarms=alarms)
            gpustats[i].add(item.drop('name'))
        if params['plot_graph']:
            for name, gpu in gpustats.items():
                gpu.plot(ax)
            ax.legend()
            fig.canvas.draw()
            fig.canvas.flush_events()

        time.sleep(params['delay'])
