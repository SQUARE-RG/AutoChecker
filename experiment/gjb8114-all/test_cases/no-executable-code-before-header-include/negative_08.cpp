volatile int source = 5;
int derived = source;

#include <ciso646> // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-3]

int main() {
    return derived;
}
