int main() {
    int value = 0;
    if ((value = 3.5)) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-1]
        value = value + 1;
    }
    return value;
}
