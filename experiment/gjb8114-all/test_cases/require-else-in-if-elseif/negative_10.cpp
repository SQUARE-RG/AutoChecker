#include <cstdlib>

int main() {
    int i = 0;
    int result = 0;
    do {
        if (i == 0) { result = 10; } else if (i == 1) { result = 20; } else if (i == 2) { result = 30; } // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-1]
        ++i;
    } while (i < 3);
    return result;
}
