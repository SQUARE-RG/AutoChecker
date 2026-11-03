#include <iostream>

enum class Color {
    Red,
    Green
};

struct Widget {
    int value;
};

int main() {
    Color color = Color::Red;
    Color* colorPtr = &color;
    Widget* widget = reinterpret_cast<Widget*>(colorPtr); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-5-1]
    (void)widget;
    return 0;
}
