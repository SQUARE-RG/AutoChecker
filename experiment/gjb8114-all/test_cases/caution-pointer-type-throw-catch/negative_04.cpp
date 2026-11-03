#include <iostream>

class Widget {
public:
    void run() {
        try {
            throw this;  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-8-2]
        } catch (Widget* self) {
            std::cout << (self != nullptr) << std::endl;
        }
    }
};

int main() {
    Widget widget;
    widget.run();
    return 0;
}
