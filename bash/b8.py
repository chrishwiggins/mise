from scipy.linalg import eigh
# Define stiffness (K) and mass (M) matrices
K = np.array([[12, -6], [-6, 4]])
M = np.array([[2, 0], [0, 1]])
# Solve the eigenvalue problem for natural frequencies
w, v = eigh(K, M)
print("Natural frequencies:", np.sqrt(w))
# Plot mode shapes
for i in range(len(w)):
    plt.plot([0, 1], [0, v[:, i][0]], label=f'Mode {i+1}')
plt.title('Mode Shapes')
plt.legend()
plt.show()

