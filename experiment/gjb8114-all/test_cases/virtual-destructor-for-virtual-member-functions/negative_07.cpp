#include <iostream>

class Widget {
public:
    Widget() = default;
    ~Widget() noexcept; // CHECK-MESSAGES: :[[@LINE]]:5: warning: {{.*}} [ucassaat-r-2-3-1]
    virtual void draw();
};

Widget::~Widget() noexcept {}

void Widget::draw() {}

int main() {
    return 0;
}
