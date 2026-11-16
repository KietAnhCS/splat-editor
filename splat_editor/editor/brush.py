@staticmethod 
def _to_screen(clip, viewport):
    left, top, width, height = viewport
    x = left + (clip[..., 0] / clip[...,3]+1) * 0.5 * width 
    y = top + (1- clip[..., 1] / clip[..., 3]) * 0.5 *height
    return x,y 

@staticmethod
def _segment_dist2(p,a,b):
    pass 

