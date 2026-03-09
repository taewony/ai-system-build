(base) 00_hello_gpu $ python --version
Python 3.11.11
(base) 00_hello_gpu $ python hello_gpu.py
PyTorch version: 2.5.1+cu124
CUDA available: True
CUDA version: 12.4
Number of GPUs: 1

GPU 0:
  Name: NVIDIA L40S
  Capability: (8, 9)
  Total memory (GB): 44.39
(base) 00_hello_gpu $ 

   echo "export HOME=/home/jovyan" >> ~/.bashrc
   source ~/.bashrc
   git config --global user.name "taewony"
   git config --global user.email "engchat@gmail.com"

echo "alias ll='ls -lrt'" >> ~/.bashrc

nano ~/.bashrc
```
# ----- 사용자 정의 프롬프트 (짧게) -----
if [ -n "$CONDA_DEFAULT_ENV" ]; then
    export PS1="($CONDA_DEFAULT_ENV) \W \$ "
else
    export PS1="\W \$ "
fi
```
source ~/.bashrc