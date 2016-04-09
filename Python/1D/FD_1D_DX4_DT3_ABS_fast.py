## FD_1D_DX4_DT3_ABS_fast.py 1-D acoustic Finite-Difference modelling
# GNU General Public License v3.0
#
# Author: Florian Wittkamp 2016
#
# Finite-Difference acoustic seismic wave simulation
# Discretization of the first-order acoustic wave equation
#
# Temporal second-order accuracy O(DT^3)
# Spatial fourth-order accuracy  O(DX^4)
#
# Temporal discretization is based on the Adams-Basforth method
# Theory is available in:
# Bohlen, T., & Wittkamp, F. (2016).
# Three-dimensional viscoelastic time-domain finite-difference
# seismic modelling using the staggered Adams?Bashforth time integrator.
# Geophysical Journal International, 204(3), 1781-1788.

##  Initialisation
print(" ")
print("Starting FD_1D_DX4_DT3_ABS_fast")

from numpy import *
import time as tm
import matplotlib.pyplot as plt

## Input Parameter

# Discretization
c1=20   # Number of grid points per dominant wavelength
c2=0.5  # CFL-Number
nx=2000 # Number of grid points
T=10     # Total propagation time

# Source Signal
f0= 10      # Center frequency Ricker-wavelet
q0= 1       # Maximum amplitude Ricker-Wavelet
xscr = 100  # Source position (in grid points)

# Receiver
xrec1=400  # Position Reciever 1 (in grid points)
xrec2=800  # Position Reciever 2 (in grid points)
xrec3=1800 # Position Reciever 3 (in grid points)

# Velocity and density
modell_v = hstack((1000*ones((around(nx/2)),float),1500*ones((around(nx/2)),float)))
rho=hstack((1*ones((around(nx/2)),float),1.5*ones((around(nx/2)),float)))

## Preparation

# Init wavefields
vx=zeros((nx),float)
p=zeros((nx),float)
vx_x=zeros((nx),float)
p_x=zeros((nx),float)
vx_x2=zeros((nx),float)
p_x2=zeros((nx),float)
vx_x3=zeros((nx),float)
p_x3=zeros((nx),float)

# Calculate first Lame-Paramter
l=rho * modell_v * modell_v

cmin=min(modell_v.flatten())  # Lowest P-wave velocity
cmax=max(modell_v.flatten())  # Highest P-wave velocity
fmax=2*f0                     # Maximum frequency
dx=cmin/(fmax*c1)             # Spatial discretization (in m)
dt=dx/(cmax)*c2               # Temporal discretization (in s)
lampda_min=cmin/fmax          # Smallest wavelength

# Output model parameter:
print("Model size: x:",dx*nx,"in m")
print("Temporal discretization: ",dt," s")
print("Spatial discretization: ",dx," m")
print("Number of gridpoints per minimum wavelength: ",lampda_min/dx)

# Create space and time vector
x=arange(0,dx*nx,dx) # Space vector
t=arange(0,T,dt)     # Time vector
nt=size(t)           # Number of time steps

# Plotting model
plt.figure(1)
plt.plot(x,modell_v)
plt.ylabel('VP in m/s')
plt.xlabel('Depth in m')
plt.figure(2)
plt.plot(x,rho)
plt.ylabel('Density in g/cm^3')
plt.xlabel('Depth in m')
plt.draw()
plt.pause(0.001)

# Source signal - Ricker-wavelet
tau=pi*f0*(t-1.5/f0)
q=q0*(1-2*tau**2)*exp(-tau**2)

# Plotting source signal
plt.figure(3)
plt.plot(t,q)
plt.title('Source signal Ricker-Wavelet')
plt.ylabel('Amplitude')
plt.xlabel('Time in s')
plt.draw()
plt.pause(0.001)

# Init Seismograms
Seismogramm=zeros((3,nt),float); # Three seismograms

# Calculation of some coefficients
i_dx=1.0/(dx)
kx=arange(5,nx-5)

## Time stepping
print("Starting time stepping...")
tic=tm.clock()
for n in range(2,nt):

        # Inject source wavelet
        p[xscr]=p[xscr]+q[n]

        # Calculating spatial derivative
        p_x[kx]=i_dx*9.0/8.0*(p[kx+1]-p[kx])-i_dx*1.0/24.0*(p[kx+2]-p[kx-1])

        # Update velocity
        vx[kx]=vx[kx]-dt/rho[kx]*(25.0/24.0*p_x[kx]-1.0/12.0*p_x2[kx]+1.0/24.0*p_x3[kx])

        # Save old spatial derivations for Adam-Bashforth method
        copyto(p_x3,p_x2)
        copyto(p_x2,p_x)

        # Calculating spatial derivative
        vx_x[kx]=i_dx*9.0/8.0*(vx[kx]-vx[kx-1])-i_dx*1.0/24.0*(vx[kx+1]-vx[kx-2])

        # Update pressure
        p[kx]=p[kx]-l[kx]*dt*(25.0/24.0*vx_x[kx]-1.0/12.0*vx_x2[kx]+1.0/24.0*vx_x3[kx])

        # Save old spatial derivations for Adam-Bashforth method
        copyto(vx_x3,vx_x2)
        copyto(vx_x2,vx_x)

        # Save seismograms
        Seismogramm[0,n]=p[xrec1]
        Seismogramm[1,n]=p[xrec2]
        Seismogramm[2,n]=p[xrec3]

toc = tm.clock()
time=toc-tic

## Plot seismograms
plt.figure(4)
plt.plot(t,Seismogramm[0,:])
plt.title('Seismogram 1')
plt.ylabel('Amplitude')
plt.xlabel('Time in s')

plt.figure(5)
plt.plot(t,Seismogramm[1,:])
plt.title('Seismogram 2')
plt.ylabel('Amplitude')
plt.xlabel('Time in s')

plt.figure(6)
plt.plot(t,Seismogramm[2,:])
plt.title('Seismogram 3')
plt.ylabel('Amplitude')
plt.xlabel('Time in s')
plt.draw()

plt.show()

print(" ")
