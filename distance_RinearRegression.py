import sklearn
from sklearn.linear_model import LinearRegression
import numpy

distance_pixel = (numpy.array([180, 220, 240, 250, 270,290, 320, 350])).reshape(8, 1)
print(distance_pixel.shape)
print(distance_pixel)
angle4 = (numpy.array([65, 55, 45, 40, 35, 30, 25, 25])).reshape(-1, 1)

angle7 = (numpy.array([-50, -45, -35, -30, -25, -25, -20, -15])).reshape(-1, 1)

angle4_and_angle7 = numpy.array([[65, -50], [55, 45], [45, -35], [40, -30], [35, -25], [30, -25], [25, -20], [25, -15]]).reshape(8, 2)
print(angle4_and_angle7.shape)


reg_distance_angle = LinearRegression()
reg_distance_angle.fit(distance_pixel, angle4_and_angle7)
print("reg_distance_angle4,slope", reg_distance_angle.coef_)
print("reg_distance_angle4,itercept", reg_distance_angle.intercept_)
#
# reg_distance_angle7 = LinearRegression()
# reg_distance_angle7.fit(distance_pixel, angle7)
# print("reg_distance_angle4,slope", reg_distance_angle7.coef_)
# print("reg_distance_angle4,itercept", reg_distance_angle7.intercept_)