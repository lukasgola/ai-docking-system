import pygame

# Initialize pygame
pygame.init()

# Initialize the joystick
pygame.joystick.init()

# Check for joystick count
joystick_count = pygame.joystick.get_count()
if joystick_count == 0:
    print("No joysticks connected")
    pygame.quit()
    exit()

# Use the first joystick
joystick = pygame.joystick.Joystick(0)
joystick.init()

print(f"Joystick name: {joystick.get_name()}")
print(f"Number of axes: {joystick.get_numaxes()}")
print(f"Number of buttons: {joystick.get_numbuttons()}")

LEFT, RIGHT, UP, DOWN = False, False, False, False
analog_keys = {0:0, 1:0, 2:0, 3:0, 4:-1, 5: -1 }

speed = 127
forward = 0
backward = 0
axL = 0
axR = 0



# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.JOYAXISMOTION:
            analog_keys[event.axis] = event.value
            #print(analog_keys)
            # Horizontal Analog

            if analog_keys[0] < -.3:
                axL = abs(analog_keys[0])
            else:
                axL = 0

            if analog_keys[0] > .3:
                axR = abs(analog_keys[0])
            else:
                axR = 0

            if analog_keys[5] > -1:
                forward = (analog_keys[5] + 1)*0.5
            else:
                forward = 0

            if analog_keys[4] > -1:
                backward = (analog_keys[4] + 1)*0.5
            else:
                backward = 0
                

        elif event.type == pygame.JOYBUTTONDOWN:
            print(f"Button {event.button} pressed")
        elif event.type == pygame.JOYBUTTONUP:
            print(f"Button {event.button} released")

    
    fS = speed * forward
    bS = speed * backward

    forSpeed = max(fS - bS, 0)
    backSpeed = max(bS - fS, 0)

    if forSpeed == 0 and backSpeed == 0:
        speedR = int(speed * axL)
        speedL = int(speed * axR)
        backR = int(speed * axR)
        backL = int(speed * axL)

    else:
        speedR = int(forSpeed + forSpeed * axL)
        speedL = int(forSpeed + forSpeed * axR)

        backR = int(backSpeed + backSpeed * axL)
        backL = int(backSpeed + backSpeed * axR)

    
    print(str(backL)+ "," + str(speedL) + " : " + str(backR) + ","  + str(speedR))

# Quit pygame
pygame.quit()
