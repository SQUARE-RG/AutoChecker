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
    Point origin; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-11-1]
    origin.x = 3;
    origin.y = 4;
    translate(origin, 1, 2);
    std::cout << origin.x << ',' << origin.y << std::endl;
    return 0;
}
