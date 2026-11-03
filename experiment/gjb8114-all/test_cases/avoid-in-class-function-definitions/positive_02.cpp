#include <iostream>

class Box {
    friend int Area(const Box& box);

public:
    Box(int width, int height);
    int Width() const;

private:
    int width_;
    int height_;
};

Box::Box(int width, int height) : width_(width), height_(height) {}

int Box::Width() const {
    return width_;
}

int Area(const Box& box) {
    return box.width_ * box.height_;
}

int main() {
    Box box(3, 4);
    std::cout << Area(box) << '\n';
    return 0;
}
