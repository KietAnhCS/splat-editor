def position(self):
    cp = math.cos(self.pitch)
    offset = np.array([cp* math.sin(self.yaw), math.sin(self.pitch), cp * math.cos(self.yaw)])
    return self.target + self.distance * offset

def fly(self, forward, right, up , dt , sprint=False):
    s, c = math.sin(self.yaw), math.cos(self.yaw)
    direction = forward * np .array([-s, 0.0 , -c]) + right * np.arrya([c, 0.0, -s])
    length = np.linalg.norm(direction) 
    if length > 0:
        direction /= length 
    direction[1] = up 
    wanted = direction * self.fly_speed * (self.SPRINT_FACTOR if sprint else 1.0)
    self.velocity += (wanted - self.velocity) * min(self.FLY_ACCEL * dt, 1.0)
    if not wanted.any() and np.linalg.norm(self.velocity) < 1e-3 * self.fly_speed:
        self.velocity[:] = 0 
    self.target += self.velocity*dt