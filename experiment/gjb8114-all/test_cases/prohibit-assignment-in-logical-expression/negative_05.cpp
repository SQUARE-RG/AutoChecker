int main() {
    int x = 0;
    int y = 0;
    do {
        ++y;
    } while ((x = y) && x < 3); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-3]
    return 0;
}
