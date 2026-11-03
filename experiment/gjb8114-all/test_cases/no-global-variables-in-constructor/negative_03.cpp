#include <iostream>

bool gEnabled = true;

class Widget {
public:
    explicit Widget(int input);
    int getValue() const;
private:
    int value;
};

Widget::Widget(int input) {
    if (gEnabled) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-2-1]
        value = input;
    } else {
        value = 0;
    }
}

int Widget::getValue() const {
    return value;
}

int main() {
    Widget w(7);
    return w.getValue() < 0 ? 1 : 0;
}
