#Built upon flap.py kinect demo. Can be found at 
# http://tinyurl.com/gon96pk
#Also referenced pygame optional lecture, can be found at 
# http://tinyurl.com/npy9e6b
#Sounds from:
# https://www.youtube.com/watch?v=29fvdnzZ0cw
# http://soundfxcenter.com/
# https://www.youtube.com/watch?v=1MK78oTKFGM
# http://soundbible.com/1610-Power-Failure.html
# http://www.sounddogs.com/results.asp?Type=&CategoryID=1038&SubcategoryID=61
from pykinect2 import PyKinectV2, PyKinectRuntime 
from pykinect2.PyKinectV2 import * 
 
import ctypes 
import _ctypes 
import pygame 
import sys 
import math 
import random
 
class GameRuntime(object): 
    def __init__(self): 
        pygame.init() 
 
        self.screen_width = 1920 
        self.screen_height = 1080

        self.flag1 = 0
        self.flag2 = 0

        self.prev_left_hand_height = 0 
        self.cur_left_hand_height = 0 
        self.left_hand_lift = 0
        self.left_hand_tutorial_weight = .16
        self.tutorial_up = 0

        self.prev_left_hand_height2 = 0 
        self.cur_left_hand_height2 = 0 
        self.left_hand_lift2 = 0
        self.tutorial_up2 = 0

        
        self.prev_left_hand_width = 0 
        self.cur_left_hand_width = 0 
        self.left_hand_swipe = 0
        self.left_hand_power_weight = .16

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

        self.wand_pos = (self.screen_width//2, self.screen_height*3/5)   #Will be set to right hand pos if right hand closes on it
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

        
        self.health_color = (0,190, 0)
        self.health_color_full = (0,255,0)
        self.health_color_warning = (180, 0, 0)
        self.warning_percent = .2
        self.power_color = (100,100,100)
        self.power_color_full = (0,0,0)
        self.bar_height = 60
        self.bar_dist_from_head = 100
        self.player_label_distance = 150
        self.player_label_radius = 20

        self.body_list = [-1,-1]

        self.max_health = 100
        self.health = self.max_health

        self.max_health2 = 100
        self.health2 = self.max_health2

        self.max_power = 70
        self.power = self.max_power-30
        self.power_increase = 5

        self.max_power2 = 70
        self.power2 = self.max_power2-30
        self.power_increase2 = 5

        self.insufficient_power_sound = 'Sound Files/Insufficient Power.mp3'

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

        self.circle_text_size = 90
        self.circle_text_size2 = 90


        #Start circles
        (self.start, self.practice, self.tutorial, self.customize) = (0,1,2,3)

        # Defining spells
        (self.north,self.south, self.east, self.west, self.clear) = (0,1,2,3,4)

        #They are easier to reference as variable names
        
        self.expelliarmus = "Expelliarmus"
        self.expelliarmus_power = 20
        self.expelliarmus_sound = 'Sound Files/Expelliarmus.mp3'

        self.stupefy = "Stupefy"
        self.stupefy_power = 30
        self.stupefy_sound = 'Sound Files/Stupefy.mp3'

        self.stupefy_damage = 30
        self.protego = "Protego"
        self.protego_sound = 'Sound Files/Protego.mp3'
        self.deflect_sound = 'Sound Files/deflect.mp3'

        self.protego_power = 50
        self.avada_kedavra_sound = 'Sound Files/Avada Kedavra.mp3'
        self.avada_kedavra_chance = .05
        self.avada_kedavra_power = (self.max_power + self.max_power2)//2    #Makes sure it can only be cast once

        self.spell_shot_sound = 'Sound Files/Spell cast.mp3'

        self.spell_book = dict()        
        self.spell_book = {(self.south, self.north): self.expelliarmus, 
                           (self.east, self.west): self.stupefy, 
                           (self.west, self.north, self.east): self.protego}
        
        self.tutorial_text = "Expelliarmus (south, north) \nStupefy (east, west) \nProtego (west, north, east)"
        self.tutorial_text_size = 60
        self.tutorial_color = (0,0,0)
        #Effects due to spells
        self.blocking  = False
        self.blocking2 = False

        self.spell = ""
        self.spell2 = ""

        self.damage_modifier = 1
        self.damage_modifier2 = 1

        #Modes

        #Intro Screen
        self.title_screen = 1
        self.title_image = ''
        self.title_text = "DUEL"
        self.title_text_size = 200
        self.title_color = (255,255,255)

        self.pause_radius = .05

        self.winner = -1
        self.start_screen = 1
        self.start_screen_sound = 'Sound Files/Start screen.mp3'
        #pygame.mixer.music.load(self.start_screen_sound)
        #pygame.mixer.music.play(-1)
        self.start_screen_music_flag = 0
        self.back_to_start_time = 0
        self.back_to_start_time2 = 0

        self.do_your_duty = 'Sound Files/Do your duty.mp3'
        self.do_your_duty_end_flag = 1
        self.do_your_duty_start_flag = 1    #Change these to get this-----------------------------------


        #Victory
        self.victory_text = ["\nIS VICTORIOUS", 
                             "Wins!", 
                             "is the superior wizard", 
                             "\nCRUSHED THE OPPOSITION", 
                             "was merciless", 
                             ", Harambe would be proud", #From Rohit Srungavarapu (rsrungav)
                             ", well done!"]
        self.victory_text_size = 100
        self.win_text_index = 0
        self.win_text_flag = 0
        self.winner_sound = 'Sound Files/Player 1 wins.mp3'
        self.winner_sound1 = 'Sound Files/Player 2 wins.mp3'
        self.winner_flag = 0

        self.backfired_sound = 'Sound Files/Backfired.mp3'

        #Practice
        self.practice_mode = 0

        #Customize
        self.customize_mode = 0

        #Main Tutorial
        self.main_tutorial = 0
        self.main_tutorial_text_size = 40
        self.main_tutorial_text = """WELCOME TO THE SPELLCASTING 101
        \nExpelliarmus (south, north) - Uses 20 power
        \n     will make the wand reset back to the original spot and reset the opponent's spell trace
        \nStupefy (east, west) - Uses 30 power
        \n    takes off 30 health
        \nProtego (west, north, east) - Uses 50 power
        \n    protects against next spell cast, but stops caster from casting another spell
        \nAvada Kedavra - The Killing Curse (north, south, east, west)
        \n    Has a 5% chance of killing the opponent immediately
        \n    If it does not, however, you will be cursed, and all your attacks do half as much damage and your max power is cut in half
        \nSwiping right with the left hand restores power
        \nSwiping up with the left hand brings up the mini tutorial
        \nSwiping down with the left hand closes the mini tutorial
        \nPractice mode is a one player mode where a backfired spell cannot damage you
        \nIn Customize mode, move the wand around to adjust width/ height and move the left hand around to adjust wand color
        \n    release the wand and bring your right hand to your left to confirm
        \nFrom anywhere, put your hands together to pause your game and return to the start screen
        """

        #Because the wand is still in the circle after casting the spell
        # and we don't want this to roll over to the next trace
        # But we still want the current circle to be an option
        self.spell_clear = 0
        self.spell_clear2 = 0
 
        # Used to manage how fast the screen updates 
        self._clock = pygame.time.Clock()
 
        # Set the width and height of the window [width/2, height/2] 
        # Change this to make it fullscreen or not
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
        if not self.practice_mode:
            pygame.draw.line(self._frame_surface, self.wand_color2, self.wand_pos2,
                             self.wand_tip2, self.wand_width2)
        
        
            grip2 = (self.wand_pos2[0] + (self.wand_tip2[0]-self.wand_pos2[0]) * self.grip_proportion2, 
                     self.wand_pos2[1] + (self.wand_tip2[1]-self.wand_pos2[1]) * self.grip_proportion2)
            #To make wand Grip 2
            pygame.draw.line(self._frame_surface, self.wand_grip_color2, self.wand_pos2, grip2, int(self.wand_width2 * self.grip_width_proportion2))


    def draw_tutorials(self):
        # tutorial 1
        if(self.tutorial_up == 1):
            self.draw_text(self.tutorial_text, (0,0), self.wand_color, self.tutorial_text_size, "NE")
            #pygame.draw.rect(self._frame_surface, self.wand_color, (0,0,200,200))
        # tutorial 2
        if(self.tutorial_up2 == 1):
            #self.draw_text(self.tutorial_text, (self.screen_width//2,0), self.wand_color, self.tutorial_text_size, "NE")
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
        clear = (north[0] - self.circle_separation_radius*5//4, north[1])
        self.circle_radius = abs(int(joint_points[PyKinectV2.JointType_Head].y - joint_points[PyKinectV2.JointType_SpineShoulder].y))//2
        self.circles = [north, south, east, west, clear]
        for center in self.circles:
            pygame.draw.circle(self._frame_surface, self.spell_circle_color, (int(center[0]), int(center[1])) , self.circle_radius, 10) 
        
        #This is the code for drawing all circles text
        self.circle_text_size =  abs(int(joint_points[PyKinectV2.JointType_Head].y - joint_points[PyKinectV2.JointType_SpineShoulder].y))
        text = ['north', 'south', 'east', 'west', 'clear']
        for i in range(len(self.circles)):
            self.draw_text(text[i], (self.circles[i][0], self.circles[i][1] - self.circle_radius*2), self.wand_color, self.circle_text_size)

        if self.blocking:
            pygame.draw.polygon(self._frame_surface, self.wand_color, [north, east, south, west])
            

    def draw_start_circles(self, joint_points):
        north = (joint_points[PyKinectV2.JointType_Head].x,joint_points[PyKinectV2.JointType_Head].y) 
        start = (north[0] - self.circle_separation_radius, north[1])
        practice = (north[0] + self.circle_separation_radius, north[1])
        tutorial = (north[0] + self.circle_separation_radius, north[1] + self.circle_separation_radius * 2)
        customize = (north[0] - self.circle_separation_radius, north[1] + self.circle_separation_radius * 2)
        self.circle_radius = abs(int(joint_points[PyKinectV2.JointType_Head].y - joint_points[PyKinectV2.JointType_SpineShoulder].y))//2
        self.circles = [start, practice, tutorial, customize]
        for center in self.circles:
            pygame.draw.circle(self._frame_surface, self.spell_circle_color, (int(center[0]), int(center[1])) , self.circle_radius, 10) 

        #This is the code for drawing all circles text
        self.circle_text_size =  abs(int(joint_points[PyKinectV2.JointType_Head].y - joint_points[PyKinectV2.JointType_SpineShoulder].y))
        text = ["start", "practice", "tutorial", "customize"]
        for i in range(len(self.circles)):
            self.draw_text(text[i], (self.circles[i][0], self.circles[i][1] - self.circle_radius*2), self.wand_color, self.circle_text_size)


    def draw_circles2(self, joint_points):
        # Gets centers of where each circle should be
        self.circle_separation_radius2 = abs(joint_points[PyKinectV2.JointType_HipLeft].y - joint_points[PyKinectV2.JointType_Head].y)//2
        north = (joint_points[PyKinectV2.JointType_Head].x,joint_points[PyKinectV2.JointType_Head].y) 
        south = (north[0], north[1] + self.circle_separation_radius2*5//2)
        east =  (north[0] + self.circle_separation_radius2, north[1] + self.circle_separation_radius2)
        west = (east[0] - self.circle_separation_radius2 * 2, east[1])
        clear = (north[0] - self.circle_separation_radius2*5//4, north[1])
        if not self.start_screen:
            self.circles2 = [north, south, east, west, clear] 
        else: self.circles2 = [clear]
        self.circle_radius2 = abs(int(joint_points[PyKinectV2.JointType_Head].y - joint_points[PyKinectV2.JointType_SpineShoulder].y))//2
        for center in self.circles2:
            pygame.draw.circle(self._frame_surface, self.spell_circle_color2, (int(center[0]), int(center[1])) , self.circle_radius2, 10) 
        
        #This is the code for drawing all circles text
        self.circle_text_size2 =  abs(int(joint_points[PyKinectV2.JointType_Head].y - joint_points[PyKinectV2.JointType_SpineShoulder].y))
        text = ['north', 'south', 'east', 'west', 'clear']
        for i in range(len(self.circles)):
            self.draw_text(text[i], (self.circles2[i][0], self.circles2[i][1] - self.circle_radius2*2), self.wand_color2, self.circle_text_size2)

        
        if self.blocking2:
            pygame.draw.polygon(self._frame_surface, self.wand_color2, [north, east, south, west])

    def draw_start_circles2(self, joint_points):
        
        north = (joint_points[PyKinectV2.JointType_Head].x,joint_points[PyKinectV2.JointType_Head].y) 
        start = (north[0] - self.circle_separation_radius, north[1])
        #practice = (north[0] + self.circle_separation_radius, north[1])
        tutorial = (north[0] + self.circle_separation_radius, north[1] + self.circle_separation_radius * 2)
        customize = (north[0] - self.circle_separation_radius, north[1] + self.circle_separation_radius * 2)
        self.circle_radius2 = abs(int(joint_points[PyKinectV2.JointType_Head].y - joint_points[PyKinectV2.JointType_SpineShoulder].y))//2
        self.circles2 = [start, tutorial, customize]
        for center in self.circles:
            pygame.draw.circle(self._frame_surface, self.spell_circle_color, (int(center[0]), int(center[1])) , self.circle_radius, 10) 

        #This is the code for drawing all circles text
        self.circle_text_size =  abs(int(joint_points[PyKinectV2.JointType_Head].y - joint_points[PyKinectV2.JointType_SpineShoulder].y))
        text = ["start", "tutorial", "customize"]
        for i in range(len(self.circles)):
            self.draw_text(text[i], (self.circles[i][0], self.circles[i][1] - self.circle_radius*2), self.wand_color, self.circle_text_size)

        

    def draw_health_power(self, joint_points):
        head = (int(joint_points[PyKinectV2.JointType_Head].x), int(joint_points[PyKinectV2.JointType_Head].y))
        health_rect = (int(head[0] - self.health//2), int(head[1] - self.bar_dist_from_head - self.bar_height), self.health, self.bar_height)
        power_rect =  (int(head[0] - self.power//2), int(head[1] - self.bar_dist_from_head - self.bar_height*2), self.power, self.bar_height)

        if self.health == self.max_health:
            pygame.draw.rect(self._frame_surface, self.health_color_full, (health_rect)) # Health bar
        elif self.health <= self.max_health * self.warning_percent:
            pygame.draw.rect(self._frame_surface, self.health_color_warning, (health_rect)) # Health bar
        else:
            pygame.draw.rect(self._frame_surface, self.health_color, (health_rect)) # Health bar
        if self.power == self.max_power:
            pygame.draw.rect(self._frame_surface, self.power_color_full, (power_rect)) # Power bar full
        else:
            pygame.draw.rect(self._frame_surface, self.power_color, (power_rect)) # Power bar 

        pygame.draw.circle(self._frame_surface, self.wand_color, (head[0], head[1] + self.player_label_distance), self.player_label_radius)

    def draw_health_power2(self, joint_points):
        head = (int(joint_points[PyKinectV2.JointType_Head].x), int(joint_points[PyKinectV2.JointType_Head].y))
        health_rect2 = (int(head[0] - self.health2//2), int(head[1] - self.bar_dist_from_head - self.bar_height), self.health2, self.bar_height)
        power_rect2 =  (int(head[0] - self.power2//2), int(head[1] - self.bar_dist_from_head - self.bar_height*2), self.power2, self.bar_height)

        if self.health2 == self.max_health2:
            pygame.draw.rect(self._frame_surface, self.health_color_full, (health_rect2)) # Health bar
        elif self.health2 <= self.max_health2 * self.warning_percent:
            pygame.draw.rect(self._frame_surface, self.health_color_warning, (health_rect2)) # Health bar
        else:
            pygame.draw.rect(self._frame_surface, self.health_color, (health_rect2)) # Health bar
        if self.power2 == self.max_power2:
            pygame.draw.rect(self._frame_surface, self.power_color_full, (power_rect2)) # Power bar full
        else:
            pygame.draw.rect(self._frame_surface, self.power_color, (power_rect2)) # Power bar 
        pygame.draw.circle(self._frame_surface, self.wand_color2, (head[0], head[1] + self.player_label_distance), self.player_label_radius)

    def draw_winner(self):
        if not self.win_text_flag:
            self.winTextIndex = random.randint(0,len(self.victory_text)-1)
            self.win_text_flag = 1
        winText = self.victory_text[self.winTextIndex]
        if self.winner == 1:
            if self.winner_flag == 0:
                pygame.mixer.music.load(self.winner_sound)
                pygame.mixer.music.play()
                self.winner_flag = 1
            pygame.draw.rect(self._frame_surface, (0,0,0) , (0,0,self.screen_width, self.screen_height))
            self.draw_text("Player 1 " + winText, (self.screen_width//2, self.screen_height//2), self.wand_color, self.victory_text_size)
        if self.winner == 2:
            if self.winner_flag == 0:
                pygame.mixer.music.load(self.winner_sound1)
                pygame.mixer.music.play()
                self.winner_flag = 1
            pygame.draw.rect(self._frame_surface, (0,0,0), (0,0,self.screen_width, self.screen_height))
            self.draw_text("Player 2 " + winText, (self.screen_width//2, self.screen_height//2), self.wand_color2, self.victory_text_size)

    def draw_main_tutorial(self):
        if self.main_tutorial:
            pygame.draw.rect(self._frame_surface, (255,255,255), (0,0,self.screen_width, self.screen_height))
            self.draw_text(self.main_tutorial_text, (0,0), (0,0,0), self.main_tutorial_text_size, "NE")

    def tip_is_in(self, center, radius, tip):
        temp = abs(center[0] - tip[0])**2 + abs(center[1] - tip[1])**2 
        return temp < radius**2

    def draw_text(self, text, location, color, size, anchor = "center"):
        textLines = text.split("\n")
        pygame.font.init()
        font = pygame.font.Font(None, size)
        for i in range(len(textLines)):
            tWidth, tHeight = font.size(textLines[i])
            toWrite = font.render(textLines[i], True, color)
            if anchor == "center":
                self._frame_surface.blit(toWrite, (location[0] - tWidth//2, location[1]-tHeight//2 + tHeight*i))
            elif anchor == "NE":
                self._frame_surface.blit(toWrite, (location[0], location[1] + tHeight*i))

    def play_spell(self,sound):
        pygame.mixer.music.stop()
        pygame.mixer.music.load(sound)
        pygame.mixer.music.play()
        pygame.mixer.music.queue(self.spell_shot_sound)

    def play(self, sound):
        pygame.mixer.music.stop()
        pygame.mixer.music.load(sound)
        pygame.mixer.music.play()

    def back_to_start_screen(self):
        self.start_screen = 1
        self.start_screen_music_flag = 0
        self.practice_mode = 0
        self.main_tutorial = 0
        self.customize_mode = 0
        self.title_screen = 0
        self.do_your_duty_start_flag = 0
        self.do_your_duty_end_flag = 0
        if self.start_screen_music_flag == 0:
            pygame.mixer.music.load(self.start_screen_sound)
            pygame.mixer.music.play(-1)
            self.start_screen_music_flag = 1

    def reset_game(self):
        self._kinect.close() 
        pygame.quit() 
        game.__init__()
        game.run()
    
    def draw_title_screen(self):
        if(self.title_screen):
            pygame.draw.rect(self._frame_surface, (0,0,0), (0,0,self.screen_width, self.screen_height))
            self.draw_text(self.title_text, (self.screen_width//2, self.title_text_size//2), self.title_color, self.title_text_size) 


        #-----------------------------------
        #from Josh Moavenzadeh (jmoavenz)
        #pygame.font.init()
        #font = pygame.font.Font(None, size)
        #tWidth, tHeight = font.size(text)
        #toWrite = font.render(text, True, color)
        #if anchor == "center":
        #    self._frame_surface.blit(toWrite, (location[0] - tWidth//2, location[1]-tHeight//2))
        #elif anchor == "NE":
        #    self._frame_surface.blit(toWrite, (location[0], location[1]))
        #-----------------------------------
 
    def run(self): 
        # -------- Main Program Loop ----------- 
        while not self._done: 
            # --- Main event loop 
            for event in pygame.event.get(): # User did something 
                if event.type == pygame.KEYDOWN:
                    if pygame.key.name(event.key) == 'escape':
                        self._done = True
                    #if pygame.key.name(event.key) in '1234567890': #For easy testing of spell tracing------------------
                    #    self.start_screen = 0
                    #    self.trace.append(int(pygame.key.name(event.key)))
                    #    print(self.trace)
                    elif(pygame.key.name(event.key) == '1'):
                        self.winner_flag = 0
                        self.winner = 1
                    elif(pygame.key.name(event.key) == '2'):
                        self.winner_flag = 0
                        self.winner = 2
                    else: self.win_text_flag = 0  #To test the win screen--------------------
                    #print(pygame.key.name(event.key))
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
                                    if(joints[PyKinectV2.JointType_Head].TrackingState != PyKinectV2.TrackingState_NotTracked 
                                        and joints[PyKinectV2.JointType_HipLeft].TrackingState != PyKinectV2.TrackingState_NotTracked
                                        and joints[PyKinectV2.JointType_SpineShoulder].TrackingState != PyKinectV2.TrackingState_NotTracked):
                                        if self.start_screen:
                                            self.draw_start_circles(joint_points)
                                        else: 
                                            if self.start_screen_music_flag == 1:
                                                pygame.mixer.music.stop()
                                                self.start_screen_music_flag = 2
                                             
                                            if not self.practice_mode and not self.main_tutorial and not self.customize_mode:   
                                                if self.do_your_duty_start_flag == 0:
                                                    pygame.mixer.music.load(self.do_your_duty)
                                                    print("loaded do your duty")
                                                    pygame.mixer.music.play()
                                                    self.do_your_duty_start_flag = 1
                                                    print("Started do your duty")
                                                #If it's not over but the sound channel is empty
                                                if(self.do_your_duty_end_flag == 0 and not pygame.mixer.music.get_busy()): 
                                                    self.do_your_duty_end_flag = 1
                                                    print("Do your duty was stopped")
                                            self.draw_circles(joint_points)
                                        #print(self.circles)


                            #To save the new left hand height and width
                            if joints[PyKinectV2.JointType_HandLeft].TrackingState != PyKinectV2.TrackingState_NotTracked: 
                                self.cur_left_hand_height = joints[PyKinectV2.JointType_HandLeft].Position.y 
                                self.cur_left_hand_width = joints[PyKinectV2.JointType_HandLeft].Position.x
                                left = (joint_points[PyKinectV2.JointType_HandLeft].x, joint_points[PyKinectV2.JointType_HandLeft].y)
                                if self.circles == []: self.spell_clear = 0
                                elif self.start_screen == 1: pass   #To stop the index out of bounds in the next line
                                elif(self.tip_is_in(self.circles[self.clear], self.circle_radius, left)):
                                    self.spell_clear = 1

                                #To pause/ return to start screen
                                if joints[PyKinectV2.JointType_HandRight].TrackingState != PyKinectV2.TrackingState_NotTracked: 
                                    left = (joints[PyKinectV2.JointType_HandLeft].Position.x, joints[PyKinectV2.JointType_HandLeft].Position.y)
                                    right = (joints[PyKinectV2.JointType_HandRight].Position.x, joints[PyKinectV2.JointType_HandRight].Position.y)
                                    if self.tip_is_in(right, self.pause_radius, left):
                                        restart = True
                                        for time in range(0,10):
                                            if not self.tip_is_in(right, self.pause_radius, left):
                                                restart = False
                                            pygame.time.delay(100)
                                        if restart:
                                            if self.winner != -1:
                                                self.reset_game()
                                            else:
                                                self.back_to_start_screen()

 
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

                        
                        if i != self.body_list[0] and not self.practice_mode:
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
                                    if (joints[PyKinectV2.JointType_Head].TrackingState != PyKinectV2.TrackingState_NotTracked 
                                        and joints[PyKinectV2.JointType_HipLeft].TrackingState != PyKinectV2.TrackingState_NotTracked
                                        and joints[PyKinectV2.JointType_SpineShoulder].TrackingState != PyKinectV2.TrackingState_NotTracked):
                                        if self.start_screen:
                                            self.draw_start_circles2(joint_points)
                                        else: 
                                            if self.start_screen_music_flag == 1:
                                                pygame.mixer.music.stop()
                                                self.start_screen_music_flag = 2
                                                
                                                pygame.mixer.music.load(self.do_your_duty)
                                            if self.do_your_duty_start_flag == 0:
                                                pygame.mixer.music.play()
                                                self.do_your_duty_start_flag = 1
                                            #If it's not over but the sound channel is empty
                                            if(self.do_your_duty_end_flag == 0 and not pygame.mixer.music.get_busy()): self.do_your_duty_end_flag = 1
                                            self.draw_circles2(joint_points)

                            #To save the new left hand height and width
                            if joints[PyKinectV2.JointType_HandLeft].TrackingState != PyKinectV2.TrackingState_NotTracked: 
                                self.cur_left_hand_height2 = joints[PyKinectV2.JointType_HandLeft].Position.y 
                                self.cur_left_hand_width2 = joints[PyKinectV2.JointType_HandLeft].Position.x
                                left = (joint_points[PyKinectV2.JointType_HandLeft].x, joint_points[PyKinectV2.JointType_HandLeft].y)
                                if self.circles2 == []: self.spell_clear2 = 0
                                elif self.start_screen == 1: pass   #To stop the index out of bounds in the next line
                                elif(self.tip_is_in(self.circles2[self.clear], self.circle_radius2, left)):
                                    self.spell_clear2 = 1

                                #To pause/ return to start screen
                                if joints[PyKinectV2.JointType_HandRight].TrackingState != PyKinectV2.TrackingState_NotTracked: 
                                    left = (joints[PyKinectV2.JointType_HandLeft].Position.x, joints[PyKinectV2.JointType_HandLeft].Position.y)
                                    right = (joints[PyKinectV2.JointType_HandRight].Position.x, joints[PyKinectV2.JointType_HandRight].Position.y)
                                    if self.tip_is_in(right, self.pause_radius, left):
                                        restart = True
                                        for i in range(0,1000):
                                            if not self.tip_is_in(right, self.pause_radius, left):
                                                restart = False
                                            pygame.time.delay(1)
                                        if restart:
                                            self.back_to_start_screen()
                                

 
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
                if self.do_your_duty_end_flag:
                    print("Spell Backfired on Player 1!")
                    self.play(self.backfired_sound)
                    self.health -= 10 + self.damage_modifier

            if self.spell != "":
                self.spell = ""
                self.trace = []

            for centerIndex in range(len(self.circles)):
                center, radius = self.circles[centerIndex], self.circle_radius
                tip = self.wand_tip
                # So here's what about to happen:
                # We are going to see if the wand tip is in a specific circle. But:
                # 1. we don't want to add something every time the timer fires, so we make circles non retraceable. But:
                # 2. That would throw index out of bounds. But:
                # 3. Using an empty list as an allowed bypass leads to a residue from a previous spell's trace into the next one. So:
                # 4. We code in a circle for the left hand to touch to clear the current spell/ to start a new spell. 
                #print(self.tip_is_in(center, radius, tip))
                if (self.tip_is_in(center, radius, tip) and (self.trace == [] or self.trace[-1] != centerIndex and not self.spell_clear)):
                    if(self.start_screen == 1):
                        if(centerIndex == self.start):
                            self.start_screen = 0
                            self.start_screen_music_flag = 1
                        if(centerIndex == self.practice):
                            self.damage_modifier = 0
                            self.damage_modifier2 = 0
                            self.start_screen = 0
                            self.start_screen_music_flag = 1
                            self.practice_mode = 1
                        if(centerIndex == self.tutorial):
                            self.main_tutorial = 1
                            self.start_screen = 0
                            self.start_screen_music_flag = 1
                            print("reached the tutorial")
                        if(centerIndex == self.customize):
                            self.customize_mode = 1
                            self.start_screen = 0
                            self.start_screen_music_flag = 1
                            

                        

                        break
                    self.trace.append(centerIndex)
                    if centerIndex == self.clear: 
                        self.trace = []
                    if self.trace != []: print("trace", self.trace)
                if(self.spell_clear): 
                    self.trace = []
                    self.spell_clear = 0
                    self.blocking = 0
                #if(self.spell_residue == 1):
                    #self.trace = []
                    #print(" "*5, self.tip_is_in(center, radius, tip))

            if (tuple(self.trace) in self.spell_book):
                self.spell = self.spell_book[tuple(self.trace)]
                #print(self.spell)
            else: self.spell = ""

            #Player 1 spellcasting
            if self.spell != "" and self.do_your_duty_end_flag:
                if not self.blocking2 and not self.blocking:
                    if self.spell == self.stupefy:
                        if self.power >= self.stupefy_power:
                            self.health2 -= self.stupefy_damage * self.damage_modifier                            
                            print("Player 1 Casts Stupefy!")
                            pygame.draw.rect(self._frame_surface, self.wand_color, (0,0,self.screen_width, self.screen_height))
                            self.play_spell(self.stupefy_sound)
                            self.power -= self.stupefy_power
                        else: 
                            print("Player 1, insufficient power")
                            self.play(self.insufficient_power_sound)
                    
                    if self.spell == self.expelliarmus:
                        if self.power >= self.expelliarmus_power:
                            print("Player 1 Casts Expelliarmus!")
                            self.play_spell(self.expelliarmus_sound)
                            self.power -= self.expelliarmus_power
                            self.is_wand_tracking2 = False
                            self.wand_pos2 = self.default_wand_pos2
                            self.wand_tip2 = self.default_wand_tip2
                        
                        else: 
                            print("Player 1, insufficient power")
                            self.play(self.insufficient_power_sound)
                    if self.spell == self.protego:
                        if self.power >= self.protego_power:
                            print("Player 1, Shield Up!")
                            self.play_spell(self.protego_sound)
                            self.power -= self.protego_power
                            self.blocking = True
                        else:
                            print("Player 1, insufficient power")
                            self.play(self.insufficient_power_sound)
                            
                elif(self.blocking):
                    print("Player 1, You can't cast a spell while you are blocking") 
                else: 
                    print("Player 1, Blocked by player 2!!")
                    self.play(self.deflect_sound)
                    self.blocking2 = False



            #Player 2 wand trace
            if not self.practice_mode:
                #Reasons to clear a trace
                if(len(self.trace2) > self.max_spell_length2):
                    self.trace2 = []
                    if self.do_your_duty_end_flag:
                        print("Spell Backfired on Player 2!")
                        self.play(self.backfired_sound)
                        self.health2 -= 10 * self.damage_modifier2

                if self.spell2 != "":
                    #self.spell_residue = 1
                    self.spell2 = ""
                    self.trace2 = []

                for centerIndex in range(len(self.circles2)):
                    center, radius = self.circles2[centerIndex], self.circle_radius2
                    tip = self.wand_tip2
                    # So here's what about to happen:
                    # We are going to see if the wand tip is in a specific circle. But:
                    # 1. we don't want to add something every time the timer fires, so we make circles non retraceable. But:
                    # 2. That would throw index out of bounds. But:
                    # 3. Using an empty list as an allowed bypass leads to a residue from a previous spell's trace into the next one. So:
                    # 4. We code in a circle for the left hand to touch to clear the current spell/ to start a new spell. 
                    #print(self.tip_is_in(center, radius, tip))
                    if (self.tip_is_in(center, radius, tip) and (self.trace2 == [] or self.trace2[-1] != centerIndex and not self.spell_clear2)):
                        if(self.start_screen == 1):
                            if(centerIndex == self.start):
                                self.start_screen = 0
                                self.start_screen_music_flag = 1
                            if(centerIndex == self.tutorial):
                                self.main_tutorial = 1
                                self.start_screen = 0
                                self.start_screen_music_flag = 1
                            if(centerIndex == self.customize):
                                self.customize_mode = 1
                                self.start_screen = 0
                                self.start_screen_music_flag = 1
                            

                            break
                        #print(self.spell_residue)
                        self.trace2.append(centerIndex)
                        if centerIndex == self.clear: 
                            self.trace2 = []
                        if self.trace2 != []: print("trace2", self.trace2)
                    if(self.spell_clear2): 
                        self.trace2 = []
                        self.spell_clear2 = 0
                        self.blocking2 = 0
                    #if(self.spell_residue == 1):
                        #self.trace = []
                        #print(" "*5, self.tip_is_in(center, radius, tip))

                if (tuple(self.trace2) in self.spell_book):
                    self.spell2 = self.spell_book[tuple(self.trace2)]
                    #print(self.spell2)
                else: self.spell2 = ""

                #Player 2 spellcasting
                if self.spell2 != "" and self.do_your_duty_end_flag:
                    if not self.blocking and not self.blocking2:
                        if self.spell2 == self.stupefy:
                            if self.power2 >= self.stupefy_power:
                                self.health -= self.stupefy_damage * self.damage_modifier2
                                print("Player 2 Casts Stupefy!")
                                self.play_spell(self.stupefy_sound)
                                self.power2 -= self.stupefy_power
                            else: 
                                print("Player 2, insufficient power")
                                self.play(self.insufficient_power_sound)
                        if self.spell2 == self.expelliarmus:
                            if self.power2 >= self.expelliarmus_power:
                                print("Player 2 Casts Expelliarmus!")
                                self.play_spell(self.expelliarmus_sound)
                                self.power2 -= self.expelliarmus_power
                                self.is_wand_tracking = False
                                self.wand_pos = self.default_wand_pos
                                self.wand_tip = self.default_wand_tip
                        
                            else: 
                                print("Player 2, insufficient power")
                                self.play(self.insufficient_power_sound)
                        if self.spell2 == self.protego:
                            if self.power2 >= self.protego_power:
                                print("Player 2, Shield Up!")
                                self.play_spell(self.protego_sound)
                                self.power2 -= self.protego_power
                                self.blocking2 = True
                            else: print("Player 2, insufficient power")
                            self.play(self.insufficient_power_sound)
                    elif(self.blocking2):
                        print("Player 2, You can't cast a spell while you are blocking") 
                    else:
                        print("Player 2, Blocked by player 1!!")
                        self.play(self.deflect_sound)
                        self.blocking = False

            #Game over...
            if self.health <= 0:
                self.winner = 2
            if self.health2 <= 0:
                self.winner = 1

            # Draw graphics 
            self.draw_wands()
            self.draw_tutorials()
            self.draw_winner()
            self.draw_main_tutorial()
            self.draw_title_screen()
 
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