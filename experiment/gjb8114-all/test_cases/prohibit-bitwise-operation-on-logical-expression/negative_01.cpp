int main() {
    int x = 0;
    int y = 1;
    if ((x == 1) | (y == 2)) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-4]
        x = 2;
    }
    return 0;
}
