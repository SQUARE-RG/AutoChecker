void configureSpeed() {
    constexpr int fSpeedO = 1;
    constexpr int fSpeed0 = 2; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-10]
    (void)fSpeedO;
    (void)fSpeed0;
}
