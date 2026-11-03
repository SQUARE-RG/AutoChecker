int main() {
    int* p = nullptr;
    p = new int(7); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-6-1]
    *p = 9;
    return 0;
}
