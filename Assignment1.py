#%% imports
import vedo as vd
import numpy as np
from vedo.pyplot import plot
from vedo import Latex
import timeit

import time


vd.settings.default_backend= 'vtk'
plt = vd.Plotter(bg2='lightblue')  # 💥 Move this UP here

#%% Function Selection
def wavy_sine_cosine(X):
    x, y = X[0], X[1]
    return np.sin(2 * x * y) * np.cos(3 * y) / 2 + 0.5

def ripple_pattern(X):
    x, y = X[0], X[1]
    return np.cos(x) * np.sin(y) + 0.5

def gaussian_hill(X):
    x, y = X[0], X[1]
    return np.exp(-x**2 - y**2)

current_function = wavy_sine_cosine  # default function
my_functions = [wavy_sine_cosine, ripple_pattern, gaussian_hill]


def objective(X):
    return current_function(X)

def change_objective(new_index):
    global current_function_index, current_function, fplt3d, fplt2d, Xi, Yi, dot_products, fplt2d_clone , fplt2d2

    current_function_index = new_index
    current_function = my_functions[new_index]

    # Clear all markers/paths
    Xi = np.empty((0, 3))
    Yi = np.empty((0, 3))
    dot_products = []
    if fplt2d_clone:
        plt.remove(fplt2d_clone)
        fplt2d_clone = None

    plt.remove("Arrow")
    plt.remove("Point")
    plt.remove("LeftClickMarker")
    plt.remove("RightClickMarker")
    plt.remove("LeftClickLabel")
    plt.remove("RightClickLabel")
    plt.remove("OptStepMarker")
    plt.remove("NewtonStepMarker")

    # Remove and regenerate plots
    plt.remove(fplt3d)
    plt.remove(fplt2d)

    fplt3d = plot(lambda x, y: objective([x, y]), c='terrain')
    fplt2d = fplt3d.clone()
    fplt2d[0].lighting('off')
    fplt2d[0].vertices[:, 2] = 0
    fplt2d[1].vertices[:, 2] = 0

    plt.add(fplt3d)
    plt.add(fplt2d)

    plt.render()

#%% Callbacks
msg = vd.Text2D(pos='bottom-left', font="VictorMono") # an empty text
msg2 = vd.Text2D(pos='top-left', font="VictorMono") # an empty text

msg5=vd.Text2D("Black: GD Energy", pos=(0.3, 0.84), c='black', font="VictorMono", s=0.8)
msg6=vd.Text2D("Orange: Newton Energy", pos=(0.3, 0.92), c='orange', font="VictorMono", s=0.8)
msg7=vd.Text2D("Green: Dot Product", pos=(0.3, 0.88), c='green', font="VictorMono", s=0.8)
current_function_index = 0  # initialize the current function index


def OnMouseMove(evt):                ### called every time mouse moves!
    global Xi, fplt3d, isDrawing, objective, msg, plt, fplt2d_clone, fplt2d2 , fplt2d, fplt3d, msg2

    if evt.object is None:          # mouse hits nothing, return
        return

    pt  = evt.picked3d               # 3d coords of point under mouse
    
    X   = np.array([pt[0],pt[1],objective([pt[0],pt[1]])])  # X = (x,y,e(x,y))
    #if isDrawing:                                 # only add points if in path drawing mode
    #    Xi = np.append(Xi,[X],axis=0)             # append to the list of points
    #    visualize_path()                          # visualize path with the new point                  
    if len(Xi) > 1 and isDrawing:                  # need at least two points to compute a distance
        txt =(
            f"X:  {vd.precision(X,2)}"
           # f"dX: {vd.precision(Xi[-1,0:2] - Xi[-2,0:2],2)}\n"
           # f"dE: {vd.precision(Xi[-1,2] - Xi[-2,2],2)}\n"
        )
    #    ar = vd.Arrow(Xi[-2,:], Xi[-1,:], s=0.001, c='orange5')
    #    plt.add(ar) # add the arrow
    else:
        txt = f"X: {vd.precision(X,2)}"
    msg.text(txt)                    # update text message

    #c = vd.Cylinder([np.append(Xi[-1,0:2], 0.0), Xi[-1,:]], r=0.01, c='orange5')
    #plt.remove("Cylinder")    
    fp = fplt3d[0].flagpole(txt, point=X,s=0.08, c='k', font="Quikhand")
    fp.follow_camera()                 # make it always face the camera
    plt.remove("FlagPole") # remove the old flagpole

    #plt.add(fp, c) # add the new flagpole and new cylinder
    plt.add(fp) # add the new flagpole
    plt.render()   # re-render the scene

dot_products = []  # initialize a list to store dot products

def run_both_optimizations():
    global Xi, Yi, dot_products , objective, gradient_descent, Newton, step_size, num_steps, msg2
    for _ in range(num_steps):
            if len(Xi) == 0 or len(Yi) == 0: 
                msg2.text("Initial guess is not set!")  # display error message
            else:
                msg2.text("")    # clear error message    
                X = Xi[-1, 0:2]  # get the last point as the starting point
                y = Yi[-1, 0:2] 
                d = gradient_descent(objective, X)        # compute the gradient descent step
                n, g_newton = Newton(objective, X)        # compute the Newton step and get the gradient
                dot_products.append(np.dot(g_newton, n))  # compute dot product
                Xi = np.vstack((Xi, np.append(X + d * step_size, objective(X + d * step_size))))  # append new point to Xi 
                Yi = np.vstack((Yi, np.append(y + Newton(objective, y)[0] * step_size, objective(y + Newton(objective, y)[0] * step_size)))) # append new point to Yi

                ar = vd.Arrow(Xi[-2,:], Xi[-1,:], s=0.001, c='orange5')
                ar2 = vd.Arrow(Yi[-2,:], Yi[-1,:], s=0.001, c='blue5')
                plt.add(ar) # add the arrow
                plt.add(ar2)

    update_2d_graph()
    plt.render()      # re-render  



def OnKeyPress(evt):               ### called every time a key is pressed
    global plt, objective, gradient_descent, Newton, update_2d_graph, fplt2d_clone, fplt2d2, Xi, Yi, dot_products, fplt3d, fplt2d, msg2
    if evt.keypress in ['c', 'C', '1', '2', '3']: # reset Xi and the arrows
        Xi = np.empty((0, 3))
        Yi = np.empty((0, 3))
        dot_products = []
        plt.remove("Arrow").render()
        plt.remove("Point").render()      # remove the old initial_guess
        plt.remove(fplt2d_clone).render() # remove the old clone plot

    if evt.keypress in ['1', '2', '3']:
        change_objective(int(evt.keypress) - 1)


    if evt.keypress in ['r', 'R']:        # run gradient descent
        run_both_optimizations()

    plt.render()  # re-render the plotter
        

def OnSliderAlpha(widget, event): ### called every time the slider is moved
    val = widget.value         # get the slider value
    fplt3d[0].alpha(val)       # set the alpha (transparency) value of the surface
    fplt3d[1].alpha(val)       # set the alpha (transparency) value of the isolines


num_steps = 10   # default number of steps
step_size = 0.1  # default step size

def OnSliderNumSteps(widget, event):
    global num_steps
    num_steps = int(widget.value)  # update the number of steps based on slider value

def OnSliderStepSize(widget, event):
    global step_size
    step_size = widget.value       # update the step size based on slider value


isDrawing = True               # global variable to track the path drawing mode

def OnRightMousePress(evt):
    global isDrawing, Xi, Yi, dot_products, fplt2d_clone , fplt2d2, fplt3d, fplt2d
    if evt.object is None:
        return

    pt = evt.picked3d
    if pt is None:
        return

    pt = np.array(pt)

    # Create a red sphere at the clicked location
    sphere = vd.Sphere(pos=pt, r=0.02, c='red')
    sphere.name = "RightClickMarker"

    # Create a label slightly above the sphere
    text_pos = pt + np.array([0.0, 0.0, 0.5])
    label = vd.Text3D(
        f"{vd.precision(pt, 2)}",
        pos=text_pos,
        s=0.04,
        c='black',
        justify='center'
    )
    label.name = "RightClickLabel"
    label.lighting('off')

    plt.add(sphere, label)
    plt.render()


def OnLeftMousePress(evt):
    global Xi, Yi, dot_products, fplt2d_clone, fplt2d2, fplt3d, fplt2d

    if evt.object is None:
        return

    pt = evt.picked3d
    if pt is None:
        return

    pt = np.array(pt)

    # Remove old markers and arrows
    plt.remove("LeftClickMarker")
    plt.remove("LeftClickLabel")
    plt.remove("Arrow")
    plt.remove("OptStepMarker")
    plt.remove("NewtonStepMarker")

    # Remove old plot if exists
    if fplt2d_clone:
        plt.remove(fplt2d_clone)
        fplt2d_clone = None

    # Add black sphere marker
    sphere = vd.Sphere(pos=pt, r=0.02, c='black')
    sphere.name = "LeftClickMarker"

    # Add label with initial guess
    text_pos = pt + np.array([0.0, 0.0, 0.5])
    label = vd.Text3D(
        f"Initial guess:\n{vd.precision(pt, 2)}",
        pos=text_pos,
        s=0.04,
        c='black',
        justify='center'
    )
    label.name = "LeftClickLabel"
    label.lighting('off')

    plt.add(sphere, label)

    # Clear old optimization paths and dot products
    Xi = np.empty((0, 3))
    Yi = np.empty((0, 3))
    dot_products = []

    # Save new starting point for both paths
    value = objective(pt[:2])
    Xi = np.append(Xi, [[pt[0], pt[1], value]], axis=0)
    Yi = np.append(Yi, [[pt[0], pt[1], value]], axis=0)

    plt.render()


  
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
    return d, np.array(g)  # return both search direction and gradient


def line_search(func, X, d, alpha=1.0):
    """
    Backtracking line search using Armijo condition.

    Parameters:
        func : objective function
        X    : current point (numpy array)
        d    : descent direction
        alpha: initial step size (default = 1.0)
        rho  : shrink factor (0 < rho < 1), typically 0.5
        c    : Armijo condition constant (typically small, e.g., 1e-4)

    Returns:
        optimal alpha step size
    """
    rho = 0.5
    c = 1e-4
    f0 = func(X)
    grad = gradient_fd(func, X)
    
    while func(X + alpha * d) > f0 + c * alpha * np.dot(grad, d):
        alpha *= rho
        if alpha < 1e-8:  # avoid infinite loop
            break
    
    return alpha


def step(func, X, search_direction_function):
    d = search_direction_function(func, X)[0]
    alpha = line_search(func, X, d)
    return X + d*alpha

def optimize(func, X, search_direction_function, tol=1e-6, iter_max=10):
    for i in range(iter_max):
        X = step(func, X, search_direction_function)
        if np.linalg.norm(gradient_fd(func, X)) < tol:
            break
    return X

def analytical_gradient(X):
    x, y = X[0], X[1]

    if current_function == wavy_sine_cosine:
        df_dx = 2 * y * np.cos(2 * x * y) * np.cos(3 * y) / 2
        df_dy = (2 * x * np.cos(2 * x * y) * np.cos(3 * y) - 
                 3 * np.sin(2 * x * y) * np.sin(3 * y)) / 2
        return np.array([df_dx, df_dy])

    elif current_function == ripple_pattern:
        df_dx = -np.sin(x) * np.sin(y)
        df_dy = np.cos(x) * np.cos(y)
        return np.array([df_dx, df_dy])

    elif current_function == gaussian_hill:
        df_dx = -2 * x * np.exp(-x**2 - y**2)
        df_dy = -2 * y * np.exp(-x**2 - y**2)
        return np.array([df_dx, df_dy])

def analytical_hessian(X):
    x, y = X[0], X[1]

    if current_function == wavy_sine_cosine:
        d2f_dx2 = -4 * y**2 * np.sin(2 * x * y) * np.cos(3 * y) / 2
        d2f_dy2 = (-4 * x**2 * np.sin(2 * x * y) * np.cos(3 * y) -
                   9 * np.sin(2 * x * y) * np.cos(3 * y) -
                   6 * x * np.cos(2 * x * y) * np.sin(3 * y)) / 2
        d2f_dxdy = (2 * np.cos(2 * x * y) * np.cos(3 * y) -
                    6 * y * np.sin(2 * x * y) * np.sin(3 * y)) / 2
        return np.array([[d2f_dx2, d2f_dxdy],
                         [d2f_dxdy, d2f_dy2]])

    elif current_function == ripple_pattern:
        d2f_dx2 = -np.cos(x) * np.sin(y)
        d2f_dy2 = -np.cos(x) * np.sin(y)
        d2f_dxdy = -np.sin(x) * np.cos(y)
        return np.array([[d2f_dx2, d2f_dxdy],
                         [d2f_dxdy, d2f_dy2]])

    elif current_function == gaussian_hill:
        e = np.exp(-x**2 - y**2)
        d2f_dx2 = e * (4 * x**2 - 2)
        d2f_dy2 = e * (4 * y**2 - 2)
        d2f_dxdy = 4 * x * y * e
        return np.array([[d2f_dx2, d2f_dxdy],
                         [d2f_dxdy, d2f_dy2]])



#%% Plotting

Xi = np.empty((0, 3))
Yi = np.empty((0, 3))
# test the optimization functions
X = optimize(objective, [0.6, 0.6], Newton, tol=1e-6, iter_max=100)

plt = vd.Plotter(bg2='lightblue')  # Create the plotter
fplt3d = plot(lambda x,y: objective([x,y]), c='terrain')      # create a plot from the function e. fplt3d is a list containing surface mesh, isolines, and axis
fplt2d = fplt3d.clone()            # clone the plot to create a 2D plot


fplt2d[0].lighting('off')          # turn off lighting for the 2D plot
fplt2d[0].vertices[:,2] = 0        # set the z-coordinate of the mesh to 0
fplt2d[1].vertices[:,2] = 0        # set the z-coordinate of the isolines to 0

fplt2d_clone = None
fplt2d2 = None

def update_2d_graph():
    global fplt2d_clone, fplt2d2, dot_products, Xi, Yi, fplt3d, fplt2d, msg2
    if len(Xi) > 1 and len(Yi) > 1:
        x_values = range(1, len(Xi) + 1)    # indexes of GD path points
        z_values = Xi[:, 2]                 # the function values for GD path points
        
        x_values_Yi = range(1, len(Yi) + 1) # indexes of Newton path points
        z_values_Yi = Yi[:, 2]              # the function values for Newton path points 

        dp_x_values = range(1, len(dot_products) + 1) # indexes of dot products points
        
        fplt2d2 = plot(x_values, z_values, c='orange5', lw=2, title="Function Values on Path/ Dot product") # create a new 2D plot for GD path
        fplt2d2 += plot(x_values_Yi, z_values_Yi, c='blue5', lw=2, like=fplt2d2)               # add the plot for Newton path to the existing one
        fplt2d2 += plot(dp_x_values, dot_products, c='green5', lw=2, like=fplt2d2)             # add the plot for dot products to the existing one

        if fplt2d_clone is not None:
            plt.remove(fplt2d_clone)
        
        fplt2d_clone = fplt2d2.clone2d(pos='top-left', size=0.8)   # clone the plot to maintain the appearance

        plt.add(fplt2d_clone)  # add the plot to the plotter




plt.add_callback('mouse move', OnMouseMove) # add Mouse move callback
plt.add_callback('key press', OnKeyPress)   # add Keyboard callback
plt.add_callback('RightButtonPressEvent', OnRightMousePress)  # add Mouse press callback
plt.add_callback('LeftButtonPressEvent', OnLeftMousePress)    # add Mouse press callback
plt.add_slider(OnSliderAlpha,0.,1.,1., title="Alpha")         # add a slider for the alpha value of the surface
plt.add_slider(OnSliderStepSize, 0.01, 1.0, value=step_size, c='red', pos=2, title="Step Size")
plt.add_slider(OnSliderNumSteps, 1, 50, value=num_steps,c='blue', pos=3, title="Num Steps")
plt.show([fplt3d, fplt2d], msg, msg2, msg5, msg6, msg7, __doc__, viewup='z')

point = np.array([0.6, 0.6])
function_to_test = my_functions[0]  # testing on wavy_sine_cosine

num_iterations = 10000

# Time for numerical gradient
t_numerical_grad = timeit.timeit(lambda: gradient_fd(function_to_test, point), number=num_iterations)
print(f"Numerical Gradient Time: {t_numerical_grad:.5f} sec for {num_iterations} iterations")

# Time for analytical gradient
t_analytical_grad = timeit.timeit(lambda: analytical_gradient(point), number=num_iterations)
print(f"Analytical Gradient Time: {t_analytical_grad:.5f} sec for {num_iterations} iterations")

# Time for numerical Hessian
t_numerical_hess = timeit.timeit(lambda: Hessian_fd(function_to_test, point), number=num_iterations)
print(f"Numerical Hessian Time: {t_numerical_hess:.5f} sec for {num_iterations} iterations")

# Time for analytical Hessian
t_analytical_hess = timeit.timeit(lambda: analytical_hessian(point), number=num_iterations)
print(f"Analytical Hessian Time: {t_analytical_hess:.5f} sec for {num_iterations} iterations")


# -------------------------------
# Task 5.3 – Epsilon Sensitivity
# -------------------------------

# -------------------------------
# Task 5.3 – Epsilon Sensitivity
# -------------------------------
print("\n--- Finite Difference Gradient vs Analytical Gradient ---")
print(f"Testing Function: {current_function.__name__}\n")

# Use multiple test points (but same current objective)
test_cases = {
    "Point A (0.6, 0.6)": np.array([0.6, 0.6]),
    "Point B (1.2, -0.8)": np.array([1.2, -0.8]),
    "Point C (0.0, 1.5)": np.array([0.0, 1.5])
}

epsilon_values = [0.1, 0.01, 0.001, 0.0001, 1e-5]

for label, X0 in test_cases.items():
    true_gradient = analytical_gradient(X0)
    print(f"\n{label} | True Gradient: [{true_gradient[0]:.6f}, {true_gradient[1]:.6f}]")

    for eps in epsilon_values:
        finite_diff_gradient = gradient_fd(objective, X0, h=eps)

        print(f"  Epsilon: {eps:.5f} | "
              f"FD: [{finite_diff_gradient[0]:.6f}, {finite_diff_gradient[1]:.6f}] | "
              f"Diff: [{finite_diff_gradient[0] - true_gradient[0]:.6f}, "
              f"{finite_diff_gradient[1] - true_gradient[1]:.6f}]")


plt.close()
# %%