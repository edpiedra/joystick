#!/usr/bin/env python

'''
***********************************************************
***                                                     ***
***   JOYSTICK:                                         ***
***      - GET DRIVE AND PAN/TILT DIRECTIONS            ***
***      - SEND DIRECTIONS AND PROGRAM CODE TO MOTORS   ***
***                                                     ***
***   PC:                                               ***
***      - RECEIVE FRAMES FROM PC                       ***
***      - DISPLAY:                                     ***
***         - TWO FRAMES FROM PC (GREEN TINT ADDED      ***
***           TO FRAME WITH PAN/TILT CONTROL WHEN IN    ***
***           DRIVE MODE)                               ***
***         - JOYSTICK DRIVE AND PAN/TILT DIRECTIONS    ***
***           (WITH PROGRAM MODE)                       ***
***         - BUTTONS: MANUAL, AUTO, AND QUIT           ***
***         - TAP ON FRAME TO TAKE PICTURE              ***
***                                                     ***
***********************************************************
'''

from modules.joystick_utilities import *
from modules.network_utilities import * 
from modules.screen_utilities import *
import multiprocessing as mp 
import time, subprocess

program_code_map = {
    0   : "DRIVE",
    1   : "AUTO",
    2   : "QUIT"
}

pan_tilt_code_map = {
    0   : "left",
    1   : "right",
}

def Joystick(
    left_speed, right_speed, program_code, pan_step,
    tilt_step, pan_tilt_code
):
    joy = ADS1115_Joystick()
    wifi = WiFi()
    motors_s = wifi._create_server(8089)
    
    running = True
    
    while running:
        joy._get_differential_speed()
        
        left_speed.value = joy.left_speed
        right_speed.value = joy.right_speed
        _program_code = program_code.value
        
        joy._get_pan_tilt()
        pan_step.value = joy.pan_step 
        tilt_step.value = joy.tilt_step 
        
        if event.is_set():
            _program_code = 2
        
        program_mode = program_code_map[_program_code] 
        pan_tilt_mode = pan_tilt_code_map[pan_tilt_code.value]
            
        message = [
            program_mode, joy.left_speed, joy.right_speed,
            joy.pan_step, joy.tilt_step, pan_tilt_mode
        ]
        
        wifi._send_list(motors_s, message)
        message = wifi._receive_list(motors_s)

        if (program_mode=="QUIT") and (message[0]==program_mode):
            running = False 
            
#    wifi._destroy(motors_s)

def Video(
    left_speed, right_speed, program_code, pan_step,
    tilt_step, pan_tilt_code
):
    wifi = WiFi()
    pc_s = wifi._create_server(8085)
    pc_s.sendall(program_code_map[program_code.value].encode("utf-8"))
    
    message = pc_s.recv(1024).decode("utf-8")
    print(message)
    pc_s.sendall(b"ok")
    
    message = pc_s.recv(1024).decode("utf-8")
    print(message)
    pc_s.sendall(b"ok")
    
    message = pc_s.recv(1024).decode("utf-8")
    print(message)
    pc_s.sendall(b"ok")
    
    gui = GogglesGUI(program_code.value)
    
    def _mouse_callback(trigger, x, y, flags, param):
        gui._mouse_callback(trigger, x, y, flags, param)
        
    cv2.namedWindow("frame", cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback("frame", _mouse_callback)
    
    running = True 
    start_time = time.time()
    
    while running:
        gui._create_canvas()
        
        left_frame = wifi._receive_frame(pc_s)
        pc_s.sendall(b"ok")
        right_frame = wifi._receive_frame(pc_s)
        
        center_canvas = np.concatenate((left_frame, right_frame), axis=0)
        top_canvas = np.concatenate((gui.left_canvas, center_canvas, gui.right_canvas), axis=1)
        screen = np.concatenate((top_canvas, gui.bottom_canvas), axis=0)
        
        text = "left-{:.2f}, right-{:.2f}".format(
            left_speed.value, right_speed.value
        )
        
        cv2.putText(
            screen, text, (570, 20), gui.FONT, 
            gui.FONT_SCALE, (255,255,255), 2
        )
        
        text = "pan-{:.2f}, right-{:.2f}".format(
            pan_step.value, tilt_step.value
        )
        
        cv2.putText(
            screen, text, (570, 40), gui.FONT,
            gui.FONT_SCALE, (255,255,255), 2
        )
        
        text = "program mode: {}".format(
            program_code_map[gui.program_code]
        )
        
        cv2.putText(
            screen, text, (570, 60), gui.FONT,
            gui.FONT_SCALE, (255,255,255), 2
        )
        
        lps = (1.0 / (time.time()-start_time))
        start_time = time.time()
        
        text = "joy lps: {:.2f}".format(lps)
            
        cv2.putText(
            screen, text, (570, 80), gui.FONT,
            gui.FONT_SCALE, (255,255,255), 2, cv2.FILLED
        )
        
        cv2.imshow("frame", screen)
        
        program_code.value = gui.program_code 
        pan_tilt_code.value = gui.pan_tilt_code
        
        message = [
            program_code_map[gui.program_code], 
            pan_tilt_code_map[gui.pan_tilt_code],
            gui.take_picture
        ]
        
        wifi._send_list(pc_s, message)
        
        if (program_code.value==2) or (cv2.waitKey(15)==27):
            event.set()
            running = False
            
#    wifi._destroy(pc_s)
    cv2.destroyAllWindows()
    

if __name__=="__main__":
    event = mp.Event()
    
    left_speed = mp.Value("d", 0.0)
    right_speed = mp.Value("d", 0.0)
    program_code = mp.Value("i", 0)
    pan_step = mp.Value("i", 0)
    tilt_step = mp.Value("i", 0)
    pan_tilt_code = mp.Value("i", 0)
    
    joystick = mp.Process(
        target=Joystick,
        args=(
            left_speed, right_speed, program_code, pan_step, 
            tilt_step, pan_tilt_code
        )
    )
    
    joystick.start()
    
    video = mp.Process(
        target=Video,
        args=(
            left_speed, right_speed, program_code, pan_step,
            tilt_step, pan_tilt_code
        )
    )
    
    video.start()
    
    time.sleep(1)
    
    msg = subprocess.Popen(
        "ssh eddy@eddy-linux.local 'source ~/.virtualenvs/opencv_cuda/bin/activate && cd ~/.virtualenvs/opencv_cuda/goggles && python goggles-pc.py'",
        shell=True
    )
    
    msg.communicate()
    
    joystick.join()
    video.join()