#include <cstddef>

int make_value() {
    return (throw NULL, 0); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-8-5]
}

int main() {
    try {
        return make_value();
    } catch (...) {
    }
    return 0;
}
