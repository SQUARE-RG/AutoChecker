#include <iostream>

int main() {
    int i = 0;
    do {
        switch (i % 3) {
            case 0:
                ++i;
                continue; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-9-3]
            case 1:
                ++i;
                continue;
            case 2:
                ++i;
                break;
        }
        std::cout << "processed: " << i << '\n';
    } while (i < 10);
    return 0;
}
