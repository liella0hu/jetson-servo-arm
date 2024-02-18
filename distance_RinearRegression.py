import sklearn
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import numpy

distance_pixel = (numpy.array([180, 220, 240, 250, 270, 290, 320, 350])).reshape(8, 1)
distance_pixel_numpy = numpy.array([180, 220, 240, 250, 270, 290, 320, 350])

angle4 = (numpy.array([65, 55, 45, 40, 35, 30, 25, 25]))#.reshape(-1, 1)

angle7 = (numpy.array([-50, -45, -35, -30, -25, -25, -20, -15]))#.reshape(-1, 1)

angle4_and_angle7 = numpy.array(
    [[65, -50], [55, -45], [45, -35], [40, -30], [35, -25], [30, -25], [25, -20], [25, -15]]).reshape(8, 2)


reg_distance_angle = LinearRegression()
reg_distance_angle.fit(distance_pixel, angle4_and_angle7)
reg_distance_angle4_slope, reg_distance_angle7_slope = float(reg_distance_angle.coef_[0]), float(reg_distance_angle.coef_[1])
reg_distance_angle4_itercept, reg_distance_angle7_itercept = float(reg_distance_angle.intercept_[0]), float(reg_distance_angle.intercept_[1])
print("reg_distance_angle4:slope", reg_distance_angle4_slope, reg_distance_angle7_slope,
      "  itercept", reg_distance_angle4_itercept, reg_distance_angle7_itercept)


# 使用numpy的polyfit函数进行最小二乘法拟合，这里我们选择拟合一次多项式（即直线）
coefficients_angle4_distance = numpy.polyfit(distance_pixel_numpy, angle4, 1)

coefficients_angle7_distance = numpy.polyfit(distance_pixel_numpy, angle7, 1)


# 创建一个表示拟合直线的函数
poly_angle4_distance = numpy.poly1d(coefficients_angle4_distance)
print("poly_angle4_distance", poly_angle4_distance)

poly_angle7_distance = numpy.poly1d(coefficients_angle7_distance)
print("poly_angle7_distance", poly_angle7_distance)

plt.scatter(distance_pixel_numpy, angle4, color='blue', label='distance_angle4')


plt.scatter(distance_pixel_numpy, angle7, color='red', label='distance_angle7')


plt.plot(distance_pixel_numpy, poly_angle4_distance(distance_pixel_numpy), color='red', label='distance_angle4_line')
plt.plot(distance_pixel_numpy, poly_angle7_distance(distance_pixel_numpy), color='blue', label='distance_angle7_line')

plt.xlabel('x')
plt.ylabel('y')
plt.legend()


def line_distance_angle(distance):
    line_distance_angle4 = int(-0.2523809523809525*distance + 106.88095238095241)
    line_distance_angle7 = int(0.21309523809523817*distance - 87.09523809523812)
    return line_distance_angle4, line_distance_angle7

plt.show()

