import time
from adafruit_servokit import ServoKit
import multiprocessing
import serial
import Jetson.GPIO as GPIO


class arm_control(object):
    def __init__(self) -> None:
        self.kit=ServoKit(channels=16)
        self.memory=[]
        self.servokit_index=[0,1,2,4,5,7]
        self.homing()

    def homing(self):  # 舵机归位
        self.kit.servo[0].angle=30
        self.kit.servo[1].angle=90
        self.kit.servo[2].angle=160
        self.kit.servo[4].angle=30
        self.kit.servo[7].angle=180
        self.kit.servo[5].angle=90
        

    def kit_relative_move(self,id:int,angle=1,time_s=1):  
        current_angle=int(self.kit.servo[id].angle)
        target_angle=current_angle+angle
        run_time=time_s/abs(angle)
        if angle>=0 and target_angle<=180:
            for i in range(current_angle, target_angle):
                self.kit.servo[id].angle=i
                time.sleep(run_time)
        if angle<0 and target_angle>=0:
            for i in range(current_angle, target_angle, -1):
                self.kit.servo[id].angle=i
                time.sleep(run_time)

    def kit_absolute_move(self, id:int, target_angle=90, time_s=1):  # 单个舵机缓慢运动到指定角度
        current_angle=int(self.kit.servo[id].angle)
        sleep_time=time_s/(abs(target_angle-current_angle)if target_angle-current_angle!=0 else 100)
        step = 1 if current_angle<=target_angle else -1
        if 0<=target_angle<=180:
            for i in range(current_angle, target_angle, step):
                self.kit.servo[id].angle=i
                time.sleep(sleep_time)

    def multiple_kit_absolute_move(self, id:int, angle_group: list, time_interval=0.5):  # 按照角度组运动，单个舵机缓慢运动到指定角度
        if 0<=id<=7 and angle_group:
            for angle in angle_group:
                self.kit_absolute_move(id,angle)
                time.sleep(time_interval)

    def multiple_kit_relative_move(self, id:int, angle_group: list, time_interval=0.5,time_s=1):  # 按照角度组运动，单个舵机缓慢从现位置运动到一定角度
        if 0<=id<=7 and angle_group:
            for angle in angle_group:
                self.kit_relative_move(id, angle,time_s=time_s)
                time.sleep(time_interval)
            

    def show_all_angle(self):
        for i in self.servokit_index:
            print(i,self.kit.servo[i].angle)

    def memory_position(self):  # 单次执行用多了就不准了不知道为啥
         for i in range(0,6):
            print(self.kit.servo[i].angle)
            self.memory.append(self.kit.servo[i].angle)

    def return_to_memory_action(self):  # 不会写捏，所以拉了依托
        if self.memory:
            for i in range(0,6):
                self.kit.servo[i].angle=self.memory[i]
                time.sleep(0.5)


    def two_servokits_linkage(self, id_1, id_2, target_relative_angle_1, target_relative_angle_2,speed_1=2, speed_2=2,run_time=2):  # 双舵机联动并基于相对位置运动
        current_angle_1,current_angle_2=self.kit.servo[id_1].angle,self.kit.servo[id_2].angle
        target_angle_1, target_angle_2= current_angle_1+target_relative_angle_1, current_angle_2+target_relative_angle_2
        run_time=run_time/max(abs(target_relative_angle_1),abs(target_relative_angle_2),1)
        cocefficien_1 = 1 if  target_relative_angle_1>=0 else -1
        cocefficien_2 = 1 if  target_relative_angle_2>=0 else -1
        counter_1, counter_2=0, 0
        # differential=max(abs(target_angle_1),abs(target_angle_2))/min(abs(target_angle_1),abs(target_angle_2))
        # while (abs(counter_1)<abs(target_relative_angle_1) or abs(counter_2)<abs(target_relative_angle_2)) and  (0<=target_angle_1<=180 and 0<=target_angle_2<=180):
        while ((abs(self.kit.servo[id_1].angle-target_angle_1>4)) or (abs(self.kit.servo[id_2].angle-target_angle_2>4))) and  (0<=target_angle_1<=180 and 0<=target_angle_2<=180):
            if  abs(counter_1)<abs(target_relative_angle_1):
                print("start_1", counter_1, "    angle",  id_1,"   ",self.kit.servo[id_1].angle)
                self.kit.servo[id_1].angle=self.kit.servo[id_1].angle+speed_1*cocefficien_1
                counter_1=counter_1+cocefficien_1*speed_1
                time.sleep(run_time)
            if  abs(counter_2)<abs(target_relative_angle_2):
                print("start_2", counter_2, "    angle", id_2,"   ",self.kit.servo[id_2].angle)
                self.kit.servo[id_2].angle=self.kit.servo[id_2].angle+speed_2*cocefficien_2
                counter_2=counter_2+cocefficien_2*speed_2
                time.sleep(run_time)
        self.kit_absolute_move(id=id_1, target_angle=int(target_angle_1), time_s=0.5)  # 角度矫正，如果速度不一样，舵机在往复运动的过程中可能不会运动到预设的角度， 所以再单舵机运动
        self.kit_absolute_move(id=id_2, target_angle=int(target_angle_2), time_s=0.5)

    def two_servokits_linkage_specified_angle(self, id_1, id_2, target_angle_1, target_angle_2,speed_1=2, speed_2=2,run_time=2):  # 两舵机联动到指定角度
        current_angle_1,current_angle_2=self.kit.servo[id_1].angle,self.kit.servo[id_2].angle
        target_relative_angle_1, target_relative_angle_2 = int(target_angle_1-current_angle_1), int(target_angle_2-current_angle_2)
        run_time=run_time/max(abs(target_relative_angle_1),abs(target_relative_angle_2),1)
        cocefficien_1 = 1 if  target_relative_angle_1>=0 else -1
        cocefficien_2 = 1 if  target_relative_angle_2>=0 else -1
        counter_1, counter_2=0, 0
        # differential=max(abs(target_angle_1),abs(target_angle_2))/min(abs(target_angle_1),abs(target_angle_2))
        # while abs(counter_1)<abs(target_relative_angle_1) or abs(counter_2)<abs(target_relative_angle_2) and  0<=target_angle_1<=180 and 0<=target_angle_2<=180:
        while ((abs(self.kit.servo[id_1].angle-target_angle_1>4)) or (abs(self.kit.servo[id_2].angle-target_angle_2>4))) and  (0<=target_angle_1<=180 and 0<=target_angle_2<=180):
            if  abs(counter_1)<abs(target_relative_angle_1):
                print("start_1", counter_1, "    angle1  ",  id_1,"  ",self.kit.servo[id_1].angle)
                self.kit.servo[id_1].angle=self.kit.servo[id_1].angle+speed_1*cocefficien_1
                counter_1=counter_1+cocefficien_1*speed_1
                time.sleep(run_time)
            if  abs(counter_2)<abs(target_relative_angle_2):
                print("start_2", counter_2, "    angle2  ", id_2,"  ",self.kit.servo[id_2].angle)
                self.kit.servo[id_2].angle=self.kit.servo[id_2].angle+speed_2*cocefficien_2
                counter_2=counter_2+cocefficien_2*speed_2
                time.sleep(run_time)
        self.kit_absolute_move(id=id_1, target_angle=int(target_angle_1), time_s=0.5)  # 角度矫正
        self.kit_absolute_move(id=id_2, target_angle=int(target_angle_2), time_s=0.5)

    def three_servos_parallel_motion(self, id_1, id_2, id_3, target_angle1, target_angle2, target_angle3, speed1=2,
                                     speed2=2, speed3=2, run_time=0.01):
        current_angle_1, current_angle_2, current_angle_3 = self.kit.servo[id_1].angle, self.kit.servo[id_2].angle, \
        self.kit.servo[id_3].angle
        target_relative_angle1, target_relative_angle2, target_relative_angle3 = int(
            target_angle1 - current_angle_1), int(target_angle2 - current_angle_2), int(target_angle3 - current_angle_3)
        cocefficien_1 = 1 if target_relative_angle1 >= 0 else -1
        cocefficien_2 = 1 if target_relative_angle2 >= 0 else -1
        cocefficien_3 = 1 if target_relative_angle3 >= 0 else -1
        counter_1, counter_2, counter_3 = 0, 0, 0
        # run_time=0.05
        while ((abs(self.kit.servo[id_1].angle - target_angle1 > 4)) or (
        abs(self.kit.servo[id_2].angle - target_angle2 > 4)) or (
               abs(self.kit.servo[id_3].angle - target_angle3 > 4))) and (
                0 <= target_angle1 <= 180 and 0 <= target_angle2 <= 180):
            if abs(counter_1) < abs(target_relative_angle1):
                # print("start_1", counter_1, "    angle1  ",  id_1,"  ",self.kit.servo[id_1].angle)
                print("start1  {}  angle {} {}".format(cocefficien_1, id_1, self.kit.servo[id_1].angle))
                self.kit.servo[id_1].angle = self.kit.servo[id_1].angle + speed1 * cocefficien_1
                counter_1 = counter_1 + cocefficien_1 * speed1
                time.sleep(run_time)
            if abs(counter_2) < abs(target_relative_angle2):
                print("start1  {}  angle {} {}".format(cocefficien_2, id_2, self.kit.servo[id_2].angle))
                self.kit.servo[id_2].angle = self.kit.servo[id_2].angle + speed2 * cocefficien_2
                counter_2 = counter_2 + cocefficien_2 * speed2
                time.sleep(run_time)
            if abs(counter_3) < abs(target_relative_angle2):
                print("start3  {}  angle {} {}".format(cocefficien_3, id_3, self.kit.servo[id_3].angle))
                self.kit.servo[id_3].angle = self.kit.servo[id_3].angle + speed3 * cocefficien_3
                counter_3 = counter_3 + cocefficien_3 * speed3
                time.sleep(run_time)
        self.kit_absolute_move(id=id_1, target_angle=int(target_angle1), time_s=0.5)  # 角度矫正
        self.kit_absolute_move(id=id_2, target_angle=int(target_angle2), time_s=0.5)
        self.kit_absolute_move(id=id_3, target_angle=int(target_angle3), time_s=0.5)

    # 从这里开始地从的控制代码就写完了，下面就是对各种机械臂动作组编辑的尝试

    def keyboard_control_servokit(self):  # 键盘测试编辑的动作组，md真的麻烦改一下参数又要中断执行一次，谁能写个舵机的qt我能跪下来喊爹
        while True:
            print("input id")
            id=int(input())
            if id in self.servokit_index:
                print("input angle")
                flag_input=input()
                if flag_input.isdigit():
                    angle_input=int(flag_input)
                    if 0<=angle_input<=180:    
                        # self.kit_relative_move(1,angle_input,1)
                        # self.kit.servo[id].angle=angle_input
                        self.kit_absolute_move(id,angle_input)
            if id==6:
                self.going_home()
            # if id==8:
            #     self.going_home()
            if id==9:
                self.two_servokits_linkage(2,3,100,-60)
                # self.two_servokits_linkage(2,3,-100,40)
            if id==10:
                self.two_servokits_linkage_specified_angle(2,4,140,50)
            if id==11:
                self.two_servokits_linkage_specified_angle(4,7,40,130)
            if id==12:
                self.raising_hand()
            if id==13:
                self.two_servokits_linkage(4,7,-60,40,3,2)
            if id==14:
                self.two_servokits_linkage(4,7,60,-40,3,2)
            if id==15:
                self.horizontal_move()
            if id==16:
                self.two_servokits_linkage_specified_angle(4,7,40,130)
                self.two_servokits_linkage(4,7,60,-50,3,2)
                time.sleep(0.5)
                self.kit_absolute_move(0,130)
                time.sleep(0.5)
                print("hanging")
                self.kit_absolute_move(4,120,1)
                time.sleep(0.5)
                self.going_home()
                self.kit_absolute_move(5,150)
                self.kit_absolute_move(0,30)
            if id==17:
                # self.two_servokits_linkage_specified_angle(4,7,30,180,run_time=3)
                self.two_servokits_linkage_specified_angle(4,7,40,130)
                self.two_servokits_linkage(4,7,60,-50,3,2,run_time=3)
            if id==18:
                self.two_servokits_linkage_specified_angle(4,7,40,130)
                self.two_servokits_linkage(4,7,50,-40,3,2,run_time=3)
            if id==19:
                self.two_servokits_linkage_specified_angle(4,7,40,130)
                self.two_servokits_linkage(4,7,40,-30,3,2,run_time=3)        
            if id==666:
                break

    def saying_hellow(self):  # 使用多进程和多角度组编辑机械臂连携动作
        self.servokit_work_process_0=multiprocessing.Process(target=self.multiple_kit_relative_move, args=(0, [-40, 40,-40, 40], 0.3, 0.3))  # 列表为动作组
        self.servokit_work_process_1=multiprocessing.Process(target=self.multiple_kit_relative_move, args=(1, [-90, 90],1,1))
        self.servokit_work_process_2=multiprocessing.Process(target=self.multiple_kit_relative_move, args=(2, [100, -100, 100], 2,2))
        self.servokit_work_process_4=multiprocessing.Process(target=self.multiple_kit_relative_move, args=(4, [80, -80, 80,-80], 1.5,1.5))
        self.servokit_work_process_3=multiprocessing.Process(target=self.multiple_kit_relative_move, args=(7, [50, -50, 50,-50], 1.5,1.5))
        # self.servokit_work_process_1.start()
        # self.servokit_work_process_2.start()
        self.servokit_work_process_4.start()
        self.servokit_work_process_3.start()
        self.servokit_work_process_0.start()
        # if not (self.servokit_work_process_1.is_alive() and self.servokit_work_process_2.is_alive()):
        #     self.servokit_work_process_0.start()


    def horizontal_move(self):
        self.servokit_work_process_4=multiprocessing.Process(target=self.kit_relative_move, args=(4, 60, 5))
        self.servokit_work_process_3=multiprocessing.Process(target=self.kit_relative_move, args=(7,  -30, 5))
        self.servokit_work_process_4.start()
        self.servokit_work_process_3.start()
        # while self.kit.servo[3].angle>=90:
        #     self.kit.servo[3].angle=self.kit.servo[3].angle-1
        #     time.sleep(0.01)   

    def going_home(self):
        self.kit_absolute_move(2,160)
        time.sleep(0.5)
        self.two_servokits_linkage_specified_angle(4, 7 , 30, 180,2,3,run_time=3)
        self.kit_absolute_move(5,90)
        # self.kit_absolute_move(0,30)
        self.kit_absolute_move(1,90)
        

    def raising_hand(self):
        self.kit_absolute_move(2,170)
        self.two_servokits_linkage_specified_angle(7,4,130,180,run_time=3)
        self.kit_absolute_move(2,30)
        self.kit_absolute_move(4,180)
     

    def  __del__(self):
        print("destroyed")


class stepping_motor(object):

    def  __init__(self):
        GPIO.setmode(GPIO.TEGRA_SOC)
        self.pul_pin='SPI1_MISO'  #  bcm 9
        GPIO.setup(self.pul_pin,GPIO.OUT,initial=GPIO.HIGH)
        self.ena_pin='SPI2_MISO'  #  bcm 10
        GPIO.setup(self.ena_pin, GPIO.OUT, initial=GPIO.HIGH)
        self.dir='SPI1_CS0'  #  bcm 8
        GPIO.setup(self.dir, GPIO.OUT, initial=GPIO.HIGH)

    def IO_init(self):
        ...

    def delay_us(self, sleep_time):
        end_time=time.perf_counter() + (sleep_time-1) / 1e6
        while time.perf_counter()<end_time:
            pass
    # def get_gpio_TEGRA_SOC():
    #     # bcm_to_tegra={
    #     #     k : list(GPIO.gpio_pin_data()[-1]['TEGRA_SOC'].key())[i] for i, k in enumerate(GPIO.gpio_pin_data()[-1]['BCM'])
    #     # }
    #     print(GPIO.gpio_pin_data())
    #     # print(bcm_to_tegra)
    def stepping_motor_IO_overturn(self, turns=360,speed=8, direction=1):
        turns=turns/360
        GPIO.output(self.dir, GPIO.HIGH) if direction==1 else GPIO.output(self.dir, GPIO.LOW)
        curr_value=GPIO.HIGH
        for i in range(0, int(3200*turns)):
            self.delay_us(100*speed)
            GPIO.output(self.pul_pin, curr_value)
            curr_value ^= GPIO.HIGH
            print("out")




if __name__ == "__main__":

    ser_arm=arm_control()
    ser_arm.show_all_angle()
    ser_arm.keyboard_control_servokit()


    # step_mt=stepping_motor()
    # print("input turns")
    # while True:
    #     turns=int(input())
    #     step_mt.stepping_motor_IO_overturn(turns=turns, speed=20,direction=1)
    #     print("keep on")

    # testi_servokit()

# while True:
#     kit.servo[0].angle=10
#     time.sleep(1)
#     print("run")
#     kit.servo[0].angle=150
    if KeyboardInterrupt:
        del ser_arm

