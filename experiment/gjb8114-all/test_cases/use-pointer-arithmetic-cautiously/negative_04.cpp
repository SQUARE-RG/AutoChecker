#include <cstddef>
#include <iostream>
#include <iterator>

std::ptrdiff_t distance(int* first, int* last) {
    return last - first; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-3-3]
}

int main() {
    int data[4] = {1, 2, 3, 4};
    std::ptrdiff_t d = distance(std::begin(data), std::end(data));
    std::cout << d << '\n';
    return 0;
}
