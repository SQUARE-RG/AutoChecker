#include <cstdlib>

int main() {
    int i = 0;
    int result = 0;
    while (i < 3) {
        if (i == 0) { result = 1; } else if (i == 1) { result = 2; } // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-1]
        ++i;
    }
    return result;
}
