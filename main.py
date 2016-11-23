import pygame
import math
import time


class Player():
    def __init__(self, w, h):
        self.x = 0
        self.y = 0
        self.x_speed = 0
        self.y_speed = 0
        self.acceleration = 0.3
        self.decceleration = 0.95
        self.width = w
        self.height = h
        self.vertices = [[self.x, self.y], [self.x + self.height, self.y], [self.x + self.height, self.y + self.width],
                         [self.x, self.y + self.width]]

    def update(self, x_speed, y_speed, collided, y_ev):
        self.x_speed += x_speed*self.acceleration
        self.y_speed += 0.1
        if collided and y_speed<0 and y_ev<0:
            self.y_speed = -10
        self.x_speed *= self.decceleration
        self.y_speed *= self.decceleration
        self.x += self.x_speed
        self.y += self.y_speed
        # We need to have a list off all the player's corners for the projection process
        self.vertices = [[self.x, self.y], [self.x+self.height, self.y], [self.x+self.height, self.y + self.width], [self.x, self.y+self.width]]

    def collision_displace(self, x, y):
        self.x += x
        self.y += y

    def project(self, normal):
        # Comments to the projection process are placed in the Polygon class
        projected = []
        for vect in self.vertices:
            dp = vect[0] * normal[0] + vect[1] * normal[1]
            projected_v = [normal[0] * dp, normal[1] * dp]
            projected_l = math.sqrt(projected_v[0] ** 2 + projected_v[1] ** 2)
            sign_p = projected_v[0] * normal[0] + projected_v[1] * normal[1]
            projected.append(math.copysign(projected_l, sign_p))
        return [min(projected), max(projected), sign_p]

    def draw(self, screen):
        pygame.draw.rect(screen, (0,0,0), [self.x, self.y, self.width, self.height])

class Polygon():
    def __init__(self, vert):
        self.vertices = vert

    def collide(self, player):
        # start = time.clock()
        # We check whether the player is colliding with the polygon
        collided = 0
        out_v = []
        out_v_val = []
        # We check the x and y axes
        # First the x axis
        normal = [1, 0]
        me_p = self.project(normal)
        player_p = player.project(normal)
        if (me_p[1] < player_p[0]) or (me_p[0] > player_p[1]):
            collided = 0
        else:
            if (me_p[1] - player_p[0]) >= 0:
                out_v_val.append(me_p[1] - player_p[0])
                out_v.append([(me_p[1] - player_p[0]) * normal[0], (me_p[1] - player_p[0]) * normal[1]])
            if (me_p[0] - player_p[1]) <= 0:
                out_v_val.append(player_p[1] - me_p[0])
                out_v.append([(me_p[0] - player_p[1]) * normal[0], (me_p[0] - player_p[1]) * normal[1]])
            collided = 1
        #If there is an overlap at the x axis, we check the y axis
        if collided:
            normal = [0, 1]
            me_p = self.project(normal)
            player_p = player.project(normal)
            if (me_p[1] < player_p[0]) or (me_p[0] > player_p[1]):
                collided = 0
            else:
                if (me_p[1] - player_p[0]) >= 0:
                    out_v_val.append(me_p[1] - player_p[0])
                    out_v.append([(me_p[1] - player_p[0]) * normal[0], (me_p[1] - player_p[0]) * normal[1]])
                if (me_p[0] - player_p[1]) <= 0:
                    out_v_val.append(player_p[1] - me_p[0])
                    out_v.append([(me_p[0] - player_p[1]) * normal[0], (me_p[0] - player_p[1]) * normal[1]])
                collided = 1
        # We check every face if there was an overlap on x and y axes
        if collided:
            for i in range(len(self.vertices)):
                nexti = (i+1) % len(self.vertices)
                # Using vector substraction we obtain the vector representing the face...
                vector = [self.vertices[nexti][0]-self.vertices[i][0], self.vertices[nexti][1]-self.vertices[i][1]]
                # ...its lenght...
                len_v = math.sqrt(vector[0]**2+vector[1]**2)
                # ... and convert it to a unit vector
                unit_v = [vector[0]/len_v, vector[1]/len_v]
                # Then we calculate the vector perpendicular to it, which represents the normal axis
                normal = [-unit_v[1], unit_v[0]]
                #We check this axis only if it is not the x nor the y axis
                if normal[0]*normal[1] != 0:
                    # We project sprites onto the axis
                    me_p = self.project(normal)
                    player_p = player.project(normal)
                    # And check for overlap
                    if (me_p[1] < player_p[0]) or (me_p[0]>player_p[1]):
                        collided = 0
                        # Thanks to the rules of the Separating Axes Theorem
                        # we can stop checking when there is no overlap on at least one of the axes
                        break
                    else:
                        if (me_p[1] - player_p[0]) >= 0:
                            out_v_val.append(me_p[1] - player_p[0])
                            out_v.append([(me_p[1] - player_p[0]) * normal[0], (me_p[1] - player_p[0]) * normal[1]])
                        if (me_p[0] - player_p[1]) <= 0:
                            out_v_val.append(player_p[1] - me_p[0])
                            out_v.append([(me_p[0] - player_p[1]) * normal[0], (me_p[0] - player_p[1]) * normal[1]])
                        collided = 1
        # We can return the correct screen colour
        # print(time.clock()-start)
        if collided:
            return [1, out_v[out_v_val.index(min(out_v_val))]]
        else:
            return [0, [0,0]]

    def project(self, normal):
        projected = []
        # We project every vortex onto the normal vector
        for vect in self.vertices:
            dp = vect[0]*normal[0] + vect[1]*normal[1]
            projected_v = [normal[0]*dp, normal[1]*dp]
            projected_l = math.sqrt(projected_v[0]**2 + projected_v[1]**2)
            # We need to calculate the dot product of the projected vector and the normal vector,
            # because the length of the projected vector will always be positive,
            # and we want it to be negative if the projected vector faces in the opposite direction
            sign_p = projected_v[0] * normal[0] + projected_v[1] * normal[1]
            projected.append(math.copysign(projected_l, sign_p))
        # We return the min and max vector length - the boundaries of the projection
        return [min(projected), max(projected), sign_p]

    def draw(self, screen):
        pygame.draw.polygon(screen, (255,0,0), self.vertices)

def main():
    pygame.init()

    # Set the width and height of the screen [width,height]
    size = [500, 500]
    screen = pygame.display.set_mode(size)

    pygame.display.set_caption("My Game")

    # Loop until the user clicks the close button.
    done = False

    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()

    # Create sprites
    player = Player(20,20)
    x_speed = 0
    y_speed = 0
    collided = 0
    polygon = Polygon([[200,200],[150,250],[200,300], [300,300], [350,250], [300,200]])
    collide = polygon.collide(player)

    # -------- Main Program Loop -----------
    while not done:
        # Event Processing
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x_speed = -1
                elif event.key == pygame.K_RIGHT:
                    x_speed = 1
                elif event.key == pygame.K_UP:
                    y_speed = -1
                elif event.key == pygame.K_DOWN:
                    y_speed = 1
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN or event.key == pygame.K_UP:
                    y_speed = 0
                elif event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    x_speed = 0
        pos = pygame.mouse.get_pos()
        mouse_x = pos[0]
        mouse_y = pos[1]

        # Game logic
        player.update(x_speed, y_speed, collided, collide[1][1])
        collide = polygon.collide(player)
        collided = collide[0]
        player.collision_displace(collide[1][0], collide[1][1])

        # Drawing
        if collided:
            colour = (0,255,0)
        else:
            colour = (255,255,255)
        screen.fill(colour)
        polygon.draw(screen)
        player.draw(screen)

        # Update the screen
        pygame.display.flip()

        # Set the maximum framerate to 60fps
        clock.tick(60)

    # Close the window
    pygame.quit()


if __name__ == "__main__":
    main()