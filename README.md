# Custom Mobile Game Console
I've decided to make this repository public as there was no reason to keep it private and I felt it'd be a fun thing to share. I do not have any plans to continue working on this project at this time.

### So, what stopped the project?
Memory issues. Ultimately with time I could have solved it and I was making efforts to solve it, but the entire system crashes due to running out of memory when switching games. Eventually I got to a point to where I was satisfied with how far I had gotten and decided to call it quits.

### The Project Goals / Origin
When I first thought of the project, I had just started getting into microcontrollers. I worked on a basic networked pair of Rapsberry Pi Pico Ws to create a motion sensor that would send signals over a Wi-Fi network to the other Pico which would flash a light and play short little tunes with a buzzer. This allowed me to place the sensor in one location and be alerted in another.

I then had the idea what if there was a game console that got back to the "root" of gaming. Sitting on the couch with a friend or family member playing simple games. My original idea was to create two separate consoles that would communicate over Wi-Fi or Bluetooth. I was going to start with some simple version of Battleship. I picked out some starter hardware, and got to coding.

What I found during this initial phase was that there would be a lot of complexity processing a game loop while also trying to listen for Wi-Fi events due to Python's limited threading capability. Since (at the time, and I have not kept up to date) there was no easy way to access the second core in the Pico while using Python, I decided to shift the focus to just a mobile game console.

I had also tested with an ESP32 as well as Arduino and while I absolutely love the ESP32 and Arduino microcontrollers - the library support for the screen I picked within the C language was not as robust. Not to mention, I had almost no experience with C and Python felt very familiar and comfortable coming from a C# background.

### Primary Goal
Challenge myself to create something from scratch. No tutorials. No guidelines. Go in blind and see what you can make.

### Pictures
![image](https://github.com/user-attachments/assets/8e1ac774-736e-40e8-a38d-9bb144f415ec)

Snake - No controls yet, "AI" was playing:

![image](https://github.com/user-attachments/assets/82c8a717-6017-454e-8a86-84f35c6e2490)

Connected hardware, including running the system off battery power:

![image](https://github.com/user-attachments/assets/aa391257-145f-4cab-a8d7-afe3a298f836)

Eventually I realized that I would need something a bit more solid than joysticks and buttons laying all over the place. So I got to work measuring and modeling (with almost no prior experience) something that would hold all of the components together. There was a bit of trial and error. First making sure I printed out something small for each component to make sure I got the measurements right. I ordered some standoffs and the prototype was starting to come together.

![image](https://github.com/user-attachments/assets/9215ba82-a561-4e7f-9f2e-c432a3f56b57)

![image](https://github.com/user-attachments/assets/fda3ce25-8843-4a1c-b6de-c1ce95d9e924)

The battery was tucked underneath the buttons on the right side. During this, I was also hoping to revisit multiplayer. Which is why the above picture contains 2 different players. I eventually dropped that.

I got to work adding a main menu and 2 more games. And then eventually worked on some better sprites rather than basic circles and sqaures.

![image](https://github.com/user-attachments/assets/d27d53aa-3c89-492e-b4dd-062d891173d2)

![image](https://github.com/user-attachments/assets/1b651075-4ca0-4cbc-ba86-fd7daa3353be)

![image](https://github.com/user-attachments/assets/bdb268a6-55f0-4371-b5a3-9d9553b5935c)

## Hardware
- Mini Speaker - PC Mount 12mm 2.048kHz
- Raspberry Pi Pico W
- Rocker Switch - SPST (right-angle)
- Thumb Joystick
- LED Tactile Buttons (White, Green, Red, & Blue)
- SparkFun USB LiPoly Charger
- Lithium Ion Battery - 2Ah
- Adafruit 1.8" TFT 180 x 128 screen
- Soft button (which I cannot find my order info on)

## Games
Snake. Traditional snake. You eat "apples" and grow in length. As you grow the game also speeds up, making it harder to maneuver tighter turns. Graphics were all done by me.

Pong. Again, traditional pong. First to 8(?) wins. Again, graphics also done by me.

Space shooter. A side-scroller that randomly spawns enemy space ships. This was not completed. Graphics were done by me a long time ago, just took them for this little game.

## Personal reflection

### What went right
For a prototype, I think a lot went right. I was not following any guides and just exploring things on my own. I went in almost entirely blind to this project and came out the otherside with an appreciation for everything microcontroller. The power of these little boards was impressive.

I think my game design went well, I was really happy with my sprites and the games performance. There was a lot of optimizing I challenged myself to figure out on my own to get it to perform well. Although there are memory leaks/crashes, I am very satisfied with where it ended up. If I were to continue this, I would add more simplistic games - tetris, simon says (since I had LED buttons), etc.

Hardware choice was also overall a win. Having LED buttons opened up a lot of potential for more interactive ideas. Ultimately, I didn't use them that much for the "final result" of the project, but they work very well for their purpose. The joystick was also a decent choice, though I feel as though a "D-Pad" would have fit better. The screen is a bit too small, but the Pico likely wouldn't have been able to handle a higher resolution with similar refresh rates. The battery also keeps this thing running 24hrs a day for many days without charging.

### What could have improved.
Memory leaks / crashes. As mentioned at the top, this ultimately killed my motivation on the project.

Joystick vs D-Pad. I think a D-Pad would have been a much better experience with this. Due to the small screen size, the joystick would feel too stiff to work with. It was very noticeable in snake.

Screen size. Even though the Pico might not have had the memory to support a larger screen, the screen is just frankly too small. (Though there are separate controllers for larger screens) Many people who have played it felt a bit of eye strain.

A better frame/shell. The board I printed was intended to be a prototype holder. It's not the most comfortable to use, though.

I tried developing a screenshot system and ultimately gave up. My hope was to be able to get clearer pictures of the games since it was very difficult using a phone camera.

# Conclusion
Hopefully sharing this project sparks some ideas in your head and maybe new more awesome things are created from it. I really enjoyed this project and I've considered multiple times revisiting it now that the Raspberry Pi Pico 2 is out with double the memory, but for now, I hope you enjoyed the read!
