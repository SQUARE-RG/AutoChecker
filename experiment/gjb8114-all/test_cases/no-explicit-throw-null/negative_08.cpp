#include <cstddef>

int choose(bool flag) {
    return flag ? 42 : throw NULL; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-8-5]
}

int main() {
    return choose(true);
}
