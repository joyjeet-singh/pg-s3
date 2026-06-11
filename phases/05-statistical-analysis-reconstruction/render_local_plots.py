import numpy as np
import matplotlib.pyplot as plt

# Render local plots script
data = np.load('topology_data.npz')
X = data['X']
vort = data['vort']
cut = data['cut']
r_vals = data['r_vals']
C = data['C']

# 1. Attractor
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')
ax.scatter(X[:, 0], X[:, 1], X[:, 2], s=0.5, c=vort, cmap='inferno')
plt.savefig('attractor_projection.pdf')

# 2. Poincare
plt.figure()
plt.scatter(cut[:, 0], cut[:, 1], s=1)
plt.savefig('poincare_section.pdf')

# 3. D2
plt.figure()
plt.loglog(r_vals, C, 'o-')
plt.savefig('correlation_dimension.pdf')
