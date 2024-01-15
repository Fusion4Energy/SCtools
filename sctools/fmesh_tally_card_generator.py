# Python Script, API Version = V22

"""
Select a body and run the script to get its FMESH and TR cards.
The body should be a prism: 6 reactangular and orthogonal faces
"""

def main():
    body = Selection.GetActive().Items[0]
    check_is_hexaedron(body)
    
    points = get_8_points(body)
    points = convert_to_cm(points)
    origin = get_point_closest_to_origin(points)
    points.remove(origin)
    
    all_vectors = get_vectors_from_origin(points, origin)
    axes = get_axes(all_vectors)
    axes = order_axes_closer_to_xyz(axes)
    imesh, jmesh, kmesh = (vec.Magnitude for vec in axes)

    matrix = [normalize(vec) for vec in axes]
    matrix.insert(0, origin)
    
    print_cards(imesh, jmesh, kmesh, matrix)

def check_is_hexaedron(body):
    if len(body.Faces) != 6:
        raise AssertionError("The body doesnt have 6 surfaces")
    
    for face in body.Faces:
         if type(face.Shape.Geometry) != Plane:
             raise AssertionError("The surfaces are not all Planes")
         
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
        if vector.Magnitude < smallest_vector.Magnitude:
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
        if Vector.Cross(x, normalize(axe)).Magnitude < Vector.Cross(x, normalize(x_axe)).Magnitude:
            x_axe = axe

    axes.remove(x_axe)

    y = Vector.Create(0,1,0)
    y_axe = axes[0]
    for axe in axes:
        if Vector.Cross(y, normalize(axe)).Magnitude < Vector.Cross(y, normalize(y_axe)).Magnitude:
            y_axe = axe

    axes.remove(y_axe)
    z_axe = axes[0]
    
    return [x_axe, y_axe, z_axe]

def normalize(vec):
    return vec / vec.Magnitude

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
    

main()

