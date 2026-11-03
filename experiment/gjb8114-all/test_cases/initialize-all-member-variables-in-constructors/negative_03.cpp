#include <iostream>

class Widget {
public:
    explicit Widget(int value);
    int getA() const { return a; }
    int getB() const { return b; }
    int getC() const { return c; }
private:
    int a;
    int b;
    int c;
};

Widget::Widget(int value) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-2-4]
    a = value;
    b = value + 1;
}

int main() {
    Widget w(7);
    std::cout << w.getA() << " " << w.getB() << '\n';
    return 0;
}
