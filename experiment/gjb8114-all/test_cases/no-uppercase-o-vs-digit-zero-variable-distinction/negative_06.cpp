int computeSpeed(int fSpeedO) {
    int fSpeed0 = fSpeedO + 1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-10]
    return fSpeed0;
}

int main() {
    return computeSpeed(0);
}
