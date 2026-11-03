int main() {
    int value = 0;
    int* p = &value;
    int** pp = &p;
    decltype(&pp) ppp = nullptr; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-1]
    return 0;
}
