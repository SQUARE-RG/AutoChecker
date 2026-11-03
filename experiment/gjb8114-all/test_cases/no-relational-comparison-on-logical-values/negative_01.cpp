int main() {
    bool outReg1 = true;
    bool outReg2 = false;
    if (outReg1 > outReg2) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-12-1]
        return 1;
    }
    return 0;
}
