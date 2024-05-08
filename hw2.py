import cv2
import numpy as np
import matplotlib.pyplot as plt

def Laplacian_filter(img):
    M, N = img.shape
    H = np.zeros((M, N))

    for u in range(M):
        for v in range(N):
            u2 = np.power((u - M / 2), 2)
            v2 = np.power((v - N / 2), 2)
            H[u, v] = -(u2 + v2)

    return H

def show_image(img):
    plt.imshow(img, cmap='gray'), plt.axis('off')
    plt.show()

# Load image
original_image = cv2.imread("gatsby.jpg", 0)
M, N = original_image.shape

# Zero-padding
P, Q = 2 * M, 2 * N
padded_image = np.zeros((P, Q))
padded_image[:M, :N] = original_image

# Centering
padded_image_shifted = np.zeros((P, Q))
for x in range(P):
    for y in range(Q):
        padded_image_shifted[x, y] = padded_image[x, y] * ((-1) ** (x + y))

# Laplacian Filter
dft_result = np.fft.fft2(padded_image_shifted)
laplacian_filter = Laplacian_filter(dft_result)
filtered_dft = np.multiply(dft_result, laplacian_filter)

# Inverse Fourier Transform
inverse_dft_result = np.fft.ifft2(filtered_dft)

# De-centering
for x in range(P):
    for y in range(Q):
        inverse_dft_result[x, y] = inverse_dft_result[x, y] * ((-1) ** (x + y))

# Remove zero-padding part and normalize
inverse_dft_result = inverse_dft_result[:M, :N]
min_val, max_val = np.min(inverse_dft_result), np.max(inverse_dft_result)
normalized_result = (inverse_dft_result - min_val) / (max_val - min_val) * 255.0

# Smoothed and Sharpened images
smoothed_image = original_image + normalized_result
sharpened_image = original_image - normalized_result

# Display images
show_image(smoothed_image.real)
show_image(sharpened_image.real)
