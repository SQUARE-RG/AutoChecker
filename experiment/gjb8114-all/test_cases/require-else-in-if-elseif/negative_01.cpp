int main() {
    int i = 0;
    int x = 0;
    if (i == 0) { x = 1; } else if (i == 1) { x = 2; } // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-1]
    return x;
}
