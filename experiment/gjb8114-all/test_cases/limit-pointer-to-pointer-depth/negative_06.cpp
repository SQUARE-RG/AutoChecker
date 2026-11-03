int main() {
    int value = 0;
    int* p = &value;
    int** pp = &p;
    auto ppp = &pp; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-1]
    (void)ppp;
    return 0;
}
