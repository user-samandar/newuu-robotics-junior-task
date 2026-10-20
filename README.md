# NewUU Robotics Internship — Task 1 (Junior Track)

## Part A — Human motion to robot

### Files
- `prompt.txt` – my text prompt for UltimateBots Studio
- `motion.csv` – the motion exported from UltimateBots Studio (LAFAN CSV format)
- `play_motion.py` – Python script that plays the motion on the G1 in MuJoCo and saves it as a video
- `motion.mp4` – the rendered video of the G1 doing the motion

**Prompt:** "raise the right arm to 130 degrees to the front, then bow" (5 s, 150 frames)

### How to reproduce
```
pip install mujoco numpy imageio imageio-ffmpeg
git clone https://github.com/unitreerobotics/unitree_rl_gym.git
python play_motion.py
```
Run it in the folder that contains `motion.csv` and the cloned `unitree_rl_gym`.


### How did I determine what the columns in the CSV represent?
- **Rows:** the file has 150 rows. UltimateBots Studio showed 150 frames for a 5 s clip,
  so one row = one frame, and 150 / 5 = 30 frames per second.
- **36 columns:** the G1 model (`g1_29dof.xml`) in MuJoCo needs exactly 36 numbers for a
  full pose (`nq = 36`): 7 for the floating base and 29 for the joints.
  So each row is one complete pose of the robot.
- **Columns 0–2 = robot position in metres (x, y, z).** In the first row they are
  0.01, −0.02, 0.78. 0.78 is close to 0.793, the pelvis height in the G1 model file.
- **Columns 3–6 = the way the robot faces.** The squares of these
  4 numbers add up to 1.000, which is true for every quaternion. If I read them as
  x, y, z, w, the x and y parts are tiny, so the robot is upright and only turned.
  If I read them as w, x, y, z, the robot would be tilted by about 54°. So the file
  stores x, y, z, w, but MuJoCo expects w, x, y, z. My script reorders them with
  `row[[6, 3, 4, 5]]`.
- **Columns 7–35 = the 29 joint angles in radians, in the same order as the joints in
  the MuJoCo model.** I tested this with my prompt: column 29 (right shoulder pitch)
  goes down to −2.65 rad, while column 22 (left shoulder pitch) never goes below 0.01.
  Only the right arm moves, as the prompt says.

## Part B — Walking policy

### Files
- `g1_circle.yaml` – the deploy config with my change
- `g1_circle_walk.mp4` – video of the G1 walking in a circle

### What I changed
One line in a copy of `deploy/deploy_mujoco/configs/g1.yaml`:
```diff
- cmd_init: [0.5, 0, 0]
+ cmd_init: [1, 0, 0.9]
```

### Why it walks in a circle
`cmd_init` is the command the policy was trained to follow:
[0.5, 0, 0] is simply [forward speed (m/s), sideways speed (m/s), turning speed (rad/s)] so it was walking straight initially, then I changed 0.5 to 1 to increase the speed and the second 0 to 0.9 so the robots starts turning 0.9 radians per second to make a circle. the reason I left the first 0 as it is that the robot would turn to sides (left and right depending on the sign of the second value), which is not required to implement.

### How to reproduce
```
pip install mujoco torch pyyaml
copy g1_circle.yaml into unitree_rl_gym/deploy/deploy_mujoco/configs/
cd unitree_rl_gym
# Windows PowerShell:  $env:PYTHONPATH = (Get-Location).Path
# Linux / macOS:       export PYTHONPATH=$PWD
python deploy/deploy_mujoco/deploy_mujoco.py g1_circle.yaml
```
The video was recorded from the MuJoCo viewer with a screen recorder.

### What inputs does the policy receive, and where do they come from?
Every 0.02 s (50 times per second), `deploy_mujoco.py` collects 47 numbers from the
simulation and gives them to the policy. They describe how the robot's body feels
right now and what it is asked to do:

The policy gets no camera image and does not know its position in the world. It only
knows how its own body feels and what command it is given. That is why changing the
command was enough to make the robot walk in a circle.

### What does the policy output, and how is it converted into joint torques?
The policy outputs 12 numbers, one per leg joint (hip pitch/roll/yaw, knee,
ankle pitch/roll on each leg). They are not torques, they are target joint angles:

- target angle = output × 0.25 + default standing angle
- a PD controller turns this into a torque:
  torque = kp × (target angle − current angle) − kd × joint speed.
  kp pulls the joint towards the target like a spring, and kd slows down fast
  movement like a brake (`kps` and `kds` in the YAML file).
- the torques are sent to the motors (`d.ctrl`). The policy runs 50 times per
  second, the PD controller 500 times per second.

So the network decides where each joint should go, and the PD controller produces
the torques that get it there.


PS: I CREATED THE README FILE WITH HELP OF AI