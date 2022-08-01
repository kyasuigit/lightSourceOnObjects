# CS3388B
# Kohei Yasui
# March 14th, 2022
# This class creates a tessel on the objects created in the image.

import numpy as np
from matrix import matrix
from cameraMatrix import cameraMatrix
from lightSource import lightSource
from object import object
from parametricObject import parametricObject
from transform import transform


class tessel:
    # constructor to initialize the faceList instance variable used to create the tessel
    def __init__(self, objectList, camera, light):
        EPSILON = 0.001
        self.__faceList = []
        face_points = []
        light_viewing_coordinates = camera.worldToViewingCoordinates(light.getPosition()) # get the viewing coordinates of light
        light_intensity = light.getIntensity() # store the intensity of the light to be used later.

        for i in objectList: # iterate over objects in objectList
            object_color = i.getColor()
            u = i.getURange()[0]
            u_delta = i.getUVDelta()[0]
            while (u + u_delta) < (i.getURange()[1] + EPSILON): # while the u value is less than the max u range
                v = i.getVRange()[0]
                v_delta = i.getUVDelta()[1]
                while (v + v_delta) < (i.getVRange()[1] + EPSILON): # while the v value is less than the max v range
                    p1 = i.getPoint(u, v)
                    p2 = i.getPoint(u, v + v_delta)
                    p3 = i.getPoint(u + u_delta, v + v_delta) # set 4 points to display the face with varying parameters.
                    p4 = i.getPoint(u + u_delta, v)

                    transform_matrix = i.getT() # find the transformation matrix for the object

                    p1 = transform_matrix * p1
                    p2 = transform_matrix * p2
                    p3 = transform_matrix * p3
                    p4 = transform_matrix * p4 ## transform the points using T

                    p1 = camera.worldToViewingCoordinates(p1)
                    p2 = camera.worldToViewingCoordinates(p2)
                    p3 = camera.worldToViewingCoordinates(p3)
                    p4 = camera.worldToViewingCoordinates(p4) ## convert to viewing coordinates

                    face_points.append(p1)
                    face_points.append(p2) # append to the list of points of the face
                    face_points.append(p3)
                    face_points.append(p4)

                    min_z = self.__minCoordinate(face_points, 2)

                    if not min_z > (camera.getNp() * -1): # if we are not behind the near plane
                        centroid_point = self.__centroid(face_points)
                        normal_vector = self.__vectorNormal(face_points).normalize() ## find centroid and normal vectors

                        if not self.__backFace(centroid_point, normal_vector):
                            S = self.__vectorToLightSource(light_viewing_coordinates, centroid_point).normalize() ## initialize variables for light source
                            R = self.__vectorSpecular(S, normal_vector) ## specular position
                            V = self.__vectorToEye(centroid_point) # vector to eye position
                            color_index = self.__colorIndex(i, normal_vector, S, R, V)
                            face_color = (int(object_color[0] * light_intensity[0] * color_index),
                                          int(object_color[1] * light_intensity[1] * color_index), ## create a tuple for RGB of the face color
                                          int(object_color[2] * light_intensity[2] * color_index))

                            pixel_faces = []
                            for j in face_points: #create a list of pixel faces and have the coordinates listed
                                pixel_faces.append(camera.viewingToPixelCoordinates(j))

                            centroid_pixel = camera.viewingToPixelCoordinates(centroid_point)
                            face = [centroid_pixel.get(2, 0), pixel_faces, face_color] # create a face object that lists its elements
                            self.__faceList.append(face) ## append to the list of faces
                    face_points = []
                    v = v + v_delta ## update values for v and u
                u = u + u_delta

    def __minCoordinate(self, facePoints, coord):
        # Computes the minimum X, Y, or Z coordinate from a list of 3D points
        # Coord = 0 indicates minimum X coord, 1 indicates minimum Y coord, 2 indicates minimum Z coord.
        min = facePoints[0].get(coord, 0)
        for point in facePoints:
            if point.get(coord, 0) < min:
                min = point.get(coord, 0)
        return min

    def __backFace(self, C, N):
        # Computes if a face is a back face with using the dot product of the face centroid with the face normal vector
        return C.dotProduct(N) > 0.0

    def __centroid(self, facePoints):
        # Computes the centroid point of a face by averaging the points of the face
        sum = matrix(np.zeros((4, 1)))
        for point in facePoints:
            sum += point
        return sum.scalarMultiply(1.0 / float(len(facePoints)))

    def __vectorNormal(self, facePoints):
        # Computes the normalized vector normal to a face with the cross product
        U = (facePoints[3] - facePoints[1]).removeRow(3).normalize()
        V = (facePoints[2] - facePoints[0]).removeRow(3).normalize()
        return U.crossProduct(V).normalize().insertRow(3, 0.0)

    def __vectorToLightSource(self, L, C):
        return (L.removeRow(3) - C.removeRow(3)).normalize().insertRow(3, 0.0)

    def __vectorSpecular(self, S, N):
        return S.scalarMultiply(-1.0) + N.scalarMultiply(2.0 * (S.dotProduct(N)))

    def __vectorToEye(self, C):
        return C.removeRow(3).scalarMultiply(-1.0).normalize().insertRow(3, 0.0)

    def __colorIndex(self, object, N, S, R, V):
        # Computes local components of shading
        Id = max(N.dotProduct(S), 0.0)
        Is = max(R.dotProduct(V), 0.0)
        r = object.getReflectance()
        index = r[0] + r[1] * Id + r[2] * Is ** r[3]
        return index

    def getFaceList(self):
        return self.__faceList
