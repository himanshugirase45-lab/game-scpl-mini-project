# SlingShot Adventure - Technical Presentation

## 1. Projectile Motion
The game implements realistic projectile motion by tracking initial velocity, launch angle, and applying a constant downward force (gravity). The initial trajectory preview is calculated using the kinematic equations of motion:
- \( v_x = v \cdot \cos(\theta) \)
- \( v_y = v \cdot \sin(\theta) + g \cdot t \)
- \( x = x_0 + v_x \cdot t \)
- \( y = y_0 + v_y \cdot t + 0.5 \cdot g \cdot t^2 \)

## 2. Collisions (Pymunk)
Collision detection and resolution are handled by the **Pymunk** physics engine. Each entity (birds, targets, structural blocks) has a rigid body with mass, friction, and elasticity properties. We track collision forces via Pymunk's `add_collision_handler`. When the impact force between a bird and a block exceeds a defined threshold, the object takes damage and breaks.

## 3. Object-Oriented Design (Classes)
The game uses inheritance and classes extensively to represent the physical world logically:
- `Entity`: The base class wrapping Pymunk physics bodies and pygame surfaces.
- `Bird`, `Block`, `Target`: Child classes with customized properties (mass, hp, special abilities).
- `GameState`: Base class for managing discrete UI menus and scenes (`MainMenu`, `PlayingState`, `VictoryScreen`).

## 4. Game Loop
The primary loop in `main.py` performs three key functions per frame:
1. **Event Handling:** Polling user input (clicks, drags, keyboard presses).
2. **State Updates:** Stepping the physics simulation forward using a fixed timestep with substeps for accuracy (`space.step(dt/5)`).
3. **Rendering:** Drawing all entities onto the Pygame surface (rotated properly based on physics body angles).

## 5. File Handling (Saving/Loading)
Player progress (unlocked levels, high scores, stars) and settings (mute, fullscreen) are persisted locally via Python's built-in `json` module. The `save_manager.py` elegantly handles creating default saves, reading the existing JSON, recovering from corruptions, and updating metrics upon completing a level.
