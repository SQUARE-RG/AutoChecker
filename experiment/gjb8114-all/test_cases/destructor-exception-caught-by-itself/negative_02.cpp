#include <iostream>
#include <stdexcept>

class Bar {
public:
    int value;
    Bar() : value(0) {}
    ~Bar() {
        if (value >= 0) {
            throw std::runtime_error("destructor failure"); // CHECK-MESSAGES: :[[@LINE]]:13: warning: {{.*}} [ucassaat-r-2-3-2]
        }
    }
};

int main() {
    try {
        Bar b;
    } catch (const std::exception& e) {
        std::cout << e.what() << '\n';
    }
    return 0;
}
