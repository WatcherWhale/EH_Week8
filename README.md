# EH_W817

EH_W817 is a small project example trojan for the course Ethical Hacking.


Features:
- Full encryption of data, only decryptable with the attackers private key.
- Has a lot of handy modules
    - passwd collector
    - public ip gathering
    - linpeass execution
    - screenshot of desktop
    - environment variable gathering
    - directory lisitng
- Nice terminal UI

## Getting started

1. To get started run the Trojan client with `python github-client.py` on the target machine.

2. On your Attacker machine start the monitor client `python monitor.py`

With this app you can track how many victims you have and how many datapoints are available.

3. To decrypt data first pull the repo by pressing `P` and then `D` in the monitor client.
