#include <iostream>

class Rectangle { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-2-2]
public:
    Rectangle(int width, int height) : width_(width), height_(height) {}
    int Area() const { return width_ * height_; }
private:
    int width_;
    int height_;
};

int main() {
    Rectangle r(3, 4);
    std::cout << r.Area() << '\n';
    return 0;
}
