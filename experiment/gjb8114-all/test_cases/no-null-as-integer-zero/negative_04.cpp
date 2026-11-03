#define NULL 0

int main() {
    int result = 5 + NULL; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-14]
    return 0;
}
