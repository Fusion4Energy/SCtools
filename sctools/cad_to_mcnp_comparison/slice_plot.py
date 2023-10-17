# Python Script, API Version = V22

from copy import deepcopy

INSTRUCTIONS_PATH = "plot_instructions.txt"

_path = GetRootPart().Document.Path
_path = "\\".join(_path.split("\\")[0:-1])


class Command:
    def __init__(self, origin=[0, 0, 0], direction=[0, 0, 1], extent=100):
        self.origin = origin
        self.direction = direction
        self.extent = extent
        self.counter = 0

    def __repr__(self):
        return (
            str(self.counter)
            + "; origin "
            + str(self.origin)
            + "; direction "
            + str(self.direction)
            + "; extent "
            + str(self.extent)
        )


def cross_product(a, b):
    result = [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]
    return result


def read_commands(instructions_file_path):
    with open(instructions_file_path, "r") as infile:
        text = infile.read()

    commands = [Command()]
    flag_reading_command = False
    for line in text.splitlines():
        words = line.split()
        for i, word in enumerate(words):
            word = word.lower()

            if word in ["or", "origin"]:
                flag_reading_command = True
                commands[-1].origin = [
                    float(words[i + 1]),
                    float(words[i + 2]),
                    float(words[i + 3]),
                ]
            elif word in ["ex", "extent"]:
                flag_reading_command = True
                commands[-1].extent = float(words[i + 1])
            elif word == "px":
                flag_reading_command = True
                commands[-1].direction = [1, 0, 0]
                commands[-1].origin[0] = float(words[i + 1])
            elif word == "py":
                flag_reading_command = True
                commands[-1].direction = [0, 1, 0]
                commands[-1].origin[1] = float(words[i + 1])
            elif word == "pz":
                flag_reading_command = True
                commands[-1].direction = [0, 0, 1]
                commands[-1].origin[2] = float(words[i + 1])
            elif word in ["bas", "basis"]:
                flag_reading_command = True
                vec1 = [float(words[i + 1]), float(words[i + 2]), float(words[i + 3])]
                vec2 = [float(words[i + 4]), float(words[i + 5]), float(words[i + 6])]
                commands[-1].direction = cross_product(vec1, vec2)

        if words[-1] != "&" and flag_reading_command:
            flag_reading_command = False
            commands.append(deepcopy(commands[-1]))
            commands[-1].counter += 1

    # Remove the last appended Command if there was no info read for it
    if not flag_reading_command:
        commands.pop(-1)

    return commands


def plot_a_slice(command):
    # Create a plane
    # the /100 will convert from cm to mm (not a mistake looks like a SpaceClaim bug)
    origin = Point.Create(
        command.origin[0] / 100,
        command.origin[1] / 100,
        command.origin[2] / 100,
    )
    direction = Direction.Create(*command.direction)
    plane_result = DatumPlaneCreator.Create(origin, direction)
    plane = plane_result.CreatedPlanes[0]

    # Use the plane to cut the geometry
    plane_selection = PlaneSelection.Create(plane)
    ViewHelper.SetSectionPlane(plane_selection)

    CORRECTION_FACTOR = 0.01 * 2
    extent = command.extent * CORRECTION_FACTOR
    ViewHelper.SetProjection(plane.Shape.Geometry.Frame, extent)

    # Save the screenshot
    DocumentSave.Execute(_path + "\\" + str(command) + ".jpg")

    # Clean the scene of created objects
    plane.Delete()


def main():
    commands = read_commands(INSTRUCTIONS_PATH)
    for command in commands:
        plot_a_slice(command)


main()
