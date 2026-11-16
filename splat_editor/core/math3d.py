"T1"
def euler_to_matrix(degrees):
    x,y,z = np.radians(degrees)
    cx, sx, cy, sy, cz, sz = math.cos(x), math.sin(x), math.cos(y), math.sin(y), math.cos(z), math.sin(z)
    rx = np.array([[1, 0, 0],[0, cx, -sx],[0, sx, cx]])
    ry = np.array([[cy, 0, sy],[0, 1, 0],[-sy, 0, cy]])
    rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return rz @ ry @ rx 

def world_transorm(self, flip):
    rot = self.transform.rotation_matrix() @ (FLIP if flip else np.identity(3))
    return rot, self.transform.translation(), float(self.transform.scale)

def world_matrix(self, flip):
    rot, t, s = self.world_transform(flip)
    m = np.identity(4)
    m = np.identity(4)
    m[:3, :3] = s*rot
    m[:3, 3] = t 
    return m
"T2"

def look_at(eye, target, up):
    forward = target - eye
    forward /= np.linalg.norm(forward)
    right = np.cross(forward, up)
    right /= np.linalg.norm(right)
    true_up = np.cross(right, forward)

    m = np.identity(4, np.float32)
    m[0, :3] = right
    m[1, :3] = true_up 
    m[2, :3] = -forward 
    m[:3, 3] = -m[:3, :3] @ eye
    return m 

def perspective(fov_y_deg, aspect, near, far):
    zoom = 1.0 / math.tan(math.radians(fov_y_deg)/2)
    m = np.zeros((4, 4), np.float32) 
    m[0, 0] = zoom / aspect 
    m[1, 1] = zoom  
    m[2, 2] = (far + near) / (near - far)
    m[2, 3] = 2* far*near / (near - far)
    m[3, 2] = -1
    return m