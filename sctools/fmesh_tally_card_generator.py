# Python Script, API Version = V22

def check_is_hexaedron(body):
    if len(body.Faces) != 6:
        return False
    
    for face in body.Faces:
         if type(face.Shape.Geometry) != Plane:
             return False
         
    return True

def get_8_points(body):
    repeated_points = []
    for face in body.Faces:
        for edge in face.Edges:
            repeated_points.append(edge.EvalStart().Point)
            repeated_points.append(edge.EvalEnd().Point)
   
    points = []
    for point in repeated_points:
        if point not in points:
            points.append(point)

    return points

def convert_to_cm(points_m):
    points_cm = []
    for point_m in points_m:
        points_cm.append(point_m * 100)
    return points_cm

def get_point_closest_to_origin(points):
    origin = points[0]
    for point in points:
        if point.Vector.Magnitude < origin.Vector.Magnitude:
            origin = point    
    
    return origin

def get_vectors_from_origin(points, origin):
    vectors = []
    for point in points:
        vectors.append(point - origin)
    return vectors

def get_smallest_vector(vectors):
    smallest_vector = vectors[0]
    for vector in vectors:
        if vector.Magnitude < smallest_vector:
            smallest_vector = vector
    return smallest_vector

def get_axes(vectors):
    vec_1 = get_smallest_vector(vectors)
    vectors.remove(vec_1)
    vec_2 = get_smallest_vector(vectors)
    vectors.remove(vec_2)
    
    normal = Vector.Cross(vec_1, vec_2)

    for vector in vectors:
        if Vector.Cross(vector, normal).Magnitude < 1e-5:
            vec_3 = vector
            return [vec_1, vec_2, vec_3]
    
    raise AssertionError("Could not find the Z-Axe")

def order_axes_closer_to_xyz(axes):
    x = Vector.Create(1,0,0)
    x_axe = axes[0]
    for axe in axes:
        if Vector.Cross(x, axe).Magnitude < Vector.Cross(x, x_axe).Magnitude:
            x_axe = axe

    axes.remove(x_axe)

    y = Vector.Create(0,1,0)
    y_axe = axes[0]
    for axe in axes:
        if Vector.Cross(y, axe).Magnitude < Vector.Cross(y, y_axe).Magnitude:
            y_axe = axe

    axes.remove(y_axe)
    z_axe = axes[0]
    
    return [x_axe, y_axe, z_axe]

def normalize(vec):
    return vec / vec.Magnitude

def inverse_matrix(matrix):
    a, b, c = matrix[0]
    d, e, f = matrix[1]
    g, h, i = matrix[2]

    determinant = a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)

    if determinant == 0:
        raise ValueError("Matrix is not invertible")

    inv_det = 1 / determinant

    inv_matrix = [
        [(e * i - f * h) * inv_det, (c * h - b * i) * inv_det, (b * f - c * e) * inv_det],
        [(f * g - d * i) * inv_det, (a * i - c * g) * inv_det, (c * d - a * f) * inv_det],
        [(d * h - e * g) * inv_det, (g * b - a * h) * inv_det, (a * e - b * d) * inv_det]
    ]

    return inv_matrix

def print_cards(imesh, jmesh, kmesh, matrix):
    text = "TR1 \n"
    for vector in matrix:
        text += "     {:.4f} {:.4f} {:.4f} \n".format(vector[0], vector[1], vector[2])
    
    text += "FMESH4:n  \n"
    text+= "     imesh {:.2f} iints 10 \n".format(imesh)
    text+= "     jmesh {:.2f} jints 10 \n".format(jmesh)
    text+= "     kmesh {:.2f} kints 10 \n".format(kmesh)
    
    text += "     tr=1"
    
    print(text)
    


body = GetRootPart().GetAllBodies()[0]
if not check_is_hexaedron(body):
    raise AssertionError()
points = get_8_points(body)
points = convert_to_cm(points)
origin = get_point_closest_to_origin(points)
points.remove(origin)
all_vectors = get_vectors_from_origin(points, origin)
axes = get_axes(all_vectors)
axes = order_axes_closer_to_xyz(axes)
imesh, jmesh, kmesh = (vec.Magnitude for vec in axes)

matrix = [normalize(vec) for vec in axes]
#matrix = inverse_matrix(matrix)
matrix.insert(0, origin)

print_cards(imesh, jmesh, kmesh, matrix)

