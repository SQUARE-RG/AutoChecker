int main() {
    int fSpeedO = 1;
    int fSpeed0 = 2; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-10]
    return fSpeedO + fSpeed0;
}
