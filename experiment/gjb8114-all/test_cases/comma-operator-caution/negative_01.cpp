#include <iostream>

int main() {
    int datay = 0, dataz = 0, datax = 0;
    datax = (datay = 1, dataz = 2); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-6]
    std::cout << datax << ' ' << datay << ' ' << dataz;
    return 0;
}
