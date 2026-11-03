#include <iterator>

void advance_two(int* ptr) {
    ptr += 2; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-3-3]
}

int main() {
    int data[5] = {1, 2, 3, 4, 5};
    advance_two(std::begin(data));
    return 0;
}
