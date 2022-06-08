import psutil
from sys import argv
from time import sleep

import seaborn as sns
from matplotlib import pyplot as plt

def plot_and_save(x, y, path, title, ylabel):
    graph = sns.lineplot(x=x, y=y)

    graph.set(title=title)
    graph.set(xlabel="Time (s)")
    graph.set(ylabel=ylabel)
    graph.get_figure().savefig(path)
    plt.close(graph.get_figure())

cmd = ["python", "-m", "train", "static_gesture", "--train-name", "test"]
sleep_time = 5.0
graph_path = "graphs"

times = []
t = 0
cpu_percents = []
ram_percents = []
number_of_cpu = psutil.cpu_count()

with psutil.Popen(cmd) as p:
    print("Starting logging...")
    p.cpu_percent()
    p.memory_percent()
    while p.status() == psutil.STATUS_RUNNING:
        times.append(t)
        t += sleep_time

        cpu_percents.append(p.cpu_percent())
        ram_percents.append(p.memory_percent())
        #print(f"CPU: {p.cpu_percent()}%")
        #print(f"RAM: {p.memory_percent()}%")
        sleep(sleep_time)
print("...finished")

if len(cpu_percents) > 0 and len(ram_percents) > 0:
    plot_and_save(times,
                  [cpu_perc/number_of_cpu for cpu_perc in cpu_percents],
                  f"{graph_path}/cpu.png",
                  "CPU usage",
                  "% of cpu")
    plot_and_save(times,
                  ram_percents,
                  f"{graph_path}/ram.png",
                  "RAM usage",
                  "% of RAM")
