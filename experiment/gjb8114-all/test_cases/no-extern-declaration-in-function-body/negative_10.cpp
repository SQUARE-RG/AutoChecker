int gCounter = 0;

void updateCounter(int mode) {
    switch (mode) {
    case 0:
        extern int gCounter; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-17]
        gCounter += 1;
        break;
    default:
        break;
    }
}
