int main() {
    int fSpeedl = 10;
    int fSpeed1 = 20; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-9]
    return fSpeedl + fSpeed1;
}
