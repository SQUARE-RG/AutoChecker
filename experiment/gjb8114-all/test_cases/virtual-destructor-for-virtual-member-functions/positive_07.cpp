#include <iostream>

class Widget {
public:
    Widget() = default;
    virtual ~Widget() noexcept;
    virtual void draw();
};

Widget::~Widget() noexcept {}

void Widget::draw() {}

int main() {
    return 0;
}
