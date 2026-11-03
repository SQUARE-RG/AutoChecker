#include <iostream>

struct Point {
    int x;
    int y;
};

void translate(Point& p, int dx, int dy) {
    p.x += dx;
    p.y += dy;
}

int main() {
    Point origin{3, 4};
    translate(origin, 1, 2);
    std::cout << origin.x << ',' << origin.y << std::endl;
    return 0;
}
