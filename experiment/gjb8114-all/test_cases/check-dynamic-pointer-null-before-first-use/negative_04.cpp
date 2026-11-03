#include <cstdlib>
#include <iostream>

int main() {
    int* data = static_cast<int*>(std::calloc(1, sizeof(int)));
    std::cout << *data; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-8]
    std::free(data);
    return 0;
}
