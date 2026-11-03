#include <cstddef>

void handle(int code) {
    switch (code) {
        case 0:
            throw NULL; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-8-5]
        default:
            break;
    }
}

int main() {
    return 0;
}
