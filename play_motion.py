import mujoco
import imageio
import numpy as np

path = "unitree_rl_gym\resources\robots\g1_description\g1_29dof.xml"
model = mujoco.MjModel.from_xml_path(path)
data = mujoco.MjData(model)

motion = np.loadtxt("motion.csv", delimiter=",")
fps = 30

model.vis.global_.offwidth = 1280
model.vis.global_.offheight = 720
renderer = mujoco.Renderer(model, 720, 1280)

camera = mujoco.MjvCamera()
camera.distance = 3.0    
camera.azimuth = 80      
camera.elevation = -15   

video = imageio.get_writer("motion.mp4", fps=fps)

for row in motion:
    data.qpos[0:3] = row[0:3]           
    data.qpos[3:7] = row[[6, 3, 4, 5]]  
    data.qpos[7:36] = row[7:36]         

    mujoco.mj_forward(model, data)      
    camera.lookat[:] = [row[0], row[1], 0.7]  
    renderer.update_scene(data, camera)
    video.append_data(renderer.render())

video.close()
print("Saved motion.mp4")
