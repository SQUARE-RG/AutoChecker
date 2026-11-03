int main() {
    int value = 7;
    do {
        int value = 0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-7]
        ++value;
    } while (value < 3);
    return 0;
}
