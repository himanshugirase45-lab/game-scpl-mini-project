# SCPL Projectile Motion & Physics Simulation

An interactive 2D physics simulation and sandbox designed for **Scientific Computing in Python (SCPL)**. Built using **Pygame** and **Pymunk (Chipmunk2D Physics Engine)**.

---

## 🌟 Key Features

1. **Realistic Classical Mechanics & Kinematics**
   - Default Earth gravitational acceleration ($g = 9.8\text{ m/s}^2$).
   - Parabolic projectile motion with vector velocity decomposition:
     $$x(t) = x_0 + v_{0x} t, \quad y(t) = y_0 + v_{0y} t + \frac{1}{2} g t^2$$
   - Live dotted trajectory prediction calculated in real-time.

2. **Bow & Slingshot Launch Mechanics**
   - Realistic elastic cord stretching based on Hooke's law:
     $$F = -k \Delta x, \quad E_p = \frac{1}{2} k (\Delta x)^2 \rightarrow v_0 = \sqrt{\frac{k}{m}} \Delta x$$
   - Vibrant 3D-shaded **Red Ball** projectile.

3. **White Stick Figure Target & Impact Dynamics**
   - Composite articulated physical body for the **White Stick Figure** target.
   - Collision detection using Pymunk contact solvers.
   - Dynamic knockback, impulse transfer, and tumbling upon ball impact.

4. **Realistic Bounces & Restitution**
   - Physical bounces governed by the coefficient of restitution ($e$):
     $$e = \frac{v_{\text{sep}}}{v_{\text{app}}}$$
   - Ball rebounds with natural damping and rolling friction until it comes to a complete rest.

5. **Live Scientific Telemetry Dashboard**
   - Launch Angle ($\theta$)
   - Launch Speed ($v_0$)
   - Current Velocity & Speed ($|v|$)
   - Height ($y$) in meters
   - Kinetic Energy ($E_k = \frac{1}{2} m v^2$) in Joules
   - Distance to Target ($d$) in meters

6. **In-Game Physics Customization Menu (Top SETTINGS Button)**
   - **Gravity ($g$)**: Unbounded slider with quick presets for Earth, Moon, Mars, Jupiter, Zero-G.
   - **Ball Elasticity**: Physical coefficient of restitution $0.0$ to $1.0$.
   - **Ground Elasticity**: $0.0$ to $1.0$.
   - **Stick Figure Elasticity**: $0.0$ to $1.0$.
   - **Target Distance (Meters)**: Unbounded dynamic slider with `[-]` / `[+]` steppers, dragging beyond limits, and mouse wheel scrolling (from $1.0\text{ m}$ to $500.0\text{ m}+$ sandbox).
   - **Bow Height (Elevation)**: Unbounded dynamic slider (from $0.2\text{ m}$ to $100.0\text{ m}+$ high launch towers).

7. **Dynamic Camera Auto-Framing & Zooming**
   - Automatically and smoothly zooms in (for close-up macro shots) and zooms out (for ultra-long distances) so the bow, ball, target, metric scale, and projectile trajectory are always perfectly visible on screen.

8. **Sleek Dark Theme & Minimalist Scientific Polish**
   - Deep indigo-slate night atmosphere with starry dust background.
   - Ground plane with metric scale zeroed at the bow ($0\text{m}$).
   - Clean static `"GAME COMPLETED"` banner in green font with thin white border upon hitting the target.

---

## 🎮 How to Run

```bash
# Install dependencies
pip install -r requirements.txt

# Launch the simulation
python main.py
```

---

## 🕹️ Controls
- **Left Click & Drag (Red Ball)**: Pull back on the bow to adjust launch angle and tension force.
- **Release Mouse**: Launch the ball into projectile flight.
- **Top HUD Buttons**:
  - `SETTINGS`: Opens the live physics and environment parameter customizer.
  - `RELOAD BALL`: Spawns the red ball back in the slingshot pouch.
  - `TELEMETRY`: Toggles the scientific computing telemetry overlay.
  - `MAIN MENU`: Returns to the main menu.
