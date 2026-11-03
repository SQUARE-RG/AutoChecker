int main() {
    int x = 3;
    int y = 1;
    do {
        --x;
    } while ((x > 0) & (y > 0)); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-4]
    return x;
}
