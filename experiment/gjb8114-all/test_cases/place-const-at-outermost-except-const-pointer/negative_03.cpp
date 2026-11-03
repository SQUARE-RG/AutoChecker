int main() {
    int a = 1;
    int const &ref = a; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-9-2]
    (void)ref;
    return 0;
}
