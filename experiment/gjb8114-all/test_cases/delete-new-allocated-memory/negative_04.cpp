int main() {
    int* p = nullptr;
    p = new int[4]; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-6-1]
    p[0] = 1;
    p[1] = 2;
    p[2] = 3;
    p[3] = 4;
    return 0;
}
