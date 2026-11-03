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

Widget::Widget(Widget&& other) noexcept : a(other.a) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-2-4]
    other.a = 0;
}

int main() {
    Widget w;
    Widget w2(std::move(w));
    std::cout << w2.getA() << std::endl;
    return 0;
}
