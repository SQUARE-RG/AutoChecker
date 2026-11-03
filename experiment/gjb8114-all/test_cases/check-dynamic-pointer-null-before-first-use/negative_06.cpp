#include <iostream>
#include <new>

int main() {
    int *counter = new (std::nothrow) int(0);
    *counter += 5; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-8]
    std::cout << *counter << '\n';
    delete counter;
    return 0;
}
