#include <iostream>

struct Point {
    int x;
    int y;
};

class Shape {
public:
    Shape() {
        p.x = 1;
        p.y = 2;
    }

    int& x_ref() { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-7-3]
        return p.x;
    }

private:
    Point p;
};

int main() {
    Shape s;
    int& rx = s.x_ref();
    rx = 42;
    std::cout << rx << std::endl;
    return 0;
}
