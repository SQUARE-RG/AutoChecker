int main() {
    int a = 1;
    int b = 2;
    bool both = (a > 0) & (b < 10); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-4]
    return both ? 0 : 1;
}
