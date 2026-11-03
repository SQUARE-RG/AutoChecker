int main() {
    int mode = 0;
    int* p = new int(7);
    switch (mode) {
        case 0:
            delete p; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-6]
            break;
        default:
            break;
    }
    return 0;
}
