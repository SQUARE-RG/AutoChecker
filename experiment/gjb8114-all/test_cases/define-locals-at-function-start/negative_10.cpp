#include <iostream>

template <typename T>
void report(T value) {
    if constexpr (sizeof(T) > 4) {
        std::cout << "large\n";
    } else {
        std::cout << "small\n";
    }
    T copy = value; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-1-4]
    std::cout << copy << '\n';
}

int main() {
    report(42);
    return 0;
}
