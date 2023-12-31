import pygame
import os
import time
import random

pygame.font.init()
WIDTH,HEIGHT=1000,750
WIN=pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Space shooter")
#COLOR 
WHITE=(255,255,255)
RED=(255,0,0)
#Load images
RED_SPACE_SHIP=pygame.image.load(os.path.join("assets","pixel_ship_red_small.png"))
GREEN_SPACE_SHIP=pygame.image.load(os.path.join("assets","pixel_ship_green_small.png"))
BLUE_SPACE_SHIP=pygame.image.load(os.path.join("assets","pixel_ship_blue_small.png"))

#LayerShip
YELLOW_SPACE_SHIP=pygame.image.load(os.path.join("assets","pixel_ship_yellow.png"))
#Laser
RED_LASER=pygame.image.load(os.path.join("assets","pixel_laser_red.png"))
GREEN_LASER=pygame.image.load(os.path.join("assets","pixel_laser_green.png"))
BLUE_LASER=pygame.image.load(os.path.join("assets","pixel_laser_blue.png"))
YELLOW_LASER=pygame.image.load(os.path.join("assets","pixel_laser_yellow.png"))
#Background
BG=pygame.transform.scale(pygame.image.load(os.path.join("assets","Background-black.png")),(WIDTH,HEIGHT))


def collide(obj1,obj2):
    offset_x=obj2.x-obj1.x
    offset_y=obj2.y-obj1.y
    return obj1.mask.overlap(obj2.mask,(offset_x,offset_y))!=None

class Laser:
    def __init__(self,x,y,img):
        self.x=x
        self.y=y
        self.img=img
        self.mask=pygame.mask.from_surface(self.img)
    
    def draw(self,window):
        window.blit(self.img,(self.x,self.y))
        
    def move(self,vel):
        self.y+=vel
    def off_screen(self,height):
        return not(self.y>=0 and self.y<=height)
    def collision(self,obj):
        return collide(self,obj)
    

class Ship:
    COOLDOWN=30
    
    def __init__(self,x,y,health=100):
        self.x=x
        self.y=y
        self.health=health
        self.ship_img=None
        self.laser_img=None
        self.lasers=[]
        self.cool_down_counter=0
    
    def cooldown(self):
        if self.cool_down_counter>=self.COOLDOWN:
            self.cool_down_counter=0
        elif self.cool_down_counter>0:
            self.cool_down_counter+=1
    
    def shoot(self):
        if self.cool_down_counter==0:
            laser=Laser(self.x,self.y,self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter=1
    
    def draw(self,window):
        window.blit(self.ship_img,(self.x,self.y)) 
        for laser in self.lasers:
            laser.draw(window)

    def move_laser(self,vel,obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health-=10
                self.lasers.remove(laser)  
            
        
    def getwidth(self):
        return self.ship_img.get_width()
    def getheight(self):
        return self.ship_img.get_height()
        
class Player(Ship):
    def __init__(self,x,y,health=100):
        super().__init__(x,y,health)
        self.ship_img=YELLOW_SPACE_SHIP
        self.laser_img=YELLOW_LASER
        self.mask=pygame.mask.from_surface(self.ship_img)
        self.max_health=health
        
    def move_laser(self,vel,objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)
    def draw(self,window):
        super().draw(window)
        self.health_bar(window)
        
    def health_bar(self,window):
        pygame.draw.rect(window,WHITE,(self.x,self.y+self.ship_img.get_height()+10,self.ship_img.get_width(),10))  
        pygame.draw.rect(window,(0,255,0),(self.x,self.y+self.ship_img.get_height()+10,self.ship_img.get_width()*(self.health/self.max_health),10))         

class Enemy(Ship):
    COLOR_MAP={
            "red":(RED_SPACE_SHIP,RED_LASER),
            "green":(GREEN_SPACE_SHIP,GREEN_LASER),
            "blue":(BLUE_SPACE_SHIP,BLUE_LASER)
          }
    
    def __init__(self,x,y,color,health=100):
        super().__init__(x,y,health)
        self.ship_img, self.laser_img=self.COLOR_MAP[color]
        self.mask=pygame.mask.from_surface(self.ship_img)
          
    def move(self,vel):
        self.y+=vel    
    
    def shoot(self):
        if self.cool_down_counter==0:
            laser=Laser(self.x-10,self.y,self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter=1
        

def main():
    run=True
    FPS=60
    level=1
    lives=5
    player_vel=5
    
    enemies=[]
    wave_length=5
    enemy_vel=1
    
    main_font=pygame.font.SysFont("comicSans",50)
    lost_font=pygame.font.SysFont("comicSans",60)
    clock=pygame.time.Clock()
    
    player=Player(300,650)
    def redraw_window():
        WIN.blit(BG,(0,0))
        #draw text
        lives_label=main_font.render(f"Lives: {lives}",1,WHITE)
        level_label=main_font.render(f"Level: {level}",1,WHITE)
        
        WIN.blit(lives_label,(10,10))
        WIN.blit(level_label,(WIDTH-level_label.get_width()-10,10))
        
        for enemy in enemies:
            enemy.draw(WIN)
            
        player.draw(WIN)
        if Lost:
            lost_label=lost_font.render("YOU LOST!",1,WHITE)
            WIN.blit(lost_label,WIDTH/2-lost_label.get_width(),350)
        
            
        pygame.display.update()
        
    Lost=False
    count_lost=0
    laser_vel=4
    
    while run:
        clock.tick(FPS)
        
        redraw_window()
        if lives<=0 or player.health<=0:
            Lost=True
            count_lost+=1
            
        if Lost:
            if count_lost>FPS*3:
                run=False
                break
            else: continue
            
        
        if len(enemies)==0:
            level+=1
            wave_length+=5
            for i in range(wave_length):
                enemy=Enemy(random.randrange(50,WIDTH-100),random.randrange(-1500,-100),random.choice(["red","blue","green"]))
                enemies.append(enemy)
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                run=False
                break
            
        keys=pygame.key.get_pressed()
        if (keys[pygame.K_a]or keys[pygame.K_LEFT])and player.x-player_vel>0:#left 
            player.x-=player_vel
        if (keys[pygame.K_d]or keys[pygame.K_RIGHT])and player.x+player_vel+player.getwidth()<WIDTH:#right
            player.x+=player_vel
        if (keys[pygame.K_s]or keys[pygame.K_DOWN]) and player.y+player_vel+10<HEIGHT:#down
            player.y+=player_vel
        if (keys[pygame.K_w]or keys[pygame.K_UP]) and player.y-player_vel-player.getheight()>0:#up sybstract 50 to make sure it is not out of the screen
            player.y-=player_vel   
        if (keys[pygame.K_SPACE]):
            player.shoot()
             
        for enemy in enemies:
            enemy.move(enemy_vel)
            enemy.move_laser(laser_vel,player)
            
            if random.randrange(0,2*60)==1:
                enemy.shoot()
            
            if collide(enemy,player):
                player.health-=10
                enemies.remove(enemy)    
            elif enemy.y+enemy.getheight()>HEIGHT:
                lives-=1
                enemies.remove(enemy)
            
            
         
        player.move_laser(-laser_vel,enemies)        
 
def main_menu():
    title_font=pygame.font.SysFont("comicSans",70)
    
    
    run=True
    while run:
        WIN.blit(BG,(0,0))
        title_label=title_font.render("Press the mouse to begin.....",1,WHITE)
        
        WIN.blit(title_label,(WIDTH/2-title_label.get_width()/2,350))
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                run=False
            if event.type==pygame.MOUSEBUTTONDOWN:
                main()
    
    pygame.quit()
               
main_menu()
        

