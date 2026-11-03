#include <iostream>

template <typename T>
int template_sum_eleven(T a1, int a2, int a3, int a4, int a5, int a6, int a7, int a8, int a9, int a10, int a11) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-7-1]
    return static_cast<int>(a1) + a2 + a3 + a4 + a5 + a6 + a7 + a8 + a9 + a10 + a11;
}

int main() {
    std::cout << template_sum_eleven(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11) << std::endl;
    return 0;
}
