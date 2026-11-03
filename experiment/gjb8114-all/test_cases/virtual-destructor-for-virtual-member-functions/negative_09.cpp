#include <iostream>

class Widget {
public:
    Widget() = default;
    ~Widget(); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-3-1]
    virtual int value() const &;
};

Widget::~Widget() {}

int Widget::value() const & {
    return 42;
}

int main() {
    Widget widget;
    std::cout << widget.value() << '\n';
    return 0;
}
