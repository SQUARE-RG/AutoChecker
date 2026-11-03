#include <iostream>

int gMode = 2;

class Widget {
public:
    explicit Widget(int seed);
    int chosenMode() const;
private:
    int chosen;
};

Widget::Widget(int seed) {
    switch (gMode) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-2-1]
        case 1:
            chosen = seed;
            break;
        case 2:
            chosen = seed + 1;
            break;
        default:
            chosen = 0;
            break;
    }
}

int Widget::chosenMode() const {
    return chosen;
}

int main() {
    Widget w(10);
    std::cout << w.chosenMode() << '\n';
    return 0;
}
