# Report for Assignment 1

**Name:** Hala Ishan  
**Student ID:** 213692296

# GUI Exploration – Before Starting Tasks

Before beginning the tasks, I explored the interactive GUI created by the `vedo` package in the assignment.

## 🔄 Interaction Summary

- 🖱️ **Mouse Movement**:  
  Hovering the mouse over the 3D surface dynamically created a path, showing sampled points.

- 🏷️ **Text Flag & Info Panel**:  
  - A **floating flag** appears next to the mouse path, showing the 3D coordinate and related values.  
  - The **bottom-left text area** displayed:
    - `X`: The selected point
    - `dX`: Distance between current and previous points
    - `dE`: Energy difference between the two

- 🔘 **Transparency Slider**:  
  A slider at the **bottom-right corner** adjusts the surface’s transparency in real time.

- ⌨️ **Keyboard – ‘c’ key**:  
  Pressing `c` resets/clears the entire path.

- 🎥 **Responsiveness**:  
  The GUI responds quickly and smoothly, allowing live interaction without restarting the script.

## 📸 Screenshot

Below is a screenshot showing the path, floating flag, and transparency slider:

![GUI Interaction](images/before_task_image1.png)


---

# Task 1.1 – Right Mouse Click Callback

## 🎯 Goal
Add a mouse callback that responds to a **right-click**, allowing users to interact with the surface in a new way.

## 🛠️ Implementation
I created a function called `OnMousePress(evt)` that is triggered when the user right-clicks. The function uses `evt.picked3d` to get the 3D coordinates under the cursor, then adds:
- A red 3D sphere at the clicked point
- A 3D text label showing the coordinates

This callback is registered using:

```python
plt.add_callback("right button press", OnMousePress)

## 📸 Screenshot

Below is a screenshot showing the a red 3D sphere at the clicked pointand a text label showing the coordinates:

![GUI Interaction](images/task_1.1_image1.png)

## 🎥 Video Demonstration

[▶ Click to watch the Task 1.1 demo video](videos/task1.1_demo.mkv)

note : when i press c i delete all the point and their labels
[▶ Click to watch the Task 1.1 demo2 - press 'c' to clear](videos/task1.1_vedio2.mkv)


---
Task 1.2 – Visualizing Function Values on the Path
🎯 Goal
Display the energy values along the path traced by the mouse (Xi) as a live-updating graph, using vedo.plot.

❌ First Attempt – Using plot() Alone
Initially, I used the plot() function from vedo directly. This successfully generated the graph, but it was embedded inside the 3D world, which made it very difficult to interpret. The graph moved with the camera, was often obscured by the surface, and lost its readability.

Below is an image showing the result of this initial approach:
![GUI Interaction](images/task_1.2_image1.png)



🧪 Fix Attempts (Still Without clone2d())
I tried improving the graph visibility using several methods, including:

📍 Repositioning it using .pos(2, -2, 1) to move it out of the main surface area

🧊 Adjusting transparency of the surface with .alpha(0.3) to avoid occlusion

🎨 Changing line color and width for contrast (lc='blue', lw=3)

⚠️ Attempting to rotate the plot with .rotateX() — which failed, since PlotXY objects do not support rotation and raised an error

Despite repositioning, the graph remained locked in the 3D space and subject to perspective distortion:


✅ Final Fix – Using clone2d()
To fully solve the issue, I applied clone2d() to the plot object. This transformed the graph into a 2D overlay, anchored to the screen rather than the 3D scene. As a result, the graph:

📌 Remains visible regardless of camera orientation

🎯 Provides a consistent and reliable visualization

👁️‍🗨️ Enhances user experience during interaction

Below is the improved result using clone2d():

![GUI Interaction](images/task_1.2_image2.png)

[▶ Or embed a video if needed:](videos/task1.2_demo.mkv)

