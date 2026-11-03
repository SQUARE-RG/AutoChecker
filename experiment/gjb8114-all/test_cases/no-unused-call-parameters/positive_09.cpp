#include <iostream>

class Widget {
public:
    int value = 0;

    friend int sum_with_offset(const Widget& w, int offset) {
        return w.value + offset;
    }
};

int main() {
    Widget w;
    w.value = 1;
    std::cout << sum_with_offset(w, 2) << std::endl;
    return 0;
}
