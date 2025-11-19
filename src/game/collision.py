"""Collision detection utilities"""

def check_collision(obj1, obj2):
    """Check collision between two game objects"""
    if hasattr(obj1, 'get_hitbox'):
        for px, py in obj1.get_hitbox():
            if int(px) == int(obj2.x) and int(py) == int(obj2.y):
                return True
    else:
        return abs(int(obj1.x) - int(obj2.x)) <= 1 and abs(int(obj1.y) - int(obj2.y)) <= 1
    return False
    
def check_bullet_collision(bullet, enemy):
    """Check if bullet hits enemy sprite area"""
    bx, by = int(bullet.x), int(bullet.y)
    ex, ey = int(enemy.x), int(enemy.y)
    
    return (ex <= bx < ex + enemy.width and 
            ey <= by < ey + enemy.height)
