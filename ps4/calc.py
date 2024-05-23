player_angle = 270

dir_u = player_angle % 360 >= 315 and player_angle % 360 < 45
dir_r = player_angle % 360 >= 45 and player_angle % 360 < 135
dir_d = player_angle % 360 >= 135 and player_angle % 360 < 225
dir_l = player_angle % 360 >= 225 and player_angle % 360 < 315

print(player_angle % 360)

print("up: ", dir_u)
print("right: ", dir_r)
print("down: ", dir_d)
print("left: ", dir_l)