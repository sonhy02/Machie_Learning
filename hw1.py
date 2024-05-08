import cv2
import numpy as np
import matplotlib.pyplot as plt


def discrete_fourier_transform(padded_image):
    rows, cols = padded_image.shape
    dft_result = np.zeros((rows, cols), dtype=complex)

    for u in range(rows):
        for v in range(cols):
            sum_ = 0.0
            for m in range(rows):
                for n in range(cols):
                    e = np.exp(-2j * np.pi * ((u * m) / rows + (v * n) / cols))
                    sum_ += padded_image[m, n] * e
            dft_result[u, v] = sum_

    return dft_result


def ideal_low_pass_filter(image):
    rows, cols = image.shape
    lpf = np.zeros((rows, cols))
    d = np.zeros((rows, cols))
    center_row = rows // 2
    center_col = cols // 2

    d0 = 10
    for u in range(rows):
        for v in range(cols):
            u_squared = np.power(u, 2)
            v_squared = np.power(v, 2)
            d[u, v] = np.sqrt(u_squared + v_squared)

    for u in range(rows):
        for v in range(cols):
            if d[np.abs(u - center_row), np.abs(v - center_col)] <= d0:
                lpf[u, v] = 1
            else:
                lpf[u, v] = 0
    return lpf


def inverse_discrete_fourier_transform(dft_image):
    M, N = dft_image.shape
    idft_result = np.zeros((M, N), dtype=complex)

    for u in range(M):
        for v in range(N):
            sum_ = 0.0
            for m in range(M):
                for n in range(N):
                    e = np.exp(2j * np.pi * ((u * m) / M + (v * n) / N))
                    sum_ += dft_image[m, n] * e
            idft_result[u, v] = sum_
    return idft_result


def show_image(img):
    plt.imshow(img, cmap='gray'), plt.axis('off')
    plt.show()


original_image = cv2.imread("gatsby.jpg", 0)
original_rows, original_cols = original_image.shape

resized_image = cv2.resize(original_image, (32, 32))
resized_rows, resized_cols = resized_image.shape

padded_rows, padded_cols = 2 * resized_rows, 2 * resized_cols
padded_image = np.zeros((padded_rows, padded_cols))
padded_image[:resized_rows, :resized_cols] = resized_image

padded_image_shifted = np.zeros((padded_rows, padded_cols))
for x in range(padded_rows):
    for y in range(padded_cols):
        padded_image_shifted[x, y] = padded_image[x, y] * ((-1) ** (x + y))

dft_result = discrete_fourier_transform(padded_image_shifted)
print("Discrete Fourier Transform completed with centering")

lpf = ideal_low_pass_filter(dft_result)

filtered_dft = np.multiply(dft_result, lpf)

inverse_dft_result = inverse_discrete_fourier_transform(filtered_dft)

for x in range(padded_rows):
    for y in range(padded_cols):
        inverse_dft_result[x, y] = inverse_dft_result[x, y] * ((-1) ** (x + y))

final_image = inverse_dft_result[:(padded_rows // 2), :(padded_cols // 2)].real
show_image(final_image)
