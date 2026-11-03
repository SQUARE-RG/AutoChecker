int gSpeedO = 1;
int gSpeed0 = 2; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-10]

int main() {
    return gSpeedO + gSpeed0;
}
