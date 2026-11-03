#include <iostream>
#include <utility>

class Widget {
public:
    Widget() : a(0), b(0) {}
    Widget(Widget&& other) noexcept;
    int getA() const { return a; }
    int getB() const { return b; }
private:
    int a;
    int b;
};

Widget::Widget(Widget&& other) noexcept : a(other.a), b(other.b) {
    other.a = 0;
    other.b = 0;
}

int main() {
    Widget w;
    Widget w2(std::move(w));
    std::cout << w2.getA() << " " << w2.getB() << std::endl;
    return 0;
}
