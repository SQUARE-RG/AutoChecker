#define CLOSE_FN() } // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-1-2]

int main() {
    int value = 0;
    return value;
    CLOSE_FN()
