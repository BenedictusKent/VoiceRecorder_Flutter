import numpy as np
x_c = [143, 164, 187, 165, 188, 210, 189, 211, 233]
y_c = [210, 233, 255, 188, 210, 234, 166, 189, 212]
A = [x_c,
    y_c,
    [1 for i in range(len(x_c))]]

real_x_r = [275, 275, 275, 325, 325, 325, 375, 375, 375]
real_y_r = [400, 450, 500, 400, 450, 500, 400, 450, 500]
B = [real_x_r,
    real_y_r,
    [1 for i in range(len(real_x_r))]]

A = np.array(A)
B = np.array(B)
T = np.matmul(B, np.linalg.pinv(A))
print('Transformation Matrix: ')
print(T)

# for i in range(len(x_c)):
#     x_r = 1.1267750978091868*x_c[i] - 1.0938629253027443*y_c[i] +343.9786726668608
#     y_r = 1.0775851441372453*x_c[i] + 1.1433776167399117*y_c[i] + 6.654863050272979
#     print('Estimated Pos: ' + str(int(x_r)) + ' ' + str(int(y_r)) + '; Real Pos: '+ str(real_x_r[i]) + ' ' + str(real_y_r[i]))