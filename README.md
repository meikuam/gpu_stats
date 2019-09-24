# gpu_stats

Simple tool to remote monitoring and get alarms for NVIDIA GPUs.
It uses ssh (openssh_wrapper) to monitor nvidia-smi tool on remote host.
### Prerequisites

- Ubuntu 18.04
- Python 3.6

Install requirements:

```bash
pip install -r requirements.txt
```

As openssh_wrapper uses rsa keys so we need to send them to remote host:

```
ssh-copy-id -i ~/.ssh/id_rsa.pub -p port user@host
```

Then set vars to `params.json`:

    - "host": name of host
    - "ssh_port": ssh port
    - "ssh_user": user login on remote host
    - "delay": delay in seconds between requests,
    - "steps": steps of graph
    - "units": for now temperature.gpu,utilization.gpu,memory.free,memory.used,memory.total can be monitored
    - "alarms": alarms for monitoring units with minimal and maximal values,
    - "plot_graph": if plot matplotlib graph or not


### Running

```bash
./run.sh
```