#include <iostream>

int getMode() { return 1; }

int main() {
    int result = 0;
    switch (getMode()) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-6]
        case 0:
            return 0;
        case 1:
            return 1;
        case 2:
            return 2;
    }
    return result;
}
