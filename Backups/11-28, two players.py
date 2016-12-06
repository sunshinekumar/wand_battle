#Heavily relied upon flap.py kinect demo. Can be found at 
# http://tinyurl.com/gon96pk
#Also referenced pygame optional lecture, can be found at 
# http://tinyurl.com/npy9e6b
from pykinect2 import PyKinectV2, PyKinectRuntime 
from pykinect2.PyKinectV2 import * 
 
import ctypes 
import _ctypes 
import pygame 
import sys 
import math 
 
class GameRuntime(object): 
    def __init__(self): 
        pygame.init() 
 
        self.screen_width = 1920 
        self.screen_height = 1080

        self.prev_left_hand_height = 0 
        self.cur_left_hand_height = 0 
        self.left_hand_lift = 0
        self.left_hand_tutorial_weight = .14
        self.tutorial_up = 0
        self.tutorial_up2 = 0

        self.right_hand_pos = (0,0)
        self.radius_to_track = 50
        self.is_wand_tracking = 0
        self.is_wand_tracking2 = 0
        self.wand_width = 30

        self.wand_color = (255,0,0)
        self.wand_wide = 90    #For drawing the wand
        self.wand_high = 90

        self.wand_pos = (self.screen_width//4, self.screen_height*3/4)   #Will be set to right hand pos if right hand closes on it
        self.wand_tip = (self.wand_pos[0] - self.wand_wide, self.wand_pos[1] - self.wand_high)

        self.wand_color2 = (0,0,255)
        self.wand_wide2 = 90
        self.wand_high2 = 90

        self.wand_pos2 = (self.screen_width//4 * 3, self.screen_height * 3/4)
        self.wand_tip2 = (self.wand_pos2[0] - self.wand_wide, self.wand_pos2[1] - self.wand_high)

        #To draw the spellcasting circles
        self.circle_separation_radius = 200
        self.circle_radius = 30
        self.spell_circle_color = (200,0,0)
        self.circles = []

        self.circle_separation_radius2 = 200
        self.circle_radius2 = 30
        self.spell_circle_color2 = (0,0,200)
        self.circles2 = []




 
        # Used to manage how fast the screen updates 
        self._clock = pygame.time.Clock() 
 
        # Set the width and height of the window [width/2, height/2] 
        self._screen = pygame.display.set_mode((960,540), pygame.HWSURFACE|pygame.DOUBLEBUF, 32) 
 
        # Loop until the user clicks the close button. 
        self._done = False 
 
        # Kinect runtime object, we want color and body frames  
        self._kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Body) 
 
        # back buffer surface for Kinect color frames, 32bit color, width and height equal to the Kinect color frame size 
        self._frame_surface = pygame.Surface((self._kinect.color_frame_desc.Width, self._kinect.color_frame_desc.Height), 0, 32) 
 
        # here we will store skeleton data  
        self._bodies = None 
 
    #Draw functions here:
    def draw_wands(self):
        # wand 1
        pygame.draw.line(self._frame_surface, self.wand_color, self.wand_pos, 
                         self.wand_tip, self.wand_width)
        # wand 2
        pygame.draw.line(self._frame_surface, self.wand_color2, self.wand_pos2,
                         self.wand_tip2, self.wand_width)

    def draw_tutorials(self):
        # tutorial 1
        if(self.tutorial_up == 1):
            pygame.draw.rect(self._frame_surface, self.wand_color, (0,0,200,200))
        # tutorial 2
        if(self.tutorial_up2 == 1):
            pygame.draw.rect(self._frame_surface, self.wand_color2, (self.screen_width//2,0,200,200))
 
    def draw_color_frame(self, frame, target_surface): 
        target_surface.lock() 
        address = self._kinect.surface_as_array(target_surface.get_buffer()) 
        ctypes.memmove(address, frame.ctypes.data, frame.size) 
        del address 
        target_surface.unlock() 

    def draw_circles(self, joint_points):
        # Gets centers of where each circle should be
        self.circle_separation_radius = abs(joint_points[PyKinectV2.JointType_HipLeft].y - joint_points[PyKinectV2.JointType_Head].y)//2
        north = (joint_points[PyKinectV2.JointType_Head].x,joint_points[PyKinectV2.JointType_Head].y) 
        south = (north[0], north[1] + self.circle_separation_radius*2)
        east =  (north[0] + self.circle_separation_radius, north[1] + self.circle_separation_radius)
        west = (east[0] - self.circle_separation_radius * 2, east[1])
        self.circles = [north, south, east, west] 
        for center in self.circles:
            pygame.draw.circle(self._frame_surface, self.spell_circle_color, (int(center[0]), int(center[1])) , self.circle_radius, 10) 

    def draw_circles2(self, joint_points):
        # Gets centers of where each circle should be
        self.circle_separation_radius2 = abs(joint_points[PyKinectV2.JointType_HipLeft].y - joint_points[PyKinectV2.JointType_Head].y)//2
        north = (joint_points[PyKinectV2.JointType_Head].x,joint_points[PyKinectV2.JointType_Head].y) 
        south = (north[0], north[1] + self.circle_separation_radius2*2)
        east =  (north[0] + self.circle_separation_radius2, north[1] + self.circle_separation_radius2)
        west = (east[0] - self.circle_separation_radius2 * 2, east[1])
        self.circles2 = [north, south, east, west] 
        for center in self.circles2:
            pygame.draw.circle(self._frame_surface, self.spell_circle_color2, (int(center[0]), int(center[1])) , self.circle_radius2, 10) 

    
 
    def run(self): 
        # -------- Main Program Loop ----------- 
        while not self._done: 
            # --- Main event loop 
            for event in pygame.event.get(): # User did something 
                if event.type == pygame.QUIT: # If user clicked close 
                    self._done = True # Flag that we are done so we exit this loop 
 
            # We have a color frame. Fill out back buffer surface with frame's data  
            if self._kinect.has_new_color_frame(): 
                frame = self._kinect.get_last_color_frame() 
                self.draw_color_frame(frame, self._frame_surface) 
                frame = None 
 
            # We have a body frame, so can get skeletons 
            if self._kinect.has_new_body_frame():  
                self._bodies = self._kinect.get_last_body_frame() 
 
                if self._bodies is not None:  
                    for i in range(0, self._kinect.max_body_count): 
                        body = self._bodies.bodies[i] 
                        if not body.is_tracked:  
                            continue  
                        
                        joints = body.joints  
                        joint_points = self._kinect.body_joints_to_color_space(joints)  #From Josh Moavenzadeh (jmoavenz)

                        if i == 0:
                            if joints[PyKinectV2.JointType_HandRight].TrackingState != PyKinectV2.TrackingState_NotTracked:
                                self.right_hand_pos = (joints[PyKinectV2.JointType_HandLeft].Position.y , joints[PyKinectV2.JointType_HandLeft].Position.x)
                                #To see if the right hand closes on the wand
                                if not self.is_wand_tracking:
                                    if (body.hand_right_state == PyKinectV2.HandState_Closed   #Right hand is closed
                                        and abs(joint_points[PyKinectV2.JointType_HandRight].x - self.wand_pos[0]) < self.radius_to_track
                                        and abs(joint_points[PyKinectV2.JointType_HandRight].y - self.wand_pos[1] < self.radius_to_track)): #Right hand is near the wand
                                        self.is_wand_tracking = 1 
                                if self.is_wand_tracking:
                                    #pygame.draw.circle(self._frame_surface, (200,0,0),
                                    #                   (int(joint_points[PyKinectV2.JointType_HandRight].x), int(joint_points[PyKinectV2.JointType_HandRight].y)), 50)

                                    #To have the wand track the hand
                                    self.wand_wide = abs(joint_points[PyKinectV2.JointType_Head].y - joint_points[PyKinectV2.JointType_Neck].y)
                                    self.wand_high = self.wand_wide
                                    self.wand_pos = (joint_points[PyKinectV2.JointType_HandRight].x, joint_points[PyKinectV2.JointType_HandRight].y)
                                    self.wand_tip = (self.wand_pos[0] - self.wand_wide, self.wand_pos[1] - self.wand_high) 
                                    if(body.hand_right_state == PyKinectV2.HandState_Open): self.is_wand_tracking = 0
                                    #Draw the circles on the body if the wand is tracking
                                    self.draw_circles(joint_points)


                            #To save the new left hand height
                            if joints[PyKinectV2.JointType_HandLeft].TrackingState != PyKinectV2.TrackingState_NotTracked: 
                                self.cur_left_hand_height = joints[PyKinectV2.JointType_HandLeft].Position.y 
                            


 
                            # calculate how fast we lift the left hand to see if we bring up the tutorial
                            self.left_hand_lift = (self.cur_left_hand_height - self.prev_left_hand_height)
                            if math.isnan(self.left_hand_lift): 
                                self.left_hand_lift = 0 
                            if(abs(self.left_hand_lift) > self.left_hand_tutorial_weight): 
                                if self.left_hand_lift < 0: #Pulls down the tutorial if we push down
                                    self.tutorial_up = 0
                                elif(self.left_hand_lift > 0): 
                                    self.tutorial_up = 1  #Brings up the tutorial if we lift up
 
                            # cycle previous and current heights for next time 
                            self.prev_left_hand_height = self.cur_left_hand_height

                        if i == 1:
                            if joints[PyKinectV2.JointType_HandRight].TrackingState != PyKinectV2.TrackingState_NotTracked:
                                self.right_hand_pos = (joints[PyKinectV2.JointType_HandLeft].Position.y , joints[PyKinectV2.JointType_HandLeft].Position.x)
                                #To see if the right hand closes on the wand
                                if not self.is_wand_tracking2:
                                    if (body.hand_right_state == PyKinectV2.HandState_Closed   #Right hand is closed
                                        and abs(joint_points[PyKinectV2.JointType_HandRight].x - self.wand_pos2[0]) < self.radius_to_track
                                        and abs(joint_points[PyKinectV2.JointType_HandRight].y - self.wand_pos2[1] < self.radius_to_track)): #Right hand is near the wand
                                        self.is_wand_tracking2 = 1 
                                if self.is_wand_tracking2:
                                    #pygame.draw.circle(self._frame_surface, (200,0,0),
                                    #                   (int(joint_points[PyKinectV2.JointType_HandRight].x), int(joint_points[PyKinectV2.JointType_HandRight].y)), 50)

                                    #To have the wand track the hand
                                    self.wand_wide2 = abs(joint_points[PyKinectV2.JointType_Head].y - joint_points[PyKinectV2.JointType_Neck].y)
                                    self.wand_high2 = self.wand_wide2
                                    self.wand_pos2 = (joint_points[PyKinectV2.JointType_HandRight].x, joint_points[PyKinectV2.JointType_HandRight].y)
                                    self.wand_tip2 = (self.wand_pos2[0] - self.wand_wide2, self.wand_pos2[1] - self.wand_high2) 
                                    if(body.hand_right_state == PyKinectV2.HandState_Open): self.is_wand_tracking2 = 0
                                    #Draw the circles on the body if the wand is tracking
                                    self.draw_circles2(joint_points)


                            #To save the new left hand height
                            if joints[PyKinectV2.JointType_HandLeft].TrackingState != PyKinectV2.TrackingState_NotTracked: 
                                self.cur_left_hand_height = joints[PyKinectV2.JointType_HandLeft].Position.y 
                            


 
                            # calculate how fast we lift the left hand to see if we bring up the tutorial
                            self.left_hand_lift = (self.cur_left_hand_height - self.prev_left_hand_height)
                            if math.isnan(self.left_hand_lift): 
                                self.left_hand_lift = 0 
                            if(abs(self.left_hand_lift) > self.left_hand_tutorial_weight): 
                                if self.left_hand_lift < 0: #Pulls down the tutorial if we push down
                                    self.tutorial_up2 = 0
                                elif(self.left_hand_lift > 0): 
                                    self.tutorial_up2 = 1  #Brings up the tutorial if we lift up
 
                            # cycle previous and current heights for next time 
                            self.prev_left_hand_height = self.cur_left_hand_height


 
            # --- Game logic 
            

            # Draw graphics 
            self.draw_wands()
            self.draw_tutorials()
 
            # Optional debugging text 
            #font = pygame.font.Font(None, 36) 
            #text = font.render(str(self.flap), 1, (0, 0, 0)) 
            #self._frame_surface.blit(text, (100,100)) 
 
            # --- copy back buffer surface pixels to the screen, resize it if needed and keep aspect ratio 
            # --- (screen size may be different from Kinect's color frame size)  
            h_to_w = float(self._frame_surface.get_height()) / self._frame_surface.get_width() 
            target_height = int(h_to_w * self._screen.get_width()) 
            surface_to_draw = pygame.transform.scale(self._frame_surface, (self._screen.get_width(), target_height))
            self._screen.blit(surface_to_draw, (0,0)) 
            surface_to_draw = None 
            pygame.display.update() 
 
            # --- Limit to 60 frames per second 
            self._clock.tick(60) 
 
        # Close our Kinect sensor, close the window and quit. 
        self._kinect.close() 
        pygame.quit() 
 
game = GameRuntime()
game.run()