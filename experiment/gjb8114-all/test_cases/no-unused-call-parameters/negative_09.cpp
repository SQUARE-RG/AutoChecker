#include <iostream>

class Widget {
public:
    int value = 0;

    friend int sum_with_offset(const Widget& w, int offset) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-7-2]
        return w.value;
    }
};

int main() {
    Widget w;
    w.value = 1;
    std::cout << sum_with_offset(w, 2) << std::endl;
    return 0;
}
