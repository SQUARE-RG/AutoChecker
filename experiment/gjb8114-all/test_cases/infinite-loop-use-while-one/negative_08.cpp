int spin() {
    int n = 0;
    do { ++n; if (n == 3) break; } while (true); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-9-4]
    return n;
}

int main() {
    return spin() == 3 ? 0 : 1;
}
