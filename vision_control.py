import cv2
import numpy
import time
import multiprocessing
from run import arm_control


def open_cap(flag,object_coordinate):
    capture = cv2.VideoCapture(0)
    while capture.isOpened():
        ret, frame = capture.read()
        frame=cv2.flip(frame,-1)
        
        c=cv2.waitKey(60)
        if flag.value==1:
            print(flag)
            hsv=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
            lower_red=numpy.array([156,50,52])
            upper_red=numpy.array([180,255,255])
            mask=cv2.inRange(hsv, lower_red, upper_red)
            contours, hierarchy=cv2.findContours(mask,cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            # cv2.drawContours(frame, contours, 0, (255,255,0),3)
            rect_area,max_area=0,0
            max_contour=0           
            if contours:
                for con in contours:
                    rect_area=cv2.contourArea(con)
                    if rect_area>max_area: 
                        max_contour=con
                        max_area=rect_area 
                    # print(max_contour)
                rect=cv2.minAreaRect(max_contour)
                box=numpy.int0(cv2.boxPoints(rect))
                for i in range(0,4):
                    object_coordinate[(i+1)*2-2]=box[i][0]
                    object_coordinate[(i+1)*2-1]=box[i][1]

                cv2.drawContours(frame, [box],0,(255,255,0),2)
                # flag.value=2
                # print(flag)
           
        cv2.imshow("frame", frame)
        if c & 0xFF==ord('q'):
            break

    capture.release()
    cv2.destroyAllWindows()

def distance_angle_map(centre_y):
    if not 0<=centre_y<=480:
        print("out of range")
        return 30,180
    if 150<=centre_y<=190:
        return 60,-50
    


if __name__=='__main__':
    arm=arm_control()
    flag=multiprocessing.Value('i', 0)
    object_coordinate=multiprocessing.Array("i", [0]*8)
    cap_process=multiprocessing.Process(target=open_cap,args=(flag, object_coordinate))

    cap_process.start()
    flag.value=0
    time.sleep(2)
    arm.keyboard_control_servokit()
    while True:
        if flag.value==0:
            print(flag)
            arm.raising_hand()
            time.sleep(1)
            flag.value=1

        if flag.value==1 and (object_coordinate[0]!=0 and object_coordinate[7]!=0):
            print(flag)
            # arm.two_servokits_linkage_specified_angle(2,4,140,50)
            centre_x=(object_coordinate[0]+object_coordinate[2]+object_coordinate[4]+object_coordinate[6])//4
            centre_y=(object_coordinate[1]+object_coordinate[3]+object_coordinate[5]+object_coordinate[7])//4
            print("centre_y",centre_y)
            while abs(centre_x-320)>30:
                if centre_x>=350 and arm.kit.servo[5].angle>=0:
                    arm.kit.servo[5].angle=arm.kit.servo[5].angle-2
                    time.sleep(0.2)
                if centre_x<=290  and arm.kit.servo[5].angle<=100:
                    arm.kit.servo[5].angle=arm.kit.servo[5].angle+2
                    time.sleep(0.2)
                centre_x=(object_coordinate[0]+object_coordinate[2]+object_coordinate[4]+object_coordinate[6])//4
                print("centre_x",centre_x)
            # flag.value=2

            if flag.value==2 and (object_coordinate[0]!=0 and object_coordinate[7]!=0):
                # distance=...
                print(flag)
                print("centre_y",centre_y)
                arm.two_servokits_linkage_specified_angle(2,4,170,40);time.sleep(0.5)
                arm.two_servokits_linkage(4,7,50,-40,3,2,run_time=3);time.sleep(0.5)  # centre_y =95 distance=15cm
                arm.two_servokits_linkage_specified_angle(4,7,30,180,run_time=3)
                # arm.two_servokits_linkage_specified_angle(2,4,140,60)
            # arm.going_home()
            # flag.value=3
    # cap_process.join()
    # if KeyboardInterrupt:
    #     cap_process.close()
    # arm.keyboard_control_servokit()
    
    # arm_process.start()

