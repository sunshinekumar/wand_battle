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

        self.prev_left_hand_height2 = 0 
        self.cur_left_hand_height2 = 0 
        self.left_hand_lift2 = 0
        self.tutorial_up2 = 0

        self.prev_left_hand_width = 0 
        self.cur_left_hand_width = 0 
        self.left_hand_swipe = 0
        self.left_hand_power_weight = .14

        self.prev_left_hand_width2 = 0 
        self.cur_left_hand_width2 = 0 
        self.left_hand_swipe2 = 0

        self.right_hand_pos = (0,0)
        self.radius_to_track = 50
        self.is_wand_tracking = 0
        self.is_wand_tracking2 = 0
        self.wand_width = 30
        self.wand_width2 = 20

        self.wand_color = (255,0,0)
        self.wand_grip_color = (200,200,200)
        self.wand_wide = 90    #For drawing the wand
        self.wand_high = 90

        self.wand_pos = (self.screen_width//4, self.screen_height*3/5)   #Will be set to right hand pos if right hand closes on it
        self.wand_tip = (self.wand_pos[0] + self.wand_wide, self.wand_pos[1] + self.wand_high)
        self.default_wand_pos = self.wand_pos
        self.default_wand_tip = self.wand_tip
        self.wand_scale = 1.2
        self.grip_proportion = .2
        self.grip_width_proportion = 1.2

        self.wand_color2 = (0,0,255)
        self.wand_grip_color2 = (200,200,200)
        self.wand_wide2 = 90
        self.wand_high2 = 90

        self.wand_pos2 = (self.screen_width//4 * 3, self.screen_height * 3/5)
        self.wand_tip2 = (self.wand_pos2[0] + self.wand_wide, self.wand_pos2[1] + self.wand_high)
        self.default_wand_pos2 = self.wand_pos2
        self.default_wand_tip2 = self.wand_tip2
        self.wand_scale2 = 1.5
        self.grip_proportion2 = .2
        self.grip_width_proportion2 = 1.3

        
        self.health_color = (0,0,255)
        self.power_color = (255,255,255)
        self.bar_height = 30
        self.bar_dist_from_head = 60
        self.player_label_distance = 60
        self.player_label_radius = 20

        self.body_list = [-1,-1]

        self.max_health = 100
        self.health = self.max_health

        self.max_health2 = 100
        self.health2 = self.max_health2

        self.max_power = 50
        self.power = self.max_power-30
        self.power_increase = 1

        self.max_power2 = 50
        self.power2 = self.max_power2-30
        self.power_increase2 = 1


        self.trace = [] #Used to store player 1's trace of the circles
        self.trace2 = [] #Same for player 2
        
        self.max_spell_length = 4
        self.max_spell_length2 = 4

        #To draw the spellcasting circles
        self.circle_separation_radius = 200
        self.circle_radius = 50
        self.spell_circle_color = self.wand_color
        self.circles = []

        self.circle_separation_radius2 = 200
        self.circle_radius2 = 50
        self.spell_circle_color2 = self.wand_color2
        self.circles2 = []


        # Defining spells
        (self.north,self.south, self.east, self.west) = (0,1,2,3)

        #They are easier to reference as variable names
        self.expelliarmus = "Expelliarmus"
        self.stupefy = "Stupefy"
        self.protego = "Protego"

        self.spell_book = dict()        
        self.spell_book = {(self.south, self.north): self.expelliarmus , 
                           (self.north, self.south): self.stupefy, 
                           (self.west, self.north, self.east): self.protego}
        """
        E will make the wand reset back to the original spot and reset the opponent's spell trace
            Uses 20 power
        Stupefy takes off 30 health
            Uses 30 power
        Protego protects against next spell cast, but stops caster from casting another spell
            Uses 50 power
        Swiping right with the left hand to restore power

        """
        #Effects due to spells
        self.blocking  = False
        self.blocking2 = False

        self.spell = ""
        self.spell2 = ""

        #Because the wand is still in the circle after casting the spell
        # and we don't want this to roll over to the next trace
        # But we still want the current circle to be an option
        self.spell_residue = 0
        self.spell_residue2 = 0
 
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
        grip = (self.wand_pos[0] + (self.wand_tip[0]-self.wand_pos[0]) * self.grip_proportion, 
                self.wand_pos[1] + (self.wand_tip[1]-self.wand_pos[1]) * self.grip_proportion)
        pygame.draw.line(self._frame_surface, self.wand_color, self.wand_pos, 
                         self.wand_tip, self.wand_width)
        #To make wand Grip 1
        pygame.draw.line(self._frame_surface, self.wand_grip_color, self.wand_pos, grip, int(self.wand_width * self.grip_width_proportion))

        # wand 2
        pygame.draw.line(self._frame_surface, self.wand_color2, self.wand_pos2,
                         self.wand_tip2, self.wand_width2)
        
        
        grip2 = (self.wand_pos2[0] + (self.wand_tip2[0]-self.wand_pos2[0]) * self.grip_proportion2, 
                 self.wand_pos2[1] + (self.wand_tip2[1]-self.wand_pos2[1]) * self.grip_proportion2)
        #To make wand Grip 2
        pygame.draw.line(self._frame_surface, self.wand_grip_color2, self.wand_pos2, grip2, int(self.wand_width2 * self.grip_width_proportion2))



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
        south = (north[0], north[1] + self.circle_separation_radius*5//2)
        east =  (north[0] + self.circle_separation_radius, north[1] + self.circle_separation_radius)
        west = (east[0] - self.circle_separation_radius * 2, east[1])
        self.circles = [north, south, east, west] 
        self.circle_radius = abs(int(joint_points[PyKinectV2.JointType_Head].y - joint_points[PyKinectV2.JointType_SpineShoulder].y))//2
        for center in self.circles:
            pygame.draw.circle(self._frame_surface, self.spell_circle_color, (int(center[0]), int(center[1])) , self.circle_radius, 10) 

    def draw_circles2(self, joint_points):
        # Gets centers of where each circle should be
        self.circle_separation_radius2 = abs(joint_points[PyKinectV2.JointType_HipLeft].y - joint_points[PyKinectV2.JointType_Head].y)//2
        north = (joint_points[PyKinectV2.JointType_Head].x,joint_points[PyKinectV2.JointType_Head].y) 
        south = (north[0], north[1] + self.circle_separation_radius2*5//2)
        east =  (north[0] + self.circle_separation_radius2, north[1] + self.circle_separation_radius2)
        west = (east[0] - self.circle_separation_radius2 * 2, east[1])
        self.circles2 = [north, south, east, west] 
        self.circle_radius2 = abs(int(joint_points[PyKinectV2.JointType_Head].y - joint_points[PyKinectV2.JointType_SpineShoulder].y))//2
        for center in self.circles2:
            pygame.draw.circle(self._frame_surface, self.spell_circle_color2, (int(center[0]), int(center[1])) , self.circle_radius2, 10) 

    def draw_health_power(self, joint_points):
        head = (int(joint_points[PyKinectV2.JointType_Head].x), int(joint_points[PyKinectV2.JointType_Head].y))
        health_rect = (int(head[0] - self.health//2), int(head[1] - self.bar_dist_from_head - self.bar_height), self.health, self.bar_height)
        power_rect =  (int(head[0] - self.power//2), int(head[1] - self.bar_dist_from_head - self.bar_height*2), self.power, self.bar_height)

        pygame.draw.rect(self._frame_surface, self.health_color, (health_rect)) # Health bar
        pygame.draw.rect(self._frame_surface, self.power_color, (power_rect)) # Power bar
        pygame.draw.circle(self._frame_surface, self.wand_color, (head[0], head[1] + self.player_label_distance), self.player_label_radius)

    def draw_health_power2(self, joint_points):
        head = (int(joint_points[PyKinectV2.JointType_Head].x), int(joint_points[PyKinectV2.JointType_Head].y))
        health_rect2 = (int(head[0] - self.health2//2), int(head[1] - self.bar_dist_from_head - self.bar_height), self.health2, self.bar_height)
        power_rect2 =  (int(head[0] - self.power2//2), int(head[1] - self.bar_dist_from_head - self.bar_height*2), self.power2, self.bar_height)

        pygame.draw.rect(self._frame_surface, self.health_color, (health_rect2)) # Health bar
        pygame.draw.rect(self._frame_surface, self.power_color, (power_rect2)) # Power bar
        pygame.draw.circle(self._frame_surface, self.wand_color2, (head[0], head[1] + self.player_label_distance), self.player_label_radius)


    def tip_is_in(self, center, radius, tip):   #Why yes, I AM still a middle schooler at heart
        temp = abs(center[0] - tip[0])**2 + abs(center[1] - tip[1])**2 
        return temp < radius**2
 
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
                            if i == self.body_list[0]: self.body_list[0] = -1
                            if i == self.body_list[1]: self.body_list[1] = -1
                            continue
                        
                        if self.body_list[0] == -1 or i == self.body_list[0]:
                            self.body_list[0] = i
                            joints = body.joints  
                            joint_points = self._kinect.body_joints_to_color_space(joints)  #From Josh Moavenzadeh (jmoavenz)
                            
                            if joints[PyKinectV2.JointType_Head].TrackingState != PyKinectV2.TrackingState_NotTracked:
                                self.draw_health_power(joint_points)

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
                                    self.wand_wide = self.wand_scale * (joint_points[PyKinectV2.JointType_WristRight].x - joint_points[PyKinectV2.JointType_ElbowRight].x)
                                    self.wand_high = self.wand_scale * (joint_points[PyKinectV2.JointType_WristRight].y - joint_points[PyKinectV2.JointType_ElbowRight].y)

                                    #self.wand_wide = abs(joint_points[PyKinectV2.JointType_Head].y - joint_points[PyKinectV2.JointType_Neck].y)
                                    #self.wand_high = self.wand_wide

                                    self.wand_pos = (joint_points[PyKinectV2.JointType_HandRight].x, joint_points[PyKinectV2.JointType_HandRight].y)
                                    self.wand_tip = (self.wand_pos[0] + self.wand_wide, self.wand_pos[1] + self.wand_high) 
                                    if(body.hand_right_state == PyKinectV2.HandState_Open): self.is_wand_tracking = 0
                                    #Draw the circles on the body if the wand is tracking
                                    if joints[PyKinectV2.JointType_Head].TrackingState != PyKinectV2.TrackingState_NotTracked:
                                        self.draw_circles(joint_points)


                            #To save the new left hand height and width
                            if joints[PyKinectV2.JointType_HandLeft].TrackingState != PyKinectV2.TrackingState_NotTracked: 
                                self.cur_left_hand_height = joints[PyKinectV2.JointType_HandLeft].Position.y 
                                self.cur_left_hand_width = joints[PyKinectV2.JointType_HandLeft].Position.x
                            


 
                            # calculate how fast we lift the left hand to see if we bring up the tutorial
                            self.left_hand_lift = (self.cur_left_hand_height - self.prev_left_hand_height)
                            if math.isnan(self.left_hand_lift): 
                                self.left_hand_lift = 0 
                            if(abs(self.left_hand_lift) > self.left_hand_tutorial_weight): 
                                if self.left_hand_lift < 0: #Pulls down the tutorial if we push down
                                    self.tutorial_up = 0
                                elif(self.left_hand_lift > 0): 
                                    self.tutorial_up = 1  #Brings up the tutorial if we lift up

                            # calculate how fast we swipe the left hand to see if add power
                            self.left_hand_swipe = (self.cur_left_hand_width - self.prev_left_hand_width)
                            if math.isnan(self.left_hand_swipe): 
                                self.left_hand_swipe = 0 
                            if(abs(self.left_hand_swipe) > self.left_hand_power_weight): 
                                if(self.left_hand_swipe > 0): 
                                    self.power+=self.power_increase  #Brings up the power if we swipe right
                                    if self.power > self.max_power: self.power = self.max_power
 
                            # cycle previous and current heights and widths for next time 
                            self.prev_left_hand_height = self.cur_left_hand_height
                            self.prev_left_hand_width = self.cur_left_hand_width

                        
                        if i != self.body_list[0]:
                            self.body_list[1] = i
                            joints = body.joints  
                            joint_points = self._kinect.body_joints_to_color_space(joints)  #From Josh Moavenzadeh (jmoavenz)
                                
                            if joints[PyKinectV2.JointType_Head].TrackingState != PyKinectV2.TrackingState_NotTracked:
                                self.draw_health_power2(joint_points)

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
                                    self.wand_wide2 = self.wand_scale2 * (joint_points[PyKinectV2.JointType_WristRight].x - joint_points[PyKinectV2.JointType_ElbowRight].x)
                                    self.wand_high2 = self.wand_scale2 * (joint_points[PyKinectV2.JointType_WristRight].y - joint_points[PyKinectV2.JointType_ElbowRight].y)



                                    self.wand_pos2 = (joint_points[PyKinectV2.JointType_HandRight].x, joint_points[PyKinectV2.JointType_HandRight].y)
                                    self.wand_tip2 = (self.wand_pos2[0] + self.wand_wide2, self.wand_pos2[1] + self.wand_high2) 
                                    if(body.hand_right_state == PyKinectV2.HandState_Open): self.is_wand_tracking2 = 0
                                    #Draw the circles on the body if the wand is tracking
                                    if joints[PyKinectV2.JointType_Head].TrackingState != PyKinectV2.TrackingState_NotTracked:
                                        self.draw_circles2(joint_points)


                            #To save the new left hand height and width
                            if joints[PyKinectV2.JointType_HandLeft].TrackingState != PyKinectV2.TrackingState_NotTracked: 
                                self.cur_left_hand_height2 = joints[PyKinectV2.JointType_HandLeft].Position.y 
                                self.cur_left_hand_width2 = joints[PyKinectV2.JointType_HandLeft].Position.x

                            
                            


 
                            # calculate how fast we lift the left hand to see if we bring up the tutorial
                            self.left_hand_lift2 = (self.cur_left_hand_height2 - self.prev_left_hand_height2)
                            if math.isnan(self.left_hand_lift2): 
                                self.left_hand_lift2 = 0 
                            if(abs(self.left_hand_lift2) > self.left_hand_tutorial_weight): 
                                if self.left_hand_lift2 < 0: #Pulls down the tutorial if we push down
                                    self.tutorial_up2 = 0
                                elif(self.left_hand_lift2 > 0): 
                                    self.tutorial_up2 = 1  #Brings up the tutorial if we lift up

                            # calculate how fast we swipe the left hand to see if add power
                            self.left_hand_swipe2 = (self.cur_left_hand_width2 - self.prev_left_hand_width2)
                            if math.isnan(self.left_hand_swipe2): 
                                self.left_hand_swipe2 = 0 
                            if(abs(self.left_hand_swipe2) > self.left_hand_power_weight): 
                                if(self.left_hand_swipe2 > 0): 
                                    self.power2 += self.power_increase2  #Brings up the power if we swipe right
                                    if self.power2 > self.max_power2: self.power2 = self.max_power2
 
                            # cycle previous and current heights and widths for next time 
                            self.prev_left_hand_height2 = self.cur_left_hand_height2
                            self.prev_left_hand_width2 = self.cur_left_hand_width2



 
            # --- Game logic 
            
            
            #Player 1 wand trace

            #Reasons to clear a trace
            if(len(self.trace) > self.max_spell_length):
                self.trace = []

            if self.spell != "":
                self.spell_residue = 1
                self.spell = ""
                self.trace = []

            #Code the clear spell action here

            for centerIndex in range(len(self.circles)):
                center, radius = self.circles[centerIndex], self.circle_radius
                tip = self.wand_tip
                # So here's what about to happen:
                # We are going to see if the wand tip is in a specific circle. But:
                # 1. we don't want to add something every time the timer fires, so we make circles non retraceable. But:
                # 2. That would throw index out of bounds. But:
                # 3. Using an empty list as an allowed bypass leads to a residue from a previous spell's trace into the next one. So:
                # 4. We code in a residue flag that turns off once the tip leaves its current circle. 
                '''
                if (self.spell_residue == 1): 
                    print(self.tip_is_in(center, radius, tip))
                    #print(self.tip_is_in(center, radius, tip))
                    if(not self.tip_is_in(center, radius, tip)):
                        #print("plz")
                        self.spell_residue = 0
                        #print(self.trace)
                '''
                print(self.tip_is_in(center, radius, tip))
                if (self.tip_is_in(center, radius, tip) and (self.trace == [] or self.trace[-1] != centerIndex) and not self.spell_residue):
                    #print(self.spell_residue)
                    self.trace.append(centerIndex)
                    print(self.trace)
                if(self.spell_residue == 1):
                    self.trace = []
                    print(" "*5, self.tip_is_in(center, radius, tip))

            if tuple(self.trace) in self.spell_book:
                self.spell = self.spell_book[tuple(self.trace)]
                print(self.spell)

            #Player 1 spellcasting
            if not self.blocking2:
                if self.spell == self.stupefy:
                    self.health2 -= 30
                    print("Cast Stupefy!")
                if self.spell == self.expelliarmus:
                    print("Cast Expelliarmus!")
                    self.is_wand_tracking2 = False
                    self.wand_pos2 = self.default_wand_pos2
                    self.wand_tip2 = self.default_wand_tip2
                if self.spell == self.protego:
                    print("Shield Up!")
                    self.blocking = True
            else: 
                print("Blocked by player 2!!")
                self.blocking2 = False



            #Player 2 wand trace


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