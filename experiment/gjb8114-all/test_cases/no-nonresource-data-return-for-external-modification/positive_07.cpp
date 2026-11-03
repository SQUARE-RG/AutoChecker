#include <iostream>

struct Point {
    int x;
    int y;
};

class Shape {
public:
    Shape() {
        p.x = 3;
        p.y = 4;
    }

    const Point& get_point() const {
        return p;
    }

private:
    Point p;
};

int main() {
    Shape s;
    const Point& p = s.get_point();
    std::cout << p.x << p.y << std::endl;
    return 0;
}
