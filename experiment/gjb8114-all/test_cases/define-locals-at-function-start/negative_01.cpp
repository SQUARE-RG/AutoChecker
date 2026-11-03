#include <cstdio>

int computeTotal(int units, int price) {
    int subtotal = units * price;
    subtotal += 5;
    int tax = subtotal / 10;  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-1-4]
    return subtotal + tax;
}

int main() {
    int value = computeTotal(2, 30);
    std::printf("%d\n", value);
    return 0;
}
