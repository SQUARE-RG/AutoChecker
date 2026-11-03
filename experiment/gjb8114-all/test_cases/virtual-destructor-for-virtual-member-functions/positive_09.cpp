#include <iostream>

class Widget {
public:
    Widget() = default;
    virtual ~Widget();
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
