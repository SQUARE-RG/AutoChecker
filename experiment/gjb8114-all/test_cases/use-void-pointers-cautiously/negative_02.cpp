// Negative case 2: an untyped pointer parameter is used to pass data generically.
#include <iostream>

void printFirstInt(void* data) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-3-2]
    int* value = static_cast<int*>(data);
    std::cout << *value << '\n';
}

int main() {
    int number = 7;
    printFirstInt(&number);
    return 0;
}
