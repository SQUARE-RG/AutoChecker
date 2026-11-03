#include <iostream>

void leakScalar() {
    int* value = new int(42);  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-6-1]
    std::cout << *value << '\n';
}

int main() {
    leakScalar();
    return 0;
}
