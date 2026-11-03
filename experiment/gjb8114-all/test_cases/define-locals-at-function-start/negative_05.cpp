#include <iostream>

void process(int mode) {
    switch (mode) {
        case 1:
            std::cout << "processing mode 1\n";
            break;
        default:
            std::cout << "default\n";
            break;
    }
    int bonus = 10; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-1-4]
    std::cout << bonus << '\n';
}

int main() {
    process(1);
    return 0;
}
