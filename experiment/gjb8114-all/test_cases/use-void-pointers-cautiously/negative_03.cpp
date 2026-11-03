#include <iostream>

struct Point {
    int x;
    int y;
};

void* makePoint(int x, int y) {  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-3-2]
    Point* p = new Point{x, y};
    return p;
}

int main() {
    Point* p = static_cast<Point*>(makePoint(3, 4));
    std::cout << p->x << ", " << p->y << std::endl;
    delete p;
    return 0;
}
