#include <iostream>

int gCounter = 5;

class Widget {
public:
    explicit Widget(int seed);
    int get() const;
private:
    int value;
};

Widget::Widget(int seed) : value(gCounter + seed) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-2-1]
}

int Widget::get() const { return value; }

int main() {
    Widget w(3);
    std::cout << w.get() << std::endl;
    return 0;
}
