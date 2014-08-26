from kivy.app import App

from kivy.storage.jsonstore import JsonStore

from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.popup import Popup

from kivy.properties import NumericProperty, ListProperty, ObjectProperty, ReferenceListProperty, StringProperty
from kivy.clock import Clock
from kivy.vector import Vector

from random import randint, choice

from os.path import join



class Game(FloatLayout):
	score = NumericProperty(0)
	switch = NumericProperty(0)
	level = NumericProperty(0)
	ballsin = NumericProperty(0)
	highscore = NumericProperty(0)
	
	pongball = ObjectProperty(None)
	playbutton = ObjectProperty(None)
	ratebutton = ObjectProperty(None)
	instructionbutton = ObjectProperty(None)
	highscorebutton = ObjectProperty(None)
	player = ObjectProperty(None)
	brick = ObjectProperty(None)
	
	bricklist = ListProperty([])
	cookielist = ListProperty([])

	#monster graphics and animations
	gmon1 = 'graphics/monster1/monster1.png'
	amon1 = 'graphics/monster1/monster1.zip'
	gmon2 = 'graphics/monster2/monster2.png'
	amon2 = 'graphics/monster2/monster2.zip'
	gmon3 = 'graphics/monster3/monster3.png'
	amon3 = 'graphics/monster3/monster3.zip'
	gmon4 = 'graphics/monster4/monster4.png'
	amon4 = 'graphics/monster4/monster4.zip'

	cookiescorejson = JsonStore(join(data_dir, 'cookiehighscore.json'))
	
	def __init__(self, *args, **kwargs):
		super(Game, self).__init__(*args, **kwargs)
		Clock.schedule_interval(self.update, 1./60)
		self.refs = [self.playbutton.__self__,
					self.ratebutton.__self__,
					self.instructionbutton.__self__,
					self.highscorebutton.__self__]
		
		if self.cookiescorejson.exists('cookiescore'):
			self.highscore = int(self.cookiescorejson.get('cookiescore')['best'])

	def update(self, dt):
		self.update_balls(dt)
		self.restart()
		self.player.move()
		
	def play_pressed(self):
		self.remove_widget(self.playbutton)
		self.remove_widget(self.ratebutton)
		self.remove_widget(self.instructionbutton)
		self.remove_widget(self.highscorebutton)
		self.pongball.velocity_y = -4
		self.pongball.velocity_x = 0
		self.ballsin += 1
		self.switch += 1
		self.score = 0
		Clock.schedule_interval(self.spawn_cookie, 1/60)
		
		
	def rate_pressed(self):
		print 'rate pressed'
		
	def instruction_pressed(self):
		some_function(self)
		
	def leader_pressed(self):
		print 'leaderboard pressed'
		
		
	def end_game(self):
		self.pongball.velocity = 0, 0
		Clock.unschedule(self.spawn_cookie)
		for cookie in self.cookielist:
			if cookie in self.children:
				self.remove_widget(cookie)
		for brick in self.bricklist:
			if brick in self.children:
				self.remove_widget(brick)
		self.pongball.center_x = self.width/2
		self.pongball.center_y = self.height - 100
		self.ballsin -= 1
		self.level = 0
		self.pongball.balllife = 4
		self.bricklist = []
		self.cookielist = []
		Clock.unschedule(self.cookie_2)
		s = Scorepop()
		s.score = self.score
		s.currentmonster = self.pongball.source[0:len(str(self.pongball.source))-4]+'.zip'
		s.open()
		self.pongball.source = 'graphics/monster1/monster1.png'
		

		
	def cookie_2(self, dt):
		for cookie in self.cookielist:
			cookie.move()
			if cookie in self.children:
				if cookie.x <= self.x-40:
					cookie.velocity_x = 2
				elif cookie.x >= self.width:
					cookie.velocity_x = -2
					
	def update_balls(self, dt):
		self.pongball.move()
				
		if self.pongball.top > self.height:
			self.pongball.velocity_y *= -1
			
		if self.pongball.collide_widget(self.player):
			vx, vy = self.pongball.velocity
			offset = (self.pongball.center_x - self.player.center_x) / (self.player.width /5)
			bounced = Vector(vx, -1 * vy)
			vel = bounced * 1.02
			self.pongball.velocity = vel.x + offset, vel.y
			self.pongball.balllife -= 1
			self.player.velocity_x = 0
			
		if self.pongball.x < 0 or self.pongball.right > self.width:
			self.pongball.velocity_x *=-1
					
		if self.pongball.y < -40 or self.pongball.balllife == 0:
			self.end_game()
		
		if self.player.x< self.x-self.player.width+20:
			self.player.velocity_x = 1
		if self.player.x > self.width-20:
			self.player.velocity_x = -1
				
		for cookie in self.cookielist:
			if cookie.collide_widget(self.pongball):
				self.score += 1
				if self.score > self.highscore:
					self.cookiescorejson.put('cookiescore', best = self.score)
					self.highscore = self.score
				self.pongball.balllife = 4
				self.level += 1
				for brick in self.bricklist:
					if brick in self.children:
						self.remove_widget(brick)
				self.remove_widget(cookie)
				self.cookielist.remove(cookie)
				self.spawn_cookie()
				
				if self.level < 5:
					self.pongball.source = self.amon1
					Clock.schedule_once(self.monster1, 1.3)					
				elif self.level >= 5 and self.level <10:
					self.pongball.source = self.amon2
					Clock.schedule_once(self.monster2, 1.3)	
				elif self.level >=10 and self.level <15:
					self.pongball.source = self.amon3
					Clock.schedule_once(self.monster3, 1.3)	
				else:
					self.pongball.source = self.amon4
					Clock.schedule_once(self.monster4, 1.3)	
					
		
		for brick in self.bricklist:
			if brick in self.children:
				if brick.collide_widget(self.pongball):
					if self.pongball.center_y >= brick.top and self.pongball.velocity_y <0\
						or self.pongball.center_y <= brick.y and self.pongball.velocity_y >0:
						self.pongball.velocity_y *= -1
					else:
						self.pongball.velocity_x *=-1
					
	def rand_outside(self):
		while True:
			num = randint(0, self.width-50)
			if num <= (self.width/2-150) or num >=(self.width/2+50):
				break
		return num	
		
	def monster1(self, dt):
		self.pongball.source = self.gmon1
	def monster2(self, dt):
		self.pongball.source = self.gmon2
	def monster3(self, dt):
		self.pongball.source = self.gmon3
	def monster4(self, dt):
		self.pongball.source = self.gmon4

		
	
	def spawn_cookie(self, *args):
		
		if len(self.cookielist) == 0:
			if self.level == 0:
				c1 = Cookie(x=self.rand_outside(), \
				y=randint(self.height - self.height / 3, self.height - 100),\
				csize = 100)
				self.cookielist.append(c1)
				self.add_widget(c1)
			#random pos, size 80
			elif self.level == 1:
				c1 = Cookie(x=randint(0, self.width - 50), \
				y=randint(self.height - self.height / 4, self.height - (self.height/13)),\
				csize = 80)
				self.cookielist.append(c1)
				self.add_widget(c1)
			#rand pos, size 60
			elif self.level == 2:
				c1 = Cookie(x=randint(0, self.width - 50), \
				y=randint(self.height - self.height / 4, self.height - (self.height/13)),\
				csize = 60)
				self.cookielist.append(c1)
				self.add_widget(c1)
			#rand pos, size 50
			elif self.level == 3:
				c1 = Cookie(x=randint(0, self.width - 50), \
				y=randint(self.height - self.height / 4, self.height - (self.height/13)),\
				csize = 50)
				self.cookielist.append(c1)
				self.add_widget(c1)
			#rand pos, size 45
			elif self.level ==4:
				c1 = Cookie(x=randint(0, self.width-40), \
				y=randint(self.height - self.height / 4, self.height - (self.height/13)),\
				csize = 45)
				self.cookielist.append(c1)
				self.add_widget(c1)
			elif self.level == 5:
				self.pongball.source = 'graphics/monster2/monster2.png'
				c1 = Cookie(x= choice([0-100,self.width]), \
				y=self.height/2,\
				csize = 100)
				self.cookielist.append(c1)
				self.add_widget(c1)
				Clock.schedule_interval(self.cookie_2, 1./60)
			elif self.level ==6:
				Clock.unschedule(self.cookie_2)
				c1 = Cookie(x= choice([0-80, self.width]), \
				y=self.height-self.height/3,\
				csize = 80)
				self.cookielist.append(c1)
				self.add_widget(c1)
				Clock.schedule_interval(self.cookie_2, 1./60)
			elif self.level ==7:
				Clock.unschedule(self.cookie_2)
				c1 = Cookie(x= choice([0-60, self.width]), \
				y=self.height-self.height/4,\
				csize = 60)
				self.cookielist.append(c1)
				self.add_widget(c1)
				Clock.schedule_interval(self.cookie_2, 1./60)		
			elif self.level ==8:
				Clock.unschedule(self.cookie_2)
				c1 = Cookie(x= choice([0-50, self.width]), \
				y=self.height-self.height/5,\
				csize = 50)
				self.cookielist.append(c1)
				self.add_widget(c1)
				Clock.schedule_interval(self.cookie_2, 1./60)
			elif self.level ==9:
				Clock.unschedule(self.cookie_2)
				c1 = Cookie(x= choice([0-40, self.width]), \
				y=self.height-self.height/6,\
				csize = 40)
				self.cookielist.append(c1)
				self.add_widget(c1)
				Clock.schedule_interval(self.cookie_2, 1./60)							
			#cookie left brick mid/bot
			elif self.level ==10:
				Clock.unschedule(self.cookie_2)				
				c1 = Cookie(x=randint(0, self.width/2-45), \
				y=randint(self.height - self.height / 4, self.height - (self.height/13)),\
				csize = 45)
				self.cookielist.append(c1)
				self.add_widget(c1)
				b1 = Brick(x = self.width/2, y = 0, brickwidth = 45,\
				brickheight = self.height/2)
				self.bricklist.append(b1)
				self.add_widget(b1)
				self.pongball.source = 'graphics/monster3/monster3.png'
			#cookie right brick mid/bot
			elif self.level == 11:
				c1 = Cookie(x=randint(self.width/2+40, self.width-30), \
				y=randint(self.height - self.height / 4, self.height - (self.height/13)),\
				csize = 45)
				self.cookielist.append(c1)
				self.add_widget(c1)
				b1 = Brick(x = self.width/2, y = 0, brickwidth = 45,\
				brickheight = self.height/2)
				self.bricklist.append(b1)
				self.add_widget(b1)
			#cookie left brick mid/top
			elif self.level ==12:
				c1 = Cookie(x=randint(0, self.width/2-45), \
				y=randint(self.height - self.height / 4, self.height - (self.height/13)),\
				csize = 45)
				self.cookielist.append(c1)
				self.add_widget(c1)
				b1 = Brick(x = self.width/2, y = self.height/2, brickwidth = 45,\
				brickheight = self.height/2)
				self.bricklist.append(b1)
				self.add_widget(b1)
			#cookie right brick mid/top	
			elif self.level ==13:
				c1 = Cookie(x=randint(self.width/2+40, self.width-30), \
				y=randint(self.height - self.height / 4, self.height - (self.height/13)),\
				csize = 45)
				self.cookielist.append(c1)
				self.add_widget(c1)
				b1 = Brick(x = self.width/2, y = self.height/2, brickwidth = 45,\
				brickheight = self.height/2)
				self.bricklist.append(b1)
				self.add_widget(b1)
			#cookie left  brick mid/mid
			elif self.level == 14:
				c1 = Cookie(x=randint(0, self.width/2 - 40), \
				y=randint(self.height - self.height / 4, self.height - (self.height/13)),\
				csize = 45)
				self.cookielist.append(c1)
				self.add_widget(c1)
				b1 = Brick(x = self.width/2, y = self.height/4, brickwidth = 45,\
				brickheight = self.height/2)
				self.bricklist.append(b1)
				self.add_widget(b1)
			#cookie right brick mid/mid
			elif self.level == 15:
				c1 = Cookie(x=randint(self.width/2+40, self.width-30), \
				y=randint(self.height - self.height / 4, self.height - (self.height/13)),\
				csize = 45)
				self.cookielist.append(c1)
				self.add_widget(c1)
				b1 = Brick(x = self.width/2, y = 0, brickwidth = 45,\
				brickheight = self.height*3/8)
				self.bricklist.append(b1)
				self.add_widget(b1)	
				b2 = Brick(x = self.width/2, y = self.height - self.height * 3/8, brickwidth = 45,\
				brickheight = self.height*3/8)
				self.bricklist.append(b2)
				self.add_widget(b2)
				self.pongball.source = 'graphics/monster4/monster4.png'

				
	def on_touch_down(self, touch):
		if touch.y < self.height/2 and touch.x < self.width/2:
			self.player.velocity_x = -6.5
		if touch.y < self.height/2 and touch.x > self.width/2:
			self.player.velocity_x = 6.5
		super(Game, self).on_touch_down(touch)
		
	def on_touch_up(self, touch):
		self.player.velocity_x = 0
		super(Game, self).on_touch_up(touch)
	
	def restart(self, *args):
		if self.switch == 1 and self.ballsin == 0:
			self.switch += 1
			
		if self.switch == 2:
			self.add_widget(self.playbutton)
			self.add_widget(self.ratebutton)
			self.add_widget(self.instructionbutton)
			self.add_widget(self.highscorebutton)
			self.switch -= 2

class PongPaddle(Widget):
	velocity_x = NumericProperty(0)
	velocity_y = NumericProperty(0)
	velocity = ReferenceListProperty(velocity_x, velocity_y)
	
	def __init__(self, **kwargs):
		super(PongPaddle, self).__init__(**kwargs)
	
	def move(self):
		self.pos = Vector(*self.velocity) + self.pos
	
	
class PongBall(Image):
	velocity_x = NumericProperty(0)
	velocity_y = NumericProperty(0)
	velocity = ReferenceListProperty(velocity_x, velocity_y)
	balllife = NumericProperty(4)
	
	
	def __init__(self, **kwargs):
		super(PongBall, self).__init__(**kwargs)
		
	def move(self):
		self.pos = Vector(*self.velocity) + self.pos
		
class Brick(Widget):
	brickwidth = NumericProperty(0)
	brickheight = NumericProperty(0)
	
	def __init__(self, **kwargs):
		super(Brick, self).__init__(**kwargs)
		
class Cookie(Image):
	csize = NumericProperty(0)
	velocity_x = NumericProperty(0)
	velocity_y = NumericProperty(0)
	velocity = ReferenceListProperty(velocity_x, velocity_y)
	
	def __init__(self, **kwargs):
		super(Cookie, self).__init__(**kwargs)
		
	def move(self):
		self.pos = Vector(*self.velocity) + self.pos

class Restart(ButtonBehavior, Image):
	def pressed(self):
		g.end_game()
		
class Background1(Image):
	pass
	
class Scorepop(Popup):
	score = NumericProperty(0)
	currentmonster = StringProperty('')	
	
class CookieApp(App):
	
	def build(self):
		self.icon = 'monster1.png'
		global data_dir
		data_dir = getattr(self, 'user_data_dir')
		global g
		g = Game()
		return g

def some_function(q, *args):
	q.highscore = App.get_running_app().score
	print q.highscore
	
def high_score_put(q, *args):
	self.highscore = App.get_running_app().score
	print "hs updated"

		
if __name__ == '__main__':
	CookieApp().run()
	
	
