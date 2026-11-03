#include <iostream>

class Widget {
public:
    Widget() : id(0) {}
    int id;
};

int main() {
    int raw[4] = {1, 2, 3, 4};
    int (*block)[4] = &raw;
    Widget *w = reinterpret_cast<Widget*>(block); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-5-1]
    std::cout << w << std::endl;
    return 0;
}
