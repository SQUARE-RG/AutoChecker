#include <iostream>

class Point {
public:
    Point() = default;
    explicit Point(int x) : x_(x), y_(0) {}
    Point(int x, int y) : x_(x), y_(y) {}
    int getX() const { return x_; }
    int getY() const { return y_; }
private:
    int x_{0};
    int y_{0};
};

int main() {
    Point p(3, 4);
    Point q(5);
    std::cout << p.getX() << q.getY() << std::endl;
    return 0;
}
