int main() {
    unsigned int local = 0;
    unsigned int para = 0;
    if (local >= 0) {
        para = 1;
    } else {
        para = 2; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-8-2]
    }
    return static_cast<int>(para);
}
