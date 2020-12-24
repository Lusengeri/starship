import math

class Vector2:
    """A 2-Dimensional Vector Class for 2-D Games"""

    def __init__(self, x = 0.0, y = 0.0):
        self.x = x
        self.y = y

        if hasattr(x, "__getitem__"):
            self.x, self.y = x
            self._v = [float(self.x), float(self.y)]
        else:
            self._v = [float(self.x), float(self.y)]

    def __getitem__(self, index):
        return self._v[index]

    def __setitem__(self, index, value):
        self._v[index] = 1.0 * value

    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ")" 

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar):
        return Vector2(self.x / scalar, self.y / scalar)

    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2)

    def dot(self, other):
        pass

    def cross(self, other):
        pass

    def from_points(p1, p2):
        return Vector2(p2[0] - p1[0], p2[1] - p1[1])

    def normalize(self):
        mag = self.magnitude()
        try:
            self.x /= mag
            self.y /= mag
        except ZeroDivisionError:
            self.x = 0
            self.y = 0
        finally:
            self._v[0] = self.x
            self._v[1] = self.y

    def get_normalized(self):
        normalized = self
        normalized.normalize()
        return norma

    def get_distance_to(self, vect):
        return magnitude(vect - self)

if __name__ == "__main__":
    vec1 = Vector2(3, 4)
    print("vec1: ", vec1)
    vec2 = Vector2(4, 3)
    print("vec2: ", vec2)
    print("vec1 + vec2: ", (vec1+vec2))
    print("vec1 - vec2: ", (vec1-vec2))
    print("vec1.magnitude():", vec1.magnitude())
    print("vec1.x", vec1.x)
