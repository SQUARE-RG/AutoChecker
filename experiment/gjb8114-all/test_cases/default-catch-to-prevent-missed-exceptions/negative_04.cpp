#include <stdexcept>

struct Widget {
    Widget() try {
        throw std::runtime_error("ctor fail");
    } catch (const std::runtime_error& e) {  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-8-1]
        (void)e;
    }
};

int main() {
    try {
        Widget w;
    } catch (...) {
    }
    return 0;
}
