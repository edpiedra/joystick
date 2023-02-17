import cv2 
import numpy as np 

class GUITemplate():
    DEFAULT_COLOR = (128, 128, 128)
    HOVER_COLOR = (40,200,40)
    CLICK_COLOR = (40,40,200)
    SELECTED_COLOR = (200,40,40)
    
    WHITE = (255,255,255)
    BLACK = (0,0,0)
    RED = (0,0,255)
    
    LEFT_CANVAS = np.zeros((480, 240, 3), dtype=np.uint8)
    RIGHT_CANVAS = np.zeros((480, 240, 3), dtype=np.uint8)
    BOTTOM_CANVAS = np.zeros((120, 800, 3), dtype=np.uint8)
    
    FONT = cv2.FONT_HERSHEY_SIMPLEX
    FONT_SCALE = 0.5
    
class GogglesGUI():
    def __init__(self, program_code):
        self.FONT = GUITemplate.FONT 
        self.FONT_SCALE = GUITemplate.FONT_SCALE
        
        self.program_code = program_code 
        self.pan_tilt_code = 0 #LEFT
        
        self._initialize_buttons()
        
    def _initialize_buttons(self):
        self.button_code = None
        self.frame_code = None
        self.take_picture = False

        self.drive_button_color = GUITemplate.DEFAULT_COLOR
        self.auto_button_color = GUITemplate.DEFAULT_COLOR
        self.quit_button_color = GUITemplate.DEFAULT_COLOR
        
        if self.program_code==0:
            self.drive_button_color = GUITemplate.SELECTED_COLOR
        elif self.program_code==1:
            self.auto_button_color = GUITemplate.SELECTED_COLOR
            
    def _mouse_callback(self, trigger, x, y, flags, param):
        self._initialize_buttons()
        
        if trigger==cv2.EVENT_LBUTTONDOWN:
            if x < 240:
                if (y < 95) and (y > 35):
                    self.button_code = 0
                    self.drive_button_color = GUITemplate.CLICK_COLOR
                elif (y < 165) and (y > 105):
                    self.button_code = 1
                    self.auto_button_color = GUITemplate.CLICK_COLOR
                elif (y < 235) and (y > 175):
                    self.button_code = 2
                    self.quit_button_color = GUITemplate.CLICK_COLOR
                    
            elif x < 560:
                if (y < 240):
                    self.frame_code = "LEFT"
                elif (y < 480):
                    self.frame_code = "RIGHT"
        
        elif trigger==cv2.EVENT_MOUSEMOVE:
            if x < 240:
                if (y < 95) and (y > 35):
                    self.drive_button_color = GUITemplate.HOVER_COLOR
                elif (y < 165) and (y > 105):
                    self.auto_button_color = GUITemplate.HOVER_COLOR
                elif (y < 235) and (y > 175):
                    self.quit_button_color = GUITemplate.HOVER_COLOR
                    
        if self.button_code is not None: self.program_code = self.button_code
        
        if self.frame_code is not None:
            if self.frame_code=="LEFT":
                if self.pan_tilt_code==0:
                    self.take_picture = True 
                else:
                    self.pan_tilt_code = 0
                    
            elif self.frame_code=="RIGHT":
                if self.pan_tilt_code==1:
                    self.take_picture = True 
                else:
                    self.pan_tilt_code = 1
            
    def _create_canvas(self):
        template = GUITemplate.LEFT_CANVAS.copy()
        
        cv2.rectangle(template, (5,35), (235,95), self.drive_button_color, -1)
        cv2.rectangle(template, (5,105), (235,165), self.auto_button_color, -1)
        cv2.rectangle(template, (5,175), (235,235), self.quit_button_color, -1)
        
        cv2.putText(template, "MODE", (30,25), self.FONT, self.FONT_SCALE, GUITemplate.WHITE, 2, cv2.FILLED)
        cv2.putText(template, "DRIVE", (40,70), self.FONT, self.FONT_SCALE, GUITemplate.BLACK, 2, cv2.FILLED)
        cv2.putText(template, "AUTO", (40,140), self.FONT, self.FONT_SCALE, GUITemplate.BLACK, 2, cv2.FILLED)
        cv2.putText(template, "QUIT", (40,210), self.FONT, self.FONT_SCALE, GUITemplate.BLACK, 2, cv2.FILLED)
        
        self.left_canvas = template.copy()
        
        self.bottom_canvas = GUITemplate.BOTTOM_CANVAS.copy()
        
        template = np.zeros((480, 240, 3), dtype=np.uint8)
        
        self.right_canvas = GUITemplate.RIGHT_CANVAS.copy()
        