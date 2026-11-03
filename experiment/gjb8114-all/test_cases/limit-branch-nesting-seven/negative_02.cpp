#include <iostream>

template <int N>
int constexpr_nested() {
    int result = 0;
    if constexpr (N > 0) {
        if constexpr (N > 1) {
            if constexpr (N > 2) {
                if constexpr (N > 3) {
                    if constexpr (N > 4) {
                        if constexpr (N > 5) {
                            if constexpr (N > 6) {
                                if constexpr (N > 7) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-4-1]
                                    result = 1;
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    return result;
}

int main() {
    std::cout << constexpr_nested<8>() << '\n';
    return 0;
}
