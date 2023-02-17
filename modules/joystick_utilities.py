import board, busio, math 
import adafruit_ads1x15.ads1115 as ADS 
from adafruit_ads1x15.analog_in import AnalogIn 

class ADS1115_Joystick():
    def __init__(self):
        print("[INFO] initializing joystick...")
        
        i2c = busio.I2C( board.SCL, board.SDA )
        ads = ADS.ADS1115( i2c )
        
        self.joy1x = AnalogIn( ads, ADS.P1 )
        self.joy1y = AnalogIn( ads, ADS.P0 )
        self.joy2x = AnalogIn( ads, ADS.P3 )
        self.joy2y = AnalogIn( ads, ADS.P2 )
        
        self.pan_max_step = 10
        self.tilt_max_step = 10
        
    def _get_differential_speed(self):
        x = self.joy1x.voltage 
        y = self.joy1y.voltage 
        
        x = ((( 5.0 - x) - 2.5) / 2.5)
        y = ((( 5.0 - y) - 2.5) / 2.5)

        if 0.1 > x > -0.1: x=0
        if 0.1 > y > -0.1: y=0
        
        if not(x==0):
            deg = math.atan(abs(y)/abs(x)) * 90 / (math.pi/2)
        else:
            deg = 90
            
        if deg >= 45:
            primary_motor_speed = y
        elif (x>=0 and y>=0) or (x<0 and y<0):
            primary_motor_speed = x
        else:
            primary_motor_speed = -x
            
        secondary_motor_proportion = (deg-45) / 45
        secondary_motor_speed = primary_motor_speed * secondary_motor_proportion
        
        if (y>=0 and x>=0) or (y<0 and x<0):
            left_wheel_speed = primary_motor_speed
            right_wheel_speed = secondary_motor_speed
        else:
            right_wheel_speed = primary_motor_speed
            left_wheel_speed = secondary_motor_speed
        
        self.left_speed = left_wheel_speed
        self.right_speed = right_wheel_speed     
    
    def _get_pan_tilt(self):
        x = self.joy2x.voltage 
        y = self.joy2y.voltage 
        
        x = ((( 5.2 - x) - 2.60) / 1.65)
        y = ((( 5.2 - y) - 2.60) / 1.65)

        if 0.1 > x > -0.1: x=0
        if 0.1 > y > -0.1: y=0
        
#        x = x * 2
#        y = y * 2
        
        self.pan_step = int(x * self.pan_max_step)
        self.tilt_step = -(int(y * self.tilt_max_step))