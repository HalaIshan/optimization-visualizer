#%% imports
import vedo as vd
import numpy as np
from vedo.pyplot import plot
from vedo import Latex

vd.settings.default_backend= 'vtk'

#%% Callbacks
msg = vd.Text2D(pos='bottom-left', font="VictorMono") # an empty text
global mouse_down
mouse_down = False

def OnMouseMove(evt):                ### called every time mouse moves!
    global Xi, mouse_down, energy_plot

    if evt.object is None:          # mouse hits nothing, return.
        return                       

    pt  = evt.picked3d               # 3d coords of point under mouse
    X   = np.array([pt[0],pt[1],objective([pt[0],pt[1]])])  # X = (x,y,e(x,y))
    if not mouse_down:                  # ignore mouse moves when mouse is down
         Xi = np.append(Xi,[X],axis=0)             # append to the list of points

    if len(Xi) > 1:               # need at least two points to compute a distance
        txt =(
            f"X:  {vd.precision(X,2)}\n"
            f"dX: {vd.precision(Xi[-1,0:2] - Xi[-2,0:2],2)}\n"
            f"dE: {vd.precision(Xi[-1,2] - Xi[-2,2],2)}\n"
        )
        ar = vd.Arrow(Xi[-2,:], Xi[-1,:], s=0.001, c='orange5')
        plt.add(ar) # add the arrow
    else:
        txt = f"X: {vd.precision(X,2)}"
    msg.text(txt)                    # update text message

    c = vd.Cylinder([np.append(Xi[-1,0:2], 0.0), Xi[-1,:]], r=0.01, c='orange5')
    plt.remove("Cylinder")    
    
    fp = fplt3d[0].flagpole(txt, point=X,s=0.08, c='k', font="Quikhand")
    fp.follow_camera()                 # make it always face the camera
    plt.remove("FlagPole") # remove the old flagpole

    plt.add(fp, c) # add the new flagpole and new cylinder
    update_energy_plot()   # 👈 Add this line
    plt.render()   # re-render the scene

def OnKeyPress(evt):               ### called every time a key is pressed
    global Xi, energy_plot
    if evt.keypress in ['c', 'C']: # reset Xi and the arrows
        Xi = np.empty((0, 3))
        plt.remove("Arrow")
        plt.remove("RightClickMarker")
        plt.remove("RightClickLabel")
        if energy_plot:
            plt.remove(energy_plot)
            energy_plot = None
        plt.render()  

def OnSliderAlpha(widget, event): ### called every time the slider is moved
    val = widget.value         # get the slider value
    fplt3d[0].alpha(val)       # set the alpha (transparency) value of the surface
    fplt3d[1].alpha(val)       # set the alpha (transparency) value of the isolines

def OnMousePress(evt):
    global mouse_down
    mouse_down = True

    pt = evt.picked3d
    if pt is None:
        return

    pt = np.array(pt)

    sphere = vd.Sphere(pos=pt, r=0.02, c='red')
    sphere.name = "RightClickMarker"
    
    # Clean coordinate label (small and above the sphere)
    text_pos = pt + np.array([0.0, 0.0, 0.5])  # move only upward (Z)
    label = vd.Text3D(
        f"{vd.precision(pt, 2)}",
        pos=text_pos,
        s=0.04,             # smaller font
        c='black',
        justify='center'
    )
    label.name="RightClickLabel"
    label.lighting('off')  # make sure it's always visible

    plt.add(sphere, label)
    plt.render()

    mouse_down = False  # Reset immediately after

  
def update_energy_plot():
    global energy_plot, plt

    if Xi.shape[0] < 2:
        return

    # Extract step indices and energy values
    steps = np.arange(len(Xi))
    energies = Xi[:, 2]

    # Remove old plot if it exists
    if energy_plot:
        plt.remove(energy_plot)

    # Create and clone the 2D energy plot
    new_plot = plot(steps, energies, lc='blue', title='Energy along path')
    energy_plot = new_plot.clone2d( pos='top-left', size=0.8)
    plt.add(energy_plot)

#%% Optimization functions
def gradient_fd(func, X, h=0.001): # finite difference gradient
    x, y = X[0], X[1]
    gx = (func([x+h, y]) - func([x-h, y])) / (2*h)
    gy = (func([x, y+h]) - func([x, y-h])) / (2*h)
    return gx, gy

def Hessian_fd(func, X, h=0.001): # finite difference Hessian
    x, y = X[0], X[1]
    gxx = (func([x+h, y]) - 2*func([x, y]) + func([x-h, y])) / h**2
    gyy = (func([x, y+h]) - 2*func([x, y]) + func([x, y-h])) / h**2
    gxy = (func([x+h, y+h]) - func([x+h, y-h]) - func([x-h, y+h]) + func([x-h, y-h])) / (4*h**2)
    H = np.array([[gxx, gxy], [gxy, gyy]])
    return H

def gradient_descent(func, X): # compute gradient step direction
    g = gradient_fd(func, X)
    return -np.array(g)

def Newton(func, X):   # compute Newton step direction
    g = gradient_fd(func, X)
    H = Hessian_fd(func, X)
    d = -np.linalg.solve(H, np.array(g))
    return np.array(d[0],d[1])

def line_search(func, X, d, alpha=1.0): 
    # todo: implement line search
    return alpha

def step(func, X, search_direction_function):
    d = search_direction_function(func, X)
    alpha = line_search(func, X, d)
    return X + d*alpha

def optimize(func, X, search_direction_function, tol=1e-6, iter_max=10):
    for i in range(iter_max):
        X = step(func, X, search_direction_function)
        if np.linalg.norm(gradient_fd(func, X)) < tol:
            break
    return X

#%% Plotting

def objective(X):
    x, y = X[0], X[1]
    return np.sin(2*x*y) * np.cos(3*y)/2+1/2

Xi = np.empty((0, 3))
energy_plot = None
# test the optimization functions
X = optimize(objective, [0.6, 0.6], Newton, tol=1e-6, iter_max=100)

plt = vd.Plotter(bg2='lightblue', size=(1600, 900))  # Create the plotter
fplt3d = plot(lambda x,y: objective([x,y]), c='terrain')      # create a plot from the function e. fplt3d is a list containing surface mesh, isolines, and axis
fplt2d = fplt3d.clone()            # clone the plot to create a 2D plot

fplt2d[0].lighting('off')          # turn off lighting for the 2D plot
fplt2d[0].vertices[:,2] = 0        # set the z-coordinate of the mesh to 0
fplt2d[1].vertices[:,2] = 0        # set the z-coordinate of the isolines to 0

plt.add_callback('mouse move', OnMouseMove) # add Mouse move callback
plt.add_callback('key press', OnKeyPress) # add Keyboard callback
plt.add_callback("right button press", OnMousePress)
plt.add_slider(OnSliderAlpha,0.,1.,1., title="Alpha") # add a slider for the alpha value of the surface
plt.show([fplt3d, fplt2d], msg, __doc__, viewup='z')
plt.close()
# %%
