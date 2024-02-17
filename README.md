使用jetson nano控制6自由度舵机机械臂
====
# 硬件部分
## 基于PCA9685控制多路舵机
jetson与pca9684通过IIC通信输出16路PWM信号<br>
导入IIC, adafruit模块
```bash
sudo apt-get install python-smbus
sudo apt-get install i2c-tools
sudo pip3 install adafruit-circuitpython-servokit
```
这样可以通过运行run.py驱动舵机
# 视觉部分，使用multiprocessing多进程运行
## opencv识别物体
见visiom_contral.py
## AI智能识别
在写了
