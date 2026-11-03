int main() {
    int value = 0;
    if (false) {
        value = 1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-8-2]
    } else {
        value = 2;
    }
    return value;
}
