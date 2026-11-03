#include <iostream>

int tooManyParameters(int p1, int p2, int p3, int p4, int p5, int p6, int p7, int p8, int p9, int p10, int p11) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-7-1]
    return p1 + p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9 + p10 + p11;
}

int main() {
    std::cout << tooManyParameters(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11) << '\n';
    return 0;
}
