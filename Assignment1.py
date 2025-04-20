#%% imports
import vedo as vd
import numpy as np
from vedo.pyplot import plot
from vedo import Latex

vd.settings.default_backend = 'vtk'

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

def objective(X):
    return current_function(X)

#%% Callbacks
msg = vd.Text2D(pos='bottom-left', font="VictorMono")
global mouse_down, fplt3d, fplt2d
mouse_down = False

def OnMouseMove(evt):
    global Xi, mouse_down, energy_plot, fplt3d

    if evt.object is None:
        return

    pt = evt.picked3d
    X = np.array([pt[0], pt[1], objective([pt[0], pt[1]])])
    if not mouse_down:
        Xi = np.append(Xi, [X], axis=0)

    if len(Xi) > 1:
        txt = (
            f"X:  {vd.precision(X,2)}\n"
            f"dX: {vd.precision(Xi[-1,0:2] - Xi[-2,0:2],2)}\n"
            f"dE: {vd.precision(Xi[-1,2] - Xi[-2,2],2)}\n"
        )
        ar = vd.Arrow(Xi[-2,:], Xi[-1,:], s=0.001, c='orange5')
        plt.add(ar)
    else:
        txt = f"X: {vd.precision(X,2)}"
    msg.text(txt)

    c = vd.Cylinder([np.append(Xi[-1,0:2], 0.0), Xi[-1,:]], r=0.01, c='orange5')
    plt.remove("Cylinder")

    fp = fplt3d[0].flagpole(txt, point=X, s=0.08, c='k', font="Quikhand")
    fp.follow_camera()
    plt.remove("FlagPole")

    plt.add(fp, c)
    update_energy_plot()
    plt.render()

def OnKeyPress(evt):
    global Xi, energy_plot, current_function

    if evt.keypress in ['c', 'C','1','2','3']:
        Xi = np.empty((0, 3))
        plt.remove("Arrow")
        plt.remove("RightClickMarker")
        plt.remove("RightClickLabel")
        if energy_plot:
            plt.remove(energy_plot)
            energy_plot = None
        plt.render()

    if evt.keypress == '1':
        current_function = wavy_sine_cosine
        reset_surface_plot()
    if evt.keypress == '2':
        current_function = ripple_pattern
        reset_surface_plot()
    if evt.keypress == '3':
        current_function = gaussian_hill
        reset_surface_plot()

def reset_surface_plot():
    global fplt3d, fplt2d, Xi, energy_plot

    Xi = np.empty((0, 3))
    if energy_plot:
        plt.remove(energy_plot)
        energy_plot = None
    plt.remove(fplt3d)
    plt.remove(fplt2d)

    fplt3d = plot(lambda x, y: objective([x, y]), c='terrain')
    fplt2d = fplt3d.clone()
    fplt2d[0].lighting('off')
    fplt2d[0].vertices[:, 2] = 0
    fplt2d[1].vertices[:, 2] = 0
    plt.add(fplt3d, fplt2d)
    plt.render()

def OnSliderAlpha(widget, event):
    global fplt3d
    val = widget.value
    fplt3d[0].alpha(val)
    fplt3d[1].alpha(val)

def OnMousePress(evt):
    global mouse_down
    mouse_down = True

    pt = evt.picked3d
    if pt is None:
        return

    pt = np.array(pt)

    sphere = vd.Sphere(pos=pt, r=0.02, c='red')
    sphere.name = "RightClickMarker"

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
    mouse_down = False

def update_energy_plot():
    global energy_plot, plt, Xi

    if Xi.shape[0] < 2:
        return

    steps = np.arange(len(Xi))
    energies = Xi[:, 2]

    if energy_plot:
        plt.remove(energy_plot)

    new_plot = plot(steps, energies, lc='blue', title='Energy along path')
    energy_plot = new_plot.clone2d(pos='top-left', size=0.8)
    plt.add(energy_plot)

#%% Optimization functions
def gradient_fd(func, X, h=0.001):
    x, y = X[0], X[1]
    gx = (func([x+h, y]) - func([x-h, y])) / (2*h)
    gy = (func([x, y+h]) - func([x, y-h])) / (2*h)
    return gx, gy

def Hessian_fd(func, X, h=0.001):
    x, y = X[0], X[1]
    gxx = (func([x+h, y]) - 2*func([x, y]) + func([x-h, y])) / h**2
    gyy = (func([x, y+h]) - 2*func([x, y]) + func([x, y-h])) / h**2
    gxy = (func([x+h, y+h]) - func([x+h, y-h]) - func([x-h, y+h]) + func([x-h, y-h])) / (4*h**2)
    H = np.array([[gxx, gxy], [gxy, gyy]])
    return H

def gradient_descent(func, X):
    g = gradient_fd(func, X)
    return -np.array(g)

def Newton(func, X):
    g = gradient_fd(func, X)
    H = Hessian_fd(func, X)
    d = -np.linalg.solve(H, np.array(g))
    return np.array([d[0], d[1]])

def line_search(func, X, d, alpha=1.0):
    return alpha

def step(func, X, search_direction_function):
    d = search_direction_function(func, X)
    alpha = line_search(func, X, d)
    return X + d * alpha

def optimize(func, X, search_direction_function, tol=1e-6, iter_max=10):
    for i in range(iter_max):
        X = step(func, X, search_direction_function)
        if np.linalg.norm(gradient_fd(func, X)) < tol:
            break
    return X

#%% Main Plotting
Xi = np.empty((0, 3))
energy_plot = None
X = optimize(objective, [0.6, 0.6], Newton, tol=1e-6, iter_max=100)

plt = vd.Plotter(bg2='lightblue', size=(1600, 900))
fplt3d = plot(lambda x, y: objective([x, y]), c='terrain')
fplt2d = fplt3d.clone()
fplt2d[0].lighting('off')
fplt2d[0].vertices[:, 2] = 0
fplt2d[1].vertices[:, 2] = 0

plt.add_callback('mouse move', OnMouseMove)
plt.add_callback('key press', OnKeyPress)
plt.add_callback("right button press", OnMousePress)
plt.add_slider(OnSliderAlpha, 0., 1., 1., title="Alpha")

plt.show([fplt3d, fplt2d], msg, __doc__, viewup='z')
plt.close()
# %%
